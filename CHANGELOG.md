# Changelog

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
