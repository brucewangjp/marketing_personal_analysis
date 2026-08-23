# Product Opportunity MVP Data Source Plan

- Version: v0.3
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Decision

The first US Product Opportunity MVP uses **free sources only**, accessed in the tier
order defined in `docs/01_Product/00_Shared_Research_Foundation.md` section 3.1
(official API first, then official export, then collection from public web pages, then
manual import). A paid licence is considered only after a free route has been shown not
to answer the research question.

Four source types:

1. **Official US statistics** — measured category sales and consumer spending from the
   Census Bureau, BEA, BLS, and FRED. Tier 1, free APIs.
2. **Google Trends** — anonymized, aggregated search interest for category and product
   terms. Tier 2 or 3; no stable official public API.
3. **Marketplace signals** — what is listed, ranked, and reviewed at the product level.
   Tier 1 where a marketplace publishes a free API, Tier 3 where it does not.
4. **Public-discussion data** — group-level pain points, unmet needs, and customer
   language. Tier 1 where the platform publishes a free API.

### What the first version measures, and at which level

This answers the open question "Does the first version need actual sales data, or is it a
demand-signal discovery tool?" from `docs/01_Product/02_US_Product_Opportunity_MVP.md`.

The answer differs by level, and the report must never blur the two:

| Level | Measured sales available? | Source | What the report may state |
| --- | --- | --- | --- |
| **Category** — a retail line, product type, or spending category | **Yes.** Dollar sales and consumer spending, measured by federal statistical agencies | Section 2 | Actual sales levels, direction, and share, with the survey's period and definition |
| **Product** — a specific item or listing | **No.** No free or paid source publishes unit sales for an individual product | Section 5 | Rank, review volume, listing density, price band — all labeled as **proxies** |

Category-level statistics lag: monthly retail sales lag weeks, annual merchandise-line
detail lags about a year. They establish whether a category is real and growing. They
never tell you what is selling this week. Marketplace proxies are timely but measure
nothing directly. The report's value comes from carrying both with their limits attached,
not from picking one.

No source at either level supports a revenue or market-size estimate for a specific
product. The report does not produce one.

## 2. Official US statistics

### Purpose

Establish whether a category has real, measured demand, how it is trending, and who spends
in it — the evidence base the marketplace proxies in section 5 cannot provide.

### Sources, in priority order

| Source | Gives | Frequency and lag | Access |
| --- | --- | --- | --- |
| **Census Monthly Retail Trade Survey (MARTS/MRTS)** | Dollar sales by NAICS retail line | Monthly, ~2–6 week lag | Free Census API; the same series are also carried in FRED |
| **Census Quarterly E-commerce Report** | E-commerce sales and share of retail | Quarterly | Free Census API / FRED |
| **Census Annual Retail Trade Survey (ARTS)** | Annual sales including, for selected industries, **sales by merchandise line** — the closest official data to product-category sales | Annual, ~1 year lag | Free Census API |
| **BEA NIPA underlying detail** (for example table `U20305`) | Personal consumption expenditure by detailed product type | Monthly/quarterly/annual | Free BEA API key |
| **BLS Consumer Expenditure Survey** | Spending by category **cross-tabulated by income, age, region, household size** | Annual | Free published tables and public-use microdata |
| **FRED** | Convenient access to many of the above, plus interest-rate, inflation, employment, and consumer-sentiment context | Varies | Free API key |

BLS Consumer Expenditure Survey deserves specific attention: it is the only free source in
this plan that says *who* spends on a category rather than only *how much* is spent. It is
the evidence base for the report's Customer insight section, and it is measured survey
data rather than inference from discussion.

### Required safeguards

- Use registered API keys and keep them outside the repository.
- Store the agency, series or table identifier, observation period, release date, and
  retrieval date on every value.
- Record the **definition** the agency uses. A NAICS retail line is a type of store, not a
  type of product; a merchandise line is closer to a product category. Reporting one as
  the other is a defect.
- Show the lag. A category statistic is never current to the report date, and the report
  states its latest observation date rather than implying otherwise.
- Do not present a category-level statistic as evidence about any specific product.

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

### Product-level sold data: what exists and what does not

Checked, and recorded here so the question is not reopened every few months:

- **eBay Marketplace Insights API** returns genuinely sold items for the last 90 days. It
  is a Limited Release API and is closed to new applicants. Treat as unavailable.
- **eBay Terapeak / Product Research** is free with a seller account and covers roughly
  three years of sold history. It is the owner's own account on a tool they are entitled to
  use, so it is a legitimate **Tier 4 manual import**, not a collection target.
- **Amazon Product Advertising API** requires an Associates account in good standing,
  which requires qualifying sales first. Unavailable until that exists.
- **Amazon Product Opportunity Explorer** and **Brand Analytics** are free but require a
  Seller Central or Brand Registry account. Same treatment as Terapeak: Tier 4 if the owner
  has an account, otherwise unavailable.
- **Paid estimators** (Keepa, Jungle Scout, Helium 10 and similar) publish modelled
  estimates, not measured sales, and their terms generally restrict re-displaying that data
  inside another product.

The conclusion stands: no free route yields measured unit sales for an individual product.
Category-level sales come from section 2 instead.

### Effect when a category has no working marketplace source

Per the shared gating rule, if no tier yields marketplace data, the **product-level** part
of the report renders as insufficient evidence, naming what is missing. The
**category-level** part is unaffected — it comes from section 2 and is always available.

- Current sales reality (report template section 4): category statistics still render;
  the product-level table renders as insufficient evidence.
- Competition and saturation (report template section 7): **Established demand** can still
  be assigned from category statistics. **Crowded** needs marketplace listing density and
  is otherwise unassignable.

## 6. Data flow

1. User selects a US category or enters a product idea, and a time window.
2. The system retrieves official category statistics and Google Trends interest signals.
3. The system retrieves public-discussion signals and marketplace signals at the best
   available tier for the category.
4. The system stores normalized evidence conforming to the shared evidence schema.
5. The analysis layer separates observations from interpretation and assigns confidence
   by the shared rubric.
6. The report links material claims to their sources and marks gated sections.

## 7. Explicit exclusions for the first MVP

- Product-level sales volume, revenue, or market-size figures presented as measured fact.
  Category-level figures from official statistics are permitted, with their period and
  definition attached.
- Any content behind a login, paywall, or access control.
- Individual-level customer, seller, or reviewer profiles.
- Stored full-text copies of reviews or discussion threads.
- User-created questionnaires and respondent recruitment.
- Supplier, wholesale, and inventory-cost data.
- Working around a source that has started blocking collection.

## 8. Next decisions

- Select the first three to five US categories for demonstration reports, using the
  criteria in section 9.
- Map each demonstration category to its NAICS retail line, ARTS merchandise line, BEA
  product type, and BLS expenditure category. This mapping is the spine of the report and
  should be built before any collector.
- Register free API keys for Census, BEA, and FRED.
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
| v0.3 | 2026-08-23 | Corrected a factual error in v0.1–v0.2, which stated that no free measured sales data exists. Free official category-level sales and spending data does exist — Census MARTS/MRTS, ARTS merchandise lines, the quarterly e-commerce report, BEA product-detail PCE, and the BLS Consumer Expenditure Survey — and is now the first source type. The no-measured-sales limit applies at the product level only. |
