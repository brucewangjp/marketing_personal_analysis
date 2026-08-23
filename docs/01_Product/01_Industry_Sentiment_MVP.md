# Industry Sentiment MVP

- Version: v0.4
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Goal

Help a research user understand group-level attention and sentiment around a US industry by combining macroeconomic context with public, aggregated interest signals.

The MVP supports research; it does not provide personalized investment advice, diagnose individuals, or execute trades.

## 2. Primary user

The initial user is the project owner, using the report for personal investment research and product-development or product-selling decisions. The user wants to answer questions such as:

- Is attention toward this industry growing or declining?
- Is the broader consumer environment optimistic, cautious, or under pressure?
- What can and cannot be concluded from the available aggregate signals?
- What should be monitored next?

The first version is a personal workspace, not a multi-user product or public reporting service.

## 2.1 Initial research scope

The first release focuses on two US industries:

- Technology.
- Healthcare.

The product will be designed for industry-level research within these sectors before expanding to other industries. Company-level research is a later expansion.

## 3. MVP workflow

1. User selects technology or healthcare and writes a research question.
2. User selects the reporting window: the most recent one month or the most recent three months.
3. The system gathers approved macroeconomic and aggregate-attention signals relevant to the subject.
4. The system creates an evidence table and an AI-generated research brief.
5. The user saves the project and a watchlist of follow-up topics.

## 3.1 Reporting cadence and time windows

- Run the industry report once per week.
- Analyze only the most recent one month or the most recent three months for each run.
- Show the exact start date, end date, retrieval date, and source-update timing in the report.
- The one-month view is for recent changes; the three-month view is for a broader trend check.

## 4. Required output

- Topic and market overview.
- Macro context, including consumer sentiment where relevant.
- Search-interest trend and change over time.
- Published aggregate sentiment measures, including their sample and methodology limitations.
- Group-level public-discussion themes when that source is connected.
- A clear statement of what the signals suggest and what they do not prove.
- Unresolved questions and suggested items to monitor.
- Evidence links or citations for material claims.

## 4.1 First data sources

The first version uses three types of free, existing online signals:

- **FRED and published aggregate sentiment indicators** for US macroeconomic context and existing consumer or investor sentiment measures.
- **Google Trends** for anonymized, aggregated search-interest signals.
- **Public-discussion data** for group-level themes expressed in natural language.

Access tiers, safeguards, and exclusions for each source are defined in
`docs/03_Data/01_Industry_Sentiment_MVP_Data_Sources.md`.

The MVP does not require the user to distribute a questionnaire. Company filings, real-time prices, trade execution, and individual-level profiles are outside the first version.

## 5. First-release boundaries

- Support US research for a limited initial set of technology and healthcare topics.
- Use free sources, accessed by the tier order in the shared source selection policy.
- Do not make price targets, trade recommendations, or automated orders.
- Do not claim to know the psychological state of any individual.
- Show uncertainty when evidence is incomplete or conflicting.

## 5.1 Shared contract

This MVP inherits the terminology, evidence schema, confidence rubric, report header,
presentation rules, and source selection policy defined in
`docs/01_Product/00_Shared_Research_Foundation.md`. Where this document and the shared
foundation disagree, the shared foundation wins.

## 6. Acceptance criteria

- A user can create and save an industry research project.
- The research brief identifies its market and time period.
- Important claims have traceable evidence and source limitations.
- The report separates observed signals from AI interpretation.
- The user can record follow-up questions and monitoring topics.

## 7. Open decisions

- Which public-discussion platform and which published investor-sentiment indicator are integrated first?
- Should the initial interface begin with a topic page or a research-question page?

Resolved: the market is the United States; exchanges are out of scope because the MVP
researches industries, not securities.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial stock-analysis MVP draft. |
| v0.2 | 2026-08-23 | Refocused from company stock analysis to industry sentiment; set technology and healthcare as the initial scope; named the first data sources. |
| v0.3 | 2026-08-23 | Set the weekly cadence and the one-month and three-month reporting windows; confirmed the project owner as the primary user. |
| v0.4 | 2026-08-23 | Adopted the shared contract and the free-first source policy; renamed the document and its file to match the sentiment scope; corrected the version header, which had stayed at v0.1 through three revisions. |
