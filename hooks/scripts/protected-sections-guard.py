#!/usr/bin/env python3
"""Stop Edit/Write calls from changing a canon protected block without the user's approval.

PreToolUse (Edit, Write, MultiEdit): work out what a Markdown file would contain after
the edit (as Claude Code's Edit tool writes it; see claude_edit.py) and deny the call if
it changes an unapproved protected block's text, removes or renames the block, or breaks
its markers. Every block is checked, even when other markers in the file are broken. A block is protected when it exists in
HEAD, the same baseline check-protected-sections.py uses. An edit that leaves a block
as it already was, or restores it to HEAD, is allowed.

UserPromptSubmit: when the user's own message contains "I approve editing protected
section: <name>", record that block as approved for the rest of the session. Only the
user's prompt is read, so the agent can't approve an edit on the user's behalf.

When the guard can't tell what an edit does (an old_string it can't find, a file
outside git, its own error), it allows the call. The Stop hook still checks the
result, and it also catches changes made some other way, such as through Bash.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin directory

from claude_edit import apply_edits
from canon_protected import (
    approval_phrases,
    load_approvals,
    load_checker,
    parse_approvals,
    read_hook_input,
    record_approvals,
)


EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}


def proposed_text(tool: str, tool_input: dict, current: str | None) -> str | None:
    """The file's text after the tool call, or None if the tool would reject the call.

    current is the file as it is now (None if it doesn't exist). Line endings are
    normalised the way check-protected-sections.py reads files, so the result compares
    with HEAD the same way the Stop check will.
    """
    if tool == "Write":
        content = tool_input.get("content")
        text = content if isinstance(content, str) else None
    else:
        edits = [tool_input] if tool == "Edit" else tool_input.get("edits")
        if not isinstance(edits, list):
            return None
        steps = []
        for edit in edits:
            if not isinstance(edit, dict):
                return None
            old, new = edit.get("old_string"), edit.get("new_string")
            if not isinstance(old, str) or not isinstance(new, str):
                return None
            steps.append((old, new, edit.get("replace_all") is True))
        text = apply_edits(current, steps)
    return None if text is None else universal_newlines(text)


def universal_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def locate(checker, path: Path) -> tuple[Path, Path] | None:
    """The file's repository root and its path there in git's spelling, or None outside git."""
    directory, tail = path.parent, [path.name]
    while not directory.exists() and directory != directory.parent:
        tail.insert(0, directory.name)
        directory = directory.parent
    try:
        # git reports the directory's real spelling, even when the path used another case.
        lines = checker.run_git(["rev-parse", "--show-toplevel", "--show-prefix"], directory).stdout.split("\n")
    except subprocess.CalledProcessError:
        return None
    root, relative = Path(lines[0]), Path(lines[1] if len(lines) > 1 else "", *tail)
    if path.exists():
        # On a case-insensitive filesystem NOTES.md opens the tracked notes.md.
        listed = checker.run_git(["ls-files", "-z", "--", f":(icase,literal){relative.as_posix()}"], root, check=False)
        names = [name for name in listed.stdout.split("\0") if name]
        if relative.as_posix() not in names:
            same = [name for name in names if os.path.samefile(root / name, path)]
            if len(same) == 1:
                relative = Path(same[0])
    return root, relative


def bodies(checker, text: str) -> dict[str, list[str]]:
    """The body of every block in text by name, found even when other markers are broken."""
    return {name: [block.body for block in found] for name, found in checker.parse_blocks_lenient(text).items()}


def denied_changes(tool: str, tool_input: dict, path: Path, approved: set[str]) -> list[str]:
    checker = load_checker()
    located = locate(checker, path)
    if located is None:
        return []
    root, relative = located

    # A name that appears twice in HEAD has no single baseline; the Stop check reports it.
    protected = {
        name: found[0] for name, found in bodies(checker, checker.read_head(root, relative)).items()
        if len(found) == 1 and name not in approved
    }
    if not protected:
        return []

    raw = path.read_bytes().decode("utf-8", "surrogateescape") if path.is_file() else None
    proposed = proposed_text(tool, tool_input, raw)
    if proposed is None:
        return []
    current = universal_newlines(raw or "")
    current_blocks, proposed_blocks = bodies(checker, current), bodies(checker, proposed)

    changes: list[str] = []
    for name, head_body in protected.items():
        found = proposed_blocks.get(name, [])
        if found == [head_body]:
            continue  # intact, or restored to HEAD
        if found == current_blocks.get(name, []):
            if found:
                continue  # this call leaves the block as it already was
            # The block's markers are already broken, so find its text instead. An empty body
            # can't be found that way, and counts as changed.
            if head_body and current.count(head_body) == proposed.count(head_body):
                continue
        if not found:
            action = "remove, rename or break the markers of"
        elif len(found) > 1:
            action = "duplicate"
        else:
            action = "change"
        changes.append(f'{relative}: would {action} protected block "{name}"')
    return changes


def deny_reason(changes: list[str]) -> str:
    lines =["[canon protected-sections] Blocked: this edit changes a protected block the user hasn't approved in this session."]
    lines.extend(changes)
    lines.append("")
    lines.append(
        "Don't make this change another way (Bash, another tool, or removing the markers). "
        "Tell the user which block you need to change and why, and ask them to approve it by replying:"
    )
    lines.extend(approval_phrases(changes))
    lines.append("Their approval is recorded when they send it; then retry the edit.")
    return "\n".join(lines)


def guard_tool_call(hook_input: dict) -> int:
    tool = hook_input.get("tool_name")
    tool_input = hook_input.get("tool_input")
    if tool not in EDIT_TOOLS or not isinstance(tool_input, dict):
        return 0
    file_path = tool_input.get("file_path")
    if not isinstance(file_path, str) or not file_path.lower().endswith(".md"):
        return 0
    try:
        # Lexically, as Claude Code resolves it: "dir/../x.md" is x.md even if dir is a symlink.
        path = Path(os.path.abspath(file_path))
        changes = denied_changes(tool, tool_input, path, load_approvals(hook_input.get("session_id")))
    except Exception as exc:
        # Allow rather than block every edit on a guard bug; the Stop hook still checks.
        print(f"[canon protected-sections] edit guard skipped: {exc!r}", file=sys.stderr)
        return 1
    if changes:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": deny_reason(changes),
            }
        }))
    return 0


def record_prompt_approvals(hook_input: dict) -> int:
    prompt = hook_input.get("prompt")
    if not isinstance(prompt, str):
        return 0
    names = parse_approvals(prompt)
    if not names:
        return 0
    listed = ", ".join(f'"{name}"' for name in names)
    if record_approvals(hook_input.get("session_id"), names):
        print(f"canon: recorded the user's approval to edit protected section {listed} for this session.")
    else:
        print(
            f"canon: the user approved editing protected section {listed}, but canon couldn't record it "
            "(no writable git directory here), so its edit guard will still block those edits. "
            "Tell the user; they can make the edit themselves or remove the markers."
        )
    return 0


def main() -> int:
    hook_input = read_hook_input()
    event = hook_input.get("hook_event_name")
    if event == "PreToolUse":
        return guard_tool_call(hook_input)
    if event == "UserPromptSubmit":
        return record_prompt_approvals(hook_input)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
