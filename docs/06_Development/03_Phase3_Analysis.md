# Phase 3: Analysis and Report Generation

- Version: v0.1
- Status: Implemented
- Updated: 2026-08-23

## 1. What Phase 3 adds

`app/analysis.py`, and a report layer that reads from it. Phase 1 and 2 built the
plumbing; this is where the report starts saying something a reader could act on, without
saying more than the evidence supports.

## 2. The two rules

### A direction is only claimed when the move clears the series' own noise

A weekly attention series wanders. Calling every wander a trend produces a report that says
something different each week while nothing has actually changed — the reader learns to
distrust it, or worse, acts on it.

A move must clear **both** bars to be called rising or falling:

| Bar | Stops |
| --- | --- |
| 10% of the opening average | Trivial moves in a quiet series |
| One standard deviation of the series | Ordinary wander in a noisy series |

Below both, the finding is **stable**, and the report says why: *"a move smaller than the
noise is not a direction."* Under four observations the direction is **indeterminate**,
which is not the same as stable — absence of evidence for a direction is not evidence of
stability, and the report distinguishes them.

Worked example from the tests: a series running `50 58 44 61 47 55 49 60 45 57 52 48 53`
swings by 17 points and ends where it started. It is reported as stable, not as a trend.

### Every stated number names the observations it came from

A finding that states a change carries a `derived_metric` record whose `derived_from`
lists every observation behind it. The schema has required this since Phase 1; this is
where it is honoured. A reader can go from "attention rose 23.8" to the exact rows.

Building a report never writes to the store. The metrics are computed and attached to
findings, so the same stored evidence always produces the same report.

## 3. What the report now states

- **Attention:** direction with the magnitude, the percentage move, the bars it cleared,
  the range, and the week-to-week variation.
- **Macro:** each indicator's level, its direction across the window when one is
  supported, and **how many days stale its latest observation is** — a monthly series is
  never allowed to imply it is current to the report date.
- **Change over time:** the supported change, plus any single period that moved more than
  two standard deviations beyond this series' usual movement, with the cause explicitly
  not claimed.
- **Monitoring list:** generated from what actually moved and what is actually missing.
  A rising subject gets "whether it is still rising next week, or the move of 23.8
  reverses"; a stable one gets "whether it breaks out of its range"; a thin window gets
  "too few observations to read a direction". It is not a fixed checklist.

## 4. Known limitations

- The direction test is a threshold rule, not a statistical model. It is deliberately
  simple enough that the report can state exactly why it concluded what it did, which
  matters more here than sensitivity.
- Notable moves are flagged, never explained. Nothing in the evidence establishes cause,
  and the finding says so.
- Sentiment remains ungeneratable until a public-discussion source is connected. Attention
  and macro data measure the environment, not what people think, and the report will keep
  reporting tone as a gap rather than inferring it.

## 5. Next

Phase 4: weekly scheduling, and the public-discussion collector that ungates the attitude
and motivation sections of both reports.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial analysis layer: noise-aware direction detection, traceable derived metrics, staleness reporting, and a generated monitoring list. |
