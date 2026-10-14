# canon

**Protected sections for Claude Code: mark the parts of your Markdown an agent must not rewrite, and canon keeps them that way.**

The worst kind of agent mistake is the silent one. Tests failing is loud — you see red and fix it. *"I quietly rewrote your hard-won voice rules while reformatting the file"* is silent: you don't notice for a week, by which point the change is buried in history. Protected sections are the cheapest fix for that class of failure.

You wrap a block of Markdown in two comment markers. From then on:

- **Before an edit,** canon blocks any `Edit`, `Write` or `MultiEdit` that would change the block, and the agent asks you for approval instead.
- **Approval comes only from you:** a line in your own message, `I approve editing protected section: <name>`. The agent can't approve for itself.
- **After each reply,** canon catches a protected block changed any other way (through Bash, a script, or by hand) and makes the agent report it, once.

## Install

```text
/plugin marketplace add Orthogon-AI-Labs/canon
/plugin install canon@canon
```

Or from a local checkout: `claude --plugin-dir /path/to/canon`.

canon needs `git` and `python3`. A block is protected once it's committed: canon compares your Markdown with `HEAD`.

## Using protected sections

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

Or ask for it: `/canon:protect <file> <section-name>` wraps the section for you. Commit the file, and the block is protected.

The `name="..."` is yours to pick — make it descriptive (`stack-lock`, `voice-rules`, `migration-schema`) because the name shows up in the failure message when something gets touched.

**Heuristic:** wrap anything you spent more than 20 minutes getting right. The ten seconds it takes to add markers buys you protection against every future agent edit silently undoing the work.

**When you actually want to change a protected block:** either remove the markers (you're saying "this isn't sacred anymore"), or approve the change in your own message:

```text
I approve editing protected section: voice-rules
```

canon records that for the rest of the session, for that block only, and lets edits to it through. The phrase has to start a line or follow punctuation ("Ok, I approve …"), so a question like "Should I approve editing protected section: voice-rules?" doesn't count.

**Manual check anytime:** `/canon:check-protected` runs the checker against `HEAD`. From a checkout of this repo:

```bash
python3 hooks/scripts/check-protected-sections.py
```

It exits 0 if every protected block is intact and 1 with the file and block name if anything was modified (2 outside a git repo). `--allow <name>` lets one approved block differ. The `protected-sections` skill wraps this with conversational triggers ("check protected sections," "did anything touch the protected blocks").

## How it works

Three hooks, all no-ops when there is nothing protected:

| Hook | When | What it does |
| --- | --- | --- |
| `UserPromptSubmit` (approvals) | You send a message | Records `I approve editing protected section: <name>` for the rest of the session. |
| `PreToolUse` (edit guard) | Before `Edit`, `Write` or `MultiEdit` on a Markdown file | Works out the file's text after the edit and blocks it if an unapproved protected block would change, be removed or renamed, or lose a marker. Edits outside blocks, and edits that restore a block to `HEAD`, go through. If the guard can't tell what an edit does, it lets it through and the `Stop` hook checks the result. |
| `Stop` (after-the-fact check) | The agent finishes a reply | Runs the checker against `HEAD`, skipping approved blocks. If an unapproved block changed some other way, it blocks the stop once and tells the agent: an edit the agent made is reverted or sent back to you for approval, and a change it didn't make is reported and left alone. Each change is reported once per session; it can't loop. |

Approvals and the record of what was reported live in the git directory (`.git/canon-protected-sections/`), so they never show in `git status`.

**What's in the plugin:**

- `skills/protected-sections/` — protect, check and approve flows, with the conversational triggers.
- `commands/canon/protect.md`, `commands/canon/check-protected.md` — `/canon:protect` and `/canon:check-protected`.
- `hooks/scripts/check-protected-sections.py` — the checker: compares changed Markdown files with protected blocks in `HEAD`. A plain CLI that works without Claude Code.
- `hooks/scripts/protected-sections-guard.py` — the edit guard and the approval recorder.
- `hooks/scripts/protected-sections-stop-hook.py` — the `Stop` hook wrapper around the checker.
- `hooks/scripts/canon_protected.py` — helpers shared by the two hook scripts.
- `fixtures/protected/` — Markdown cases for testing the checker by hand.

## Honest limitations

- **Not a security boundary.** Bash and other tools aren't checked before they run; the `Stop` hook catches their changes afterwards. An agent set on getting around canon could also write the approvals file itself. canon guards against accidental rewrites, not a hostile agent.
- **Only committed blocks are protected.** Markers you've added but not committed aren't guarded yet.
- **Approvals need a git repository at the session's working directory.** Started outside one, canon can't record approvals, so the guard keeps blocking; edit the file yourself or remove the markers.
- **Hooks are a Claude Code feature.** In other agents, run the checker yourself.

## What happened to the rest of canon

Earlier versions of canon were a whole project setup: a `canon-init` bootstrap, `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` templates and memory hooks, installs of Compound Engineering and `/last30days`, the `look-back`, `optimize` and `graduate-skill` skills, an eval runner, and a Codex port. Much of that now overlaps with what Claude Code does on its own, so canon is now just protected sections. Everything removed is on the [`archive/canon-full`](https://github.com/Orthogon-AI-Labs/canon/tree/archive/canon-full) branch, with its credits.

## Credits

Protected sections are original to canon. Earlier versions packaged work by Andrej Karpathy, Every Inc, Matt Van Horn and Mervin Praison; see [CREDITS.md](CREDITS.md).

## License

MIT. See [LICENSE](LICENSE).

## Part of the agent reliability toolkit

canon is one of three pieces published by [Orthogon AI Labs](https://github.com/Orthogon-AI-Labs):

- **canon** *(this plugin)* — protected sections: stops your agent from rewriting what you said not to touch
- **[agent-verify](https://github.com/Orthogon-AI-Labs/agent-verify)** — claim verification; catches when your agent says it ran tests / deployed / merged but didn't
- **[ShelfAI Pro](https://shelfai.ai)** *(commercial)* — team and enterprise governance: tenant isolation, audit export, policy enforcement, staged change control, and a dashboard for the proposal lifecycle

Each piece installs independently. They compose: agent-verify checks "protected sections are intact" claims using canon's markers, and ShelfAI Pro aggregates both layers across an org.
