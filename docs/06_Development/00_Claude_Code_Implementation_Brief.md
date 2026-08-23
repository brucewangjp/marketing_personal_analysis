# Claude Code Implementation Brief

- Version: v0.1
- Status: Ready for implementation planning
- Updated: 2026-08-23

## 1. Objective

Build the first version of a personal industry-sentiment research workspace. It is for one user: the project owner. The workspace supports personal investment research and product-development or product-selling decisions.

The output is a source-backed weekly report for either:

- US technology industry.
- US healthcare industry.

Each report analyzes the most recent one month or most recent three months of available data.

## 2. Read these documents first

Before designing or writing the application, read:

1. `docs/00_Vision.md`
2. `docs/01_Product/01_Stock_Analysis_MVP.md`
3. `docs/02_Research/01_Stock_MVP_Industry_Scope.md`
4. `docs/03_Data/01_Stock_MVP_Data_Source_Plan.md`
5. `docs/04_Architecture/00_System_Architecture.md`
6. `docs/05_Design/01_Industry_Sentiment_Report_Template.md`

The report template is the output contract. Design internal data structures, interfaces, and workflows backward from it.

## 3. Product boundaries

### Build now

- A personal web workspace.
- Industry selection: US technology or US healthcare.
- Time-window selection: most recent one month or most recent three months.
- Manual report generation.
- Weekly report scheduling capability or a clearly designed scheduling placeholder.
- Source-backed report view.
- Evidence and limitations displayed next to important conclusions.
- FRED integration for macroeconomic and aggregate-sentiment context.
- A Google Trends adapter that uses only a permitted data-access method.
- A pluggable interface for future region-specific public-discussion sources.

### Do not build now

- User accounts, teams, billing, or a public-facing product.
- Trading, price targets, buy/sell recommendations, or order execution.
- Individual-level psychological profiling or mental-health inference.
- Scraping, crawling, or automated collection from a discussion platform without explicit permission.
- Integration of Japan, China, or Europe discussion sources before the applicable source rights are confirmed.

## 4. Required report content

The report must contain every section defined in `docs/05_Design/01_Industry_Sentiment_Report_Template.md`:

1. Header: industry, question, chosen period, geography, generated date, included sources, limitations.
2. Executive summary.
3. Attention trend.
4. Macro and aggregate-sentiment context.
5. Group attitude: positive, cautious, negative, mixed, or insufficient evidence.
6. Motivations and concerns.
7. Change over time.
8. Evidence and confidence.
9. Monitoring list.

The interface must distinguish observed evidence, AI interpretation, and uncertainty.

## 5. Data-source rules

### FRED

- Use FRED for macroeconomic indicators and permitted aggregate sentiment measures.
- Store the source, series identifier, observation period, retrieval date, and attribution requirements.
- Keep API credentials out of version control.

### Google Trends

- Treat Google Trends as relative attention, not absolute demand, sentiment, or purchase intent.
- Preserve query terms, geography, time window, retrieval date, and attribution requirements.
- Do not assume an unofficial automated method is allowed. If a permitted programmatic source is not available, support an explicit manual import path and document the limitation.

### Public discussion sources

- Build a source-adapter interface but do not connect a live source until its terms, data-access method, retention, attribution, and AI-use rules are approved.
- The interface must support future regional sources selected by: region, country, language, research object, audience, and source purpose.
- Aggregate at group level; do not identify, score, or profile individual people.

## 6. Recommended implementation sequence

### Phase 1 — Report-first application shell

- Choose a simple, maintainable web stack and document the choice in the repository.
- Build the industry and time-window selector.
- Build the report page from the report template using clearly labeled sample data.
- Build evidence, source, confidence, and limitation components.

### Phase 2 — Evidence and data pipeline

- Define the smallest internal model required to create the report.
- Implement evidence storage with source, date, scope, type, and limitation metadata.
- Implement FRED collection and normalization.
- Implement the Google Trends adapter or manual-import workflow, according to permitted access.

### Phase 3 — Analysis and report generation

- Produce attention-trend and macro-context sections from collected data.
- Generate conclusions only when evidence supports them.
- Return “insufficient evidence” when a finding cannot be supported.
- Generate the monitoring list from recent changes and data gaps.

### Phase 4 — Scheduling and future-source readiness

- Add a weekly-generation mechanism suitable for the chosen runtime.
- Implement the public-discussion adapter contract with a mock provider, not an unauthorized live connector.
- Document how a compliant US, Japan, China, or European source can be added later.

## 7. Definition of done for the first working version

The first working version is complete when:

- The user can select US technology or US healthcare.
- The user can select a one-month or three-month lookback period.
- The user can generate a readable report page.
- The report contains all required sections, including evidence and limitations.
- FRED data can populate the macro-context section.
- Google Trends is represented through a compliant integration or a documented manual-import workflow.
- Missing evidence is visibly labeled rather than fabricated.
- The application does not produce investment advice or individual psychological profiles.
- Basic tests cover report generation, evidence display, and empty or insufficient-data states.

## 8. Required handoff from Claude Code

When implementation planning is complete, provide:

- A brief technical design and chosen stack.
- A list of files to create or modify.
- A phased implementation plan.
- Assumptions and unresolved source-access questions.
- Instructions for running the project locally.

When the first working version is complete, provide:

- A summary of completed features.
- Test results.
- Known limitations.
- The next recommended task.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial Claude Code implementation brief for the industry-sentiment MVP. |
