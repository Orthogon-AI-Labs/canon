# Spec 03: `/canon:optimize` Alpha

## One-Liner

Add a measured skill-optimization loop: run evals, propose bounded edits, preserve protected sections, accept only strict validation improvements, and write an optimization report.

## Strategic Frame

canon started as project memory. `canon optimize` graduates it into measured skill evolution.

The principle: a `SKILL.md` is not just documentation. It is trainable external state for an agent. canon should optimize that state without turning it into unreviewable slop.

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

## Scope

In scope for alpha:

- One skill at a time.
- Local eval file.
- Bounded Markdown patch proposals.
- Strict-improvement validation gate.
- Protected-section awareness.
- Rejected edit log.
- Human-readable report.

Out of scope for alpha:

- Full benchmark suite.
- Cloud eval runner.
- Multi-skill joint optimization.
- Open-ended writing/design evals without a verifier.
- Automatic marketplace publishing.

## Eval File Format

```yaml
name: seo-report-skill
skill: skills/seo-report/SKILL.md
metric: pass_rate
threshold:
  accept: strict_improvement
tasks:
  - id: local-seo-audit
    input: fixtures/seo/local-client.md
    expected:
      contains:
        - "review velocity"
        - "GBP category"
        - "30/60/90"
      not_contains:
        - "generic SEO tips"
  - id: competitor-gap
    input: fixtures/seo/competitors.md
    expected:
      json_schema: fixtures/seo/opportunity.schema.json
```

Alpha can support simple graders:

- `contains`
- `not_contains`
- `regex`
- `json_schema`
- `command`

## Optimization Loop

1. Load skill.
2. Run baseline eval.
3. Reflect on failures and successes.
4. Propose bounded edits:

   - 1-4 edits by default.
   - Add/delete/replace only.
   - No full rewrite.
   - No protected-section edits.

5. Apply candidate patch to temp copy.
6. Run validation eval.
7. Accept only if validation score strictly improves.
8. Reject ties and regressions.
9. Write report.

## Proposed Files

```text
skills/optimize/SKILL.md
templates/eval.yaml
docs/specs/03-canon-optimize-alpha.md
docs/optimize.md
```

If a script layer is acceptable:

```text
hooks/scripts/canon-eval.sh
hooks/scripts/canon-optimize.sh
```

Later CLI package:

```text
bin/canon
src/eval/
src/optimize/
```

## Report Format

```markdown
# canon optimize report: seo-report

## Baseline
- Score: 6/10
- Failures: local-seo-audit, competitor-gap

## Candidate Edit
- Edit budget: 4
- Protected sections touched: no
- Summary:
  1. Added required "evidence before recommendation" rule.
  2. Replaced vague output section with JSON schema reminder.

## Validation
- Score: 8/10
- Verdict: ACCEPTED

## Rejected Ideas
- Add 900-token background section: rejected, too broad.
```

## Safety Rules

- Never touch protected sections by default.
- Never accept equal-score edits.
- Never accept edits that remove examples unless the eval improves and the report calls it out.
- Never optimize without an eval file.
- If the grader is weak, label the result as "low-confidence improvement."

## Implementation Plan

1. Add eval file template.
2. Add optimize skill that explains and orchestrates the loop manually.
3. Add protected-section dependency from Spec 02.
4. Implement simple local graders through shell or a small script.
5. Add temp-copy patch flow.
6. Add report writing under `.canon/reports/optimize/<skill>/<timestamp>.md`.
7. Update README with alpha warning.

## Acceptance Criteria

- `/canon:eval skills/foo` runs tasks and reports a baseline score.
- `/canon:optimize skills/foo` refuses to run without evals.
- Candidate patches are bounded.
- Protected sections are preserved.
- Ties are rejected.
- Improvements write both the skill diff and the report.
- Regressions leave the original skill untouched.

## Tests

Use a toy skill:

```text
fixtures/skills/toy-email/SKILL.md
fixtures/evals/toy-email.yaml
```

Create one task the baseline fails because it omits a required field. The optimizer should add a narrow rule, pass validation, and accept.

Regression test: create a candidate that improves one task but breaks another. It must reject unless total validation strictly improves according to the configured metric.

## Launch Copy

`canon optimize` treats your skills like trainable source code: eval first, bounded edits, protected sections, strict validation gate.

> Inspired by the **SkillOpt** pattern ([arXiv 2605.23904](https://arxiv.org/abs/2605.23904); ref. implementation [github.com/muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering)) — original implementation, not bundled code. See `CREDITS.md` → Inspirations.
