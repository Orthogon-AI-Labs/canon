# AGENTS.md — {{PROJECT_NAME}}

> Codex workspace instructions. Read this file at the start of every session, then use `MEMORY.md` and `ERRORS.md` as the durable project context.

## Project Context

- **Project:** {{PROJECT_NAME}}
- **Primary collaborator:** {{USER_NAME}} ({{USER_ROLE}})
- **Stack:** {{STACK}}
- **Voice / working style:** {{VOICE}}

## Session Start

At the start of each session:

1. Read `MEMORY.md` when present.
2. Read `ERRORS.md` when present.
3. Scan this file for protected sections and repo-local skill pointers.
4. If either memory file is missing, continue normally and mention the gap only when it matters to the task.

## Implementation Discipline

Before implementation-shaped work, consult `ERRORS.md` for similar prior failures. Surface a match only when it clearly applies.

When a meaningful decision lands, or when a shipped unit of work changes the shape of the project, append a concise entry to `MEMORY.md`. Keep high-signal history; do not log trivial one-shot fixes.

Respect protected sections in Markdown files:

```markdown
<!-- canon:protected:start name="stable-invariant" -->
This section requires explicit approval before edits.
<!-- canon:protected:end -->
```

Run the protected-section checker before finalizing Markdown edits when it is available:

```bash
python3 .canon/codex/bin/check-protected-sections.py
```

If the user explicitly approves a protected edit, pass the section name:

```bash
python3 .canon/codex/bin/check-protected-sections.py --allow stable-invariant
```

## Repo-Local Skills

Prefer repo-local canon skills before broad reasoning. In Codex workspaces installed by canon, portable skill docs live under:

```text
.canon/codex/skills/
```

Use them when the user asks to:

- look back over recent work and identify reusable workflows
- check or edit protected Markdown sections
- evaluate or optimize a skill with bounded, measured edits

## Canon Workflows

Use the look-back workflow when asked to mine recent work. Start with a shortlist and evidence before creating or extending any asset.

Use the protected-sections workflow when asked to lock, inspect, or verify important Markdown blocks.

Use the optimize workflow only when an eval exists or the user asks you to create one first. Run evals with `.canon/codex/bin/canon-eval.sh <eval>.yaml` (use a `.json` eval to avoid the PyYAML dependency). Preserve protected sections, use bounded edits, and accept only strict validation improvements.

## Runtime Boundaries

This Codex setup does not depend on Claude Code hooks or slash commands. Treat hook behavior as explicit discipline: read memory at session start, check errors before implementation, and write memory when important work lands.
