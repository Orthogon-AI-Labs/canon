---
name: decision-log
description: >
  This skill should be used when the user says "log this decision", "remember
  this choice", "save this to MEMORY.md", "session end", "wrapping up",
  "let's stop here", or any phrase that signals a significant decision or the
  close of a working session that should be persisted to MEMORY.md at the
  project root.
metadata:
  version: "0.1.0"
---

# Decision Log

Append structured entries to `MEMORY.md` at the project root so that future sessions can read decisions and session summaries instead of re-deriving them.

This skill handles two kinds of writes: **decision entries** (a single significant choice the user wants persisted) and **session summaries** (everything accomplished in the current session).

## When to Run

**Decision entries** — trigger on phrases like:

- "log this decision"
- "remember this choice"
- "save this to MEMORY.md"
- "we're going with X instead of Y" (when the user signals it should be remembered)

**Session summaries** — trigger on phrases like:

- "session end"
- "wrapping up"
- "let's stop here"
- "we're done for today"

If the user's phrasing is ambiguous, ask which kind of write they want before proceeding.

## Workflow

### 1. Locate MEMORY.md

Look for `MEMORY.md` at the project root (the same directory as `package.json`, `pyproject.toml`, `.git`, or wherever the user has been working). If it doesn't exist, suggest running the `canon-init` skill first and ask whether to create a stub MEMORY.md now or skip the write.

### 2. Compose the entry

**For decision entries**, format as:

```markdown
## YYYY-MM-DD: <one-line decision title>

- **What was decided:** <the choice>
- **Why:** <the reason>
- **What was rejected and why:** <alternatives considered and why they lost>
- **Files / areas affected:** <if applicable>
```

**For session summaries**, format as:

```markdown
## YYYY-MM-DD: Session summary

- **Worked on:** <high-level summary>
- **Completed:** <what shipped>
- **In progress:** <what's left>
- **Decisions made:** <link to decision entries above or inline list>
- **Next session priorities:** <what to pick up next>
```

Pull session content from the conversation history rather than asking the user to repeat themselves. Confirm the draft with the user before writing.

### 3. Append, never overwrite

Use `Edit` or append-mode `Write` to add the new entry to the **top** of the section, just below the header, so the most recent entries are visible first. Never delete or modify existing entries.

### 4. Confirm the write

Show the user the appended block and the line range in MEMORY.md. Offer to also update `ERRORS.md` if the session involved a failure pattern worth logging there.

## Notes for Claude

- **Be terse.** Each entry should be readable in five seconds. The "why" matters more than the "what."
- **Don't editorialize.** Capture the decision the user actually made, not the one Claude thinks they should have made.
- **Date format is YYYY-MM-DD.** Use the system date, not what the user thinks today is.
- **If MEMORY.md already has an entry for today**, append under the same date heading rather than creating a duplicate date header.
- **Cross-reference ERRORS.md** when a decision was driven by a past failure — mention "see ERRORS.md: <entry>" in the "Why" line.
