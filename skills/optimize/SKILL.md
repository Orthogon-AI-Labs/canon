---
name: optimize
description: >
  Use when the user asks to evaluate or optimize a skill or a context file
  (CLAUDE.md / MEMORY.md / AGENTS.md), improve it with bounded edits, prune a
  context file to cut token cost, preserve protected sections, or accept only
  changes that improve validation results.
metadata:
  version: "0.2.0"
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

Refuse to optimize without an eval file. Offer to draft an eval from `${CLAUDE_PLUGIN_ROOT}/templates/eval.yaml`.

## Script Helpers

Run an eval:

```bash
${CLAUDE_PLUGIN_ROOT}/hooks/scripts/canon-eval.sh evals/<name>.yaml
```

Check protected sections:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-protected-sections.py
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

## Context files (CLAUDE.md / MEMORY.md / AGENTS.md)

`optimize` also prunes context files, not just skills. The evidence canon is built on (repo README, "What the evidence says"; arXiv 2602.11988) is that smaller, human-curated context files perform as well or better at lower token cost. This mode makes a file **strictly smaller** while proving behavior didn't regress.

It is the same loop with two differences: edits are **deletions/consolidations only** (never invent or rewrite content), and the eval measures two axes — **cost** (deterministic) and **behavior** (the project's own tests).

### Detect the target

If the target path is `CLAUDE.md`, `MEMORY.md`, `AGENTS.md`, or matches `templates/CLAUDE-*.md`, use this context-file mode. Otherwise use the skill mode above.

### Scaffold the eval

If no eval exists, scaffold one:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/optimize/scaffold-context-eval.sh CLAUDE.md --command "<your test command>"
```

This writes `evals/<name>-context.json` with a `cost-budget` task (`max_chars` set to the file's current size) and, if `--command` is given, a `behavior-held` task that runs your tests. Without a behavior command, optimize runs cost-only and you must label the result low-confidence.

### What to delete (in priority order)

1. Architecture / overview / "Project context" prose — the study found removing it changes nothing and saves tokens.
2. Generic behavior preferences that belong in `GLOBAL-defaults.md` (response style, confirmation gates, step-by-step) — they don't belong in a per-project file.
3. Duplicated or restated rules.

Never delete: stack locks, hard constraints, non-standard patterns, gotchas, persistence pointers, or anything inside a protected block.

### The loop

1. Run the baseline eval. Record the `cost-budget` char count and the `behavior-held` result.
2. Propose 1–4 bounded deletions from the priority list. Never touch protected sections.
3. Apply the patch.
4. Re-run the eval. **Accept only if** the file is now strictly smaller than the recorded baseline **and** `behavior-held` still passes. Reject any behavior regression, and reject a deletion that doesn't reduce size.
5. After an accepted prune, lower the eval's `max_chars` to the new size to lock the gain.
6. Write the report under `.canon/reports/optimize/<file>/<timestamp>.md`, recording chars before/after and the behavior verdict.

### Honesty

- If there is no behavior command, you are only measuring cost. Say so and label the result "cost-only, behavior operator-judged (low-confidence)."
- canon does not run an agent across a benchmark to measure task success — that's out of scope. "Behavior held" means the user's own tests held. Don't claim more.

## Hard Rules

- One target at a time (one skill, or one context file).
- Protected sections are preserved unless the user explicitly approves a named block.
- Candidate changes are bounded patches, not broad rewrites. For context files, deletions/consolidations only.
- Improvements must be measured by the eval, not vibes. A context-file prune must reduce size and hold behavior.
