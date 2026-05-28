# Credits

`canon` is a packaging of patterns developed by people in the agent-tooling community. This file lists every component, where it came from, and what canon adds.

---

## Andrej Karpathy — CLAUDE.md / MEMORY.md / ERRORS.md pattern

The three-file persistence pattern at the heart of canon is Karpathy's. The viral thread that established it reported coding accuracy moving from roughly 65% to roughly 94% with the four-line minimum `CLAUDE.md` alone. The 21-rule template shipped in `templates/CLAUDE-full.md` is a direct adaptation.

What canon uses:
- The three-file structure (`CLAUDE.md` for behavior, `MEMORY.md` for decisions, `ERRORS.md` for failures)
- The four-rule minimum and the 21-rule maximum
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

`/last30days` runs parallel community-knowledge searches across Reddit, X, YouTube, TikTok, Instagram, HN, Polymarket, and the open web, producing a synthesized brief that feeds into `/ce:plan` as fresh source material. Without it, `/ce:plan` is grounded only in your codebase; with it, the plan is also grounded in what the world has said about the problem in the last month.

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

## The agentic-program-strategies vault

The synthesis that produced canon came from a vault of agent-tooling notes maintained at [github.com/orthogon-ai-labs](https://github.com/orthogon-ai-labs). The relevant source files were:

- *Karoathsynrules* — the viral 21-rule CLAUDE.md thread captured in full
- *Karpathys knowledge base* / *Karpathy llm wiki* / *How to make karpathys system* — Karpathy's three-layer knowledge-base pattern, of which the CLAUDE.md trio is the simplest case
- *Productivity Tools and Claude Code Hacks* — Matt Van Horn's `/ce:plan` + `/ce:work` workflow notes

See `synthesis-and-ideas.md` in that vault for the full reading.

---

## What's original to canon

The pieces above are the prior art. What's new here:

- A single-command bootstrap that installs all four components (canon's persistence layer, Compound Engineering, /last30days, and the auto-write hooks) and wires them together
- The `hooks.json` discipline: `SessionStart` reads MEMORY.md + ERRORS.md into context; `Stop` writes to MEMORY.md when work substantial enough to log lands; `UserPromptSubmit` invokes `errors-check` in read mode silently before approaches are suggested
- The three CLAUDE.md template sizes (minimal / standard / full) so the user picks the ramp that fits the project's maturity
- The errors-check two-way pattern: silent read on UserPromptSubmit, write on user phrasing
- The auto-install opt-out flags so users who want the persistence layer without the install side effects can decline

If you build on this, attribution is appreciated but not required (MIT license). Calling it "canon by Orthogon AI Labs" in your own README is enough.
