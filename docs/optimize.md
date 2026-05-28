# canon optimize

`canon optimize` is an alpha workflow for improving one `SKILL.md` at a time with measured, bounded edits.

The rule is simple: eval first, patch narrowly, validate, and keep only strict improvements.

## Eval Files

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

If a task has `expected.command`, the command output is graded. Otherwise the runner reads the task `input` file and grades that text.

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
