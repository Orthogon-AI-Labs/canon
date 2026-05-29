# Credits

`canon` is a packaging of patterns developed by people in the agent-tooling community. This file lists every component, where it came from, and what canon adds.

---

## Andrej Karpathy — CLAUDE.md / MEMORY.md / ERRORS.md pattern

The three-file persistence pattern at the heart of canon is Karpathy's: a small, human-written context file the agent reads at task start, plus a decision log and a failure log. The full template shipped in `templates/CLAUDE-full.md` is a direct adaptation. (canon no longer repeats the viral "65% → 94%" accuracy figure; see the README's "What the evidence says" for the measured picture.)

What canon uses:
- The three-file structure (`CLAUDE.md` for behavior, `MEMORY.md` for decisions, `ERRORS.md` for failures)
- The four-rule minimum and the full template maximum
- The "session end → append to MEMORY.md" discipline

What canon adds:
- Three CLAUDE.md template sizes (minimal / standard / full) so users can pick the right ramp
- Hooks that keep MEMORY.md and ERRORS.md fresh automatically rather than relying on user discipline
- A read mode on ERRORS.md that runs silently before approach suggestions

---

## Every Inc — Compound Engineering (`/ce:plan` + `/ce:work`)

Repository: [github.com/EveryInc/compound-engineering-plugin](https://github.com/EveryInc/compound-engineering-plugin)

Compound Engineering provides the planning and execution half of the loop that pairs with canon's persistence half. `/ce:plan` runs parallel research agents to produce a structured `plan.md` for a given task. `/ce:work` executes that plan and ticks off acceptance criteria.

What canon uses:
- The auto-install step in `canon-init` runs `/plugin marketplace add EveryInc/compound-engineering-plugin` and `/plugin install compound-engineering` so users get both halves of the loop from one bootstrap command
- The README and documentation point at `/ce:plan` → `/ce:work` → MEMORY.md as the canonical loop

What canon adds:
- The persistence half of that loop (MEMORY.md update on session end)
- Nothing else — Compound Engineering is installed and used unchanged

If you want to opt out of the auto-install, the init skill asks before running it.

---

## Matt Van Horn — `/last30days` skill

Repository: [github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)

`/last30days` runs parallel community-knowledge searches across Reddit, Hacker News, Polymarket, GitHub, X / Twitter, YouTube, TikTok, Instagram, Threads, Pinterest, Bluesky, and the open web, producing a synthesized brief that feeds into `/ce:plan` as fresh source material. Without it, `/ce:plan` is grounded only in your codebase; with it, the plan is also grounded in what the world has said about the problem in the last month.

The skill follows a bring-your-own-keys model. Reddit (with comments), Hacker News, Polymarket, and GitHub work with zero credentials. X via browser session, YouTube via `yt-dlp`, and Bluesky via app password are also free. The paid unlocks (TikTok, Instagram, Threads, Pinterest, YouTube comments) require a ScrapeCreators API key (10,000 free calls, paid after); Perplexity Sonar and Brave search are optional pay-as-you-go layers.

What canon uses:
- The auto-install step in `canon-init` runs the install commands so users get the research → plan → execute → persist loop end-to-end
- The README positions `/last30days <topic>` → `/ce:plan <task>` → `/ce:work` → MEMORY.md as the recommended workflow

What canon adds:
- Nothing — `/last30days` is installed and used unchanged. The opt-out flag in the init skill applies here too.

---

## Mervin Praison — look-back meta-prompt

Source: [Codex Meta-Prompt: Turn Repeated Sessions Into Skills, Subagents, and Automations](https://mer.vin/2026/05/codex-meta-prompt-turn-repeated-sessions-into-skills-subagents-and-automations/) (mer.vin, May 25, 2026)

The `look-back` skill in canon is a direct adaptation of Mervin Praison's meta-prompt for asking Codex to mine recent sessions, Memories, and Chronicle for repeated workflows worth packaging as the smallest useful skill, subagent, or automation. The evidence order, the four creation gates (frequency ≥2, stable I/O, material benefit, no duplicate), and the skill/subagent/automation decision frame are his.

What canon uses:
- The structured meta-prompt body (evidence order, gates, decision frame, shortlist-before-create discipline)
- The "create only high-confidence missing items" rule
- The cross-form taxonomy: skill / custom subagent / automation / skip

What canon adds:
- Packaging the prompt as a triggerable skill (`canon-look-back` / `/canon:look-back`) instead of paste-into-Codex
- Adaptation for both Codex and Claude Code surfaces — canon's port keeps the prompt content runtime-agnostic
- Activation via natural-language triggers ("look back over my recent work," "what should I package as a skill") in addition to the slash command

Mervin's other relevant work: [PraisonAI](https://docs.praison.ai) (agent framework) and [github.com/MervinPraison](https://github.com/MervinPraison).

---

## Inspirations — canon-original implementations, not bundled code

The components above are upstream work canon installs or wraps. The two skills below are different: the *pattern* came from elsewhere, but the code is canon's own. canon does not install or vendor their code — it reimplements the idea, and defers to the original where one exists.

### SkillOpt — the basis for `optimize`

- Paper: *SkillOpt*, one of the first to treat markdown `SKILL.md` files as trainable parameters with a proper optimization framework — [arXiv 2605.23904](https://arxiv.org/abs/2605.23904).
- Referenced implementation: [github.com/muratcankoylan/Agent-Skills-for-Context-Engineering](https://github.com/muratcankoylan/Agent-Skills-for-Context-Engineering).

What canon takes from it: the eval-first loop, the strict-improvement validation gate (ties rejected), bounded edits (best skills land in 1–4 accepted edits), and the "compactness wins" lesson. canon's `optimize` skill and `/canon:optimize` command are an original implementation of that pattern, extended to context files in [`docs/specs/06-optimize-context-files.md`](docs/specs/06-optimize-context-files.md).

### Autobrowse (Browserbase) — the basis for `graduate-skill`

- Autobrowse, created by Shubhankar ([@_shubhankar](https://x.com/_shubhankar)) and written up by Kyle Jeong ([@kylejeong](https://x.com/kylejeong)) of Browserbase ([@browserbase](https://x.com/browserbase)).

What canon takes from it: the "iterate on a real task until it converges, then graduate the winning approach into a durable, reusable skill" loop. canon's `graduate-skill` ([`docs/specs/05-autobrowse-skill-graduation.md`](docs/specs/05-autobrowse-skill-graduation.md)) is an original implementation with an explicit Browserbase-compatibility path — if Autobrowse is present, canon defers to it rather than duplicating it.

---

## The agentic-program-strategies vault

The synthesis that produced canon came from a vault of agent-tooling notes maintained at [github.com/Orthogon-AI-Labs](https://github.com/Orthogon-AI-Labs). The relevant source files were:

- *Karoathsynrules* — the viral CLAUDE.md rules thread captured in full
- *Karpathys knowledge base* / *Karpathy llm wiki* / *How to make karpathys system* — Karpathy's three-layer knowledge-base pattern, of which the CLAUDE.md trio is the simplest case
- *Productivity Tools and Claude Code Hacks* — notes on Compound Engineering's `/ce:plan` + `/ce:work` workflow

See `synthesis-and-ideas.md` in that vault for the full reading.

---

## What's original to canon

The pieces above are the prior art. What's new here:

- A single-command bootstrap that installs all four components (canon's persistence layer, Compound Engineering, /last30days, and the auto-write hooks) and wires them together
- The `hooks.json` discipline: `SessionStart` reads MEMORY.md + ERRORS.md into context; `Stop` *proposes* a MEMORY.md entry for confirmation when work substantial enough to log lands (silent-append is an opt-in); `UserPromptSubmit` invokes `errors-check` in read mode silently before approaches are suggested
- The three CLAUDE.md template sizes (minimal / standard / full) so the user picks the ramp that fits the project's maturity
- The errors-check two-way pattern: silent read on UserPromptSubmit, write on user phrasing
- The auto-install opt-out flags so users who want the persistence layer without the install side effects can decline

If you build on this, attribution is appreciated but not required (MIT license). Calling it "canon by Orthogon AI Labs" in your own README is enough.
