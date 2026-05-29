---
description: Optimize a skill or context file with a bounded eval-first canon workflow
argument-hint: "<skill-or-context-path> --eval <eval-file> [--max-edits N]"
allowed-tools: [Read, Glob, Grep, Bash, Edit, MultiEdit, Skill]
---

# /canon:optimize

Route this slash command to the `optimize` skill.

The user invoked:

```text
/canon:optimize $ARGUMENTS
```

The target may be a **skill** (`skills/<name>/SKILL.md`) or a **context file** (`CLAUDE.md`, `MEMORY.md`, `AGENTS.md`, or a `templates/CLAUDE-*.md`). Pick the mode by the target path; the `optimize` skill documents both.

Require a target path and an eval file:

```text
<skill-path>    --eval <eval-file>
<context-file>  --eval <eval-file>
```

If `--eval` is missing, refuse to optimize and explain that `canon optimize` never runs without an eval file.

- For a **skill**, offer `${CLAUDE_PLUGIN_ROOT}/templates/eval.yaml` as the starter.
- For a **context file**, offer to scaffold one:
  `${CLAUDE_PLUGIN_ROOT}/scripts/optimize/scaffold-context-eval.sh <context-file> --command "<your test command>"`
  This writes a cost-budget (`max_chars`) + behavior eval. Without a behavior command it runs cost-only; say so and label the result low-confidence.

When both inputs exist, follow the `optimize` skill exactly:

1. Run the baseline eval.
2. Propose 1-4 bounded edits unless `--max-edits` says otherwise. For a context file these are **deletions/consolidations only** — never invent or rewrite content.
3. Preserve protected sections unless a named block is explicitly approved.
4. Apply only narrow patches.
5. Run validation. For a context file, accept only if the file is strictly smaller **and** the behavior check still passes; then lower `max_chars` to the new size.
6. Accept only strict validation improvements.
7. Write the optimization report under `.canon/reports/optimize/<target>/<timestamp>.md`.
