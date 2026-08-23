# Industry Sentiment Report Template

- Version: v0.1
- Status: Draft
- Updated: 2026-08-23

## 1. Purpose

This document defines the final report the user should receive for the US technology or US healthcare industry. Implementation should work backward from this report: Claude Code may choose the internal data layout, storage model, and screens needed to produce every required section.

The report analyzes group-level online signals. It does not diagnose individuals, provide personal investment advice, or claim that an online sample represents all people.

## 2. Report header

Every report begins with:

- Industry: US technology or US healthcare.
- Research question.
- Time range: most recent one month or most recent three months.
- Report cadence: weekly.
- Geographic scope.
- Generated date.
- Sources included and sources not yet available.
- One-sentence statement of the report’s limitations.

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

## 6. Group attitude

### User-facing view

Show the dominant group-level attitudes found in approved online signals:

| Attitude | Meaning | Evidence summary |
| --- | --- | --- |
| Positive | People express optimism, interest, confidence, or enthusiasm. | Source-backed summary. |
| Cautious | People express uncertainty, wait-and-see behavior, or mixed expectations. | Source-backed summary. |
| Negative | People express concern, avoidance, disappointment, or distrust. | Source-backed summary. |

If evidence is insufficient, the report must say so instead of assigning an attitude.

## 7. Motivations and concerns

### User-facing view

For each visible attitude, show the main explanations people give or that are strongly supported by the available signals:

- Reasons for interest or optimism.
- Reasons for hesitation or uncertainty.
- Reasons for concern or avoidance.
- Topics that are becoming more important over time.

Each theme includes a source, date range, and short evidence summary.

## 8. Change over time

### User-facing view

Describe what has changed during the selected period:

- Attention increase or decrease.
- Tone becoming more positive, cautious, negative, or mixed.
- New concerns or new sources of optimism.
- Changes that are strongly supported versus changes that remain uncertain.

## 9. Evidence and confidence

### User-facing view

Every material finding includes:

- Data source.
- Date or measurement period.
- Geographic and industry scope.
- Evidence summary or metric.
- Confidence: high, medium, low, or insufficient evidence.
- Limitation of that source.

The report must make it easy for a user to open the original source where permitted.

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

Claude Code should treat this document as the output contract. It should design the data schema, collection workflow, analysis steps, API shape, and user-interface layout required to create this report reliably.

## 13. Time-window behavior

- A weekly run uses either a one-month or three-month lookback window selected by the user.
- The report must make the selected window visible in its header and charts.
- A result from the one-month window should not be compared directly with the three-month window without a clear label.
- Sources that update less frequently must show their latest available observation date rather than implying they are current to the report date.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial report-first template for the industry-sentiment MVP. |
