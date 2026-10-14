# canon fixtures

Small fixtures for testing the protected-section checker by hand.

## Protected Sections

`fixtures/protected/` contains Markdown examples for the protected-section checker:

- `unchanged.md`
- `edit-outside-block.md`
- `edit-inside-block.md`
- `removed-block.md`
- `renamed-block.md`
- `unbalanced-marker.md`

These are static examples for manual tests. To test diff behavior, copy one case into a temporary git repository, commit the protected baseline, then replace it with a changed case before running `hooks/scripts/check-protected-sections.py`.
