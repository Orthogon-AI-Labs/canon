# canon

**The canonical setup for Claude Code projects, with an experimental Codex port.**

One command installs three pieces of community work and wires them together as one system: Andrej Karpathy's `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` persistence trio, Every Inc's Compound Engineering `/ce:plan` + `/ce:work` planning loop, and Matt Van Horn's `/last30days` research skill. canon adds the bootstrap and the hooks that keep the discipline from rotting.

## What it composes

| Piece | Source | Role |
|---|---|---|
| `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` trio | [Karpathy](https://x.com/karpathy) | Behavioral spec + decision log + failure log. The viral thread reports coding accuracy ~65% → ~94% with the four-line minimum `CLAUDE.md` alone. |
| `/ce:plan` + `/ce:work` | [Every Inc — Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) | Parallel research agents produce a structured plan; execution ticks off acceptance criteria. |
| `/last30days` | [Matt Van Horn](https://github.com/mvanhorn/last30days-skill) | Parallel community-knowledge search across Reddit / HN / Polymarket / GitHub / X / YouTube / TikTok / Instagram / Bluesky / open web — grounds `/ce:plan` in fresh source material. Most sources free; ScrapeCreators key unlocks paid platforms. |

The canonical loop is **research → plan → execute → persist**:

```
/last30days <topic>     → research
/ce:plan <task>         → plan, grounded in fresh research
/ce:work                → execute
MEMORY.md auto-updates  → persist (via canon's Stop hook)
```

## What canon adds

The four pieces above are the prior art. canon is the glue:

- **One-command bootstrap** that installs Compound Engineering and `/last30days`, writes the persistence trio at the project root, and wires up the hooks — all in one go. You can opt out of any sub-install.
- **Hooks that keep the persistence layer fresh** — `SessionStart` reads MEMORY.md and ERRORS.md into context automatically; `Stop` writes to MEMORY.md when work substantial enough to log lands; `UserPromptSubmit` runs `errors-check` silently before approaches are suggested.
- **Three CLAUDE.md template sizes** — `minimal` (Karpathy's 4-line core), `standard` (recommended — 4 rules + stack lock + voice + persistence pointers), `full` (the complete 21-rule template) — so the file fits the project's maturity.
- **The errors-check two-way pattern** — silent read on every implementation-shaped prompt before approaches are suggested, explicit write on "log this failure" phrasing. Stops the agent from re-proposing approaches you already ruled out.
- **The look-back workflow** — mines recent memory, errors, sessions, and git history for repeated work that should become a skill, subagent, automation proposal, or extension.
- **An experimental Codex port** — `AGENTS.md`, portable skill docs, a no-hooks install path, and a `doctor` check for Codex workspaces.
- **Protected Markdown sections** — a shared marker convention and checker that flags accidental edits to slow lessons.
- **The optimize alpha** — eval-first, bounded skill edits that preserve protected sections and keep only strict validation improvements.
- **The opt-out flags** — if you want the persistence half without the auto-installs, every sub-install can be declined and you still get the full canon experience minus the planning/research wiring.

That's it. canon is intentionally small — under 1,000 lines of shell, Markdown, and JSON. The intelligence is in the upstream work; canon's job is to compose it cleanly and keep it from going stale.

## Install

```bash
# In Claude Code
/plugin install /path/to/canon.plugin

# Or via a marketplace
/plugin marketplace add orthogon-ai-labs/canon
/plugin install canon
```

After install, run the init skill once per project:

```
set up canon in this folder
```

The init skill is the full bootstrap. It:

1. Asks which CLAUDE.md size you want (minimal / standard / full) and confirms project name, owner, stack, voice
2. **Installs Compound Engineering for you** — runs `/plugin marketplace add EveryInc/compound-engineering-plugin` and `/plugin install compound-engineering`. Skipped if already installed; opt-out if you don't want it.
3. **Installs `/last30days` for you** from `github.com/mvanhorn/last30days-skill`. Skipped if already installed; opt-out if you don't want it.
4. Checks for existing `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` collisions
5. Writes the three files to your project root
6. Wires up the auto-write hooks (already in this plugin — no extra step)
7. Reports what got created and suggests `/last30days <topic>` → `/ce:plan <task>` → `/ce:work` to verify end-to-end

### Codex experimental install

For Codex workspaces, use the portable installer from this repo:

```bash
scripts/install-codex.sh init --runtime codex --root /path/to/project
scripts/install-codex.sh doctor --runtime codex --root /path/to/project
```

The Codex path writes `AGENTS.md`, `MEMORY.md`, `ERRORS.md`, portable skill docs under `.canon/codex/skills/`, and a protected-section checker under `.canon/codex/bin/`. Existing main files are skipped by default with append/replace guidance; pass `--force` only after reviewing the existing files.

Use `--dry-run` to preview the install before writing or replacing files.

## Using protected sections

The worst kind of agent mistake is the silent one. Tests failing is loud — you see red and fix it. *"I quietly rewrote your hard-won voice rules while reformatting the file"* is silent: you don't notice for a week, by which point the change is buried in history. Protected sections are the cheapest fix for that class of failure.

Wrap any chunk of a Markdown file with two HTML-comment markers:

```markdown
# Project context

We use Python 3.11, FastAPI, and Postgres 16.

<!-- canon:protected:start name="stack-lock" -->

The stack is locked. Don't suggest switching to Node or Mongo.
Don't pull in async libraries that aren't already in `pyproject.toml`.
The ORM is SQLAlchemy 2.0 async — not Django, not Tortoise.

<!-- canon:protected:end -->

## Voice

<!-- canon:protected:start name="voice-rules" -->

Write like a tired senior engineer. No marketing language.
Cite specific line numbers when discussing code.
Never use the word "delve."

<!-- canon:protected:end -->
```

The `name="..."` is yours to pick — make it descriptive (`stack-lock`, `voice-rules`, `migration-schema`) because the name shows up in the failure message when something gets touched.

**Heuristic:** wrap anything you spent more than 20 minutes getting right. The ten seconds it takes to add markers buys you protection against every future agent edit silently undoing the work.

**When you actually want to change a protected block:** either remove the markers (you're saying "this isn't sacred anymore"), or use canon's explicit override phrasing so the change is intentional and recorded. Either is fine; the point is that the change is deliberate rather than accidental.

**Manual check anytime:**

```bash
python3 hooks/scripts/check-protected-sections.py
```

Runs from the repo root. Exits 0 if every protected block is intact, exits 1 with the file and block name if anything was modified. The `protected-sections` skill also wraps this with conversational triggers ("check protected sections," "did anything touch the protected blocks").

## What's in the plugin

**Six skills:**

- `canon-init` — the bootstrap above. Triggers on phrases like "set up canon", "set up CLAUDE.md", "initialize project memory", "bootstrap claude.md".
- `decision-log` — appends decision entries and session summaries to MEMORY.md. Triggers on "log this decision", "remember this choice", "session end", "wrapping up". Pulls content from conversation history rather than re-asking.
- `errors-check` — two-way skill. **Read mode** (silent): scans ERRORS.md before suggesting implementation approaches and surfaces matches when confident. **Write mode**: appends new failure entries on "log this failure", "this didn't work, remember for next time".
- `look-back` — reviews recent work and proposes reusable skills, subagents, automations, extensions, or skips with evidence.
- `protected-sections` — wraps and checks protected Markdown blocks so important invariants are not overwritten by accident.
- `optimize` — runs the alpha skill optimization loop: eval baseline, patch narrowly, validate, preserve protected sections, and report the result.

**Three hooks:**

- `SessionStart` — reads MEMORY.md and ERRORS.md from the project root into context at the start of every session.
- `Stop` — when a response completes a unit of work substantial enough to log, automatically invokes `decision-log`. Conservative — won't write for trivial responses.
- `UserPromptSubmit` — for implementation-shaped requests, silently invokes `errors-check` in read mode before any approach is proposed.

**Templates:**

- `CLAUDE-minimal.md` — Karpathy's four rules + stack + persistence pointers. ~5 minute setup.
- `CLAUDE-standard.md` — minimal plus stack lock, voice rules, scope discipline. ~30 minute setup. **Recommended starter.**
- `CLAUDE-full.md` — the complete 21-rule template. ~2 hour setup.
- `AGENTS-codex.md` — Codex workspace instructions that make memory/error discipline explicit without hooks.
- `eval.yaml` — starter eval file for `canon optimize`.
- `MEMORY.md` / `ERRORS.md` — empty starters with the expected format and threshold rules.

**Script helpers:**

- `hooks/scripts/check-protected-sections.py` — checks changed Markdown files against protected blocks in `HEAD`.
- `hooks/scripts/canon-eval.sh` — runs the alpha eval format used by `optimize`.
- `fixtures/` — small manual fixtures for protected-section checks, look-back evidence, and toy optimize evals.

**Codex port:**

- `ports/codex/README.md` — install, doctor, and runtime notes.
- `ports/codex/SKILL-look-back.md` — mines recent work for reusable workflows.
- `ports/codex/SKILL-protected-sections.md` — protects and verifies Markdown invariants.
- `ports/codex/SKILL-optimize.md` — runs a measured, bounded skill-optimization loop.
- `scripts/install-codex.sh` — portable `init`, `install`, and `doctor` commands for Codex workspaces.

## How to extend

- **Add custom CLAUDE.md sections** by editing `templates/CLAUDE-standard.md` after install — your edits survive re-runs of the init skill, which always asks before overwriting.
- **Disable hooks** by editing `hooks/hooks.json` — set the matcher to a value that never matches, or remove the entry entirely. The skills still work without hooks; they'll just trigger on user phrasing instead of automatically.
- **Tune the Stop hook's conservativeness** in `hooks/hooks.json` — the prompt explicitly tells the hook to be conservative; loosen or tighten the threshold language to taste.
- **Add new protected sections** anywhere in your Markdown — see the [Using protected sections](#using-protected-sections) section above for the marker syntax and workflow.
- **Evaluate a skill** by copying `templates/eval.yaml`, filling in deterministic tasks, and running `hooks/scripts/canon-eval.sh evals/<skill>.yaml`.
- **Try the shipped toy eval** with `hooks/scripts/canon-eval.sh fixtures/evals/toy-email.yaml`.

## Honest limitations

- **Hooks are a Claude Code primitive.** They work cleanly in Claude Code; Cowork support for hooks is more limited. The three skills work in both surfaces.
- **Codex support is explicit rather than automatic.** The Codex port uses `AGENTS.md`, portable skill docs, and manual/doctor checks instead of Claude hook events.
- **MEMORY.md goes stale if you don't ship.** The Stop hook only writes when work substantial enough to log lands. If you spend a week noodling without finishing anything, MEMORY.md won't get richer.
- **ERRORS.md read-mode quality is bounded by semantic match.** A failure logged as "auth flow keeps redirecting" might not get matched against a new prompt about "session cookies." For high-stakes projects, periodically read ERRORS.md yourself.
- **The four-line minimum is enough for most projects.** The full 21-rule template helps mature codebases; on a fresh repo it's overkill.

## Credits

canon is glue. The intelligence is in the upstream work, credited inline above and in detail in [CREDITS.md](CREDITS.md):

- **Andrej Karpathy** — `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` pattern and the 21-rule template
- **Every Inc** — [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) (`/ce:plan` + `/ce:work`)
- **Matt Van Horn** — [/last30days](https://github.com/mvanhorn/last30days-skill) research skill
- **Mervin Praison** — [Codex meta-prompt](https://mer.vin/2026/05/codex-meta-prompt-turn-repeated-sessions-into-skills-subagents-and-automations/) (the basis for canon's `look-back` skill)

The synthesis came from the [agentic-program-strategies vault](https://github.com/orthogon-ai-labs).

## License

MIT. See [LICENSE](LICENSE).

## Part of the agent reliability toolkit

canon is one of three pieces published by [Orthogon AI Labs](https://github.com/orthogon-ai-labs):

- **canon** *(this plugin)* — the canonical setup for Claude Code projects
- **[agent-verify](https://github.com/orthogon-ai-labs/agent-verify)** — claim verification; catches when your agent says it ran tests / deployed / merged but didn't
- **[ShelfAI Pro](https://shelfai.ai)** *(commercial)* — team and enterprise governance: tenant isolation, audit export, policy enforcement, staged change control, and a dashboard for the proposal lifecycle

Each piece installs independently. They compose: MEMORY.md can record agent-verify's catches, and ShelfAI Pro aggregates both layers across an org.
