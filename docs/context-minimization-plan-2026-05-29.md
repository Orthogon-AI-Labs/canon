# canon — context minimization plan

**Date:** 2026-05-29
**Author:** Noah / Orthogon AI Labs (drafted via Claude)
**Status:** Proposal. Decide the open questions at the end, then turn the build order into specs.
**Applies to:** canon v0.5.0

---

## The change in one line

Reframe canon from *"the canonical setup that writes and loads context files"* to *"the plugin that keeps your context files small, human-curated, and evidence-pruned."*

The machinery stays — persistence trio, hooks, templates, optimize, evals. What changes is what canon optimizes *for*. Today its instinct is to add context and persist more of it over time. The current evidence says the winning move is the opposite: keep context lean, keep it human-authored, and prove any change against an eval.

---

## Why now — the evidence changed under us

When canon was built, the load-bearing claim was Karpathy's viral thread: a four-line `CLAUDE.md` takes coding accuracy from ~65% to ~94%. That number is in canon's README today as the reason the whole pattern works.

Since then there's an actual study. ETH Zurich, February 2026, *"Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?"* (arXiv 2602.11988). 138 tasks across 12 Python repos plus 300 SWE-bench Lite tasks, four coding agents, three conditions (no context file / LLM-generated / developer-written). What it found:

- **LLM-generated context files reduced task success in 5 of 8 settings** — about **−3% versus no context file at all** — and **increased inference cost by over 20%** by driving more steps.
- **Human-written context files gave a modest real gain** — about **+4% on AGENTbench**.
- Removing an **"Architecture" / overview section** while keeping only commands, constraints, and non-standard patterns produced **the same agent behavior at a lower token budget**.

The headline is not "context files are bad." It's narrower and more useful: **human-curated, minimal context helps a little; machine-generated, growing context hurts and costs more.** canon currently sits on the wrong side of that line in three specific places. The good news is the fix is small — canon already has every piece it needs.

---

## Where canon is misaligned today

### 1. The headline evidence claim is unreproducible

The README leads with Karpathy's ~65% → ~94% figure. That's a single viral thread. The only rigorous measurement to date puts human-written context at roughly **+4%**, not +29 points, and shows machine-generated context net-negative. A tool whose whole pitch is discipline and evidence should not lead with a number it can't reproduce.

Note the nuance in canon's favor: the four-line file is *human-written and minimal*, which is exactly the category the study found helpful. So canon's instinct (small, human-authored) is right. The magnitude of the claim is what's wrong.

### 2. Auto-write hooks generate context that's loaded into every session

This is the real one. canon's `Stop` hook auto-appends LLM-written entries to `MEMORY.md`; `SessionStart` (`load-memory.sh`) reads `MEMORY.md` and `ERRORS.md` into context at the start of every session. The loader caps at the first 200 lines, and because the decision-log skill appends newest-first (to the top of the Entries section), that cap does correctly favor recent entries — so this is not unbounded, and it's not broken. But the content loaded every session is still **LLM-generated context**, which is the category the study found net-negative (−3%, +20% cost). The "be conservative" instruction in the Stop prompt slows how fast that content accumulates; it does not change what category it's in.

### 3. The templates carry generic behavior tuning as per-project context

`CLAUDE-full.md` (87 lines) and parts of `CLAUDE-standard.md` are model-behavior preferences, not project facts: "kill the filler," "match length to the task," "show options before acting," plus a Goal/Audience/Project-context overview block. The study is direct about this — only commands, constraints, and non-standard patterns move task success; overview and behavioral prose don't, and they're paid for in tokens on *every* task. Generic behavior preferences belong in the user's **global** `~/.claude` settings, not duplicated into each project's context file.

---

## The reposition — same machinery, inverted goal

Five moves. canon keeps everything; it just changes its default bias from "persist more" to "keep minimal and prove it."

### Move 1 — Fix the evidence story (README + claims)

- Replace the 65% → 94% headline with the measured framing: *human-written, minimal context files give a modest but real gain (~+4% in the one rigorous study); machine-generated, bloated ones hurt (−3%) and cost more (+20%). canon's job is to keep you in the first category.*
- Keep Karpathy credited — the minimal-file instinct is correct — but stop leaning on the unreproducible number.
- Add a short "What the evidence says" section citing the study. This is on-ethos: canon and agent-verify are meant to be the "evidence over assertion" lab, so the positioning should itself be grounded.

### Move 2 — Make context size a managed budget, not a side effect

- The loader already caps at 200 newest-first lines, which is a crude budget. Go further: load **an index of recent decisions** the agent can expand on demand (progressive disclosure) rather than the raw slice, and stop re-injecting the static Format/Permanent-facts boilerplate at the top of `MEMORY.md` every session.
- Add a **context budget**: canon warns when `CLAUDE.md` + `MEMORY.md` + `ERRORS.md` loaded per session exceeds a token threshold, and points the user at `optimize` to prune.

### Move 3 — Convert auto-writes from silent-append to propose-and-confirm

- The `Stop` hook should **propose** a `MEMORY.md` entry (show the diff) rather than silently append LLM-generated text. A human approving the entry moves the content from the study's −3% "LLM-generated" bucket into the +4% "human-written" bucket. It's a cheap change with a direct evidence basis.
- Default to propose-and-confirm; keep silent-append as an opt-in for users who want the hands-off behavior.

### Move 4 — Extend `optimize` from skills to context files (the headline mechanism)

Today `optimize` targets one `SKILL.md`: eval-first, 1–4 bounded edits, accept only strict improvements, never touch protected sections. Generalize the *same* loop to context files:

- `canon optimize CLAUDE.md` (and `MEMORY.md` / `AGENTS.md`) proposes bounded **deletions** — architecture/overview sections, generic behavior prose, duplicated rules — measures against the project eval, and keeps the prune only if the score holds and token/step cost drops.
- This mechanically operationalizes the study: it removes the sections shown not to help and proves the result didn't regress.
- **This is canon's differentiator in a 9,000-plugin market.** Almost every context/memory plugin *adds*. canon becomes the one that *prunes and proves*. Lead the README with it.
- **Honest caveat to preserve:** `canon-eval` is currently a grader, not a skill runner (it grades static text unless a task's `command:` actually exercises the project). So "prove it didn't regress" depends on a real task command or operator judgment. State that plainly in the spec; don't oversell automated proof. Fixing the grader→runner gap is arguably a prerequisite for Move 4 to mean anything, and should be called out as such.

### Move 5 — Split project facts from behavior preferences in the templates

- Rewrite the ramps around the evidence:
  - **minimal** = recommended default (human-written, small — the category that helps).
  - **standard** = stack lock + constraints + non-standard patterns + gotchas only.
  - **full** = relabel honestly: *"most of this is generic behavior tuning. Put it in your global `~/.claude` settings, not per-project context — it costs tokens on every task, and the evidence says behavior/overview prose doesn't improve task success."*
- Drop the Goal/Audience/Project-context overview block from the context file, or cut it to one line — that's the "Architecture section" the study found removable with no change in behavior.
- Add a one-line template note: *don't put architecture overviews in `CLAUDE.md`.*
- Optional: ship a separate "global settings" starter so the behavior prose has a home to move *to*, rather than just being deleted.

---

## What not to do

- **Don't delete the persistence trio or the hooks.** The machinery is fine; only its default bias needs inverting.
- **Don't abandon `MEMORY.md` / `ERRORS.md`.** A decision log and a failure log are human-written and useful. The fix is bounding what's *loaded into context*, not dropping the logs.
- **Don't auto-prune context without a measured gate.** Machine-editing context unverified is the original sin restated. Every prune goes through the eval, same as `optimize` does for skills today.
- **Don't claim canon "improves accuracy by X%."** After this plan, canon's claim is narrower and defensible: it keeps your context minimal and proves changes against your eval. That's a better claim than a number you can't reproduce.

---

## Build order

1. **README evidence fix.** Cheap, high-credibility, no behavior risk. Do first.
2. **Templates split** — minimal as default, full relabeled, overview block dropped. Mostly editing Markdown.
3. **Propose-and-confirm `Stop` hook** (silent-append becomes opt-in).
4. **Bounded/indexed `SessionStart` loading + context-budget warning.**
5. **`canon optimize <context-file>`** — the headline. Spec it last because it depends on the budget metric (4) and on closing the `canon-eval` grader→runner gap. This is the move worth a proper spec in `docs/specs/`.

---

## Decided (2026-05-29)

1. **README claim — cut it.** Remove the 65% → 94% figure entirely. Lead with the study and canon's narrower, defensible claim: *keep your context minimal and human-curated, and prove changes against an eval.* Karpathy stays credited for the minimal-file pattern.
2. **Auto-write default — propose-and-confirm.** The `Stop` hook proposes a `MEMORY.md` entry for the user to confirm rather than writing silently. Silent-append becomes an opt-in. This moves canon's own output from the study's −3% "LLM-generated" bucket toward the "human-approved" one.
3. **Behavior prose — ship a global-settings starter.** Don't just delete the generic behavior rules from the templates; give them a home. canon ships a `~/.claude` global-defaults starter, and the per-project templates keep only project facts (commands, constraints, non-standard patterns, gotchas).
4. **`canon-eval` runner — ship the tractable upgrade now.** On inspection, `canon-eval` already runs arbitrary `command`s and grades their output, so task-success measurement can already be wired to the user's own test suite. The real gap for *context-file* optimization is a deterministic **size/token metric** to prove a prune cut cost — that ships now (a `max_chars` grader). A full agent-task runner (invoking an agent across tasks, as the ETH study did) is explicitly **out of scope** for canon's size; `optimize` proves "cost dropped" deterministically and "behavior held" via the user's `command`. See `docs/specs/06-optimize-context-files.md`.

---

## Sources

- ETH Zurich, *Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?* (arXiv 2602.11988, Feb 2026) — https://arxiv.org/abs/2602.11988
- InfoQ summary — https://www.infoq.com/news/2026/03/agents-context-file-value-review/
- Engineer's Codex, *Your Agents.md Might Be Making AI Worse* — https://www.engineerscodex.com/agents-md-making-ai-worse/
- canon v0.5.0 — `README.md`, `hooks/hooks.json`, `hooks/scripts/load-memory.sh`, `templates/CLAUDE-{minimal,standard,full}.md`, `skills/optimize/SKILL.md`, `docs/optimize.md`
