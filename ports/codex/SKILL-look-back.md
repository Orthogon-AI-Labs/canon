---
name: canon-look-back
description: >
  Use when the user asks to look back over recent work, mine repeated workflows,
  identify reusable skills, find automation candidates, or package recurring
  work into a durable asset.
metadata:
  version: "0.1.0"
  runtime: "codex"
---

# canon look-back

Review recent work and propose the smallest reusable asset: a skill, subagent, automation proposal, or extension to something that already exists.

## When to Use

Run this workflow when the user says things like:

- "look back over my recent work"
- "find repeated workflows"
- "what should become a skill"
- "mine my last 30 days for automations"
- "turn repeated work into reusable assets"

## Evidence Order

Inspect available sources in this order:

1. `MEMORY.md`, `ERRORS.md`, and `AGENTS.md`.
2. Recent local session summaries if present.
3. Existing skills, agents, commands, and automation definitions.
4. Git history when useful for dates and repeated task shapes.
5. External or optional systems only when the user explicitly asks.

If a source is missing, note it briefly in the final report and keep going.

## Candidate Rules

Recommend packaging only when the candidate:

- occurred at least twice, or is clearly likely to recur and costly to repeat
- has stable inputs
- has a repeatable procedure
- has a clear output or stopping condition
- improves speed, quality, consistency, or reliability
- is not already adequately covered by an existing asset

Default to "skip" when evidence is weak.

## Workflow

1. Build a compact shortlist before creating or editing files.
2. Include evidence and dates for each candidate when available.
3. Choose the smallest useful form:
   - Skill: reusable workflow or playbook.
   - Subagent: bounded specialist role or investigation task.
   - Automation: recurring check, reminder, monitor, or report.
   - Extend existing: an existing asset covers most of the workflow.
   - Skip: one-off, sensitive, vague, or poorly evidenced.
4. Prefer extending existing assets over creating duplicates.
5. Ask before editing existing non-canon files.
6. Create only high-confidence missing assets after the shortlist is accepted.
7. Finish with created items, skipped items, and items needing more evidence.

## Output Shape

```markdown
## Shortlist
- <candidate>: <recommended form> — <evidence>

## Recommended Actions
- Create / extend / skip: <why>

## Notes
- Missing sources:
- Needs more evidence:
```
