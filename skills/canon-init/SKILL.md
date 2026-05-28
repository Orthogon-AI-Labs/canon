---
name: canon-init
description: >
  This skill should be used when the user asks to "set up CLAUDE.md", "initialize
  project memory", "bootstrap claude.md", "create MEMORY.md", "set up persistent
  context", "install Karpathy's CLAUDE.md trio", or wants to add the
  CLAUDE.md / MEMORY.md / ERRORS.md persistence layer to a project root.
metadata:
  version: "0.1.0"
---

# Project Memory Init

Bootstrap a project with the persistent-context trio that pairs with Compound Engineering: `CLAUDE.md` (behavioral spec the agent reads at session start), `MEMORY.md` (decision log written as work happens), and `ERRORS.md` (failure log consulted before suggesting approaches).

The pattern raises Claude Code coding accuracy from ~65% to ~94% on its own (per the viral Karpathy CLAUDE.md thread) by killing three waste-buckets: re-explaining context every session, unauthorized scope changes, and forgotten decisions.

## When to Run

Trigger this skill when the user:

- Starts a new project that will see repeated Claude Code or Cowork sessions
- Wants to stop re-explaining context every session
- References Karpathy's CLAUDE.md, the 21-rule template, or the MEMORY.md / ERRORS.md trio
- Asks how to make Claude remember decisions across sessions
- Wants the persistence half of the Compound Engineering loop

## Workflow

### 1. Confirm scope

Before writing any files, ask the user:

- Which directory is the project root (default: current working directory)
- Which CLAUDE.md size: **minimal** (Karpathy's 4-line core, fastest setup), **standard** (recommended — 4 rules + decision log + tech stack lock, ~30 min setup), or **full** (the 21-rule template, ~2 hr setup)
- Whether to also wire up the auto-write hooks (defaults to yes — the hooks are what keep MEMORY.md from going stale)
- Whether to also install **Compound Engineering** (defaults to yes — it is the planning half of the loop this plugin is the persistence half of)
- Whether to also install **/last30days** (defaults to yes — it is the research step that grounds `/ce:plan` in current community knowledge instead of stale training data)
- The project name, the user's name and role, and the tech stack — so the templates aren't generic

If the user doesn't supply these, infer from the project's existing files (package.json, pyproject.toml, README) and confirm before writing.

### 2. Install Compound Engineering (if opted in)

Compound Engineering is a separate plugin by @EveryInc that provides `/ce:plan` and `/ce:work` — the planning + execution half of the loop. `canon` is the persistence half. They are designed to compose: every `/ce:plan` lands on top of an agent that has read CLAUDE.md, MEMORY.md, and ERRORS.md; every `/ce:work` that ships writes its outcome back via the Stop hook.

If the user opted in (default):

1. **Check for prior install.** Look for the `/ce:plan` slash command in the current environment. If it's available, skip ahead — Compound Engineering is already installed. Confirm this to the user with one line and move on.

2. **Add the marketplace.** If `/ce:plan` is not available, instruct the user (or run on their behalf, if the host environment allows) to execute:

   ```
   /plugin marketplace add EveryInc/compound-engineering-plugin
   ```

   This registers the plugin source. It is a one-time operation per host environment, not per project.

3. **Install the plugin.** Then run:

   ```
   /plugin install compound-engineering
   ```

   The user may need to confirm the install in the Claude Code or Cowork UI. Wait for confirmation before proceeding to the file-writing step.

4. **Verify.** After install, confirm `/ce:plan` is now available. If verification fails (because the marketplace name changed, the plugin moved, or the user is on a host that doesn't support plugin installs from a skill), report the failure clearly and continue with the rest of the bootstrap — the persistence half still works without Compound Engineering, the user just won't have `/ce:plan` and `/ce:work` to pair with it.

5. **Note for offline / restricted hosts.** If the host environment is Cowork without plugin-install permissions, or the user is offline, surface the marketplace add + install commands as a copy-paste block they can run later when they next open Claude Code, and continue with the rest of the bootstrap.

If the user opted out, skip this entire step.

### 3. Install /last30days (if opted in)

`/last30days` is an open-source skill by Matt Van Horn ([github.com/mvanhorn/last30days-skill](https://github.com/mvanhorn/last30days-skill)). It runs parallel searches across Reddit, Hacker News, Polymarket, GitHub, X / Twitter, YouTube, TikTok, Instagram, Threads, Pinterest, Bluesky, and the open web — typically returning a structured brief in 2-3 minutes. The point: ground `/ce:plan` in *current* community knowledge instead of training-data-era information.

**Cost and setup model (bring your own keys).** Most of `/last30days` is free out of the box: Reddit (with comments), Hacker News, Polymarket, and GitHub work with zero credentials. X / Twitter works free via browser session (just be logged into x.com), YouTube via `yt-dlp` (free), Bluesky via app password (free). The paid unlocks are optional: TikTok, Instagram, Threads, Pinterest, and YouTube comments require a **ScrapeCreators API key** (10,000 free calls, paid after). Perplexity Sonar (via OpenRouter) and Brave web search are optional pay-as-you-go layers. The `/last30days` setup wizard handles all of this on first run — users who only want the free tier can skip the paid unlocks.

The canonical loop is **research → plan → work**:

```
/last30days <topic>     # research
/ce:plan <task>         # plan, grounded in fresh research
/ce:work                # execute
```

If the user opted in (default):

1. **Check for prior install.** Look for the `/last30days` slash command in the current environment. If it's available, skip ahead and confirm one-liner to the user.

2. **Install via the Claude Code marketplace.** If not available, run:

   ```
   /plugin marketplace add mvanhorn/last30days-skill
   ```

   That's the install per Matt's README. If Claude Code prompts for an explicit install confirmation, accept it. For other surfaces (claude.ai web, OpenClaw, Gemini CLI, manual), see the install matrix in [the upstream README](https://github.com/mvanhorn/last30days-skill).

3. **Verify.** After install, confirm `/last30days` is now available. If verification fails, report clearly and continue with the rest of the bootstrap — the persistence + planning loop still works without `/last30days`, the user just won't have the research step pre-wired.

4. **First-run wizard.** On first invocation of `/last30days`, the upstream setup wizard appears and walks the user through optional credential setup. Reddit + HN + Polymarket + GitHub work without any credentials, so the wizard can be fully skipped without losing core value.

5. **Note for offline / restricted hosts.** Same fallback as Compound Engineering — surface the GitHub URL and install command as a copy-paste block for the user to run later, and continue.

If the user opted out, skip this entire step.

### 4. Check for collisions

Read existing `CLAUDE.md`, `MEMORY.md`, `ERRORS.md` at the project root. If any exist:

- Don't overwrite. Show the user the diff between current and proposed
- Offer three options: replace, append-only (preserve existing content under a `## Existing` heading), or skip
- Default to skip if the user is unsure

### 5. Write the files

Use templates in `${CLAUDE_PLUGIN_ROOT}/templates/`:

- `CLAUDE-minimal.md` — Karpathy's 4 viral rules only
- `CLAUDE-standard.md` — 4 rules + stack lock + MEMORY/ERRORS pointers + voice rules
- `CLAUDE-full.md` — the full 21-rule template from the viral thread
- `MEMORY.md` — empty decision log with the expected section headers
- `ERRORS.md` — empty failure log with the expected section headers

For each template, do a find-and-replace pass on these placeholders before writing to the project root:

- `{{PROJECT_NAME}}` — project name
- `{{USER_NAME}}` — user's name
- `{{USER_ROLE}}` — user's role
- `{{STACK}}` — tech stack lines (one per line: Language, Framework, Package manager, etc.)
- `{{VOICE}}` — writing-style description if provided, otherwise leave the section as a TODO comment
- `{{DATE}}` — today's date (YYYY-MM-DD) for MEMORY.md and ERRORS.md headers

If the user didn't provide a field, leave a `{{TODO: ...}}` marker so the file is obviously incomplete and easy to grep for.

### 6. Wire up hooks (default yes)

The bundled hooks in `${CLAUDE_PLUGIN_ROOT}/hooks/hooks.json` are auto-registered when the plugin is installed. No file copying is needed. But explain to the user what the hooks do:

- `SessionStart` — reads MEMORY.md + ERRORS.md into the agent's context at the start of every session
- `Stop` — when Claude finishes a response that completes a unit of work, appends a structured entry to MEMORY.md

If the user opts out of hooks, instruct them to instead say "session end" or "log this decision" verbally when they want a write — the `decision-log` skill in this plugin will pick that up.

### 7. Confirm and hand off

After writing files, output:

- The exact paths created
- A one-line summary of what's in each
- Compound Engineering install status (installed by this run, already present, or skipped per user opt-out / install failed)
- `/last30days` install status (installed by this run, already present, or skipped per user opt-out / install failed)
- A reminder that the bundled `decision-log` and `errors-check` skills handle the manual write/read cases when the hooks aren't sufficient
- A reminder that `look-back`, `protected-sections`, and `optimize` are also available for workflow mining, Markdown invariants, and eval-gated skill improvement
- The canonical loop in one line: `/last30days <topic>` → `/ce:plan <task>` → `/ce:work`
- A suggested first command pair: try `/last30days <topic related to your project>` followed by `/ce:plan <your first task>` — to verify the full loop is wired up end to end

## Output Files

Always produce these at the project root (unless skipped due to collision):

- `CLAUDE.md` — the behavioral spec
- `MEMORY.md` — empty decision log, ready to grow
- `ERRORS.md` — empty failure log, ready to grow

## Notes for Claude

- **Be specific in placeholders.** Generic CLAUDE.md files are the failure mode the original Karpathy thread calls out. Push the user for concrete stack details and voice rules.
- **Don't write code in CLAUDE.md.** The file is rules and context, not implementation.
- **Keep MEMORY.md and ERRORS.md empty at bootstrap.** Don't seed them with examples — they grow from real work.
- **The 4-line minimum is the right starter for most users.** Suggest expanding only once they've seen value.
