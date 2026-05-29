# Run report: craigslist-like — iter-001

## Result

FAIL — `price` came back empty.

## What happened

- Navigated to the listing URL.
- Read `h1.listing-title` → got the title.
- Read `.location` → got the location.
- Read `time.posted` → got the posted date.
- Read `.price` → **empty**. The price block is injected by a lazy-loaded script after first paint, so the selector resolved before the value existed.

## Extracted

```json
{
  "status": "partial",
  "data": {
    "title": "Mid-century walnut desk",
    "price": "",
    "location": "Oakland",
    "posted": "2026-05-12"
  }
}
```

## Hypothesis for next iteration

Wait for network idle (or for `.price` to be non-empty) before reading the price field.
