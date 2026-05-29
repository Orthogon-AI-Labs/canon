---
name: graduate-skill
description: >
  Use when the user asks to turn a repeated browser/task workflow or a set of
  run traces into a durable skill — "graduate this task", "make a skill from
  this trace", "turn this browser workflow into a skill", or "iterate
  strategy.md until this task is reliable".
metadata:
  version: "0.1.0"
---

# canon graduate-skill

Turn repeated work — especially browser/task traces — into a durable, self-contained `SKILL.md`. Where `look-back` notices that something *should* become a skill and `optimize` improves an *existing* skill against evals, `graduate-skill` is the step in between: run the task, study the trace, make one bounded change to `strategy.md`, re-run, converge, then graduate.

This skill is intentionally trace-driven and conservative. It never invents a skill from a single run, and it never copies secrets or raw transcripts into the graduated output.

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

## Workspace Layout

All graduation state lives under `.canon/graduation/`:

```text
.canon/graduation/
├── tasks/
│   └── <task-name>/
│       ├── task.md        # fixed definition — what success means
│       ├── strategy.md    # the only fast-changing state during iteration
│       ├── reports/       # one report per run (iter-001.md, iter-002.md, …)
│       └── graduated/
│           └── SKILL.md   # the final, self-contained skill
└── README.md
```

Scaffold a workspace deterministically:

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/graduation/scaffold.sh <task-name>
```

`scaffold.sh` is collision-safe — it skips existing files, supports `--root`, `--force`, and `--dry-run`, and never clobbers a `strategy.md` you have been iterating on.

## `task.md` — fixed definition

`task.md` is written once and rarely changes. It records the objective, inputs, expected output schema, observable success criteria, and constraints. Start from `${CLAUDE_PLUGIN_ROOT}/templates/graduation-task.md`. Do not put strategy in `task.md` — that belongs in `strategy.md`.

## `strategy.md` — the only fast-changing state

The strategy file is where every iteration's lesson lands. Keep it tight.

Good strategy entries:

- The fast path — the shortest sequence that has actually worked.
- Exact commands or navigation steps.
- Selectors, URLs, timing notes, and known API endpoints.
- Failure recovery for the specific failure you observed.
- What not to do again.

Bad strategy entries:

- Vague encouragement ("be careful with the form").
- Full transcripts.
- Credentials of any kind.
- Broad rewrites after a single failure.

## Loop

1. Scaffold `task.md` (and `strategy.md`) if they do not exist.
2. Run the task with the current strategy — manually, or from existing traces under `--from-traces`.
3. Save a trace summary and a report to `reports/iter-NNN.md`.
4. Read the **exact** failure point. Don't guess.
5. Form **one** hypothesis.
6. Edit `strategy.md` with a single bounded change.
7. Re-run.
8. Stop on convergence or when `--iterations` is reached.
9. Graduate to a self-contained `SKILL.md` under `graduated/`.

**Default convergence rule:**

- Passes 2 of the last 3 runs, **or**
- Max iterations reached *with* meaningful improvement and known limitations documented.

If neither holds, do **not** graduate. Report what's still flaky and stop.

## Graduated Skill Requirements

The graduated `SKILL.md` (start from `${CLAUDE_PLUGIN_ROOT}/templates/graduated-skill.md`) **must** include:

- Frontmatter `name` and `description`.
- Purpose.
- When to use.
- Required tools / env.
- Workflow (the converged fast path).
- Site/task-specific gotchas.
- Failure recovery.
- Expected output schema.
- A source note:

  ```text
  Generated from canon skill graduation: <task-name>, <n> iterations, <date>.
  ```

It **must not** include:

- Raw transcripts.
- Secrets or credentials.
- Named local session flags or private paths.
- Claims that were never validated by a run.

Wrap any hard-won invariant in the graduated skill with protected-section markers so a later edit can't silently undo it:

```markdown
<!-- canon:protected:start name="<task>-fast-path" -->
The converged steps that actually work. Don't rewrite without re-running.
<!-- canon:protected:end -->
```

## Browserbase Compatibility

canon does not reimplement browser execution. If a Browserbase / Autobrowse skill or workspace is present:

1. Detect it.
2. Use its existing trace/report artifacts as the input for the loop (point `--from-traces` at them).
3. Apply canon conventions for reports, protected sections, and final skill placement.

If Browserbase is absent, the manual trace-driven loop above still works — you supply the run summaries.

## Handoff to optimize

Once a skill is graduated and has a couple of repeatable tasks, it becomes a candidate for `/canon:optimize`: write an eval from `${CLAUDE_PLUGIN_ROOT}/templates/eval.yaml`, then tighten the graduated skill against it. Mention this as the suggested next step in the final report, but don't run it automatically.

## Hard Rules

- Trace before graduate — never graduate from a single unverified run.
- One bounded `strategy.md` change per iteration. No broad rewrites after a single failure.
- `task.md` is fixed; `strategy.md` is fast-changing. Never blur the two.
- The graduated skill is self-contained and excludes traces, secrets, and unvalidated claims.
- Ask before editing existing non-canon files.
