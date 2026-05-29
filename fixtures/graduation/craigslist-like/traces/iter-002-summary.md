# Run report: craigslist-like — iter-002

## Result

PASS — all four fields extracted.

## Change applied (one bounded strategy edit)

Before reading `.price`, wait for it to be non-empty (network-idle wait), with a fallback to the `og:price:amount` meta tag when the visible block is still empty after the wait.

## What happened

- Navigated to the listing URL.
- Waited for `.price` to be non-empty (≤ 5s).
- All four fields resolved.

## Extracted

```json
{
  "status": "success",
  "data": {
    "title": "Mid-century walnut desk",
    "price": "$240",
    "location": "Oakland",
    "posted": "2026-05-12"
  }
}
```

## Notes

- The meta-tag fallback also covered a second listing where the price block never rendered.
- Two consecutive passing runs → convergence rule met.
