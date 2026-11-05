---
description: Check changed Markdown files for protected-section edits
argument-hint: "[--allow=<section-name>]"
allowed-tools: [Bash, Skill]
---

# /canon:check-protected

Route this slash command to the `protected-sections` skill in check mode.

The user invoked:

```text
/canon:check-protected $ARGUMENTS
```

Run the checker from the repository root:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/check-protected-sections.py $ARGUMENTS
```

Only if `${CLAUDE_PLUGIN_ROOT}` isn't set, in a Codex-installed workspace (from `archive/canon-full`) where the checker lives under `.canon/codex/bin/`, use:

```bash
python3 .canon/codex/bin/check-protected-sections.py $ARGUMENTS
```

Accept only `--allow=<section-name>` as a meaningful argument (with `=`, so a name starting with `-` isn't read as an option). If the checker fails, report the exact file and protected block name and ask for explicit approval before proceeding.
