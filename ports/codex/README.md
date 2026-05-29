# canon for Codex

The Codex port gives a workspace the canon persistence pattern without Claude Code hooks:

- `AGENTS.md` carries runtime instructions.
- `MEMORY.md` records decisions and shipped work.
- `ERRORS.md` records failed approaches worth avoiding.
- `.canon/codex/skills/` stores portable canon skill docs.
- `.canon/codex/bin/check-protected-sections.py` verifies protected Markdown blocks.
- `.canon/codex/bin/canon-eval.sh` runs the alpha eval format used by the optimize workflow.

## Install

From this repository:

```bash
scripts/install-codex.sh init --runtime codex --root /path/to/project
```

`install` is an alias for `init`.

The installer writes only missing files by default. If `AGENTS.md`, `MEMORY.md`, or `ERRORS.md` already exists, it skips that file and prints append/replace guidance. Use `--force` only when you have decided to replace existing files.

Use `--dry-run` to preview all writes without creating the target directory or changing files.

Useful options:

```bash
scripts/install-codex.sh init --runtime codex \
  --root /path/to/project \
  --name "Project Name" \
  --user "Noah" \
  --role "owner" \
  --stack "TypeScript, React, Node" \
  --voice "direct, concise, implementation-first"
```

Preview a replacement before using `--force`:

```bash
scripts/install-codex.sh init --runtime codex --root /path/to/project --force --dry-run
```

## Doctor

```bash
scripts/install-codex.sh doctor --runtime codex --root /path/to/project
```

Doctor checks:

- `AGENTS.md` exists.
- `MEMORY.md` exists.
- `ERRORS.md` exists.
- protected-section checker is installed.
- eval runner is installed.
- portable skill docs are installed.
- no unresolved `{{...}}` template placeholders remain in the main files.

## After Install

Ask Codex:

```text
read AGENTS.md, then run scripts/install-codex.sh doctor --runtime codex
```

Then try:

```text
look back over recent work and suggest reusable skills
```

## Portable Skills

The source skill docs in this folder are copied into `.canon/codex/skills/` during install:

- `SKILL-look-back.md`
- `SKILL-protected-sections.md`
- `SKILL-optimize.md`

They are intentionally runtime-light. If Codex later supports first-class repo-local skill discovery, these files can be copied or linked into that location without changing the workspace memory model.
