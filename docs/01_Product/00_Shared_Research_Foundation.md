# Shared Research Foundation

- Version: v0.3
- Status: Approved for MVP
- Updated: 2026-08-23

## Purpose

Both MVPs run the same core workflow: define a research question, gather approved
public signals, analyze them with AI, preserve supporting evidence, and produce a
source-backed report.

This document is the **single source of truth** for everything the two MVPs share.
When a downstream document needs a report header, a confidence label, an evidence
record, or the evidence/interpretation rule, it references this document instead of
restating it. If a definition here and a definition elsewhere disagree, this document wins.

Documents governed by this contract:

- `docs/01_Product/01_Industry_Sentiment_MVP.md`
- `docs/01_Product/02_US_Product_Opportunity_MVP.md`
- `docs/05_Design/01_Industry_Sentiment_Report_Template.md`
- `docs/05_Design/02_US_Product_Opportunity_Report_Template.md`

## 1. Shared workflow

1. Create a research project.
2. Define the subject, market, time period, and research question.
3. Collect signals from the sources listed in the applicable `03_Data` source plan.
4. Normalize and store source references and collection dates.
5. Use AI to extract themes, changes, risks, and opportunities.
6. Generate a report in which material conclusions link to evidence.

## 2. Shared product requirements

- Project workspace with saved research questions.
- Source inventory and collection status.
- Evidence records conforming to the schema in section 5.
- AI research summary that distinguishes facts, signals, and hypotheses.
- Report export or shareable view.
- Clear data-rights, copyright, and privacy boundaries for every source.

## 3. Non-negotiable principles

- Do not present inference as verified fact.
- Make important conclusions traceable to evidence.
- Record the period and market covered by each result.
- Never use private or restricted data without authorization.
- Record how every source was accessed, so a rights question can be answered later.

## 3.1 Source selection policy

The project prefers sources that are **free to use** and reaches for a paid licence only
when a free route cannot answer the research question. Within the free set, access
methods are tried in this order, and the method actually used is stored on every record
in the `access_method` field.

| Tier | Access method | Use when | Record as |
| --- | --- | --- | --- |
| 1 | Official API, free tier | The source publishes one. Always preferred. | `api` |
| 2 | Official export or download the source offers | No API, but the source publishes files or a permitted export. | `export` |
| 3 | Collection from public web pages | No API and no export, and the page is publicly readable without an account. | `web_collection` |
| 4 | Manual import by the owner | Automated collection is blocked, unreliable, or not worth the effort. | `manual` |

Tier 3 is permitted, and is expected for sources that publish no API. It carries operating
rules, because ignoring them produces blocked collectors and evidence that cannot be
defended:

- Identify the collector honestly and keep request rates low enough to be unnoticeable.
- Respect `robots.txt` and any stated rate limit.
- Store the minimum needed as evidence: a metric, a short excerpt, and a link back —
  not a copy of the page or a corpus of full review text.
- Re-fetch on the report cadence, not continuously.
- If a source starts blocking, drop it to Tier 4 rather than working around the block.

Three limits hold at every tier, whatever the price or the access method:

1. **No content behind a login, paywall, or access control.** Only what a signed-out
   visitor can read.
2. **No personal data.** No usernames, profiles, or anything that identifies or scores an
   individual. Aggregate to the group level at collection time.
3. **No redistribution of someone else's content as a product asset.** Excerpts as
   evidence with attribution, not stored copies of full text.

A source that cannot be used within these limits is recorded as unavailable, and the
sections depending on it are gated under section 9.

## 4. Terminology

These terms are contractual. Use them with exactly these meanings in every document,
interface label, and stored record.

| Term | Meaning |
| --- | --- |
| **Source** | An external data provider listed in a `03_Data` source plan, with its access tier recorded. |
| **Signal** | A measured value or text sample retrieved from a source, before interpretation. |
| **Observation** | A signal stored verbatim with its source and time metadata. Never modified. |
| **Derived metric** | A value computed from observations by a documented rule (a change rate, an average). Reproducible. |
| **Interpretation** | A statement produced by AI or by analysis logic that goes beyond what a signal directly states. Always labeled as such. |
| **Evidence** | An observation or derived metric attached to a specific claim in a report. |
| **Theme** | A recurring topic identified across multiple signals, always reported with its supporting evidence. |
| **Proxy** | A signal used to stand in for something it does not directly measure (for example, marketplace rank standing in for sales). Always labeled as a proxy. |

## 5. Shared evidence schema

Every collected item is stored with these fields, whatever its source type. A collector
that cannot populate a required field must not store the record.

| Field | Required | Description |
| --- | --- | --- |
| `record_id` | yes | Stable internal identifier. |
| `record_type` | yes | `observation`, `derived_metric`, or `interpretation`. |
| `source_id` | yes | Identifier of the source in the applicable source plan. |
| `source_type` | yes | For example `macro_indicator`, `search_interest`, `public_discussion`, `marketplace`. |
| `publisher` | yes | Organization that published the data. |
| `access_method` | yes | `api`, `export`, `web_collection`, or `manual` (section 3.1). |
| `subject` | yes | Industry, category, or product idea researched. |
| `query_or_series_id` | yes | FRED series ID, Trends query configuration, or equivalent. |
| `geography` | yes | Geographic scope of the value. |
| `period_start`, `period_end` | yes | Period the value actually covers. |
| `observed_at` | no | Publication or release date, where the source provides one. |
| `retrieved_at` | yes | When the system fetched it. |
| `value` or `excerpt` | yes | The measurement, or the minimum text needed as evidence. |
| `unit` | conditional | Required for any numeric value. |
| `rights_note` | yes | Attribution, redistribution, and AI-use constraints for this record. |
| `retention_rule` | yes | How long the record may be kept, and its deletion trigger. |
| `limitation` | yes | What this record does not prove. |
| `derived_from` | conditional | Required for `derived_metric` and `interpretation`: the `record_id`s it rests on. |

An `interpretation` record with an empty `derived_from` is invalid. This is what makes
"separate evidence from interpretation" enforceable rather than a style guideline.

## 6. Shared confidence rubric

Both reports label every material finding with one of four levels. The level is assigned
by these rules, not by impression.

| Level | Assign when |
| --- | --- |
| **High** | Two or more independent listed sources support the claim, each covering the report's stated period and geography, and each with a documented methodology. |
| **Medium** | One listed source with a documented methodology covers the claim for the stated period and geography; or two or more sources agree but one has partial coverage. |
| **Low** | Only an indirect or proxy signal supports the claim; or listed sources conflict; or coverage is partially outside the stated period or geography. |
| **Insufficient evidence** | No listed source covers the claim, or the only available source's period or scope does not match the report window. |

Rules that apply to every level:

- A finding whose only support is an `interpretation` record cannot exceed **Low**.
- Public-discussion data is a self-selected sample. A finding resting on it alone cannot
  exceed **Medium**, and must carry the sampling limitation.
- **Insufficient evidence** is a valid and expected report outcome. The system must
  return it rather than lowering the standard to produce a conclusion.

## 7. Shared report header

Every report begins with these fields. Templates add subject-specific fields; they do not
remove these.

- Subject researched (industry, category, or product idea).
- Research question.
- Market and geographic scope.
- Time range covered, with explicit start and end dates.
- Report cadence.
- Generated date.
- Sources included.
- Sources expected but not available for this run, and the effect of each gap.
- One-sentence statement of the report's limitations.

## 8. Shared presentation rules

- Show the source and time range next to every conclusion.
- Label observation, derived metric, and interpretation differently in the interface.
- Show the confidence level and the key limitation with every material finding.
- Where a source updates less frequently than the report cadence, show its latest
  available observation date rather than implying it is current to the report date.
- Never present a proxy as the thing it stands in for.

## 9. Shared gating rule for unavailable sources

A report section whose only data source is not yet connected must render as
**Insufficient evidence**, naming the missing source and what it would add. It must not
be silently omitted, and it must not be filled from a source that does not support it.

Each report template marks which of its sections are gated in this way.

## 10. Open decisions

- Data storage and retention policy for the evidence store.
- Report sharing permissions, if the workspace ever moves beyond a single user.
- Export formats beyond the readable web page.

Decisions previously open here and now resolved:

| Question | Resolved in |
| --- | --- |
| First approved data sources | `docs/03_Data/01_Industry_Sentiment_MVP_Data_Sources.md`, `docs/03_Data/02_Product_Opportunity_MVP_Data_Sources.md` |
| First supported market and language | US, English — `docs/02_Research/01_Industry_Sentiment_MVP_Scope.md` |
| Report format | `docs/05_Design/01_...` and `docs/05_Design/02_...` templates |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial shared foundation draft. |
| v0.2 | 2026-08-23 | Made this the shared contract: added terminology, evidence schema, confidence rubric, report header, presentation rules, and the gating rule for unavailable sources. Moved resolved decisions to a resolution table. |
| v0.3 | 2026-08-23 | Added the free-first, API-first source selection policy with a four-tier access model that permits collection from public web pages, and the three limits that hold at every tier. |
