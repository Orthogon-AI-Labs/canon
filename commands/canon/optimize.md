---
description: Optimize a skill with a bounded eval-first canon workflow
argument-hint: "<skill-path> --eval <eval-file> [--max-edits N]"
allowed-tools: [Read, Glob, Grep, Bash, Edit, MultiEdit, Skill]
---

# /canon:optimize

Route this slash command to the `optimize` skill.

The user invoked:

```text
/canon:optimize $ARGUMENTS
```

Require a target skill path and an explicit eval file:

```text
<skill-path> --eval <eval-file>
```

If `--eval` is missing, refuse to optimize and explain that `canon optimize` never runs without an eval file. Offer `templates/eval.yaml` as the starter.

When both inputs exist, follow the `optimize` skill exactly:

1. Run the baseline eval.
2. Propose 1-4 bounded edits unless `--max-edits` says otherwise.
3. Preserve protected sections unless a named block is explicitly approved.
4. Apply only narrow patches.
5. Run validation.
6. Accept only strict validation improvements.
7. Write the optimization report under `.canon/reports/optimize/<skill>/<timestamp>.md`.
