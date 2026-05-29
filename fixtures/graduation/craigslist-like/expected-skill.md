---
name: classifieds-listing-extract
description: >
  Use to extract structured details (title, price, location, posted date) from a
  single classifieds-style listing page and return them as JSON.
metadata:
  version: "0.1.0"
---

# classifieds-listing-extract

## Purpose

Extract title, price, location, and posted date from one classifieds-style listing page and return a structured JSON object.

## When to Use

- "pull the details from this listing"
- "extract title/price/location from this classifieds page"

## Required Tools / Env

- A browser automation tool (manual or Browserbase) that can navigate a URL and wait on selectors.
- No credentials — listings are public.

## Workflow

<!-- canon:protected:start name="classifieds-listing-extract-fast-path" -->
1. Navigate to the listing URL.
2. Read `h1.listing-title`, `.location`, and `time.posted`.
3. Wait for `.price` to be non-empty (network-idle, ≤ 5s) before reading it.
4. If `.price` is still empty, fall back to the `og:price:amount` meta tag.
5. Return the four fields as JSON with `status: "success"`.
<!-- canon:protected:end -->

## Gotchas

- The price block is lazy-loaded after first paint — reading `.price` immediately returns empty. Always wait for it.
- Some listings never render the visible price block; the `og:price:amount` meta tag is the reliable fallback.

## Failure Recovery

- Empty `price` after the wait → read the `og:price:amount` meta tag.
- Any field empty after both paths → return `status: "partial"` with the fields that resolved, rather than a fabricated value.

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

---

*Generated from canon skill graduation: craigslist-like, 2 iterations, 2026-05-15.*
