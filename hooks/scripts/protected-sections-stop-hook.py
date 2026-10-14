#!/usr/bin/env python3
"""Stop hook: tell the agent when a turn left a canon protected block changed without approval.

Runs check-protected-sections.py unchanged and translates its result for Claude
Code. A Stop hook that exits 1 is a non-blocking error: its output never reaches
the model. So on a violation this exits 2 with the report on stderr, which blocks
the stop once and hands the report to the agent.

Blocks the user approved in this session (recorded from their own prompt by
protected-sections-guard.py) are passed to the checker with --allow, so an approved
edit doesn't block. The edit guard stops unapproved Edit/Write calls before they
run; this hook catches whatever else changed a block, such as Bash or the user.

stop_hook_active is true when the agent is already continuing because a Stop hook
blocked. The check is skipped then, so it blocks at most once per stop.

Each violation is reported once per session. A violation is a file, a block, and
the block's current text, so line shifts don't repeat a report but a further edit
to the block does. Violations that clear are forgotten, so if one comes back it is
reported again. The record lives in the repository's git directory.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep __pycache__ out of the plugin directory

from canon_protected import (
    CHECKER,
    approval_phrases,
    delete,
    load_approvals,
    load_checker,
    read_hook_input,
    read_json,
    session_file,
    write_json,
)


FAILURE_RE = re.compile(
    r'^x (?P<path>.+) \((?P<source>working tree|index)\): '
    r'(?P<kind>touched|removed or renamed) protected block "(?P<name>[^"]+)"'
)


def violation_key(checker, root: Path, failure: str) -> str:
    """Identify a violation by file, block and the block's current text, not line numbers."""
    match = FAILURE_RE.match(failure)
    if match is None:
        # Marker syntax errors carry no line numbers, so the line itself is stable.
        return failure
    path, name = Path(match["path"]), match["name"]
    try:
        if match["source"] == "index":
            text = checker.read_index(root, path)
        else:
            text = checker.read_worktree(root, path)
        block = checker.parse_blocks(text).get(name)
    except (checker.ParseError, OSError, ValueError, subprocess.SubprocessError):
        block = None
    if block is None:
        state = "missing"
    else:
        state = hashlib.sha256(block.body.encode("utf-8", "surrogateescape")).hexdigest()
    return "\0".join([match["kind"], path.as_posix(), name, state])


def load_reported(path: Path | None) -> set[str]:
    data = read_json(path)
    reported = data.get("reported") if isinstance(data, dict) else None
    if not isinstance(reported, list):
        return set()
    return {key for key in reported if isinstance(key, str)}


def save_reported(path: Path | None, keys: set[str]) -> None:
    """Record the violations reported so far. If this fails, the next stop reports them again."""
    if keys:
        write_json(path, {"reported": sorted(keys)})
    else:
        delete(path)


def unreported(failures: list[str], state: Path | None) -> list[str]:
    """Record the current violations for this session and return the ones not reported before."""
    checker = load_checker()
    root = checker.repo_root()
    keys = [violation_key(checker, root, failure) for failure in failures]
    reported = load_reported(state)
    save_reported(state, set(keys))
    return [failure for failure, key in zip(failures, keys) if key not in reported]


def block_reason(failures: list[str]) -> str:
    phrases = approval_phrases(failures)
    lines = ["[canon protected-sections] Protected Markdown blocks differ from HEAD, and the user hasn't approved them in this session:"]
    lines.extend(failures)
    lines.append("")
    lines.append("Before you finish, tell the user which protected block changed, by file and block name.")
    lines.append(
        "- If you made the change, revert it, or ask the user to approve it by replying with "
        + " / ".join(f'"{phrase}"' for phrase in phrases)
        + "."
    )
    lines.append("- If you did not make the change (for example, the user edited the file), report it and leave it.")
    lines.append("This check blocks once; your next reply ends the turn.")
    return "\n".join(lines)


def main() -> int:
    hook_input = read_hook_input()
    if hook_input.get("stop_hook_active") is True:
        return 0

    session_id = hook_input.get("session_id")
    command = [sys.executable, str(CHECKER)]
    # --allow=NAME, not "--allow NAME": a name starting with "-" would otherwise be read as an option.
    command.extend(f"--allow={name}" for name in sorted(load_approvals(session_id)))
    result = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    # 2: not a git repository, so nothing to compare against.
    if result.returncode == 2:
        return 0

    state = session_file(session_id)

    # 0: intact. Forget anything reported earlier, so a violation that comes back is reported again.
    if result.returncode == 0:
        save_reported(state, set())
        return 0

    failures = [line for line in result.stdout.splitlines() if line.startswith("x ")]
    if result.returncode == 1 and failures:
        try:
            new_failures = unreported(failures, state)
        except Exception as exc:
            # The memory only suppresses repeats. If it breaks, report everything rather than nothing.
            new_failures = failures
            print(f"[canon protected-sections] per-session memory unavailable: {exc!r}", file=sys.stderr)
        if not new_failures:
            return 0
        print(block_reason(new_failures), file=sys.stderr)
        return 2

    # Anything else is the checker failing (an uncaught exception also exits 1, with no
    # "x " lines). Report it as a non-blocking error rather than blocking the stop.
    print("[canon protected-sections] checker failed", file=sys.stderr)
    print((result.stderr or result.stdout).strip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
