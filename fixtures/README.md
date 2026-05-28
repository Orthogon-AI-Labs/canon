# canon fixtures

Small fixtures for the v0.4 roadmap specs.

## Protected Sections

`fixtures/protected/` contains Markdown examples for the protected-section checker:

- `unchanged.md`
- `edit-outside-block.md`
- `edit-inside-block.md`
- `removed-block.md`
- `renamed-block.md`
- `unbalanced-marker.md`

These are static examples for manual tests. To test diff behavior, copy one case into a temporary git repository, commit the protected baseline, then replace it with a changed case before running `hooks/scripts/check-protected-sections.py`.

## Optimize

Run the toy eval from the repository root:

```bash
hooks/scripts/canon-eval.sh fixtures/evals/toy-email.yaml
```

Expected score:

```text
score: 2/2
```

## Look-Back

`fixtures/look-back-fixture/` gives a tiny memory/session corpus with repeated SEO report work and an existing `seo-report` skill, so `look-back` should recommend extending the existing skill rather than creating a duplicate.
