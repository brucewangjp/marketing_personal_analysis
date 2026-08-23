# Industry Sentiment MVP Data Source Plan

- Version: v0.5
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Decision

The first Industry Sentiment MVP uses three types of free, existing online data, accessed
in the tier order defined in `docs/01_Product/00_Shared_Research_Foundation.md`
section 3.1 (official API first, then export, then public web pages, then manual import):

1. **FRED and published aggregate sentiment indicators** — US macroeconomic data and existing consumer or investor sentiment measures.
2. **Google Trends** — anonymized, aggregated search-interest signals.
3. **Public-discussion data** — public group discussion used only for aggregated themes and sentiment.

All records conform to the shared evidence schema, and all findings are labeled with the
shared confidence rubric, both defined in the shared research foundation.

This keeps the first release focused on group-level context, attention, published attitudes, and discussion themes rather than financial statements, real-time trading data, individual profiling, or newly conducted surveys.

## 2. FRED

### Purpose

Use FRED to provide macroeconomic and consumer-sentiment context for US research topics.

### Initial use cases

- Retrieve interest-rate, inflation, employment, and consumption indicators where relevant.
- Include the University of Michigan Consumer Sentiment series as aggregate consumer-sentiment context where licensing and attribution requirements are met.
- Link every value to its FRED series, observation period, and retrieval date.

### Required safeguards

- Use a registered API key and keep it outside the repository.
- Store the series identifier, observation date, release date when available, and retrieval date.
- Label each indicator with its geography, frequency, measurement period, and attribution requirements.
- Do not infer individual attitudes or company-specific causation from macroeconomic correlation alone.

## 3. Google Trends

### Purpose

Use Google Trends to understand changes in anonymized, aggregated public search interest for a company, industry, product, or related topic in the United States.

### Initial indicators

- Compare a selected topic with related topics over a defined period.
- Record geographic scope, period, search type, and query terms.
- Show interest as a relative signal, not absolute search volume, sentiment, or purchase intent.

### Access

Google Trends publishes no stable public API. Use the export the Trends interface offers
(Tier 2) or collect the same public series (Tier 3), falling back to manual import
(Tier 4) if collection becomes unreliable. Record which tier produced each record, and
show the limitation in the report when a series was imported by hand.

### Required safeguards

- Retain required attribution.
- Preserve the exported or retrieved result, query configuration, and retrieval date.
- Do not identify or profile individual searchers.
- Do not equate search interest with positive sentiment or a decision to buy.

## 4. Public-discussion data

### Purpose

Use an approved platform or licensed provider to identify group-level discussion themes, expressed sentiment, motivations, and concerns in natural language.

### Access

Prefer a platform that publishes a free API with a registered application (Tier 1). Where
no such API exists, collect public threads under the Tier 3 operating rules. This adapter
is shared with the Product Opportunity MVP — build it once.

- Store only the minimum data needed for evidence, attribution, and time-based analysis.
- Aggregate results by topic and time period; do not identify, score, or profile individual users.
- Treat public discussion as a biased sample of people who choose to post, not as a representative survey.

### Required safeguards

- Register an application where the platform offers one, and stay inside its rate limits.
- Do not use collected discussion content to train models.
- Preserve the source, link, and date for material report evidence.
- Discard author identity at collection time.
- A finding resting only on public discussion cannot exceed Medium confidence.

## 5. Data flow

1. User selects the US technology or healthcare industry and writes a research question.
2. The system retrieves selected FRED series and Google Trends interest signals.
3. The system retrieves approved, published sentiment indicators and approved public-discussion signals.
4. The system stores normalized evidence with source and time metadata.
5. The analysis layer creates a research brief that separates source facts from interpretation.
6. The report links material claims back to the original source.

## 6. Explicit exclusions for the first MVP

- Financial statements and company-filings analysis.
- User-created questionnaires and respondent recruitment.
- Real-time or delayed stock prices.
- Trading signals, price targets, or trade execution.
- Individual psychological profiles or mental-health inferences.
- Any content behind a login, paywall, or access control.
- Stored full-text copies of discussion threads.
- Working around a source that has started blocking collection.
- Personalized investment advice.

## 7. Next technical decisions

- Select the first set of FRED series for macro context and consumer sentiment.
- Define the initial Google Trends topic list and comparison rules.
- Select existing published investor-sentiment indicators whose use and attribution are permitted.
- Choose the first public-discussion platform and register an application for it.
- Decide where API credentials will be stored for local development and production.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Approved SEC EDGAR and FRED as the first Stock MVP sources. |
| v0.2 | 2026-08-23 | Replaced SEC EDGAR with Google Trends; refocused the MVP on macro context and group-level attention signals. |
| v0.3 | 2026-08-23 | Added first-party surveys and approved public-discussion data as core sources. |
| v0.4 | 2026-08-23 | Removed user-created surveys; refocused on existing online aggregate signals and approved public discussion. |
| v0.5 | 2026-08-23 | Adopted the free-first, tiered access policy; adopted the shared evidence schema and confidence rubric; corrected the version header, which had stayed at v0.1 through four revisions. |
