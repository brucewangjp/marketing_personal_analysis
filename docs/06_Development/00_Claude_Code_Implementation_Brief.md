# Claude Code Implementation Brief

- Version: v0.4
- Status: Ready for implementation planning
- Updated: 2026-08-23

## 1. Objective

Build the first version of a personal industry-sentiment research workspace. It is for one user: the project owner. The workspace supports personal investment research and product-development or product-selling decisions.

The output is a source-backed weekly report for either:

- US technology industry.
- US healthcare industry.

Each report analyzes the most recent one month or most recent three months of available data.

## 1.1 Build order

Two MVPs share one core and one architecture. This is a confirmed decision (D10 in
`docs/00_Foundation/00_Decision_Log.md`), not a suggestion open to revisiting during
implementation. Build them in this order:

| Order | MVP | Reuses |
| --- | --- | --- |
| 1 | Industry Sentiment — US technology and healthcare | — |
| 2 | Product Opportunity — US categories and product ideas | Collection, evidence store, analysis, and report shell from MVP1, unchanged |

Do not build MVP2 features during MVP1. Do build MVP1's collection, evidence, and report
layers generically enough that MVP2 adds a collector and a template, not a second system.

## 2. Read these documents first

Before designing or writing the application, read:

1. `docs/00_Vision.md`
2. `docs/01_Product/00_Shared_Research_Foundation.md` — **the shared contract; read this second and treat it as binding**
3. `docs/01_Product/01_Industry_Sentiment_MVP.md`
4. `docs/02_Research/01_Industry_Sentiment_MVP_Scope.md`
5. `docs/03_Data/01_Industry_Sentiment_MVP_Data_Sources.md`
6. `docs/04_Architecture/00_System_Architecture.md`
7. `docs/05_Design/01_Industry_Sentiment_Report_Template.md`

For MVP2, additionally:

8. `docs/01_Product/02_US_Product_Opportunity_MVP.md`
9. `docs/03_Data/02_Product_Opportunity_MVP_Data_Sources.md`
10. `docs/05_Design/02_US_Product_Opportunity_Report_Template.md`

The shared foundation fixes the evidence schema, confidence rubric, report header, and
source access policy — do not redesign them. The report template is the output contract
for everything else: design internal data structures, interfaces, and workflows backward
from it.

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
- A Google Trends adapter following the tiered access policy, with a manual-import fallback.
- A collector adapter contract that public-discussion and marketplace sources plug into
  later without changing the analysis or report layers.

### Do not build now

- User accounts, teams, billing, or a public-facing product.
- Trading, price targets, buy/sell recommendations, or order execution.
- Individual-level psychological profiling or mental-health inference.
- Any collection of content behind a login, paywall, or access control.
- Storage of personal identity data or full-text copies of third-party content.
- Non-US markets and non-English sources.
- MVP2's marketplace collector and opportunity report.

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
- Trends publishes no stable public API. Use the interface's export (Tier 2) or collect the
  public series (Tier 3), and always ship the Tier 4 manual-import path as well — series
  availability is not guaranteed, and a run must be able to proceed without it.

### Public discussion sources

- Prefer a platform that publishes a free API with a registered application (Tier 1);
  collect public threads (Tier 3) only where no such API exists.
- Aggregate at group level. Discard author identity at collection time; do not identify,
  score, or profile individual people.
- Store short excerpts with a link back, never full threads.
- The interface must support future regional sources selected by: region, country,
  language, research object, audience, and source purpose.

### Collector rules that apply to every source

- Declare the access tier and record it on every stored record.
- Respect `robots.txt` and any stated rate limit; identify the collector honestly.
- Re-fetch on the report cadence, not continuously.
- If a source begins blocking, fall back to manual import. Do not build evasion, rotate
  identities, or work around a block.
- Keep all credentials out of version control.

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
- Implement the public-discussion collector against its chosen source, which ungates the
  attitude and motivation sections of both reports.
- Document how a US, Japan, China, or European source can be added later.

### Phase 5 — Second MVP

- Add the official-statistics collector for Census, BEA, and BLS, which supply MVP2's
  measured category sales and spending-by-demographic evidence. This extends the FRED
  collector built in Phase 2 rather than replacing it.
- Add the marketplace collector, following the tier order in the MVP2 source plan.
- Add the product opportunity report template.
- Reuse collection, evidence storage, analysis, and the report shell without forking them.

## 7. Definition of done for the first working version

The first working version is complete when:

- The user can select US technology or US healthcare.
- The user can select a one-month or three-month lookback period.
- The user can generate a readable report page.
- The report contains all required sections, including evidence and limitations.
- FRED data can populate the macro-context section.
- Google Trends is represented through an automated adapter or the manual-import workflow.
- Report sections whose source is not connected render as insufficient evidence naming the
  missing source, rather than being omitted or filled from an unrelated signal.
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
| v0.2 | 2026-08-23 | Added the two-MVP build order and MVP2's documents; adopted the tiered access policy in place of the blanket approved-source rule; added universal collector rules and Phase 5. |
| v0.3 | 2026-08-23 | Added the official-statistics collector to Phase 5, following confirmation that free measured category sales data is available. |
| v0.4 | 2026-08-23 | Recorded the shared-core build order as a confirmed decision and linked it to the decision log. |
