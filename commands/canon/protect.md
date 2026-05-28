---
description: Protect a Markdown section with canon protected-section markers
argument-hint: "<file> <section-name>"
allowed-tools: [Read, Edit, MultiEdit, Bash, Skill]
---

# /canon:protect

Route this slash command to the `protected-sections` skill in protect mode.

The user invoked:

```text
/canon:protect $ARGUMENTS
```

Parse `$ARGUMENTS` as:

```text
<file> <section-name>
```

If either argument is missing, ask for the missing value. Once both are known, wrap only the user-intended Markdown section with:

```markdown
<!-- canon:protected:start name="<section-name>" -->
...
<!-- canon:protected:end -->
```

Keep the edit narrow, preserve the section body exactly, and run the protected-section checker after the edit when the repository is a git worktree.
