---
description: Run a canon alpha eval for a skill or eval file
argument-hint: "<eval-file | skill-path>"
allowed-tools: [Read, Glob, Bash, Skill]
---

# /canon:eval

Route this slash command to the `optimize` skill's eval workflow.

The user invoked:

```text
/canon:eval $ARGUMENTS
```

Resolve the eval target as follows:

1. If `$ARGUMENTS` names an existing `.yaml`, `.yml`, or `.json` eval file, run:

   ```bash
   hooks/scripts/canon-eval.sh <eval-file>
   ```

2. If `$ARGUMENTS` names a skill path, derive the skill slug from the path and look for:

   ```text
   evals/<skill-slug>.yaml
   evals/<skill-slug>.json
   ```

   Run the first one that exists.

3. If no eval file exists, refuse to run and tell the user to create one from:

   ```text
   templates/eval.yaml
   ```

Do not invent an eval silently. Running an eval is read-only except for normal shell/cache artifacts.
