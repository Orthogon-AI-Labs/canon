---
name: canon-protected-sections
description: >
  Use when the user asks to protect a Markdown section, check protected
  sections, verify that protected blocks survived a diff, or approve a specific
  protected-section edit.
metadata:
  version: "0.1.0"
  runtime: "codex"
---

# canon protected sections

Protected sections preserve slow lessons while allowing the surrounding document to evolve.

## Marker Syntax

```markdown
<!-- canon:protected:start name="routing-invariant" -->
This section encodes a slow lesson. Edits require explicit approval.
<!-- canon:protected:end -->
```

Names should be stable, lowercase, and descriptive.

## When to Use

Use this workflow when the user says things like:

- "protect this section"
- "make sure this invariant cannot be overwritten"
- "check protected sections"
- "did this diff touch protected blocks"
- "I approve editing protected section: <name>"

## Workflow

1. For a protection request, wrap the exact Markdown block with balanced markers.
2. For a check request, run:

   ```bash
   python3 .canon/codex/bin/check-protected-sections.py
   ```

3. If the checker reports a touched protected block, stop and show the file and block name.
4. If the user explicitly approves the edit, rerun with:

   ```bash
   python3 .canon/codex/bin/check-protected-sections.py --allow <name>
   ```

5. Keep the approval narrow. Approval for one block does not approve other protected blocks.

## Rules

- Do not edit protected block bodies without explicit approval.
- Do not rename protected blocks without explicit approval.
- Do not remove protected markers without explicit approval.
- New protected blocks are allowed when markers are balanced.
- Unbalanced markers are always a failure.
