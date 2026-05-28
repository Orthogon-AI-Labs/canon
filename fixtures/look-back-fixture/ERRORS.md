# ERRORS.md - look-back fixture

## Entries

## 2026-05-12: API key leaked into draft output

- **What didn't work:** Including raw environment snippets in generated reports.
- **Why it failed:** The draft copied secrets-adjacent context into user-facing prose.
- **What worked instead:** Redact secrets and include only variable names.
- **Note for next time:** Add a guardrail checklist for report generation.
