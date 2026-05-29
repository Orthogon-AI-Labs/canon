---
name: optimize
description: >
  Use when the user asks to evaluate or optimize a skill, improve a SKILL.md
  with bounded edits, preserve protected sections, or accept only changes that
  improve validation results.
metadata:
  version: "0.1.0"
---

# canon optimize

Optimize one skill at a time with an eval-first loop: run baseline, propose bounded edits, preserve protected sections, validate, and keep only strict improvements.

## User Surface

Commands:

```text
/canon:eval skills/<name>
/canon:optimize skills/<name>
/canon:optimize skills/<name> --max-edits 4 --eval evals/<name>.yaml
```

Natural triggers:

- "optimize this skill"
- "run this skill against evals"
- "improve this SKILL.md but keep protected sections"
- "only keep the edit if it improves"

## Required Inputs

- One target skill file.
- A local eval file, or explicit permission to create one first.
- A deterministic metric, usually pass rate.

Refuse to optimize without an eval file. Offer to draft an eval from `templates/eval.yaml`.

## Script Helpers

Run an eval:

```bash
hooks/scripts/canon-eval.sh evals/<name>.yaml
```

Check protected sections:

```bash
python3 hooks/scripts/check-protected-sections.py
```

## How Validation Works (alpha)

`canon-eval.sh` grades text; it does not run a `SKILL.md`. The `metric` and `threshold` fields in the eval file are advisory in this alpha — the runner does not enforce them. To measure a skill's actual behavior, a task's `command:` must run the skill and emit its output; otherwise the eval grades a static fixture and the score won't move when you edit the skill. You (or the agent) make the strict-improvement decision by comparing the baseline and validation scores. YAML eval files need PyYAML; a `.json` eval runs without it.

## Optimization Loop

1. Load the target skill.
2. Run baseline eval.
3. Reflect on failures and successes.
4. Propose bounded edits:
   - 1-4 edits by default.
   - Add/delete/replace only.
   - No full rewrite.
   - No protected-section edits.
5. Apply the candidate patch.
6. Run validation eval.
7. Accept only if validation score strictly improves.
8. Reject ties and regressions.
9. Write a report under `.canon/reports/optimize/<skill>/<timestamp>.md`.

## Safety Rules

- Never touch protected sections by default.
- Never accept equal-score edits.
- Never accept edits that remove examples unless the eval improves and the report calls it out.
- Never optimize without an eval file.
- If the grader is weak, label the result as "low-confidence improvement."

## Report Format

```markdown
# canon optimize report: <skill>

## Baseline
- Score: <passed>/<total>
- Failures: <task ids>

## Candidate Edit
- Edit budget: <n>
- Protected sections touched: no
- Summary:
  1. <bounded edit>

## Validation
- Score: <passed>/<total>
- Verdict: ACCEPTED | REJECTED

## Rejected Ideas
- <idea>: <reason>
```

## Hard Rules

- One skill at a time.
- Protected sections are preserved unless the user explicitly approves a named block.
- Candidate changes are bounded patches, not broad rewrites.
- Improvements must be measured by the eval, not vibes.
