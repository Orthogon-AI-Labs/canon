"""Shared helpers for canon's protected-sections hooks.

Used by protected-sections-stop-hook.py and protected-sections-guard.py. The checker,
check-protected-sections.py, does not import this: it stays a standalone CLI that the
Codex port copies on its own.

Per-session state lives in the git directory of the repository the session started in
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
PHRASE_RE = re.compile(r"I approve editing protected section:", re.IGNORECASE)
# Where the phrase may start: a line (after a blockquote ">", a bullet or a number) or a sentence.
LINE_START_RE = re.compile(r"[ \t]*(?:>[ \t]*)*(?:(?:[-*+]|\d+[.)])[ \t]+)?")
SENTENCE_START_RE = re.compile(r"[.!?,][ \t]+$")
OPENERS = "*\"\u201c'\u2018"  # bold, italics or quotes around the whole phrase
CLOSERS = "*\"\u201d'\u2019"
NAME_QUOTES = {'"': '"', "\u201c": "\u201d", "`": "`", "'": "'", "\u2018": "\u2019"}
BARE_NAME_RE = re.compile(r"[\w-]+(?:[./][\w-]+)*")  # printed without quotes; anything else is quoted
FENCE_RE = re.compile(r"[ \t]*(?:```|~~~)")
# Claude Code also sends text it generates as a prompt, such as a background task's
# <task-notification>, which can hold agent-written text or command output.
SYSTEM_PROMPT_RE = re.compile(r"\s*<[A-Za-z][\w-]*[\s>]")
SYSTEM_BLOCK_RE = re.compile(r"<(task-notification)>.*?</\1>", re.DOTALL)
BANNER = "[canon protected-sections]"
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
    """A per-session state file, or None when there is no usable session id or git directory.

    The file is in the repository the session started in (CLAUDE_PROJECT_DIR), not the hook's
    current directory, which follows the agent's `cd`.
    """
    if not isinstance(session_id, str) or not SESSION_ID_RE.fullmatch(session_id):
        return None
    base = Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--git-path", STATE_DIR],
            cwd=base,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return base / result.stdout.strip() / f"{session_id}{suffix}.json"


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
    except OSError:
        return False
    prune(path)
    return True


def prune(path: Path) -> None:
    """Remove other sessions' week-old state files. A file that can't be removed is left."""
    session = path.name.split(".", 1)[0]
    cutoff = time.time() - STATE_MAX_AGE_SECONDS
    try:
        files = list(path.parent.glob("*.json"))
    except OSError:
        return
    for stale in files:
        try:
            if stale.name.split(".", 1)[0] != session and stale.stat().st_mtime < cutoff:
                stale.unlink()
        except OSError:
            continue


def delete(path: Path | None) -> None:
    if path is None:
        return
    try:
        if path.exists():
            path.unlink()
    except OSError:
        pass


def parse_approvals(prompt: str) -> list[str]:
    """Block names the user approved in their own message, in order, without duplicates.

    The phrase counts where it starts a line (after a bullet, a number, ">", bold or a quote
    mark) or a sentence, and the name has to end the line or its sentence. It doesn't count
    in a question, in a code block, in a prompt Claude Code generated, or in a message that
    quotes canon's own report (which contains the phrase).
    """
    if SYSTEM_PROMPT_RE.match(prompt) or BANNER in prompt:
        return []
    lines = SYSTEM_BLOCK_RE.sub("", prompt).splitlines()
    names: list[str] = []
    fenced = False
    for index, line in enumerate(lines):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        following = next((later for later in lines[index + 1:] if later.strip()), "")
        if fenced or set(following.strip()) == {"?"}:
            continue
        for match in PHRASE_RE.finditer(line):
            name = approved_name(line[:match.start()], line[match.end():])
            if name and name not in names:
                names.append(name)
    return names


def approved_name(before: str, after: str) -> str | None:
    """The block name in one use of the phrase, or None if this use isn't an approval."""
    before = before.rstrip(OPENERS)
    if not (LINE_START_RE.fullmatch(before) or SENTENCE_START_RE.search(before)):
        return None  # "Should I approve ...", "say: I approve ..."
    after = after.lstrip(" \t")
    if after[:1] in NAME_QUOTES:
        end = after.find(NAME_QUOTES[after[0]], 1)
        if end == -1:
            return None
        name, rest = after[1:end].strip(), after[end + 1:]
    else:
        name = re.match(r'[^\s"\u201c\u201d`*]*', after).group(0).rstrip(".,;:!?)")
        rest = after[len(name):]
    rest = rest.lstrip(CLOSERS)
    if not name or rest[:1] == "?" or (rest.strip() and rest[0] not in ".!,;"):
        return None  # a question, or the sentence goes on ("... rules is what I won't say")
    return name


def approval_phrase(name: str) -> str:
    """The phrase for one block, quoting a name that parse_approvals would otherwise misread."""
    return APPROVAL.format(name if BARE_NAME_RE.fullmatch(name) else f'"{name}"')


def approval_phrases(lines: list[str]) -> list[str]:
    """The approval phrase for each block named in a report, or the template if none is named."""
    names: list[str] = []
    for line in lines:
        for name in BLOCK_NAME_RE.findall(line):
            if name not in names:
                names.append(name)
    return [approval_phrase(name) for name in names] or [APPROVAL.format("<name>")]


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
