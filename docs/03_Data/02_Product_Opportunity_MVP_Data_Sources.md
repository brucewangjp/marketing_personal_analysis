# Product Opportunity MVP Data Source Plan

- Version: v0.2
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Decision

The first US Product Opportunity MVP uses **free sources only**, accessed in the tier
order defined in `docs/01_Product/00_Shared_Research_Foundation.md` section 3.1
(official API first, then official export, then collection from public web pages, then
manual import). A paid licence is considered only after a free route has been shown not
to answer the research question.

Four source types:

1. **FRED** — US consumption and retail demand context. Tier 1, free API.
2. **Google Trends** — anonymized, aggregated search interest for category and product
   terms. Tier 2 or 3; no stable official public API.
3. **Marketplace signals** — what is actually listed, ranked, and reviewed. Tier 1 where
   a marketplace publishes a free API, Tier 3 where it does not.
4. **Public-discussion data** — group-level pain points, unmet needs, and customer
   language. Tier 1 where the platform publishes a free API.

### What the first version does and does not measure

This answers the open question "Does the first version need actual sales data, or is it a
demand-signal discovery tool?" from `docs/01_Product/02_US_Product_Opportunity_MVP.md`.

The first version is a **demand-signal and marketplace-proxy discovery tool**. It reports
what is listed, ranked, searched, reviewed, and discussed. It does not report unit sales,
revenue, or market size, because:

- No major US marketplace publishes unit sales volume through any interface, free or paid.
  Ranking, review count, and listing count are **proxies** (shared terminology, section 4)
  and are labeled as such everywhere they appear.
- Tools that do sell sales figures publish modelled *estimates*, and their terms generally
  restrict re-displaying that data inside another product.

This is a limit on what the data can support, not a limit on budget or on effort. Every
free route to marketplace evidence is in scope and listed in section 5.

## 2. FRED

### Purpose

Provide US demand and spending context for a product category, so that a category's
attention signal can be read against the broader consumer environment.

### Initial use cases

- Retail and e-commerce sales indicators for overall demand direction.
- Personal consumption expenditure indicators for category-adjacent spending context.
- Price indices where a category's affordability is part of the research question.
- The University of Michigan Consumer Sentiment series as aggregate consumer context,
  where licensing and attribution requirements are met.

### Required safeguards

- Use a registered API key and keep it outside the repository.
- Store the series identifier, observation period, release date when available, and
  retrieval date.
- Label each indicator with its geography, frequency, and attribution requirements.
- Do not present a macroeconomic indicator as evidence that a specific product sells.

## 3. Google Trends

### Purpose

Measure change in anonymized, aggregated US search interest for a category, product term,
or problem description.

### Initial indicators

- Interest over time for a category or product term across the selected window.
- Comparison between related terms to show relative, not absolute, attention.
- Rising and related queries as candidate emerging topics.
- Seasonality check across a longer window before calling a rise a trend.

### Access

Google Trends publishes no stable public API. Use the export the Trends interface offers
(Tier 2) or collect the same public series (Tier 3), and fall back to manual import
(Tier 4) if collection becomes unreliable. Record which tier produced each record.

### Required safeguards

- Retain required attribution.
- Preserve the query configuration, geography, window, and retrieval date.
- Show interest as a relative signal, never as search volume, sentiment, or purchase intent.
- Do not identify or profile individual searchers.
- Do not treat a rising term as evidence that a product will sell. It is a lead.

## 4. Public-discussion data

### Purpose

Identify group-level pain points, unmet needs, desired improvements, objections, and the
words customers actually use — the substance of the report's Emerging customer opportunity
and Customer insight sections.

### Access

This is the same source and the same adapter as the Industry Sentiment MVP — build it once,
use it for both. Prefer a platform that publishes a free API with a registered application
(Tier 1); use public pages (Tier 3) only where no such API exists.

- Aggregate by topic and period. Do not identify, score, or profile individual users.
- Store only the minimum text needed for evidence and attribution.
- Treat public discussion as a self-selected sample, never as a representative survey.

### Required safeguards

- Register an application where the platform offers one, and stay inside its rate limits.
- Do not use collected content to train models.
- Preserve source, thread link, and date for material report evidence.
- Discard author identity at collection time; store the topic and period, not the person.
- A finding resting only on public discussion cannot exceed Medium confidence
  (shared rubric, section 6).

## 5. Marketplace signals

### Purpose

Populate the report's Current sales reality view and the competition and saturation
assessment with evidence of what is listed, ranked, reviewed, and competed over.

### Access, in tier order

Evaluate candidates in this order and take the first that works for a given category.
Confirm each one's current terms and free-tier limits at integration time; programme
rules change, and this list records intent, not a verified snapshot.

| Tier | Candidate | Gives | Notes |
| --- | --- | --- | --- |
| 1 | Marketplaces publishing a free developer API (for example eBay, Etsy, Best Buy) | Listings, categories, prices, listing counts, some ranking | Free developer registration; usually per-day call limits. Start here. |
| 1 | Amazon Product Advertising API | Catalog and ranking data | Requires an Associates account in good standing, which requires qualifying sales first. Treat as unavailable until that exists. |
| 3 | Public marketplace pages with no API — best-seller lists, category listings, public review counts | Rank position, listing density, review volume, price bands | Follow the Tier 3 operating rules. Large marketplaces block aggressive collection; keep rates low and drop to Tier 4 on blocking rather than working around it. |
| 4 | Manual import | Same fields, entered or uploaded by the owner | Fallback whenever automated collection is blocked or not worth maintaining. |

### What marketplace signals mean

Every value from this source type is stored as a **proxy** and rendered with its
limitation. Specifically:

- A best-seller rank orders items within a category at a moment. It is not a sales count,
  and ranks are not comparable across categories.
- A review count reflects accumulated purchases over an unknown period, filtered by who
  chooses to review. It is a lagging, biased proxy for volume.
- Listing count and price spread indicate competitive density, not demand.

### Required safeguards

- Store rank, count, and price values with the exact retrieval timestamp — these change
  continuously and a value without a timestamp is worthless.
- Never present rank, review count, or listing count as sales, revenue, or market share.
- Store review evidence as short excerpts with a link back, never as a full-text corpus.
- Collect no seller or reviewer identity.
- Record the marketplace, category path, and geography with every value.

### Effect while a category has no working marketplace source

Per the shared gating rule, if no tier yields marketplace data for the category being
researched, these report elements render as **Insufficient evidence**, naming what is
missing:

- Current sales reality (report template section 4).
- Competition and saturation states **Established demand** and **Crowded**
  (report template section 7). **Emerging** and **Uncertain** remain assignable from
  search and discussion signals alone.

## 6. Data flow

1. User selects a US category or enters a product idea, and a time window.
2. The system retrieves FRED context series and Google Trends interest signals.
3. The system retrieves public-discussion signals and marketplace signals at the best
   available tier for the category.
4. The system stores normalized evidence conforming to the shared evidence schema.
5. The analysis layer separates observations from interpretation and assigns confidence
   by the shared rubric.
6. The report links material claims to their sources and marks gated sections.

## 7. Explicit exclusions for the first MVP

- Sales volume, revenue, or market-size figures presented as measured fact.
- Any content behind a login, paywall, or access control.
- Individual-level customer, seller, or reviewer profiles.
- Stored full-text copies of reviews or discussion threads.
- User-created questionnaires and respondent recruitment.
- Supplier, wholesale, and inventory-cost data.
- Working around a source that has started blocking collection.

## 8. Next decisions

- Select the first three to five US categories for demonstration reports, using the
  criteria in section 9.
- Select the first set of FRED series for consumption and retail context.
- Define the initial Google Trends term list and comparison rules per category.
- Register free developer accounts for the Tier 1 marketplace candidates and record
  their actual rate limits.
- Decide where API credentials are stored for local development.

## 9. Category selection criteria

A category qualifies for the first demonstration reports when it has:

- Enough US search volume for Google Trends to return a stable, non-noisy series.
- Visible public discussion in which people describe problems, not only products.
- A plausible path to differentiation, so a report conclusion could change a decision.
- No regulated-product constraints that would change the compliance analysis
  (health claims, supplements, medical devices, firearms, alcohol).

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial data source plan for the Product Opportunity MVP. Resolved the sales-data question: the first version reports demand signals and marketplace proxies, not measured sales. |
| v0.2 | 2026-08-23 | Adopted the free-first, tiered access policy: marketplace signals are collected through free APIs where available and public pages where not, instead of being deferred. |
