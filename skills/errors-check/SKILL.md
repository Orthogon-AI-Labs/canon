---
name: errors-check
description: >
  This skill should be used before suggesting an implementation approach for a
  problem that resembles past work — when the user asks "how should I fix X",
  "what's the best way to do Y", "let's tackle Z", or whenever a non-trivial
  approach is about to be proposed. Also triggers on "log this failure",
  "add to ERRORS.md", or "this didn't work, remember it for next time".
metadata:
  version: "0.1.0"
---

# Errors Check

Two-way skill for the failure log:

1. **Read mode** — before suggesting an approach, check `ERRORS.md` for prior failures on similar problems and surface the rejected approaches.
2. **Write mode** — when the user reports a failed approach, append a structured entry so future sessions don't re-derive the same dead end.

This is the "stop suggesting things we already tried" mechanism. It is what keeps Claude from re-proposing Drizzle three months after the team picked Prisma for a specific reason.

## When to Run

**Read mode** — trigger silently before proposing implementation for:

- Bug fixes
- Architecture choices
- Library / tool selection
- Performance work
- Any task involving more than two file edits

Don't ask the user — just check, then mention what was found if anything matches.

**Write mode** — trigger on phrases like:

- "log this failure"
- "add to ERRORS.md"
- "this didn't work, remember for next time"
- "took N attempts to figure out — log it"

## Workflow

### Read mode

1. Locate `ERRORS.md` at the project root. If absent, skip silently — don't pester the user.
2. Read the file and scan for entries whose "What didn't work" or topic line is semantically close to the problem at hand. Match on concepts, not exact strings.
3. If a match is found, **surface it before proposing an approach**: "Before I propose anything — ERRORS.md notes that <X> was tried for a similar problem and didn't work because <Y>. The fix that worked was <Z>. Want me to proceed with that pattern, or are conditions different now?"
4. If no match, proceed normally without mentioning the check.

### Write mode

1. Locate `ERRORS.md` at the project root. If absent, suggest creating it (or running `canon-init`).
2. Compose the entry:

```markdown
## YYYY-MM-DD: <one-line description of the problem>

- **What didn't work:** <the failed approach>
- **Why it failed:** <root cause, as best understood>
- **What worked instead:** <the actual fix>
- **Note for next time:** <one-liner future-Claude should remember>
- **Files / areas affected:** <if applicable>
```

3. Pull details from the conversation rather than re-asking the user. Confirm the draft before writing.
4. Append the new entry to the **top** of the entries section. Never overwrite.

## Threshold rule

Per Karpathy's original framing: log an entry **only when an approach took more than two attempts to get right**. One-shot fixes don't belong in ERRORS.md — they belong in the implementation. The signal-to-noise ratio of ERRORS.md is what makes it useful; flooding it with trivial misfires defeats the purpose.

## Notes for Claude

- **Read mode is the higher-value half.** Most users won't write to ERRORS.md often; the value comes from catching repeated mistakes.
- **Match semantically, not by string.** "auth flow keeps redirecting" and "session cookie not set across subdomains" might describe the same root cause.
- **Don't surface false matches.** If you're not confident the past entry applies, don't mention it — false positives make the user ignore the skill.
- **Cross-reference MEMORY.md** when a logged failure caused a decision to be made — link to the relevant MEMORY.md entry.
