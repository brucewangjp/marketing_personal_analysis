# Industry Sentiment Report Template

- Version: v0.2
- Status: Draft
- Updated: 2026-08-23

## 1. Purpose

This document defines the final report the user should receive for the US technology or US healthcare industry. Implementation should work backward from this report: Claude Code may choose the internal data layout, storage model, and screens needed to produce every required section.

The report analyzes group-level online signals. It does not diagnose individuals, provide personal investment advice, or claim that an online sample represents all people.

## 1.1 Shared contract

The report header, terminology, evidence schema, confidence rubric, presentation rules,
and the gating rule for unavailable sources are defined once in
`docs/01_Product/00_Shared_Research_Foundation.md`. This template does not restate them.

Sections marked **Gated** below depend on a source that may not be connected for a given
run. Under the shared gating rule they render as *Insufficient evidence*, naming the
missing source and what it would have added. They are never omitted and never filled from
a source that does not support them.

## 2. Report header

The shared report header (shared foundation, section 7), with these subject-specific values:

- Subject: US technology or US healthcare.
- Time range: most recent one month or most recent three months.
- Report cadence: weekly.

## 3. Executive summary

The opening section gives a short answer to the research question:

- Overall attention: rising, stable, or falling.
- Overall group tone: positive, cautious, negative, mixed, or insufficient evidence.
- The two or three strongest reasons behind the current tone.
- The most important recent change.
- What should be monitored next.

This section must distinguish observed signals from the system’s interpretation.

## 4. Attention trend

### User-facing view

- A time-series chart of online search interest.
- Current direction: rising, stable, or falling.
- Comparison with related industry terms when useful.
- Dates of notable changes.

### Required explanation

Explain that search interest measures relative attention, not the number of people, their sentiment, or a decision to buy.

## 5. Macro and aggregate sentiment context

### User-facing view

- Relevant macroeconomic indicators, such as interest rates, inflation, employment, or consumption.
- Existing aggregate consumer or investor sentiment measures when permitted.
- A short explanation of how the broader environment may relate to the industry.

### Required explanation

Do not state that macroeconomic correlation proves why people feel or act a certain way.

## 6. Group attitude — **Gated: public-discussion source**

### User-facing view

Show the dominant group-level attitudes found in approved online signals:

| Attitude | Meaning | Evidence summary |
| --- | --- | --- |
| Positive | People express optimism, interest, confidence, or enthusiasm. | Source-backed summary. |
| Cautious | People express uncertainty, wait-and-see behavior, or mixed expectations. | Source-backed summary. |
| Negative | People express concern, avoidance, disappointment, or distrust. | Source-backed summary. |

If evidence is insufficient, the report must say so instead of assigning an attitude.

Until a public-discussion source is connected, this is the expected state of this section:
search interest and macro indicators measure attention and environment, not attitude, and
must not be used to infer one.

## 7. Motivations and concerns — **Gated: public-discussion source**

### User-facing view

For each visible attitude, show the main explanations people give or that are strongly supported by the available signals:

- Reasons for interest or optimism.
- Reasons for hesitation or uncertainty.
- Reasons for concern or avoidance.
- Topics that are becoming more important over time.

Each theme includes a source, date range, and short evidence summary.

This section states why people hold a view, which only natural-language sources can
support. Without a connected public-discussion source it renders as insufficient evidence.

## 8. Change over time

### User-facing view

Describe what has changed during the selected period:

- Attention increase or decrease.
- Tone becoming more positive, cautious, negative, or mixed.
- New concerns or new sources of optimism.
- Changes that are strongly supported versus changes that remain uncertain.

## 9. Evidence and confidence

Every material finding carries the fields and the confidence level defined by the shared
evidence schema and confidence rubric (shared foundation, sections 5 and 6). The report
must make it easy for a user to open the original source where permitted.

Industry-specific note: a finding supported only by Google Trends is attention evidence at
**Low** or **Medium** confidence depending on series stability, and can never support a
statement about sentiment.

## 10. Monitoring list

End with a short list of items to follow in the next report:

- Search terms or attention signals to watch.
- Macro or aggregate-sentiment indicators to watch.
- Discussion themes that may be shifting.
- Important data gaps that need another source before a conclusion is possible.

## 11. Layout requirements for implementation

- Start with the executive summary and show the evidence behind it nearby.
- Use charts only where they make a change over time easier to understand.
- Always show source and time range next to a conclusion.
- Clearly label evidence, interpretation, and uncertainty differently.
- Present the report as a readable web page first; export formats can come later.

## 12. Development instruction

Claude Code should treat this document, together with the shared contract it references,
as the output contract for the first MVP. It should design the collection workflow,
analysis steps, API shape, and user-interface layout required to create this report
reliably. The evidence schema is already fixed by the shared foundation.

A first working version in which sections 6 and 7 render as insufficient evidence is a
correct outcome, not an incomplete one.

## 13. Time-window behavior

- A weekly run uses either a one-month or three-month lookback window selected by the user.
- The report must make the selected window visible in its header and charts.
- A result from the one-month window should not be compared directly with the three-month window without a clear label.
- Sources that update less frequently must show their latest available observation date rather than implying they are current to the report date.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial report-first template for the industry-sentiment MVP. |
| v0.2 | 2026-08-23 | Referenced the shared contract instead of restating the header and confidence levels; marked sections 6 and 7 as gated on the public-discussion source. |
