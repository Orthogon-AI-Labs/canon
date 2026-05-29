# Task: craigslist-like

## Objective

Extract the structured details (title, price, location, posted date) from a single classifieds-style listing page and return them as JSON.

## Inputs

- URL: a single listing page on a classifieds-style site
- Credentials needed: none (public listing)
- User-provided fields: none

## Expected Output

```json
{
  "status": "success",
  "data": {
    "title": "string",
    "price": "string",
    "location": "string",
    "posted": "string"
  }
}
```

## Success Criteria

- `title`, `price`, `location`, and `posted` are all non-empty strings.
- `status` is `"success"`.

## Constraints

- Do not store secrets.
- Do not write outside `.canon/graduation/tasks/craigslist-like/`.
- One bounded `strategy.md` change per iteration.
