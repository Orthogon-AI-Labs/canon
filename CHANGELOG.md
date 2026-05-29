# Changelog

## 0.5.0 - 2026-05-29

- Added the `graduate-skill` skill and `/canon:graduate-skill` command (spec 05): turn repeated browser/task traces into a durable, self-contained `SKILL.md` via a bounded `strategy.md` iteration loop, with a Browserbase-compatible trace path and a handoff to `/canon:optimize`.
- Added `scripts/graduation/scaffold.sh` (collision-safe `--root` / `--force` / `--dry-run`), `templates/graduation-task.md`, `templates/graduated-skill.md`, `docs/graduation.md`, and the `fixtures/graduation/craigslist-like` smoke fixture.
- Codex port now ships the eval runner: `install-codex.sh` copies `canon-eval.{sh,py}` into `.canon/codex/bin/`, `doctor` checks for it, and `SKILL-optimize.md` references it.
- Documented that `canon-eval` is a grader, not a skill runner — `metric`/`threshold` are advisory and the strict-improvement gate is operator-judged (docs/optimize.md, skills/optimize/SKILL.md, templates/eval.yaml).
- Added a dependency-free `fixtures/evals/toy-email.json` and documented the PyYAML requirement for YAML evals.
- README: added a "Supported runtimes" table and a "Skill lifecycle" section, corrected the hook list to four hooks, and fixed the `AGENTS-codex.md` reference.
- Reconciled spec 04 with the Codex reference implementation (template naming, smoke-test guidance).
- Fixed bundled-resource path resolution: `/canon:*` command and skill bodies now reference the protected-section checker, eval runner, scaffolder, and templates via `${CLAUDE_PLUGIN_ROOT}/...` so they resolve when canon is installed as a plugin (not only from a repo checkout). Docs note that bare paths assume the canon repo.

## 0.4.0 - 2026-05-28

- Added experimental Codex support with `AGENTS.md`, portable Codex skill docs, and `scripts/install-codex.sh init|install|doctor --runtime codex`.
- Added `look-back`, `protected-sections`, and `optimize` skills, plus `/canon:*` command wrappers for the v0.4 user surface.
- Added protected Markdown blocks and a checker that compares working tree and index changes against `HEAD`.
- Added an alpha eval runner and `templates/eval.yaml` for eval-gated skill optimization.
- Added a Stop hook that checks protected sections after substantial work.

## 0.3.0 - Initial public canon plugin

- Added the Claude Code bootstrap for `CLAUDE.md`, `MEMORY.md`, and `ERRORS.md`.
- Added `decision-log` and `errors-check` skills.
- Added hooks for session memory loading, conservative decision logging, and pre-implementation error checks.
