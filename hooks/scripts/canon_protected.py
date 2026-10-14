"""Shared helpers for canon's protected-sections hooks.

Used by protected-sections-stop-hook.py and protected-sections-guard.py. The checker,
check-protected-sections.py, does not import this: it stays a standalone CLI that the
Codex port copies on its own.

Per-session state lives in the git directory of the session's working directory
(.git/canon-protected-sections/), so it never shows in git status:

- <session_id>.json            violations the Stop hook has already reported
- <session_id>.approvals.json  blocks the user approved with the approval phrase
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


CHECKER = Path(__file__).with_name("check-protected-sections.py")
STATE_DIR = "canon-protected-sections"
STATE_MAX_AGE_SECONDS = 7 * 24 * 60 * 60
SESSION_ID_RE = re.compile(r"[A-Za-z0-9_-]{1,128}")
APPROVAL = "I approve editing protected section: {}"
# The phrase has to open a line or follow punctuation ("Ok, I approve ..."), so "Should I
# approve editing protected section: x?" doesn't count. A quoted name may contain spaces;
# a bare name ends at whitespace.
APPROVAL_RE = re.compile(
    r'(?:^|(?<=[.!?,;:–—-])[ \t]+)[ \t]*I approve editing protected section:[ \t]*(?:"([^"\n]+)"|(\S+))',
    re.IGNORECASE | re.MULTILINE,
)
TRAILING_PUNCTUATION = ".,;:!?)"
NAME_QUOTES = "`'\"*"
BLOCK_NAME_RE = re.compile(r'protected block "([^"]+)"')


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


def session_file(session_id: object, suffix: str = "") -> Path | None:
    """A per-session state file, or None when there is no usable session id or git directory."""
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
    return Path(result.stdout.strip()) / f"{session_id}{suffix}.json"


def read_json(path: Path | None) -> object:
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def write_json(path: Path | None, data: object) -> bool:
    """Atomically write a state file and prune other sessions' week-old files. False if it failed."""
    if path is None:
        return False
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps(data), encoding="utf-8")
        os.replace(tmp, path)
        session = path.name.split(".", 1)[0]
        cutoff = time.time() - STATE_MAX_AGE_SECONDS
        for stale in path.parent.glob("*.json"):
            if stale.name.split(".", 1)[0] != session and stale.stat().st_mtime < cutoff:
                stale.unlink()
    except OSError:
        return False
    return True


def delete(path: Path | None) -> None:
    if path is None:
        return
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def parse_approvals(prompt: str) -> list[str]:
    """Block names approved in a user prompt, in order, without duplicates."""
    names: list[str] = []
    for quoted, bare in APPROVAL_RE.findall(prompt):
        name = quoted.strip() if quoted else bare.rstrip(TRAILING_PUNCTUATION).strip(NAME_QUOTES).rstrip(TRAILING_PUNCTUATION)
        if name and name not in names:
            names.append(name)
    return names


def approval_phrases(lines: list[str]) -> list[str]:
    """The approval phrase for each block named in a report, or the template if none is named."""
    names: list[str] = []
    for line in lines:
        for name in BLOCK_NAME_RE.findall(line):
            if name not in names:
                names.append(name)
    return [APPROVAL.format(name) for name in names] or [APPROVAL.format("<name>")]


def load_approvals(session_id: object) -> set[str]:
    data = read_json(session_file(session_id, ".approvals"))
    names = data.get("approved") if isinstance(data, dict) else None
    if not isinstance(names, list):
        return set()
    return {name for name in names if isinstance(name, str)}


def record_approvals(session_id: object, names: list[str]) -> bool:
    path = session_file(session_id, ".approvals")
    if path is None:
        return False
    return write_json(path, {"approved": sorted(load_approvals(session_id) | set(names))})
