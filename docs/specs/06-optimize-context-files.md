# Spec 06 — `canon optimize` for context files

**Status:** Implemented (size grader, scaffold script, and the optimize context-file mode all shipped)
**Lands in:** canon 0.6
**Author:** Noah / Orthogon AI Labs

---

## One-line

Generalize `canon optimize` from one `SKILL.md` to context files (`CLAUDE.md`, `MEMORY.md`, `AGENTS.md`): propose bounded deletions, prove against an eval that the prune cut cost without regressing behavior, keep only strict improvements.

---

## Why

The evidence canon is now built on (see the repo README, "What the evidence says," and `docs/context-minimization-plan-2026-05-29.md`) is that small, human-written context files help and large, generated ones hurt and cost more. canon should give users a measured way to *get smaller* — not just guidance to do it by hand. The existing `optimize` loop (eval-first, bounded edits, strict-improvement-only, protected-section-safe) is exactly the right machine; it just needs to target context files and to measure the axis that matters for them: cost.

This is also canon's differentiator. In a crowded plugin ecosystem nearly every context/memory tool *adds*; canon becomes the one that *prunes and proves*.

---

## What already shipped (the dependency)

`canon-eval` now supports two deterministic size graders in a task's `expected` block:

- `max_chars: <int>` — fails if the graded text is longer than the limit.
- `min_chars: <int>` — fails if it is shorter.

Char count is a stable, dependency-free proxy for token cost. This is what lets an eval assert "the pruned file is under N chars" deterministically. Tested: pass case, fail case (reports the actual char count), and no regression on the shipped toy eval.

---

## Scope

In:
- A `canon optimize <context-file>` mode (and `/canon:optimize CLAUDE.md`) reusing the existing loop: baseline → bounded edits → validate → accept only strict improvement → write a report.
- Edits are **deletions / consolidations only** for context files: remove architecture/overview sections, generic behavior prose that belongs in `GLOBAL-defaults.md`, and duplicated rules. No new content invented.
- The accept gate combines two measurements:
  1. **Cost dropped** — a `max_chars` task asserting the pruned file is smaller (deterministic, runs anywhere).
  2. **Behavior held** — a user-supplied `command` task that runs the project's own tests/checks and must not regress.
- Protected sections (`<!-- canon:protected:start -->`) are never touched, same as today.
- A report under `.canon/reports/optimize/<file>/<timestamp>.md` showing chars before/after and the behavior-eval verdict.

Not in:
- **A full agent-task runner.** canon does not invoke an agent across a benchmark to measure success the way the ETH study did — that is out of scope for canon's size. "Behavior held" is measured by the user's own `command` (their test suite), or, absent one, is explicitly operator-judged and labeled low-confidence.
- Auto-pruning without an eval. If there is no behavior `command` and no size assertion, `optimize` refuses, same as it refuses to optimize a skill without an eval today.
- Inventing or rewriting content. Deletions and consolidations only.

---

## Behavior

1. Load the target context file. Resolve protected sections; they are off-limits.
2. Baseline: run the eval. Record char count and the behavior-`command` result.
3. Propose 1–4 bounded deletions, prioritizing: overview/architecture sections, generic behavior prose with a home in `GLOBAL-defaults.md`, duplicated rules.
4. Apply the candidate patch.
5. Validate: re-run the eval. Accept only if `max_chars` now passes (smaller) **and** the behavior `command` does not regress. Reject ties on cost and any behavior regression.
6. Write the report.

---

## Acceptance criteria

1. `canon optimize CLAUDE.md` with an eval that has a `max_chars` task and a behavior `command` task prunes the file, and accepts only when chars drop and the command result holds.
2. A candidate that reduces chars but regresses the behavior command is **rejected**.
3. Protected sections are never modified; a candidate that would touch one is rejected before validation.
4. With no behavior `command` available, `optimize` still runs on the size axis but labels the result "cost-only, behavior operator-judged (low-confidence)."
5. The report records chars before/after and the behavior verdict.
6. `canon-eval` `max_chars`/`min_chars` graders: pass when within budget, fail with the actual char count when not. (Met — shipped with this spec.)

---

## Open questions

- **Token estimate vs char count.** Char count is the dependency-free proxy that shipped. If a more accurate token count is wanted later, add an optional `max_tokens` grader behind a tokenizer dependency — but keep `max_chars` as the no-dependency default.
- **Default behavior command.** Should `canon-init` offer to scaffold a behavior `command` (e.g. `npm test`) into the optimize eval, so the "behavior held" axis isn't empty for most users? Likely yes; decide during implementation.

---

## Cross-link

Implements Move 4 of `docs/context-minimization-plan-2026-05-29.md`. The size grader is the shipped dependency; this spec is the loop that consumes it.
