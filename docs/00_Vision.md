# Global Consumer Intelligence Platform — Vision

- Version: v0.3
- Status: Draft
- Updated: 2026-08-23

## 1. Product vision

Build an AI-first market and consumer intelligence platform that turns changing market, company, industry, and consumer signals into practical decisions for investment analysis and product positioning.

The platform has two connected uses:

- **Investment analysis** — understand companies, industries, brands, consumer demand, and market change to support investment research.
- **Product positioning** — understand target customers' preferences, needs, pain points, and purchase motivations to support product and marketing decisions.

## 2. Problem

Market and consumer signals are scattered across social media, reviews, surveys, search trends, company information, competitor content, news, and internal business data. Collecting and interpreting them is slow, expensive, and difficult to sustain over time.

The platform should help teams:

- Discover what target consumers care about and where their pain points are.
- Identify emerging trends, purchase motivations, and changes in sentiment.
- Compare a brand with competitors across markets.
- Turn complex evidence into clear, actionable conclusions.
- Give marketing, product, and research teams a shared view of consumer reality.
- Connect consumer and market changes with companies and industries relevant to investment research.

## 3. Primary users

### Initial primary user

The first MVP is a personal research workspace for the project owner. It supports two personal decision contexts:

- Investment research.
- Product development and product-selling research.

The initial version is not designed as a multi-user team product or a public reporting service.

### Future users

| User | Primary need |
| --- | --- |
| Brand and marketing leaders | Set positioning, communication strategy, and market priorities. |
| Marketing teams | Identify audience, content, and campaign opportunities. |
| Product teams | Understand customer feedback, unmet needs, and competitive gaps. |
| Consumer insight and research teams | Run research, monitor trends, and prepare reports more efficiently. |
| Executives | Make faster market decisions grounded in consumer evidence. |
| Individual investors and investment researchers | Monitor companies, industries, demand signals, and investment hypotheses. |

## 4. Product value

The product is not merely a data dashboard. It is a consumer intelligence assistant that:

1. **Aggregates** — connects public and authorized market, company, and consumer data sources.
2. **Understands** — uses AI to identify themes, sentiment, motivations, pain points, and changes.
3. **Assesses** — highlights trends, opportunities, risks, and competitive differences.
4. **Enables action** — produces recommendations and reports for marketing, product, and strategy decisions.

## 5. Initial scope

The first release is a personal research workspace delivering two report products on one
shared core. Both are US-only and English-only.

| # | MVP | Question it answers | Status |
| --- | --- | --- | --- |
| 1 | **Industry Sentiment** — US technology and healthcare | How is attention and group sentiment around this industry changing, and what does the evidence not prove? | Specified; built first |
| 2 | **Product Opportunity** — US categories and product ideas | What is selling now, what unmet need is emerging, and how crowded is it? | Specified; built second on the same core |

The shared core, defined in `docs/01_Product/00_Shared_Research_Foundation.md`:

- Create a research project with a subject, market, period, and research question.
- Collect signals from free sources, using the tiered access policy.
- Store every signal against a common evidence schema with source, period, rights, and limitation.
- Separate observation, derived metric, and interpretation, and never blur them.
- Assign confidence by a common rubric, including *insufficient evidence* as a valid answer.
- Produce a source-backed report on a weekly cadence.

Brand-versus-competitor comparison, multi-user sharing, and non-US markets are later
expansions, not first-release scope.

## 6. Out of scope for the first release

- Full advertising buying, campaign execution, or budget management.
- Replacing CRM or customer-operations systems.
- Replacing all professional quantitative market research.
- Automatic publishing of marketing content or advertising.
- Collection or use of private data without authorization.

## 7. Success criteria

Measured against the first MVP, for a single user — the project owner. These are the
targets the first release is judged against; they are deliberately checkable rather than
aspirational.

| # | Criterion | Target |
| --- | --- | --- |
| 1 | Owner time to produce one weekly report | Under 15 minutes, including any manual import step |
| 2 | Material claims carrying a source, period, and confidence level | 100% — a claim without them is a defect |
| 3 | Interpretations traceable to the records they rest on | 100% — enforced by the evidence schema |
| 4 | Sections with no connected source rendering as *insufficient evidence* | 100% — never omitted, never filled from an unrelated signal |
| 5 | Monitoring items produced per report | At least three, each tied to a specific signal or evidence gap |
| 6 | Weekly reports produced in a row without the owner abandoning the habit | Eight — the real test of whether the output is worth reading |

Criterion 6 is the one that decides whether the product is worth extending. The others can
all be satisfied by a report nobody wants to read.

## 8. Open questions

Still open:

- Whether the workspace ever becomes a product for other users, and what would have to be
  true first.
- Which market comes after the United States, and what that costs in source re-review.
- Whether company-level research is added to the Industry Sentiment MVP after the
  industry-level workflow is validated.

Resolved since v0.2:

| Question | Answer | Recorded in |
| --- | --- | --- |
| Which industries, countries, languages? | US technology and healthcare; United States; English | `02_Research/01_Industry_Sentiment_MVP_Scope.md` |
| Which data sources first? | FRED, Google Trends, public discussion; marketplace for MVP2 | `03_Data/01_...` and `03_Data/02_...` |
| Who is the initial user? | The project owner. Not a brand, agency, or research team | Section 3 |
| What report format? | The two templates | `05_Design/01_...` and `05_Design/02_...` |
| What data-rights and privacy boundaries? | The tiered source policy and its three universal limits | `01_Product/00_Shared_Research_Foundation.md` section 3.1 |
| Which investment workflow first? | Industry-level attention and sentiment research, not security selection | `01_Product/01_Industry_Sentiment_MVP.md` |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial vision draft. |
| v0.2 | 2026-08-23 | Added investment-analysis use case and shared market-intelligence scope. |
| v0.3 | 2026-08-23 | Recorded the personal-workspace primary user in the change log, where v0.2 had changed section 3 without noting it. Replaced the initial scope with the two specified MVPs, made the success criteria measurable, and moved the resolved open questions to a resolution table. |
