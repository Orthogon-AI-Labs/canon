#!/usr/bin/env python3
"""Stop hook: tell the agent when a turn touched a canon protected block.

Runs check-protected-sections.py unchanged and translates its result for Claude
Code. A Stop hook that exits 1 is a non-blocking error: its output never reaches
the model. So on a violation this exits 2 with the report on stderr, which blocks
the stop once and hands the report to the agent.

stop_hook_active is true when the agent is already continuing because a Stop hook
blocked. The check is skipped then, so it blocks at most once per stop and an
approved edit can still finish.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


CHECKER = Path(__file__).with_name("check-protected-sections.py")
BLOCK_NAME_RE = re.compile(r'protected block "([^"]+)"')
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

    # 0: intact. 2: not a git repository, so nothing to compare against.
    if result.returncode in (0, 2):
        return 0

    failures = [line for line in result.stdout.splitlines() if line.startswith("x ")]
    if result.returncode == 1 and failures:
        print(block_reason(failures), file=sys.stderr)
        return 2

    # Anything else is the checker failing (an uncaught exception also exits 1, with no
    # "x " lines). Report it as a non-blocking error rather than blocking the stop.
    print("[canon protected-sections] checker failed", file=sys.stderr)
    print((result.stderr or result.stdout).strip(), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
