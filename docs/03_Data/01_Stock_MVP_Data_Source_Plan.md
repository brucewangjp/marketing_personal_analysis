# Stock MVP Data Source Plan

- Version: v0.1
- Status: Approved for MVP
- Updated: 2026-08-23

## 1. Decision

The first Stock Analysis MVP will use exactly two sources:

1. **SEC EDGAR** — US public-company filings and structured financial facts.
2. **FRED** — US macroeconomic and regional economic time series.

This keeps the first release focused on transparent, source-backed research rather than real-time trading data.

## 2. SEC EDGAR

### Purpose

Use SEC EDGAR to obtain company disclosures and financial facts relevant to a user-selected US public company.

### Initial use cases

- Identify the company and its latest relevant filings.
- Extract selected structured financial facts where available.
- Link findings to the relevant filing and reporting period.
- Surface management-stated risks and major business changes for user review.

### Required safeguards

- Identify the application with an appropriate User-Agent.
- Respect SEC fair-access and request-rate guidance.
- Cache results and avoid repeated downloads of the same filing.
- Preserve filing URL, form type, filing date, and reporting period with every extracted fact.
- Do not treat AI summaries of filings as a substitute for the original filing.

## 3. FRED

### Purpose

Use FRED to provide the macroeconomic context relevant to a company or industry research project.

### Initial indicators

- Interest rates.
- Inflation.
- Unemployment and employment.
- Retail sales and consumer-spending indicators where applicable.

### Required safeguards

- Store the FRED series identifier, observation date, release date when available, and retrieval date.
- Use a registered API key and keep it outside the repository.
- Label each indicator with its geography, frequency, and measurement period.
- Do not infer company-specific causation from macroeconomic correlation alone.

## 4. Data flow

1. User selects a US public company or industry and writes a research question.
2. The system retrieves relevant SEC filing information and selected FRED series.
3. The system stores normalized evidence with source and time metadata.
4. The analysis layer creates a research brief that separates source facts from interpretation.
5. The report links material claims back to the original source.

## 5. Explicit exclusions for the first MVP

- Real-time or delayed stock prices.
- Trading signals, price targets, or trade execution.
- Paid financial data feeds.
- Automated collection from sources not explicitly approved.
- Personalized investment advice.

## 6. Next technical decisions

- Select the first set of FRED series by industry.
- Define the normalized evidence schema.
- Define SEC request throttling, caching, and retry behavior.
- Decide where API credentials will be stored for local development and production.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Approved SEC EDGAR and FRED as the first Stock MVP sources. |
