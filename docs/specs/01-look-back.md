# Spec 01: `/canon:look-back`

## One-Liner

Add a canon skill that mines the user's recent work and proposes the smallest reusable asset: a skill, subagent, automation, or extension to something that already exists.

## Why This Ships First

This is the fastest release that makes canon feel proactive. canon already installs memory; `/canon:look-back` turns that memory into leverage by asking, "What are you repeating that should become a reusable workflow?"

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

Expected output:

1. A compact shortlist of repeated workflows.
2. Evidence and dates for each candidate.
3. Recommended form: skill, subagent, automation, extend existing, or skip.
4. Only high-confidence missing assets created or extended.
5. A final report with created items, skipped items, and "needs more evidence" items.

## Scope

In scope:

- A new `skills/look-back/SKILL.md`.
- A reusable prompt embedded in the skill body.
- Read-only discovery across available local context.
- Conservative file creation for high-confidence assets.
- README mention under "What's in the plugin."

Out of scope for v1:

- A CLI binary.
- Semantic clustering across all shell history.
- Automatic cron creation.
- Editing third-party skills without explicit confirmation.
- Writing to Chronicle or external services.

## Evidence Order

The skill should inspect evidence in this order:

1. Recent canon files: `MEMORY.md`, `ERRORS.md`, `CLAUDE.md`.
2. Recent Codex or Claude session summaries if locally available.
3. Existing skills, custom agents, slash commands, and automations.
4. Chronicle if enabled, discovery only.
5. Git history when useful for dates and repeated task shape.

If a source is missing, the skill states that it skipped the source and continues.

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

## Proposed Files

```text
skills/look-back/SKILL.md
docs/specs/01-look-back.md
README.md
```

Optional later:

```text
templates/SKILL-basic.md
templates/SUBAGENT-basic.md
templates/AUTOMATION-proposal.md
```

## Implementation Plan

1. Add `skills/look-back/SKILL.md` with frontmatter:

   ```yaml
   name: look-back
   description: >
     Use when the user asks to review recent work, mine repeated workflows,
     identify useful skills/subagents/automations, or package recurring work.
   ```

2. Port the prompt from the vault note into the skill body with canon-specific references to `MEMORY.md` and `ERRORS.md`.
3. Add a hard "shortlist before creating" rule.
4. Add a hard "extend before duplicate" rule.
5. Add a hard "ask before editing existing non-canon files" rule.
6. Update `README.md` to list `look-back` as a fourth skill.
7. Update `.claude-plugin/plugin.json` keywords:

   ```json
   "skill-discovery",
   "workflow-mining",
   "look-back"
   ```

## Acceptance Criteria

- Running "look back over my recent work" activates the skill.
- The skill reads `MEMORY.md` and `ERRORS.md` first when present.
- The first response is a shortlist, not immediate file writes.
- It never creates speculative broad skills.
- It reuses or extends existing skills when a close match exists.
- It produces a clear final report.
- README documents the skill in one paragraph.

## Tests

Manual fixture:

```text
tmp/look-back-fixture/
├── MEMORY.md     # includes 3 repeated "SEO report" sessions
├── ERRORS.md     # includes repeated API key leak mistake
├── skills/
│   └── seo-report/SKILL.md
└── sessions/
    ├── 2026-05-01.md
    ├── 2026-05-08.md
    └── 2026-05-15.md
```

Expected behavior:

- Recommends extending `seo-report`, not creating `seo-report-v2`.
- Recommends a guardrail checklist for the repeated API-key mistake.
- Skips any one-off session.

## Launch Copy

canon used to remember your project. Now it can look back and tell you what should become reusable.
