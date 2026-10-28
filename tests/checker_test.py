"""Tests for check-protected-sections.py: which changes it sees, and its CLI contract.

Usage: python3 checker_test.py WORKDIR
Set CANON_CLONE to the canon checkout under test (default: this repo).
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
CLONE = Path(os.environ.get("CANON_CLONE", Path(__file__).resolve().parent.parent))
CHECKER = CLONE / "hooks/scripts/check-protected-sections.py"
WORK = Path(sys.argv[1])
ENV = {k: v for k, v in os.environ.items() if not k.startswith(("LANG", "LC_", "PYTHONIOENCODING"))}
# A UTF-8 locale gives Python a strict stdout (only the C locale gets surrogateescape); PYTHONIOENCODING
# makes that hold on runners where en_US.UTF-8 isn't installed.
STRICT_UTF8 = {"LANG": "en_US.UTF-8", "PYTHONIOENCODING": "utf-8:strict"}

results = []


def expect(label, got, want, detail=""):
    ok = got == want
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f" (want {want!r}) {detail}"))


def blk(name, body):
    return f'<!-- canon:protected:start name="{name}" -->\n{body}\n<!-- canon:protected:end -->\n'


def git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def make_repo(name, files):
    """A fresh repo with `files` ({path: str or bytes}) committed."""
    repo = WORK / name
    shutil.rmtree(repo, ignore_errors=True)
    repo.mkdir(parents=True)
    git(repo, "-c", "init.defaultBranch=main", "init", "-q")
    git(repo, "config", "user.email", "t@e.x")
    git(repo, "config", "user.name", "t")
    for rel, content in files.items():
        write(repo / rel, content)
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", "base")
    return repo


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))


def check(repo, *args, env=None):
    env = {**ENV, **(env or {})}
    p = subprocess.run([sys.executable, str(CHECKER), *args], cwd=repo, capture_output=True, env=env)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def failures(out):
    return [line[2:] for line in out.splitlines() if line.startswith("x ")]


shutil.rmtree(WORK, ignore_errors=True)
WORK.mkdir(parents=True)

print("== CLI contract")
repo = make_repo("clean", {"notes.md": blk("b", "Original.")})
code, out, _ = check(repo)
expect("clean repo: exit 0", code, 0)
expect("clean repo: stdout", out, "[canon protected-sections]\nok: protected sections are intact\n")
write(repo / "notes.md", blk("b", "Rewritten."))
code, out, _ = check(repo)
expect("touched block: exit 1", code, 1)
expect("touched block: stdout", out, "[canon protected-sections]\n"
       'x notes.md (working tree): touched protected block "b" (lines 1-3)\n\n'
       "To proceed, explicitly confirm: I approve editing protected section: <name>\n")
expect("--allow=b: exit 0", check(repo, "--allow=b")[0], 0)
expect("--allow=-dash (another block): still exit 1", check(repo, "--allow=-dash")[0], 1)
code, out, err = check(WORK)
expect("outside a git repo: exit 2", (code, err.strip()), (2, "[canon protected-sections] not inside a git repository"))

print("== File names git diff used to hide")
for name in ["café.md", "日本語/規則.md", "docs/naïve rules.md", "GUIDE.MD", "Notes.Md"]:
    repo = make_repo("names", {name: blk("b", "Original.")})
    write(repo / name, blk("b", "Rewritten by Bash."))
    code, out, _ = check(repo)
    expect(f"{name}: block change reported", (code, failures(out)),
           (1, [f'{name} (working tree): touched protected block "b" (lines 1-3)']))
repo = make_repo("not-md", {"notes.txt": blk("b", "Original."), "page.mdx": blk("b", "Original.")})
write(repo / "notes.txt", blk("b", "Rewritten."))
write(repo / "page.mdx", blk("b", "Rewritten."))
expect("non-.md files are not checked", check(repo)[0], 0)

print("== Renames")
repo = make_repo("rename", {"docs/rules.md": blk("b", "Original.")})
git(repo, "mv", "docs/rules.md", "docs/policy.md")
write(repo / "docs/policy.md", blk("b", "Rewritten after git mv."))
git(repo, "add", "-A")
code, out, _ = check(repo)
expect("git mv + edited block, staged: exit 1", code, 1)
expect("...reported against the old path", failures(out),
       ['docs/rules.md (index): removed or renamed protected block "b" (was lines 1-3)'])

print("== Merge conflicts")
TWO = "# Notes\n\n" + blk("b", "Keep this.") + "\nFooter.\n"
for label, topic, main, want in [
    ("conflict outside the block", TWO.replace("Footer.", "Footer T."), TWO.replace("Footer.", "Footer M."), 0),
    ("conflict inside the block", TWO.replace("Keep this.", "Topic."), TWO.replace("Keep this.", "Main."), 1),
]:
    repo = make_repo("merge", {"notes.md": TWO})
    git(repo, "checkout", "-q", "-b", "topic")
    write(repo / "notes.md", topic)
    git(repo, "commit", "-qam", "topic")
    git(repo, "checkout", "-q", "main")
    write(repo / "notes.md", main)
    git(repo, "commit", "-qam", "main")
    expect(f"{label}: merge stops with a conflict", git(repo, "merge", "topic", check=False).returncode, 1)
    code, out, _ = check(repo)
    expect(f"{label}: exit", code, want, out)
    expect(f"{label}: nothing reported against the index", [f for f in failures(out) if "(index)" in f], [])

print("== Byte order mark before a first-line marker")
repo = make_repo("bom", {"n.md": "﻿" + blk("b", "Keep this.") + "Outside.\n"})
write(repo / "n.md", "﻿" + blk("b", "Keep this.") + "Outside, edited.\n")
expect("change outside the block: exit 0", check(repo)[:2], (0, "[canon protected-sections]\nok: protected sections are intact\n"))
write(repo / "n.md", "﻿" + blk("b", "Changed.") + "Outside.\n")
code, out, _ = check(repo)
expect("change inside the block: reported by name", failures(out), ['n.md (working tree): touched protected block "b" (lines 1-3)'])

print("== Bytes that aren't UTF-8")
for label, env in (("default locale", None), ("UTF-8 locale", STRICT_UTF8)):
    repo = make_repo("bytes", {"a.md": blk("voice", "Original."),
                               "z.md": b'<!-- canon:protected:start name="caf\xe9" -->\nOld.\n<!-- canon:protected:end -->\n',
                               "y.md": b'<!-- canon:protected:start name="b" -->\ncaf\xe9\n<!-- canon:protected:end -->\nout \xff\n'})
    write(repo / "a.md", blk("voice", "Rewritten."))
    write(repo / "z.md", b'<!-- canon:protected:start name="caf\xe9" -->\nNew.\n<!-- canon:protected:end -->\n')
    write(repo / "y.md", b'<!-- canon:protected:start name="b" -->\ncaf\xe9\n<!-- canon:protected:end -->\nout \xfe\n')
    code, out, err = check(repo, env=env)
    expect(f"{label}: no traceback, both blocks reported, byte change outside y.md's block ignored",
           (code, "Traceback" in err, [f.split(" ")[0] for f in failures(out)]), (1, False, ["a.md", "z.md"]), err)
    write(repo / "y.md", b'<!-- canon:protected:start name="b" -->\ncaf\xe8\n<!-- canon:protected:end -->\nout \xff\n')
    code, out, _ = check(repo, env=env)
    expect(f"{label}: byte change inside y.md's block reported", "y.md" in [f.split(" ")[0] for f in failures(out)], True)

print("== Broken markers don't hide other blocks")
DOC = ("## Voice (draft)\n" + blk("voice", "Write plainly.") + "\n## Routing\n\n" + blk("rules", "Requests use the blue gateway."))
repo = make_repo("broken", {"doc.md": DOC})
# Claude Code's Edit with an empty new_string also deletes the newline after old_string: the heading
# and the start marker end up on one line, and the markers no longer parse.
write(repo / "doc.md", DOC.replace(" (draft)\n", "").replace("blue", "green"))
code, out, _ = check(repo)
expect("start marker joined to the heading + another block rewritten", (code, failures(out)), (1, [
    'doc.md: invalid protected marker syntax in working tree: end marker without matching start marker',
    'doc.md (working tree): removed or renamed protected block "voice" (was lines 2-4)',
    'doc.md (working tree): touched protected block "rules" (lines 7-9)',
]))
code, out, _ = check(repo, "--allow=voice")
expect("...with voice approved, the syntax error and rules are still reported", (code, len(failures(out))), (1, 2))
write(repo / "doc.md", DOC.replace("Write plainly.\n<!-- canon:protected:end -->\n", "Write plainly.\n"))
code, out, _ = check(repo, "--allow=voice")
expect("approved block's end marker deleted, nothing else changed: only the syntax error", failures(out), [
    'doc.md: invalid protected marker syntax in working tree: nested protected block "rules" inside "voice"'])
write(repo / "doc.md", DOC + blk("rules", "A second copy."))
code, out, _ = check(repo)
expect("duplicate block name: syntax error, and rules isn't treated as intact", failures(out), [
    'doc.md: invalid protected marker syntax in working tree: duplicate protected block "rules"',
    'doc.md (working tree): removed or renamed protected block "rules" (was lines 8-10)'])

print("== Lenient parse agrees with the strict one on valid text")
spec = importlib.util.spec_from_file_location("checker_mod", CHECKER)
mod = sys.modules["checker_mod"] = importlib.util.module_from_spec(spec)  # dataclasses look the module up
spec.loader.exec_module(mod)
for text in [DOC, "", "no markers\n", "﻿" + blk("b", "x"), blk("a", "") + blk("b", "two\nlines"), "x\r\n" + blk("c", "crlf\r")]:
    expect(f"same blocks for {text[:30]!r}", mod.parse_blocks_lenient(text), mod.parse_blocks(text))

pycache = [str(p) for p in CLONE.rglob("__pycache__") if ".git" not in p.parts]
expect("no __pycache__ written into the plugin", pycache, [])
print(f"--- {sum(results)}/{len(results)} passed")
sys.exit(0 if all(results) else 1)
