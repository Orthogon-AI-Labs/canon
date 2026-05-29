# Spec 05: Autobrowse-Style Skill Graduation

> Inspired by **Autobrowse** (Browserbase) — created by Shubhankar ([@_shubhankar](https://x.com/_shubhankar)), written up by Kyle Jeong ([@kylejeong](https://x.com/kylejeong)). Original implementation with a Browserbase-compatibility path, not bundled code. See `CREDITS.md` → Inspirations.

## One-Liner

Add a canon workflow for turning repeated browser/task traces into durable skills: define task, run, inspect trace, update `strategy.md`, iterate, converge, graduate `SKILL.md`.

## Strategic Frame

`canon optimize` improves existing skills with evals. Skill graduation creates new skills from lived traces. Together they make canon a lifecycle manager: discover, graduate, protect, optimize.

## User Surface

Commands:

```text
/canon:graduate-skill <task-name>
/canon:graduate-skill <task-name> --iterations 5
/canon:graduate-skill <task-name> --from-traces .canon/traces/<task>
```

Natural triggers:

- "turn this browser workflow into a skill"
- "graduate this repeated task"
- "make a skill from this trace"
- "iterate strategy.md until this task is reliable"

## Scope

In scope:

- Workspace convention under `.canon/graduation/`.
- `task.md` template.
- `strategy.md` iterative scratchpad.
- Trace/report format.
- Graduation template for `SKILL.md`.
- Manual and Browserbase-compatible paths.

Out of scope for v1:

- Owning Browserbase execution.
- CAPTCHA/proxy infrastructure.
- Publishing to public skill registry.
- Optimizing arbitrary non-verifiable tasks.

## Workspace Layout

```text
.canon/graduation/
├── tasks/
│   └── <task-name>/
│       ├── task.md
│       ├── strategy.md
│       ├── reports/
│       │   ├── iter-001.md
│       │   └── iter-002.md
│       └── graduated/
│           └── SKILL.md
└── README.md
```

## `task.md` Template

````markdown
# Task: <name>

## Objective
<What the agent must accomplish.>

## Inputs
- URL:
- Credentials needed:
- User-provided fields:

## Expected Output
```json
{
  "status": "success",
  "data": {}
}
```

## Success Criteria
- <Observable pass/fail condition>

## Constraints
- Do not store secrets.
- Do not write outside `.canon/graduation/tasks/<name>/`.
````

## `strategy.md` Rules

The strategy file is the only fast-changing state during iteration.

Good strategy entries include:

- Fast path.
- Exact commands or navigation steps.
- Selectors, URLs, timing notes, and known API endpoints.
- Failure recovery.
- What not to do again.

Bad strategy entries:

- Vague encouragement.
- Full transcripts.
- Credentials.
- Broad rewrites after a single failure.

## Loop

1. Scaffold `task.md`.
2. Run the task with the current strategy.
3. Save trace summary and report.
4. Read the exact failure point.
5. Form one hypothesis.
6. Edit `strategy.md` with a bounded change.
7. Re-run.
8. Stop after pass stability or max iterations.
9. Graduate to self-contained `SKILL.md`.

Default convergence rule:

- Passes 2 of last 3 runs, or
- Max iterations reached with meaningful improvement and known limitations documented.

## Graduated Skill Requirements

Graduated `SKILL.md` must include:

- Frontmatter name and description.
- Purpose.
- When to use.
- Required tools/env.
- Workflow.
- Site/task-specific gotchas.
- Failure recovery.
- Expected output schema.
- Source note:

  ```text
  Generated from canon skill graduation: <task-name>, <n> iterations, <date>.
  ```

It must not include:

- Raw transcripts.
- Secrets.
- Named local session flags.
- Claims that were not validated.

## Proposed Files

```text
skills/graduate-skill/SKILL.md
templates/graduation-task.md
templates/graduated-skill.md
docs/specs/05-autobrowse-skill-graduation.md
docs/graduation.md
```

Optional:

```text
scripts/graduation/scaffold.sh
scripts/graduation/report.sh
```

## Browserbase Compatibility

If Browserbase Autobrowse is installed, canon should not reimplement it. It should:

1. Detect the Browserbase skill/workspace if present.
2. Use its trace/report artifacts as input.
3. Apply canon conventions for protected sections, reports, and final skill placement.

If Browserbase is absent, canon still supports a manual trace-driven loop.

## Implementation Plan

1. Add graduation skill.
2. Add task and final skill templates.
3. Add `.canon/graduation/` workspace docs.
4. Add README section: "Skill lifecycle."
5. Wire protected-section guidance into graduated skills.
6. Add optional handoff to `/canon:optimize` after graduation.

## Acceptance Criteria

- User can scaffold a task workspace.
- `strategy.md` is created and updated separately from `task.md`.
- Reports are saved per iteration.
- Final `SKILL.md` is self-contained.
- Final skill includes gotchas and failure recovery.
- Final skill excludes traces and secrets.
- Browserbase users get a compatibility path instead of duplicate machinery.

## Tests

Manual trace fixture:

```text
fixtures/graduation/craigslist-like/
├── task.md
├── traces/
│   ├── iter-001-summary.md
│   └── iter-002-summary.md
└── expected-skill.md
```

Expected:

- The workflow reads trace summaries.
- It adds one bounded strategy change per iteration.
- It graduates a skill with a fast path and gotchas.

## Launch Copy

canon can now graduate repeated work into skills: run the task, study the trace, improve `strategy.md`, and keep the reusable procedure.
