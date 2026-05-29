# canon optimize

`canon optimize` is an alpha workflow for improving one target at a time — a `SKILL.md`, or a **context file** (`CLAUDE.md` / `MEMORY.md` / `AGENTS.md`) — with measured, bounded edits.

The rule is simple: eval first, patch narrowly, validate, and keep only strict improvements.

For context files the goal is to get **smaller**: edits are deletions/consolidations only, and a prune is accepted only if the file is strictly smaller (deterministic `max_chars` budget) **and** the project's own behavior check still passes. Scaffold the eval with `scripts/optimize/scaffold-context-eval.sh <context-file> --command "<your tests>"`. The full procedure is in the `optimize` skill under "Context files." This operationalizes the context-minimization plan (`docs/context-minimization-plan-2026-05-29.md`).

## Eval Files

> The bare `hooks/scripts/...` and `templates/...` paths below assume you're working inside the canon repo. When canon is installed as a plugin, use the `/canon:eval` and `/canon:optimize` commands — they resolve the bundled runner and template via `${CLAUDE_PLUGIN_ROOT}`.

Start from:

```bash
cp templates/eval.yaml evals/<skill>.yaml
```

Then run:

```bash
hooks/scripts/canon-eval.sh evals/<skill>.yaml
```

Or try the shipped toy fixture:

```bash
hooks/scripts/canon-eval.sh fixtures/evals/toy-email.yaml
```

Supported alpha graders:

- `contains`
- `not_contains`
- `regex`
- `json_schema`
- `command`
- `max_chars` / `min_chars` — deterministic size budget. Fails if the graded text is over (`max_chars`) or under (`min_chars`) the limit; the failure reports the actual char count. Char count is a dependency-free proxy for token cost, used by `canon optimize <context-file>` (spec 06) to prove a prune cut cost. Pair with a `command` task that runs your project's tests to confirm behavior held.

If a task has `expected.command`, the command output is graded. Otherwise the runner reads the task `input` file and grades that text.

YAML eval files require PyYAML. A `.json` eval file with the same structure runs with no extra dependency — see `fixtures/evals/toy-email.json` for the shipped JSON variant.

**How validation works in this alpha (read this).** `canon-eval.sh` is a *grader*, not a skill runner. It does not execute a `SKILL.md`, and it does not read the `metric` or `threshold` fields — those are advisory. To actually measure a skill's behavior, point a task's `command:` at something that runs the skill and writes its output to stdout; otherwise the runner only grades static fixture text and editing the skill won't change the score. The "accept only strict improvements" decision is made by you (or the agent) comparing the baseline and validation scores — it is not enforced by the runner.

## Optimization Loop

1. Run the baseline eval.
2. Inspect failures.
3. Propose 1-4 edits to the target skill.
4. Check protected sections.
5. Apply the candidate patch.
6. Run the eval again.
7. Accept only if the score strictly improves.
8. Write a report under `.canon/reports/optimize/<skill>/<timestamp>.md`.

## Protected Sections

The optimizer must preserve protected blocks:

```markdown
<!-- canon:protected:start name="routing-invariant" -->
Do not rewrite this slow lesson without explicit approval.
<!-- canon:protected:end -->
```

Check them with:

```bash
python3 hooks/scripts/check-protected-sections.py
```

## Alpha Limits

- One skill at a time.
- Local eval files only.
- No cloud eval runner.
- No automatic marketplace publishing.
- Weak graders must be labeled as low confidence in the report.
