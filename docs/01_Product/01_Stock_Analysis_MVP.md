# Stock and Industry Sentiment MVP

- Version: v0.1
- Status: Draft
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
2. User selects a market and time period.
3. The system gathers approved macroeconomic and aggregate-attention signals relevant to the subject.
4. The system creates an evidence table and an AI-generated research brief.
5. The user saves the project and a watchlist of follow-up topics.

## 4. Required output

- Topic and market overview.
- Macro context, including consumer sentiment where relevant.
- Search-interest trend and change over time.
- Published aggregate sentiment measures, including their sample and methodology limitations.
- Group-level public-discussion themes when an approved source is available.
- A clear statement of what the signals suggest and what they do not prove.
- Unresolved questions and suggested items to monitor.
- Evidence links or citations for material claims.

## 4.1 First data sources

The first version uses three types of online, existing signals:

- **FRED and published aggregate sentiment indicators** for US macroeconomic context and existing consumer or investor sentiment measures.
- **Google Trends** for anonymized, aggregated search-interest signals.
- **Approved public-discussion data** for group-level themes expressed in natural language.

The MVP does not require the user to distribute a questionnaire. Company filings, real-time prices, trade execution, and individual-level profiles are outside the first version.

## 5. First-release boundaries

- Support US research for a limited initial set of technology and healthcare topics.
- Use only explicitly approved, public, or licensed sources.
- Do not make price targets, trade recommendations, or automated orders.
- Do not claim to know the psychological state of any individual.
- Show uncertainty when evidence is incomplete or conflicting.

## 6. Acceptance criteria

- A user can create and save an industry research project.
- The research brief identifies its market and time period.
- Important claims have traceable evidence and source limitations.
- The report separates observed signals from AI interpretation.
- The user can record follow-up questions and monitoring topics.

## 7. Open decisions

- Which country and exchanges should be supported first?
- Which approved public-discussion source and existing investor-sentiment indicator should be integrated first after a compliance review?
- Should the initial interface begin with a topic page or a research-question page?

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial stock-analysis MVP draft. |
