# Sentiment MVP Data Source Plan

- Version: v0.1
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Decision

The first Stock and Industry Sentiment MVP will use four complementary data-source types:

1. **FRED** — US macroeconomic data and aggregate consumer-sentiment context.
2. **Google Trends** — anonymized, aggregated search-interest signals.
3. **First-party survey** — direct responses about attitude, motivations, concerns, and stated intent.
4. **Approved public-discussion data** — public group discussion used only for aggregated themes and sentiment.

This keeps the first release focused on group-level context, attention, stated attitudes, and discussion themes rather than financial statements, real-time trading data, or individual profiling.

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

### Required safeguards

- Use data only through permitted methods and retain required attribution.
- Preserve the exported or retrieved result, query configuration, and retrieval date.
- Do not identify or profile individual searchers.
- Do not equate search interest with positive sentiment or a decision to buy.

## 4. First-party survey

### Purpose

Use a voluntary questionnaire to measure the target group’s stated attitude, motivations, concerns, confidence, and intended action directly.

### Initial question areas

- Familiarity with the company, industry, or topic.
- Positive and negative attitudes.
- Main reasons for interest, confidence, concern, or avoidance.
- Stated intention to buy, hold, avoid, or learn more, where applicable.
- Optional broad demographic or experience segments only when necessary to interpret group differences.

### Required safeguards

- Obtain consent and explain the purpose of collection.
- Do not collect sensitive personal data unless there is a clearly justified and compliant need.
- Keep identity separate from analysis responses where possible.
- Report group-level results only; do not generate psychological profiles of individuals.
- Identify sample size, recruitment method, field dates, and limitations in every report.

## 5. Approved public-discussion data

### Purpose

Use an approved platform or licensed provider to identify group-level discussion themes, expressed sentiment, motivations, and concerns in natural language.

### Initial approach

- The initial candidate is a platform with an authorized data-access route, subject to a separate terms, privacy, and AI-use review.
- Store only the minimum data needed for evidence, attribution, and time-based analysis.
- Aggregate results by topic and time period; do not identify, score, or profile individual users.
- Treat public discussion as a biased sample of people who choose to post, not as a representative survey.

### Required safeguards

- Confirm the platform’s current terms, approved use case, attribution, retention, and deletion requirements before integration.
- Do not use collected discussion content to train models unless the relevant rights and permissions explicitly allow it.
- Preserve the source and date for material report evidence.

## 6. Data flow

1. User selects a US company, industry, or topic and writes a research question.
2. The system retrieves selected FRED series and Google Trends interest signals.
3. The system collects consented survey responses and approved public-discussion signals.
4. The system stores normalized evidence with source and time metadata.
5. The analysis layer creates a research brief that separates source facts from interpretation.
6. The report links material claims back to the original source.

## 7. Explicit exclusions for the first MVP

- Financial statements and company-filings analysis.
- Real-time or delayed stock prices.
- Trading signals, price targets, or trade execution.
- Individual psychological profiles or mental-health inferences.
- Automated collection from sources not explicitly approved.
- Personalized investment advice.

## 8. Next technical decisions

- Select the first set of FRED series for macro context and consumer sentiment.
- Define the initial Google Trends topic list and comparison rules.
- Design the first survey and recruitment plan.
- Choose the first approved public-discussion source after a compliance review.
- Define the normalized evidence schema across all four source types.
- Decide where API credentials will be stored for local development and production.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Approved SEC EDGAR and FRED as the first Stock MVP sources. |
| v0.2 | 2026-08-23 | Replaced SEC EDGAR with Google Trends; refocused the MVP on macro context and group-level attention signals. |
| v0.3 | 2026-08-23 | Added first-party surveys and approved public-discussion data as core sources. |
