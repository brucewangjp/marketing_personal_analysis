# Phase 2: Evidence and Data Pipeline

- Version: v0.1
- Status: Implemented
- Updated: 2026-08-23

## 1. What Phase 2 adds

Collectors, and the contract they all implement. The evidence schema, store, and report
layers are unchanged from Phase 1 — which is what Phase 1 was shaped to prove.

| Module | Responsibility |
| --- | --- |
| `app/config.py` | Settings from the environment and a gitignored `.env`. Credentials never enter the repository. |
| `app/collectors/base.py` | The collector contract, the request and result types, and shared record construction. |
| `app/collectors/fred.py` | FRED, Tier 1 free API. |
| `app/collectors/trends_csv.py` | Google Trends, Tier 4 manual import and Tier 2 export. |
| `app/collect.py` | The run: executes collectors, writes records, reports what happened. |

## 2. The contract

```python
class Collector(Protocol):
    source_id: str
    def collect(self, request: CollectionRequest) -> CollectionResult: ...
```

**A collector that cannot run does not raise.** It returns a result carrying `reason`, and
the run continues with the sources that did work. This is the link between the collection
layer and the gating rule: a source that fails produces no records, the report finds none,
and the section says *insufficient evidence*. A crash would instead lose the whole run,
including the sources that were fine.

Failures are graded:

| Failure | Effect |
| --- | --- |
| Missing API key | The source is unavailable; the reason names where to get a key. |
| Host unreachable or timing out | The source is unavailable. |
| One series rejected or unknown | A warning. The other series still collect. |
| One malformed observation | Skipped silently; a missing value is never stored as a zero. |
| A record the schema rejects | Counted against that collector as a defect, not written. |

## 3. FRED

Free API key from https://fredaccount.stlouisfed.org/apikeys, kept in `.env`.

The collector reads each series' own metadata before its observations, so the **series'
frequency decides the period each observation covers**: a monthly indicator dated the
first of the month is stored as covering the whole month, never as a single day. FRED
marks a missing observation with `"."`; that row is skipped rather than stored as zero.

Five shared macroeconomic series ship as the default set: `FEDFUNDS`, `CPIAUCSL`,
`UNRATE`, `UMCSENT`, `INDPRO`. Sector-specific series are left empty in
`SUBJECT_SERIES` until their ids are verified against FRED on a real run — an unknown id
produces a warning, not a failed report, so a rename never costs a whole week.

## 4. Google Trends

Trends publishes no stable public API, so the implementation brief requires the manual
path to ship. The owner exports "Interest over time" and drops the CSV into
`data/imports/trends/`. An example of the expected format is in
`examples/trends_interest_over_time_example.csv`.

The parser tolerates the export's leading preamble, a `Week`, `Day`, or `Month` column, a
byte-order mark, and the `<1` value Trends writes for interest below one — stored as 0.5
with that fact recorded in the record's limitation, because dropping it would misrepresent
a real low reading as no reading at all.

Records collected this way carry `access_method=manual` and a limitation saying the value
is current only to the export. A future automated export adapter passes
`tier=AccessMethod.EXPORT` and the same parser serves it.

## 5. Running a collection

```
cp .env.example .env          # then add your FRED key
.venv/bin/python -m app.collect --subject "US technology" --window 3m
```

Options: `--as-of YYYY-MM-DD` for a reproducible run, `--dry-run` to collect without
writing, `--drop-sample` to remove the Phase 1 sample records once real ones exist.

The run prints one line per source with its tier, record count, and status, then names any
unavailable source and reminds the reader that the report will say so.

## 6. Known limitations

- No collection has been run against the live FRED API from the development sandbox, whose
  egress proxy rejects `api.stlouisfed.org`. Every collector test runs against a mocked
  transport. The first real run needs a key and network access.
- `SUBJECT_SERIES` is empty: sector context is not yet collected.
- Census, BEA, and BLS collectors — MVP2's measured category sales — are Phase 5.
- The report cannot distinguish "source not connected" from "source connected but its
  collection failed". Both render as insufficient evidence, which is correct for the
  reader; the *why* is in the collection run's output. Keeping the report ignorant of
  collection is deliberate: it reads the evidence store and nothing else.

## 7. Next

Phase 3: derive findings from collected signals rather than from series shape, and generate
the monitoring list from real changes and gaps.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial Phase 2 collectors: contract, FRED, Google Trends import, and the collection run. |
