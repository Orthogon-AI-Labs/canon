# Spec 02: Protected Sections

## One-Liner

Add a protected-section convention for Markdown files and a diff checker that flags edits touching protected regions unless explicitly allowed.

## Why This Ships Second

Protected sections are the smallest useful piece of the SkillOpt story. They let canon say: "fast edits can improve skills, but slow lessons do not get overwritten by accident."

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

Protected block syntax:

```markdown
<!-- canon:protected:start name="routing-invariant" -->
This section encodes a slow lesson. Edits require explicit approval.
<!-- canon:protected:end -->
```

Override phrase:

```text
I approve editing protected section: routing-invariant
```

## Scope

In scope:

- Canonical marker format.
- A checker script that compares protected blocks against `HEAD`.
- A skill or command prompt that runs the checker.
- README docs.
- Compatibility note for agent-verify.

Out of scope for v1:

- Cryptographic signatures.
- Remote policy service.
- Multi-branch protected-section registry.
- Non-Markdown file formats.

## Proposed Files

```text
hooks/scripts/check-protected-sections.sh
skills/protected-sections/SKILL.md
docs/specs/02-protected-sections.md
README.md
```

Optional shared implementation:

```text
hooks/scripts/check-protected-sections.py
templates/PROTECTED-SECTIONS.md
```

## Checker Behavior

`check-protected-sections` should:

1. Enumerate changed Markdown files:

   ```bash
   git diff --name-only -- '*.md'
   ```

2. For each changed file, parse protected blocks in `HEAD:<file>` and working tree.
3. Fail when:

   - A protected block exists in `HEAD` but is removed.
   - A protected block's body changes.
   - A protected block is renamed.
   - Marker syntax is unbalanced.

4. Pass when:

   - No changed files contain protected blocks.
   - Edits occur outside protected blocks.
   - New protected blocks are added with balanced markers.

5. Print exact file and block name for failures.

Example failure:

```text
[canon protected-sections]
✗ skills/browser/SKILL.md touched protected block "routing-invariant"
  To proceed, explicitly confirm: I approve editing protected section: routing-invariant
```

## Hook Strategy

Preferred:

- Run as a `Stop` hook after substantial edits.
- If supported by host, also run before final response when changed Markdown files exist.

Fallback:

- Expose as an explicit skill command and document it as part of `canon optimize`.

## agent-verify Integration

agent-verify should reuse the same convention as a claim/check:

- Claim phrase: "protected sections are intact"
- Verifier: `check-protected-sections`
- Failure response: append correction block and list touched protected blocks.

This keeps the convention shared across the reliability stack.

## Implementation Plan

1. Add parser/checker script.
2. Add `skills/protected-sections/SKILL.md`.
3. Update canon README with marker syntax and override phrase.
4. Add `protected-sections` keyword to plugin metadata.
5. Open companion issue/PR in agent-verify to add the same verifier.
6. Add a note in future `canon optimize` spec: optimizer must never touch protected sections unless explicitly allowed.

## Acceptance Criteria

- Balanced protected blocks pass.
- Unbalanced markers fail.
- Edits outside protected regions pass.
- Edits inside protected regions fail with the section name.
- Removing a protected block fails.
- New protected blocks can be added.
- README documents the syntax and override phrase.

## Tests

Fixture cases:

```text
fixtures/protected/
├── unchanged.md
├── edit-outside-block.md
├── edit-inside-block.md
├── removed-block.md
├── renamed-block.md
└── unbalanced-marker.md
```

Expected:

- First two pass.
- Last four fail with exact block name and path.

## Launch Copy

canon now supports protected Markdown sections: the slow lessons stay locked while the fast parts keep evolving.
