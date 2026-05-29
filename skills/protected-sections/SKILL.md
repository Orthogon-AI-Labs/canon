---
name: protected-sections
description: >
  Use when the user asks to protect a Markdown section, check protected
  sections, verify that protected blocks survived a diff, or approve a specific
  protected-section edit.
metadata:
  version: "0.1.0"
---

# canon protected sections

Protected sections preserve slow lessons while allowing the surrounding Markdown to evolve.

## User Surface

Commands:

```text
/canon:protect <file> <section-name>
/canon:check-protected
```

Natural triggers:

- "protect this section"
- "make sure this skill invariant cannot be overwritten"
- "check protected sections"
- "did this diff touch protected blocks"
- "I approve editing protected section: <name>"

## Marker Syntax

```markdown
<!-- canon:protected:start name="routing-invariant" -->
This section encodes a slow lesson. Edits require explicit approval.
<!-- canon:protected:end -->
```

Use stable, descriptive names. Lowercase slug names are best.

## Checker

Run this from the repository root:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-protected-sections.py
```

If the protected checker has been copied into a project by the Codex installer, run:

```bash
python3 .canon/codex/bin/check-protected-sections.py
```

To allow one explicitly approved block:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-protected-sections.py --allow routing-invariant
```

## Workflow

1. For `/canon:protect`, wrap the exact Markdown block with balanced markers.
2. For `/canon:check-protected`, run the checker.
3. If the checker fails, report the file and protected block name.
4. If the user approved a named block, rerun with `--allow <name>`.
5. Keep approval narrow. Approval for one block does not approve other protected blocks.

## Failure Meaning

The checker fails when:

- A protected block exists in `HEAD` but is removed.
- A protected block body changes.
- A protected block is renamed.
- Marker syntax is unbalanced.

It passes when:

- No changed Markdown files contain protected blocks.
- Edits occur outside protected blocks.
- New protected blocks are added with balanced markers.
- An explicitly allowed block changed and was passed with `--allow`.

## Output Shape

Example failure:

```text
[canon protected-sections]
x skills/browser/SKILL.md (working tree): touched protected block "routing-invariant"

To proceed, explicitly confirm: I approve editing protected section: <name>
```

## Hard Rules

- Do not edit protected block bodies without explicit approval.
- Do not rename protected blocks without explicit approval.
- Do not remove protected markers without explicit approval.
- Treat unbalanced markers as a hard failure.
