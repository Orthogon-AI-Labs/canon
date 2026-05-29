# Changelog

## Unreleased — context minimization

Repositioned canon around the evidence on context files (ETH Zurich, arXiv 2602.11988): small, human-written context helps; large, machine-generated context hurts and costs more. See `docs/context-minimization-plan-2026-05-29.md`.

- README: removed the unreproducible "~65% → ~94%" accuracy claim; added a "What the evidence says" section grounding canon's narrower claim (keep context minimal and human-curated, prove changes against an eval).
- `Stop` memory hook now **proposes** a MEMORY.md entry for confirmation instead of writing silently; silent-append is an opt-in (the hook prompt documents the toggle). Updated README hook descriptions to match.
- Templates: added `GLOBAL-defaults.md` (generic behavior preferences for `~/.claude`, not per-project context); trimmed the overview/Goal/Audience block from `CLAUDE-standard.md` and `CLAUDE-full.md`; relabeled `full` as not-the-default with a pointer to the global starter. Added a "no architecture overview" note.
- `canon-eval`: added deterministic `max_chars` / `min_chars` graders (dependency-free token-cost proxy). Documented in `docs/optimize.md` and `templates/eval.yaml`.
- `optimize` now handles **context files** (`CLAUDE.md` / `MEMORY.md` / `AGENTS.md`), not just skills: deletions-only edits, accept only if the file is strictly smaller and the behavior check still passes, protected sections preserved. Skill bumped to 0.2.0; `/canon:optimize` and the command brief updated.
- Added `scripts/optimize/scaffold-context-eval.sh` — generates a context-file optimize eval (a `max_chars` cost budget at the file's baseline size plus an optional behavior `command`). Collision-safe `--root` / `--force` / `--dry-run`.
- `docs/specs/06-optimize-context-files.md` implemented (size grader + scaffold + optimize context-file mode all shipped).

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
