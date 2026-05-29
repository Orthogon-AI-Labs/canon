# Task: {{TASK_NAME}}

## Objective

<What the agent must accomplish, in one or two sentences.>

## Inputs

- URL:
- Credentials needed: <name them; never paste values here>
- User-provided fields:

## Expected Output

```json
{
  "status": "success",
  "data": {}
}
```

## Success Criteria

- <Observable pass/fail condition. Be concrete — "price field is a non-empty string", not "looks right".>

## Constraints

- Do not store secrets.
- Do not write outside `.canon/graduation/tasks/{{TASK_NAME}}/`.
- One bounded `strategy.md` change per iteration.
