# canon skill graduation

`graduate-skill` turns repeated work — especially browser/task traces — into a durable, self-contained `SKILL.md`. It is the "create a new skill from lived runs" half of canon's skill lifecycle.

## Where it sits in the lifecycle

```
look-back   → notices repeated work that should become a skill
graduate    → runs the task, iterates strategy.md, graduates a SKILL.md
protect     → locks the hard-won fast path with protected-section markers
optimize    → tightens the graduated skill against an eval
```

## Workspace

Everything lives under `.canon/graduation/`:

```text
.canon/graduation/
├── tasks/
│   └── <task-name>/
│       ├── task.md        # fixed definition
│       ├── strategy.md    # the only fast-changing state
│       ├── reports/       # iter-001.md, iter-002.md, …
│       └── graduated/
│           └── SKILL.md   # final, self-contained skill
└── README.md
```

Scaffold it deterministically:

```bash
scripts/graduation/scaffold.sh <task-name>
scripts/graduation/scaffold.sh <task-name> --root /path/to/project
scripts/graduation/scaffold.sh <task-name> --dry-run     # preview, writes nothing
```

The scaffolder is collision-safe: it skips files that already exist (use `--force` to replace), and it never clobbers a `strategy.md` you have been iterating on.

## The loop

1. Scaffold `task.md` / `strategy.md`.
2. Run the task with the current strategy — or ingest existing traces with `--from-traces`.
3. Save a report to `reports/iter-NNN.md`.
4. Read the exact failure point.
5. Form one hypothesis.
6. Make one bounded `strategy.md` change.
7. Re-run.
8. Stop on convergence.
9. Graduate the skill.

**Convergence rule:** passes 2 of the last 3 runs, *or* max iterations reached with meaningful improvement and documented limitations. If neither holds, don't graduate — report what's still flaky.

## Graduated skill

Start from `templates/graduated-skill.md`. The final skill must be self-contained (purpose, when-to-use, required tools, workflow, gotchas, failure recovery, output schema, source note) and must exclude raw transcripts, secrets, and unvalidated claims. Wrap the converged fast path in `<!-- canon:protected:start name="..." -->` markers so a later edit can't silently undo it.

## Browserbase compatibility

canon does not own browser execution. If a Browserbase / Autobrowse skill is installed, point `--from-traces` at its trace/report artifacts and apply canon conventions on top (reports, protected sections, final placement). If it's absent, the manual trace-driven loop still works.

## Handoff to optimize

Once a graduated skill has a couple of repeatable tasks, write an eval from `templates/eval.yaml` and run `/canon:optimize` against it. Graduation is suggested as a handoff in the final report, never run automatically.

## Alpha limits

- Manual or Browserbase trace input only — canon does not drive the browser itself.
- No publishing to a public skill registry.
- Graduation requires real runs; a single unverified run is never enough.
