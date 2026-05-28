---
name: look-back
description: >
  Use when the user asks to review recent work, mine repeated workflows,
  identify useful skills, subagents, automations, or package recurring work into
  reusable assets.
metadata:
  version: "0.1.0"
---

# canon look-back

Mine recent work for repeated workflows and propose the smallest reusable asset: a skill, subagent, automation proposal, or extension to something that already exists.

This workflow is intentionally conservative. It should produce a shortlist before creating files, and it should skip weak candidates.

## User Surface

Primary command:

```text
/canon:look-back
```

Natural triggers:

- "look back over my recent work"
- "find repeated workflows"
- "what should become a skill"
- "mine my last 30 days for automations"
- "turn repeated work into reusable assets"

## Evidence Order

Inspect available evidence in this order:

1. Recent canon files: `MEMORY.md`, `ERRORS.md`, and `CLAUDE.md`.
2. Recent Codex or Claude session summaries if locally available.
3. Existing skills, custom agents, slash commands, and automations.
4. Chronicle if enabled, discovery only.
5. Git history when useful for dates and repeated task shape.

If a source is missing, state that it was skipped and continue.

## Candidate Rules

A candidate can be packaged only when it satisfies all of these:

- It occurred at least twice, or is clearly likely to recur and costly to repeat.
- It has stable inputs.
- It has a repeatable procedure.
- It has a clear output or stopping condition.
- It materially improves speed, quality, consistency, or reliability.
- It is not already adequately covered.

Default to "skip" when evidence is weak.

## Smallest Form Decision Table

| Form | Use When | Output Location |
|---|---|---|
| Skill | Reusable workflow or playbook | `skills/<slug>/SKILL.md` |
| Subagent | Bounded specialist role or investigation task | `agents/<slug>.md` or documented prompt |
| Automation | Recurring check, reminder, report, or monitor | Proposal only in v1 |
| Extend existing | Existing skill covers 70%+ of workflow | Patch existing skill after confirmation |
| Skip | One-off, sensitive, vague, or poorly evidenced | Report only |

## Workflow

1. Read evidence in the order above.
2. Inventory existing reusable assets before proposing new ones.
3. Build a compact shortlist with evidence, dates, and recommended form.
4. Ask before editing existing non-canon files.
5. Prefer extending an existing asset over creating a duplicate.
6. Create or extend only high-confidence assets after the shortlist is accepted.
7. Finish with created items, skipped items, and needs-more-evidence items.

## Shortlist Format

```markdown
## Shortlist
- **<candidate>** — <skill | subagent | automation | extend existing | skip>
  - Evidence: <sources and dates>
  - Why this form: <one sentence>
  - Confidence: <high | medium | low>

## Recommended Next Step
<One small action, or "no asset yet">
```

## Hard Rules

- Shortlist before creating.
- Extend before duplicate.
- Ask before editing existing non-canon files.
- Never create speculative broad skills.
- Never include secrets, raw transcripts, or private local paths in generated assets unless the user explicitly asks.
