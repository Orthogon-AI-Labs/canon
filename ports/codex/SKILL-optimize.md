---
name: canon-optimize
description: >
  Use when the user asks to evaluate or optimize a skill, improve a SKILL.md
  with bounded edits, preserve protected sections, or accept only changes that
  improve validation results.
metadata:
  version: "0.1.0"
  runtime: "codex"
---

# canon optimize

Treat skill files as trainable external state: eval first, propose bounded edits, preserve protected sections, and keep only strict validation improvements.

## When to Use

Use this workflow when the user says things like:

- "optimize this skill"
- "run this skill against evals"
- "improve this SKILL.md but keep protected sections"
- "only keep the edit if it improves"

## Required Inputs

- A target skill file.
- A local eval file or explicit permission to create one first.
- A clear metric, usually pass rate over deterministic tasks.

Refuse to optimize without an eval. Offer to draft the eval instead.

## Script Helpers

The Codex installer copies both tools into `.canon/codex/bin/`. Run an eval:

```bash
.canon/codex/bin/canon-eval.sh evals/<name>.yaml
```

YAML eval files need PyYAML; a `.json` eval file with the same structure runs with no extra dependency. The runner grades text — it does not execute a `SKILL.md` and does not enforce the `metric`/`threshold` fields. To measure a skill's behavior, point a task's `command:` at something that runs the skill; otherwise the eval grades a static fixture. You make the strict-improvement decision by comparing the two scores.

Check protected sections:

```bash
python3 .canon/codex/bin/check-protected-sections.py
```

## Workflow

1. Read the target skill and eval file.
2. Run the baseline eval with `.canon/codex/bin/canon-eval.sh`.
3. Check protected sections:

   ```bash
   python3 .canon/codex/bin/check-protected-sections.py
   ```

4. Reflect on failures and successes.
5. Propose 1-4 bounded edits by default.
6. Do not touch protected sections unless the user explicitly approves the named block.
7. Apply the candidate to a temp copy or a small patch.
8. Run validation eval.
9. Accept only if the validation score strictly improves.
10. Reject ties and regressions.
11. Write a human-readable report under `.canon/reports/optimize/<skill>/<timestamp>.md` when a change is accepted or rejected after validation.

## Safety Rules

- Never full-rewrite a skill as an "optimization."
- Never accept equal-score edits.
- Never remove examples unless validation improves and the report calls it out.
- Label the result as low confidence when the grader is weak.
- Prefer extending an existing skill over creating a duplicate one.

## Report Shape

```markdown
# canon optimize report: <skill>

## Baseline
- Score:
- Failures:

## Candidate Edit
- Edit budget:
- Protected sections touched:
- Summary:

## Validation
- Score:
- Verdict:

## Rejected Ideas
- <idea>: <reason>
```
