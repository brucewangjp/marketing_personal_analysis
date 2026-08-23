# Phase 1 Technical Design

- Version: v0.1
- Status: Implemented
- Updated: 2026-08-23

## 1. Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3.11 | Every source in both data-source plans — FRED, Census, BEA, BLS — is a plain HTTP JSON API, and Python has the shortest path from response to normalized record. |
| Web | FastAPI + Jinja2, server-rendered HTML | The report is a document, not an application. Server-rendered pages mean no build step and no JavaScript toolchain to maintain for a single-user tool. |
| Store | SQLite | One user, one machine, weekly writes. A file that can be copied and inspected with any SQLite viewer beats a server process. |
| Charts | Inline SVG, generated server-side | Avoids a charting dependency and keeps the report readable with no network access. |
| Tests | pytest | — |

Deliberately not chosen: a JavaScript SPA framework (adds a build step and a second
language for a document-shaped output), an ORM (the evidence schema is one table with
fixed fields), and a charting library (one line chart does not justify a dependency).

## 2. Module map

| Module | Responsibility | Specified by |
| --- | --- | --- |
| `app/models.py` | The evidence record, its field rules, and write-time validation | Shared foundation section 5 |
| `app/sources.py` | Source registry: publisher, access tier, whether methodology is documented, whether values are proxies, connection state | Shared foundation section 3.1, both source plans |
| `app/confidence.py` | The confidence rubric as executable rules | Shared foundation section 6 |
| `app/store.py` | SQLite evidence store; rejects invalid records at write time | Shared foundation section 5 |
| `app/reporting.py` | Section assembly, the gating rule, and the report view model | Shared foundation sections 7–9 |
| `app/reports/industry_sentiment.py` | The MVP1 report: which sections exist, what each needs | `docs/05_Design/01_Industry_Sentiment_Report_Template.md` |
| `app/charts.py` | Server-side SVG line chart | Report template section 4 |
| `app/sample.py` | Clearly labeled sample evidence for Phase 1 | Implementation brief, Phase 1 |
| `app/main.py` | Routes: selector, report | Implementation brief, Phase 1 |

The report layer never reads a source directly. It reads the evidence store, which is what
makes MVP2 a matter of adding a collector and a template rather than a second system.

## 3. What Phase 1 does and does not do

Done:

- Evidence schema enforced at write time, including the rule that an interpretation
  without `derived_from` is rejected.
- Confidence rubric applied to every finding, including the two caps.
- Gating rule applied to sections whose source is not connected.
- Report page rendering every section of the MVP1 template from stored evidence.
- Industry and time-window selector.
- Sample evidence, labeled as sample in the store and in the interface.

Not yet, by design — these are Phases 2 to 4:

- Real collectors. No network call is made anywhere in this phase.
- Scheduling. The weekly run is manual for now.
- Analysis that derives findings from raw signals. Phase 1 findings come from sample data.

## 4. Running it

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.seed          # load sample evidence into ./data/evidence.db
.venv/bin/uvicorn app.main:app --reload
.venv/bin/python -m pytest            # tests
```

## 5. Handoff

Required by `00_Claude_Code_Implementation_Brief.md` section 8.

### Completed

- Evidence schema enforced at write time. An interpretation or derived metric without
  `derived_from` is rejected, as is a reference to a record that is not stored, an
  observation claiming to derive from something, a numeric value without a unit, and a
  record from an unregistered source.
- Confidence rubric implemented as rules, including both caps and the demotion of a
  two-source claim to Medium when coverage of the window is partial.
- Gating rule: sections 6 and 7 of the report template render as insufficient evidence
  naming the missing source and what it would provide.
- Report page rendering every template section, an SVG attention chart, the evidence
  table with periods and retrieval dates, and separate labels for observation, derived
  metric, and interpretation.
- Industry and window selector; a source table showing connection state.
- Sample evidence, flagged in the store and declared in the report header.

### Test results

75 tests pass, covering the schema rules, store behavior, every rubric branch, gating,
report assembly for both industries and both windows, the empty-store case, and the
rendered pages.

### Known limitations

- No collectors. Every record is sample data. Reports say so.
- Findings are assembled from series shape, not from analysis. Real analysis is Phase 3.
- The weekly run is manual; scheduling is Phase 4.
- Group attitude and motivations will stay gated until a public-discussion source is
  connected. This is the specified behavior, not an incomplete feature.

### Assumptions made

- A report defaults to the latest period the store covers, not to today, so a report
  generated after a quiet week is not silently empty.
- `direction()` compares the first and last third of a series rather than its endpoints.
  Endpoints alone are too noisy for a weekly report; a third at each end smooths that
  without pretending to be a trend model.

### Next recommended task

Phase 2: replace `app/sample.py` with a FRED collector. The evidence schema, store, and
report layers do not change — the collector writes the same records the sample module
writes now, which is what Phase 1 was shaped to prove.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial Phase 1 technical design and stack choice. |
