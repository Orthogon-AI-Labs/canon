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
- **Shell changes are reported right away.** If a shell command changes a protected block (`sed -i`, a heredoc, a script), canon tells the agent as soon as the command finishes, while it can still undo the change.
- **Other changes are caught at the end of the reply.** If a protected block changed some other way, such as you editing the file, the agent has to report it when it finishes its reply.
- **Each change is reported once.** A change reported after a shell command isn't reported again at the end of the reply. It is reported again if the block's text changes further, or if it's undone and then comes back.

To stop protecting a block, remove its markers.

## Check by hand

Run `/canon:check-protected` in Claude Code, or this from a checkout of this repo:

```bash
python3 hooks/scripts/check-protected-sections.py
```

It exits 0 if every protected block matches the last commit, 1 if one changed (with the file and block name), and 2 outside a git repository. `--allow=<name>` lets one approved block differ (write it with `=`, so a name starting with `-` isn't read as an option).

## Limits

- canon catches accidental rewrites. It doesn't stop an agent that is deliberately working around it: shell commands are checked only after they run, and an agent could write the approval record itself.
- The check after a shell command reports a change; it doesn't undo it. Because that report isn't repeated at the end of the reply, an agent that ignores it can still leave the change out of its reply.
- Only Claude Code's `Bash` tool is checked as it runs. A block changed by another tool, such as an MCP server's, is caught at the end of the reply.
- The check after each `Bash` command adds about 0.2 s to it (median 203 ms over 20 runs on an Apple-silicon Mac, in a small repository).
- Markers you haven't committed yet aren't protected.
- Approvals only work when the session starts inside a git repository. Outside one, edit the file yourself or remove the markers.
- An approval covers every block with that name, in any file. Give blocks distinct names.
- canon compares against the last commit, so a change that has been committed is no longer reported.
- Only `.md` files are checked (any case, such as `NOTES.MD`), not `.markdown` or `.mdx`.
- Markers inside a code block count: an example block in a code fence is protected like any other.
- The end-of-reply check, and the check after each shell command, cover the repository the session started in, the current one, any repository the agent edited Markdown in, and their submodules. A repository changed only by shell commands isn't checked unless it is one of those.
- The edit guard works out an edit's result the way Claude Code 2.1.312's `Edit` tool applies it. If a later version applies edits differently, the end-of-reply check still catches the result.
- The automatic blocking needs Claude Code hooks. With other agents, run the checker yourself.

## How it works

Four hooks, which do nothing in a project without protected blocks:

- **When you send a message:** records any `I approve editing protected section: <name>` line.
- **Before `Edit`, `Write` or `MultiEdit` on a `.md` file:** works out the file's new text and blocks the edit if an unapproved protected block would change, be removed or renamed, or have its markers broken.
- **After each `Bash` command, whether it succeeded or failed:** runs the end-of-reply check below and tells the agent at once about any unapproved change it hasn't been told about.
- **When the agent finishes a reply:** compares protected blocks against the last commit and makes the agent report any unapproved change it hasn't been told about.

Both checks share one record of what they reported. A change is a file, a block and the block's current text, so a change reported after a command isn't repeated at the end of the reply, an edit elsewhere in the file that only moves the block isn't reported, and a further edit to the block is. Once a block matches the last commit again, it is dropped from the record.

Approvals and the record of reported changes are kept in `.git/canon-protected-sections/` of the repository the session started in, so they never show up in `git status`.

## Earlier versions

canon used to be a full project setup, with `CLAUDE.md` / `MEMORY.md` / `ERRORS.md` templates, memory hooks and several other skills. Since 0.6.0 it does only protected sections. The old version is on the [`archive/canon-full`](https://github.com/Orthogon-AI-Labs/canon/tree/archive/canon-full) branch. See [CHANGELOG.md](CHANGELOG.md) and [CREDITS.md](CREDITS.md).

## License

MIT. Built by [Orthogon AI Labs](https://github.com/Orthogon-AI-Labs). Works alongside [agent-verify](https://github.com/Orthogon-AI-Labs/agent-verify), which checks what a coding agent says it did.
