# canon

canon stops Claude Code from rewriting the parts of your Markdown files you've marked as protected.

## Install

In Claude Code:

```text
/plugin marketplace add Orthogon-AI-Labs/canon
/plugin install canon@canon
```

Or load a local checkout: `claude --plugin-dir /path/to/canon`.

canon needs `git` and `python3`.

## Protect a section

Wrap the section in two markers and commit the file:

```markdown
<!-- canon:protected:start name="voice-rules" -->
Write plainly. No marketing language.
<!-- canon:protected:end -->
```

You can also ask Claude to do it with `/canon:protect <file> <section-name>`. Pick a descriptive name, because it appears in every warning about that block.

A block is protected once it's committed: canon compares your files against the last commit.

## What happens next

- **The agent can't edit the block.** canon blocks any `Edit`, `Write` or `MultiEdit` that would change, remove or rename a protected block, and the agent has to ask you first. Edits outside the block go through.
- **Only you can approve a change.** Put this line in your own message, on a line or sentence of its own:

  ```text
  I approve editing protected section: voice-rules
  ```

  That approves blocks with that name for the rest of the session. If the name has spaces, put it in quotes: `I approve editing protected section: "voice rules"`. The agent can't approve for itself: canon doesn't count the phrase in a question, a code block, text Claude Code adds to the conversation, or a message that quotes canon's own report.
- **Other changes are caught at the end of the reply.** If a protected block changed some other way, such as a shell command or a script, the agent has to report it when it finishes its reply. Each change is reported once.

To stop protecting a block, remove its markers.

## Check by hand

Run `/canon:check-protected` in Claude Code, or this from a checkout of this repo:

```bash
python3 hooks/scripts/check-protected-sections.py
```

It exits 0 if every protected block matches the last commit, 1 if one changed (with the file and block name), and 2 outside a git repository. `--allow=<name>` lets one approved block differ (write it with `=`, so a name starting with `-` isn't read as an option).

## Limits

- canon catches accidental rewrites. It doesn't stop an agent that is deliberately working around it: shell commands are checked only after they run, and an agent could write the approval record itself.
- Markers you haven't committed yet aren't protected.
- Approvals only work when the session starts inside a git repository. Outside one, edit the file yourself or remove the markers.
- An approval covers every block with that name, in any file. Give blocks distinct names.
- canon compares against the last commit, so a change that has been committed is no longer reported.
- Only `.md` files are checked (any case, such as `NOTES.MD`), not `.markdown` or `.mdx`.
- Markers inside a code block count: an example block in a code fence is protected like any other.
- The end-of-reply check covers the repository the session started in, the current one, any repository the agent edited Markdown in, and their submodules. A repository changed only by shell commands isn't checked unless it is one of those.
- The edit guard works out an edit's result the way Claude Code 2.1.312's `Edit` tool applies it. If a later version applies edits differently, the end-of-reply check still catches the result.
- The automatic blocking needs Claude Code hooks. With other agents, run the checker yourself.

## How it works

Three hooks, which do nothing in a project without protected blocks:

- **When you send a message:** records any `I approve editing protected section: <name>` line.
- **Before `Edit`, `Write` or `MultiEdit` on a `.md` file:** works out the file's new text and blocks the edit if an unapproved protected block would change, be removed or renamed, or have its markers broken.
- **When the agent finishes a reply:** compares protected blocks against the last commit and makes the agent report any unapproved change.

Approvals and the record of reported changes are kept in `.git/canon-protected-sections/` of the repository the session started in, so they never show up in `git status`.

## Earlier versions

canon used to be a full project setup, with `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` templates, memory hooks and several other skills. Since 0.6.0 it does only protected sections. The old version is on the [`archive/canon-full`](https://github.com/Orthogon-AI-Labs/canon/tree/archive/canon-full) branch. See [CHANGELOG.md](CHANGELOG.md) and [CREDITS.md](CREDITS.md).

## License

MIT. Built by [Orthogon AI Labs](https://github.com/Orthogon-AI-Labs). Works alongside [agent-verify](https://github.com/Orthogon-AI-Labs/agent-verify), which checks what a coding agent says it did.
