#!/usr/bin/env python3
"""Stop Edit/Write calls from changing a canon protected block without the user's approval.

PreToolUse (Edit, Write, MultiEdit): work out what a Markdown file would contain after
the edit and deny the call if it changes an unapproved protected block's text, removes
or renames the block, or breaks its markers. A block is protected when it exists in
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
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin directory

from canon_protected import (
    approval_phrases,
    load_approvals,
    load_checker,
    parse_approvals,
    read_hook_input,
    record_approvals,
)


EDIT_TOOLS = {"Edit", "Write", "MultiEdit"}


def proposed_text(tool: str, tool_input: dict, current: str) -> str | None:
    """The file's text after the tool call, or None if the tool would reject the call."""
    if tool == "Write":
        content = tool_input.get("content")
        return content if isinstance(content, str) else None

    edits = [tool_input] if tool == "Edit" else tool_input.get("edits")
    if not isinstance(edits, list):
        return None
    text = current
    for edit in edits:
        if not isinstance(edit, dict):
            return None
        old, new = edit.get("old_string"), edit.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str):
            return None
        if old == "":
            # An empty old_string only creates a file that doesn't exist yet.
            if text:
                return None
            text = new
            continue
        count = text.count(old)
        replace_all = edit.get("replace_all") is True
        if count == 0 or (count > 1 and not replace_all):
            return None
        text = text.replace(old, new) if replace_all else text.replace(old, new, 1)
    return text


def find_root(checker, path: Path) -> Path | None:
    directory = path.parent
    while not directory.exists() and directory != directory.parent:
        directory = directory.parent
    try:
        return Path(checker.run_git(["rev-parse", "--show-toplevel"], directory).stdout.strip())
    except subprocess.CalledProcessError:
        return None


def body_of(blocks: dict | None, name: str) -> str | None:
    if blocks is None:
        return None
    block = blocks.get(name)
    return None if block is None else block.body


def denied_changes(tool: str, tool_input: dict, path: Path, approved: set[str]) -> list[str]:
    checker = load_checker()
    root = find_root(checker, path)
    if root is None:
        return []
    try:
        relative = path.resolve().relative_to(root.resolve())
    except ValueError:
        return []

    try:
        head_blocks = checker.parse_blocks(checker.read_head(root, relative))
    except checker.ParseError:
        return []  # HEAD's markers are already broken; the Stop hook reports that.
    protected = {name: block for name, block in head_blocks.items() if name not in approved}
    if not protected:
        return []

    current = checker.read_worktree(root, relative)
    proposed = proposed_text(tool, tool_input, current)
    if proposed is None:
        return []

    try:
        current_blocks = checker.parse_blocks(current)
    except checker.ParseError:
        current_blocks = None
    try:
        proposed_blocks = checker.parse_blocks(proposed)
    except checker.ParseError as exc:
        if current_blocks is None or exc.block_name in approved:
            return []
        return [f"{relative}: would break protected block markers ({exc})"]

    changes: list[str] = []
    for name, head_block in protected.items():
        new_body = body_of(proposed_blocks, name)
        if new_body == head_block.body:
            continue  # intact, or restored to HEAD
        if current_blocks is not None and new_body == body_of(current_blocks, name):
            continue  # this call leaves the block as it already was
        action = "remove or rename" if new_body is None else "change"
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
    if not isinstance(file_path, str) or not file_path.endswith(".md"):
        return 0
    try:
        changes = denied_changes(tool, tool_input, Path(file_path), load_approvals(hook_input.get("session_id")))
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
