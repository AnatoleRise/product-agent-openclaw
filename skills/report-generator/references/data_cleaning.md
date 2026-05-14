# Data Cleaning Rules

## Purpose

Transform raw search and fetched webpage results into structured data suitable for product exploration reports and difference panels.

## Exclusion Rules

Discard results matching these URL patterns in normal analysis:

```
google.com/search
bing.com/search
youtube.com
twitter.com / x.com
facebook.com
reddit.com
linkedin.com/company
g2.com
capterra.com
trustpilot.com
```

For `market_monitoring`, weak or social sources may be retained only as unverified risk signals when they contain specific evidence. Mark them as `[unverified]`.

## Structured Data Extraction

### Product Information

From each valid crawled result, extract:

| Field | Source | Rule |
|-------|--------|------|
| `name` | Page title | First segment before `-`, `|`, `–` separators |
| `vendor` | Domain or content | Company name from domain or "by {Vendor}" pattern |
| `website` | Result URL | Must be a valid HTTP URL |
| `description` | Content snippet | First 200 characters of relevant content |
| `features` | Content | Named capabilities mentioned in the text |
| `pricing` | Pricing page/content | Plan names, public prices, billing model |
| `updates` | Changelog/blog/news | Release date, change type, impacted feature |
| `risk_signals` | News/status/user feedback | Complaint, outage, negative news, uncertainty |
| `source_type` | URL/content | official, pricing, docs, changelog, media, report, user_feedback |

### Verification Status

- `verified`: Found official website with clear product information
- `partial`: Found product mention but limited official information
- `unverified`: Only found third-party mentions

### Market Insights

Extract qualitative statements about:
- Market trends and growth
- Technology directions
- User preferences
- Competitive dynamics
- Market gaps and product opportunities
- Feature implementation patterns
- Pricing changes and campaign signals
- Risks, complaints, outages, or negative sentiment

Mark each insight with its source URL.

### Difference Panel Dimensions

Prepare normalized dimensions for `difference-panel`:

| Intent | Dimensions |
|--------|------------|
| `market_landscape` | market_positioning, target_users, core_capabilities, pricing_band, ecosystem, opportunity_gap |
| `feature_iteration` | entry_point, core_flow, automation_level, rules_permissions, data_feedback, user_feedback, known_pitfalls |
| `product_competition` | positioning, core_features, pricing_model, target_users, integrations, differentiation |
| `market_monitoring` | release_updates, pricing_changes, market_campaigns, negative_signals, risk_level, response_suggestion |

## Deduplication

1. **By URL**: Keep only one result per URL, prefer the one with more content
2. **By product name**: Merge entries for the same product (case-insensitive match)
3. **By content**: Discard near-duplicate snippets (>80% similarity)

## Output Format

```json
{
  "products": [
    {
      "name": "string",
      "vendor": "string",
      "website": "string",
      "description": "string",
      "features": ["string"],
      "pricing": "string",
      "updates": ["string"],
      "risk_signals": ["string"],
      "verification_status": "verified | partial | unverified",
      "sources": [{"url": "string", "title": "string"}]
    }
  ],
  "insights": [
    {
      "category": "string",
      "content": "string",
      "source_url": "string"
    }
  ],
  "difference_dimensions": [
    {
      "dimension": "string",
      "product": "string",
      "status": "领先 | 持平 | 缺失 | 未知",
      "evidence": "string",
      "source_url": "string",
      "uncertainty": "verified | partial | unverified"
    }
  ],
  "excluded": [
    {
      "name": "string",
      "reason": "string"
    }
  ]
}
```
