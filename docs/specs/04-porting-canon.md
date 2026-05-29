# Spec 04: Porting canon to any agent runtime

## One-Liner

canon is not a Claude Code plugin. canon is a set of conventions for persistent agent context that can be ported to any agent runtime. This spec documents the three things a port needs, what they have to satisfy, and how the existing Codex port instantiates each one — so the community can write the Hermes / OpenCode / Aider / next-thing ports without back-and-forth.

## Strategic Frame

The value of canon is the discipline (the three-file persistence trio + the wiring that keeps it fresh) and the composed loop (research → plan → execute → persist). The runtime is implementation detail. Claude Code happens to be where canon was born; Codex is the reference second port. Every other agent that reads a persistence file and runs skills can be a canon target.

We do **not** ship integrations for runtimes we don't dogfood. The Codex port exists because the conventions are documented and the install model is portable, but the cross-vendor story only stays credible if community-contributed ports follow the same shape. This spec defines that shape.

## The three things a canon port needs

Every canon port must ship these three pieces. Anything else is optional polish.

### 1. A persistence-file template

The runtime's equivalent of `CLAUDE.md` — the file the agent reads at session start, where behavioral rules and project context live. Each runtime has a different convention; the port maps canon's discipline onto whichever file the runtime already reads.

Known runtime mappings:

| Runtime | Persistence file | Notes |
|---|---|---|
| Claude Code | `CLAUDE.md` | Canon's native target. |
| Codex (OpenAI) | `AGENTS.md` | Cross-vendor convention adopted by multiple agentic CLIs. |
| Hermes (Nous Research) | `SOUL.md` | Distinct from CLAUDE/AGENTS. Python-native runtime. |
| OpenCode | `OPENCODE.md` or `AGENTS.md` | Claude-Code-style fork; convention is moving toward `AGENTS.md`. |
| Cursor | `.cursorrules` (legacy) or `AGENTS.md` | Newer Cursor versions prefer `AGENTS.md`. |
| Aider | `CONVENTIONS.md` | Read at session start via `--read`. |

`MEMORY.md` and `ERRORS.md` are runtime-agnostic — every port uses the same filenames and the same internal format. Only the *behavioral spec* file varies.

The template must instruct the agent to:

1. Read `MEMORY.md` and `ERRORS.md` at session start when present.
2. Consult `ERRORS.md` before implementation-shaped work.
3. Update `MEMORY.md` when a meaningful decision or shipped unit of work lands.
4. Respect protected sections (`<!-- canon:protected:start -->` markers).
5. Prefer repo-local skills before broad reasoning.
6. Use look-back-style workflow mining when asked.

### 2. An install script with collision-safe writes

A runtime-specific installer that writes the persistence trio (and any portable skills) into a target repo without clobbering existing user content. Must support at least:

- `init` — create the canon files at a target path
- `doctor` — verify all expected files are present and unmodified placeholders are filled
- `--root <path>` — explicit target directory
- `--force` — opt-in overwrite of existing files (off by default)
- `--dry-run` — print intended writes without touching the filesystem (recommended; required for v2)

Collision behavior must be: **skip with guidance by default**, never silently overwrite. The script should print what was created, what was skipped, and what would have been written under `--force`.

The Codex reference implementation lives at `scripts/install-codex.sh`. Its structure (heredoc templates, `${VAR}` substitution, doctor checks) is a fine starting point but not required — the only requirement is the collision-safe write semantics above.

### 3. A skill-format adaptation layer

canon ships its core skills (`look-back`, `protected-sections`, `optimize`) as Claude-Code SKILL.md files with frontmatter. Each port must translate these into the target runtime's skill convention while preserving the underlying *content* (the prompt body, the workflow rules, the user-facing triggers).

Common adaptations:

- **Frontmatter shape** — Claude Code uses `name:` + `description:`. Codex uses "Use when / Don't use when" headers. Hermes loads via `tools.toml`. The port should match the runtime's loader.
- **Slash command names** — canon's `/canon:*` namespace may need different prefixing depending on runtime convention.
- **Hook references** — the Claude Code version of `look-back` references the `Stop` hook implicitly through canon's hook layer. Ports without an equivalent lifecycle event have to wire the skill into natural-trigger phrases or a wrap-up command.
- **Path references** — `${CLAUDE_PLUGIN_ROOT}` is Claude-specific. Each port substitutes the equivalent install path.

The portable skill body — the actual prompt content — should be runtime-agnostic. If a skill mentions `/canon:protect` as a slash command in one runtime and `say "protect this section" to canon` in another, that's fine — the trigger surface changes per runtime, the discipline doesn't.

## Reference implementation: the Codex port

The Codex port is the current canonical example of all three pieces. Walk through it as the reference when building a new port.

| Piece | Lives at | What it does |
|---|---|---|
| Persistence-file template | `templates/AGENTS-codex.md` | Codex-flavored AGENTS.md with the six required instructions, plus `{{...}}` placeholders for project name, owner, stack |
| Install script | `scripts/install-codex.sh` | Heredoc-templated installer with `init`, `install`, `doctor` subcommands, `--root`, `--force`, `--dry-run`. Writes `AGENTS.md` / `MEMORY.md` / `ERRORS.md` and copies portable skills under `.canon/codex/skills/` |
| Skill adaptation | `ports/codex/SKILL-*.md` | Three portable skill files: `look-back`, `protected-sections`, `optimize`. Namespaced as `canon-*` to avoid collision. Strip Claude-only references; reference the installed paths |

Anything a new port does differently from the Codex port is fine — but anything a new port does the *same way* should follow the Codex pattern, so users moving between ports see a consistent experience.

## Acceptance criteria for a new port

A new port lands when:

1. A persistence-file template exists at `templates/<RUNTIME>-canon.md` (or equivalent) that satisfies the six required instructions above.
2. An install script at `scripts/install-<runtime>.sh` (or a `bin/canon` subcommand) implements `init` and `doctor` with collision-safe writes.
3. The three core skills (`look-back`, `protected-sections`, `optimize`) are adapted to the runtime's skill format and ship under `ports/<runtime>/`.
4. A `ports/<runtime>/README.md` explains the install path, the runtime-specific differences, and any limitations vs the Claude Code reference.
5. The main canon README's runtime mapping table includes the new port.
6. The PR includes a basic smoke test (manual fixtures fine — see Codex port's `tmp/codex-port-*` for shape).

## Wanted ports

These are the runtimes the canon maintainers think are highest-value next ports. Community contributors welcome. Each ships as a separate PR.

- **Hermes** (Nous Research, Python-native, [github.com/NousResearch/hermes](https://github.com/NousResearch) — exact repo TBD) — uses `SOUL.md` as the persistence file. Has 5 execution backends (local/Docker/SSH/Singularity/Modal). A canon-for-Hermes port should map the persistence trio onto SOUL + MEMORY + ERRORS and adapt skills to whatever Hermes's skill loader expects. Likely the second-most-interesting port after Codex because Hermes's user base is distinct from Anthropic's.
- **OpenCode** (Claude-Code-style OSS fork, growing community) — the install path is structurally similar to Claude Code because OpenCode forks much of Claude Code's plugin model. This is likely the **lowest-effort port** of any major runtime. Good first PR for someone learning canon's shape.
- **Cursor** — newer versions read `AGENTS.md`. Could potentially share the Codex `AGENTS-codex.md` template with minor adjustments. Cursor has the largest install base of any runtime listed here.
- **Aider** — reads `CONVENTIONS.md` via `--read` flag. Aider's user base is smaller but very technical and disciplined; canon's value prop should land cleanly.

If you want to ship one of these, see **Contributing a port** below.

## Contributing a port

1. Open a GitHub issue at [orthogon-ai-labs/canon](https://github.com/orthogon-ai-labs/canon) titled `Port: <runtime>` to coordinate.
2. Mirror the Codex port structure (templates, scripts, ports/<runtime>/, ports/<runtime>/README.md).
3. Add your runtime to the persistence-file mapping table in this spec.
4. Submit the PR with a smoke-test demonstration showing `init` + `doctor` against an empty target repo, an existing-conflict repo, and a force-override case.
5. Add the runtime to the canon main README's "Supported runtimes" table.

## Out of scope

- A unified `canon` CLI that dispatches across runtimes — possible long-term, not required for v1.
- Auto-detection of which runtime a target repo is meant for — explicit `--runtime` flag is fine.
- GUI installers.
- Distribution through runtime marketplaces (e.g., Codex app marketplace) — those can come once a port is stable.

## Launch copy

canon now ships with a documented model for porting to any agent runtime. The Codex port is the reference implementation; Hermes, OpenCode, Cursor, and Aider are wanted next. Open an issue if you're starting a port — we'll help you avoid the gotchas the Codex port already hit.
