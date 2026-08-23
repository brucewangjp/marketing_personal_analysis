# Stock Analysis MVP

- Version: v0.1
- Status: Draft
- Updated: 2026-08-23

## 1. Goal

Help an individual investor or research user investigate a company or industry by bringing together public market, company, news, competitive, and consumer-demand signals into an evidence-backed research brief.

The MVP supports research; it does not provide personalized investment advice or execute trades.

## 2. Primary user

An investor researching a listed company, brand, or industry who wants to answer questions such as:

- What has changed recently for this company or industry?
- What consumer-demand or competitive signals could affect the business?
- What evidence supports a bullish, bearish, or uncertain view?
- What should I monitor next?

## 2.1 Initial research scope

The first release focuses on US-listed companies connected to:

- Artificial-intelligence infrastructure and software.
- Semiconductors and semiconductor equipment.

The product will be designed for company-level research within these sectors before expanding to other industries.

## 3. MVP workflow

1. User enters a company, ticker, or industry and a research question.
2. User selects a market and time period.
3. The system gathers approved public signals relevant to the subject.
4. The system creates an evidence table and an AI-generated research brief.
5. The user saves the project and a watchlist of follow-up topics.

## 4. Required output

- Company or industry overview.
- Recent developments and source-backed signals.
- Consumer-demand, competitive, and market observations where available.
- Bullish factors, risks, and unresolved questions.
- Suggested items to monitor.
- Evidence links or citations for material claims.

## 4.1 First data sources

The first version uses only:

- **SEC EDGAR** for US public-company filings and structured financial facts.
- **FRED** for US macroeconomic indicators.

Real-time prices, trade execution, and third-party news feeds are outside the first version.

## 5. First-release boundaries

- Support research for a limited initial set of markets and public companies.
- Use only explicitly approved, public, or licensed sources.
- Do not make price targets, trade recommendations, or automated orders.
- Show uncertainty when evidence is incomplete or conflicting.

## 6. Acceptance criteria

- A user can create and save a company or industry research project.
- The research brief identifies its market and time period.
- Important claims have traceable evidence.
- The report separates evidence from AI interpretation.
- The user can record follow-up questions and monitoring topics.

## 7. Open decisions

- Which country and exchanges should be supported first?
- Which approved data sources are available for company, news, and market signals?
- Should the initial interface begin with a company page or a research-question page?

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial stock-analysis MVP draft. |
