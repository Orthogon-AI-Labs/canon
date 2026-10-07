#!/usr/bin/env python3
"""Stop hook: tell the agent when a turn touched a canon protected block.

Runs check-protected-sections.py unchanged and translates its result for Claude
Code. A Stop hook that exits 1 is a non-blocking error: its output never reaches
the model. So on a violation this exits 2 with the report on stderr, which blocks
the stop once and hands the report to the agent.

stop_hook_active is true when the agent is already continuing because a Stop hook
blocked. The check is skipped then, so it blocks at most once per stop and an
approved edit can still finish.

Each violation is reported once per session. A violation is a file, a block, and
the block's current text, so line shifts don't repeat a report but a further edit
to the block does. Violations that clear are forgotten, so if one comes back it is
reported again. The record lives in the repository's git directory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


CHECKER = Path(__file__).with_name("check-protected-sections.py")
BLOCK_NAME_RE = re.compile(r'protected block "([^"]+)"')
FAILURE_RE = re.compile(
    r'^x (?P<path>.+) \((?P<source>working tree|index)\): '
    r'(?P<kind>touched|removed or renamed) protected block "(?P<name>[^"]+)"'
)
SESSION_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,128}")
STATE_DIR = "canon-protected-sections"
STATE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
APPROVAL = "I approve editing protected section: {}"


def read_hook_input() -> dict:
    raw = sys.stdin.read() if not sys.stdin.isatty() else ""
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("[canon protected-sections] ignoring hook input that is not JSON", file=sys.stderr)
        return {}
    return data if isinstance(data, dict) else {}


def load_checker():
    spec = importlib.util.spec_from_file_location("canon_check_protected_sections", CHECKER)
    module = importlib.util.module_from_spec(spec)
    # @dataclass resolves the checker's string annotations through sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


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


def state_file(session_id: object) -> Path | None:
    """Per-session record of reported violations, or None when there is no usable session id."""
    if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
        return None
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", STATE_DIR],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip()) / f"{session_id}.json"


def load_reported(path: Path | None) -> set[str]:
    if path is None:
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    reported = data.get("reported") if isinstance(data, dict) else None
    if not isinstance(reported, list):
        return set()
    return {key for key in reported if isinstance(key, str)}


def save_reported(path: Path | None, keys: set[str]) -> None:
    """Record the violations reported so far. If this fails, the next stop reports them again."""
    if path is None:
        return
    try:
        if not keys:
            if path.exists():
                path.unlink()
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps({"reported": sorted(keys)}), encoding="utf-8")
        os.replace(tmp, path)
        # Sessions that ended with violations still pending leave a file behind; drop old ones.
        cutoff = time.time() - STATE_MAX_AGE_SECONDS
        for stale in path.parent.glob("*.json"):
            if stale != path and stale.stat().st_mtime < cutoff:
                stale.unlink()
    except OSError:
        pass


def unreported(failures: list[str], state: Path | None) -> list[str]:
    """Record the current violations for this session and return the ones not reported before."""
    checker = load_checker()
    root = checker.repo_root()
    keys = [violation_key(checker, root, failure) for failure in failures]
    reported = load_reported(state)
    save_reported(state, set(keys))
    return [failure for failure, key in zip(failures, keys) if key not in reported]


def block_reason(failures: list[str]) -> str:
    names: list[str] = []
    for failure in failures:
        for name in BLOCK_NAME_RE.findall(failure):
            if name not in names:
                names.append(name)
    phrases = [APPROVAL.format(name) for name in names] or [APPROVAL.format("<name>")]

    lines = ["[canon protected-sections] Protected Markdown blocks differ from HEAD:"]
    lines.extend(failures)
    lines.append("")
    lines.append("Before you finish, tell the user which protected block changed, by file and block name.")
    lines.append(
        "- If the user already approved that block in this conversation with "
        + " / ".join(f'"{phrase}"' for phrase in phrases)
        + ", keep the edit and say it was made under that approval."
    )
    lines.append(
        "- Otherwise, if you made the change, do not treat it as accepted: revert it, or ask the user "
        "to approve it by replying with that exact phrase."
    )
    lines.append("- If you did not make the change (for example, the user edited the file), report it and leave it.")
    lines.append("This check blocks once; your next reply ends the turn.")
    return "\n".join(lines)


def main() -> int:
    hook_input = read_hook_input()
    if hook_input.get("stop_hook_active") is True:
        return 0

    result = subprocess.run(
        [sys.executable, str(CHECKER)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    # 2: not a git repository, so nothing to compare against.
    if result.returncode == 2:
        return 0

    state = state_file(hook_input.get("session_id"))

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
