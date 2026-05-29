---
name: {{SKILL_NAME}}
description: >
  <When this skill should fire. Match the runtime's loader convention.>
metadata:
  version: "0.1.0"
---

# {{SKILL_NAME}}

## Purpose

<What this skill reliably does, in one or two sentences.>

## When to Use

- <Trigger phrase or condition>
- <Trigger phrase or condition>

## Required Tools / Env

- <Tool, browser, API, or env var the skill depends on>

## Workflow

The converged fast path — the shortest sequence that actually worked across runs.

<!-- canon:protected:start name="{{SKILL_NAME}}-fast-path" -->
1. <Step that has been validated by a run>
2. <Step>
3. <Step>
<!-- canon:protected:end -->

## Gotchas

- <Site/task-specific trap discovered during iteration, and how to avoid it.>

## Failure Recovery

- <Observed failure → the recovery that worked.>

## Expected Output

```json
{
  "status": "success",
  "data": {}
}
```

---

*Generated from canon skill graduation: {{TASK_NAME}}, {{ITERATIONS}} iterations, {{DATE}}.*
