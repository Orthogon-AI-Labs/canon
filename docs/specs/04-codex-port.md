# Spec 04: canon for Codex

## One-Liner

Port canon's persistence and skill-management patterns to Codex with portable templates, runtime-specific adapters, and the same memory/error discipline.

## Strategic Frame

canon should not be "a Claude Code plugin." canon should be the portable reliability layer for agent workspaces. The Codex port is the proof.

## User Surface

Commands:

```text
scripts/install-codex.sh init --runtime codex
scripts/install-codex.sh install --runtime codex
scripts/install-codex.sh doctor --runtime codex
```

If no CLI exists yet, expose as a portable skill:

```text
set up canon for Codex in this folder
```

Natural triggers:

- "set up canon for Codex"
- "port canon to Codex"
- "make this repo Codex-ready"
- "install the canon memory trio for Codex"

## Scope

In scope:

- Codex-oriented `AGENTS.md` template.
- `MEMORY.md` and `ERRORS.md` templates reused from canon.
- Codex skill format for `look-back`, `protected-sections`, and `optimize`.
- Runtime adapter docs.
- One install path that does not depend on Claude plugin hooks.

Out of scope for v1:

- Full Claude plugin parity.
- Codex app marketplace distribution.
- Deep Chronicle integration.
- GUI installer.

## Runtime Differences

| Capability | Claude Code canon | Codex canon |
|---|---|---|
| Main instructions | `CLAUDE.md` | `AGENTS.md` |
| Hooks | Claude plugin hooks | Explicit commands / skills first |
| Skills | `skills/<name>/SKILL.md` | Codex skills or repo-local docs |
| Memory load | `SessionStart` hook | Agent instruction in `AGENTS.md` |
| Stop write | `Stop` hook | Explicit "session end" / future automation |
| Error check | `UserPromptSubmit` hook | Manual or wrapped command |

## Proposed Files

```text
ports/codex/AGENTS.md
ports/codex/SKILL-look-back.md
ports/codex/SKILL-protected-sections.md
ports/codex/SKILL-optimize.md
ports/codex/README.md
docs/specs/04-codex-port.md
```

Optional:

```text
templates/AGENTS-codex.md
scripts/install-codex.sh
```

## Codex AGENTS.md Requirements

The Codex template must instruct the agent to:

1. Read `MEMORY.md` and `ERRORS.md` at session start when present.
2. Consult `ERRORS.md` before implementation-shaped work.
3. Update `MEMORY.md` when a meaningful decision or shipped unit of work lands.
4. Respect protected sections.
5. Prefer repo-local skills before broad reasoning.
6. Use look-back style workflow mining when asked.

## Install Flow

1. Detect current workspace.
2. Check for existing `AGENTS.md`, `MEMORY.md`, and `ERRORS.md`.
3. If collisions exist, offer append/skip/replace guidance.
4. Write missing files.
5. Copy or reference portable skill docs.
6. Print next commands:

   ```text
   Ask Codex: "read AGENTS.md, then run scripts/install-codex.sh doctor --runtime codex"
   Ask Codex: "look back over recent work and suggest reusable skills"
   ```

## `scripts/install-codex.sh doctor --runtime codex`

Doctor checks:

- `AGENTS.md` exists.
- `MEMORY.md` exists.
- `ERRORS.md` exists.
- Protected-section checker is available.
- Portable skills are installed or linked.
- No unresolved `{{TODO}}` template placeholders remain.

## Implementation Plan

1. Create `ports/codex/README.md`.
2. Create `templates/AGENTS-codex.md`.
3. Port `look-back` as a Codex-friendly skill doc.
4. Port protected sections as a runtime-agnostic checker.
5. Port optimize alpha as a command/spec workflow.
6. Update main README: "canon supports Claude Code today; Codex port is experimental."

## Acceptance Criteria

- A fresh repo can be made Codex-ready without Claude plugin hooks.
- The Codex template clearly maps to `MEMORY.md` and `ERRORS.md`.
- Existing files are not overwritten without confirmation.
- `scripts/install-codex.sh doctor --runtime codex` has clear pass/fail output.
- Runtime-specific instructions do not leak Claude-only commands.

## Tests

Manual fixture:

```text
tmp/codex-port-empty/
tmp/codex-port-existing-agents/
tmp/codex-port-existing-memory/
```

Expected:

- Empty fixture gets all files.
- Existing `AGENTS.md` fixture produces append/skip/replace guidance.
- Existing memory fixture preserves prior logs.

## Launch Copy

canon is becoming runtime-portable. Claude Code gets hooks; Codex gets explicit workspace discipline. The memory model stays the same.
