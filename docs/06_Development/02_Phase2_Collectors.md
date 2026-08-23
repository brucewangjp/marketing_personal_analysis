# Phase 2: Evidence and Data Pipeline

- Version: v0.2
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
| `app/collectors/trends_api.py` | Google Trends, Tier 3 automated collection from the public interface. |
| `app/collectors/trends_csv.py` | Google Trends, Tier 4 manual import and Tier 2 export. |
| `app/collectors/trends.py` | Tries Tier 3, falls back to Tier 4. |
| `app/collect.py` | The run: executes collectors, writes records, reports what happened. |
| `app/check.py` | Self-check: confirms this machine can reach the sources and that their responses still match what the collectors expect. |

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

Google publishes no documented API for Trends, so the source runs at two tiers and tries
them in policy order.

### Tier 3 — automated collection

The Trends web interface calls an internal endpoint; the collector calls the same one.
This is the Tier 3 route the source selection policy permits when no API and no export
exists. It is unauthenticated, sends no cookies or credentials, reads only what a
signed-out visitor sees, and stores a metric plus the query configuration — never a page
copy and nothing personal.

**When Google declines, it gives up.** A 429 or 403 is a failed result after a single
attempt, and the run drops to Tier 4. There is no retry loop, no identity rotation, and no
attempt to get around a block: that is the policy, and in practice pushing through would
lose the source permanently.

The endpoint is undocumented and does change. A response shape the collector does not
recognise is a failed source, not a crash, and the CSV path takes over.

### Tier 4 — manual import

The reliable path, and the reason the automated one can be allowed to fail. The owner
exports "Interest over time" and drops the CSV into `data/imports/trends/`. An example of
the expected format is in `examples/trends_interest_over_time_example.csv`.

The parser tolerates the export's leading preamble, a `Week`, `Day`, or `Month` column, a
byte-order mark, and the `<1` value Trends writes for interest below one — stored as 0.5
with that fact recorded in the record's limitation, because dropping it would misrepresent
a real low reading as no reading at all.

Records carry the tier that actually produced them — `web_collection` or `manual` — and
the manual ones say in their limitation that the value is current only to the export.
`--no-automated-trends` forces the CSV path.

## 5. Running a collection

```
cp .env.example .env          # then add your FRED key
.venv/bin/python -m app.check # confirm the sources are reachable and understood
.venv/bin/python -m app.collect --subject "US technology" --window 3m
```

Options: `--as-of YYYY-MM-DD` for a reproducible run, `--dry-run` to collect without
writing, `--drop-sample` to remove the Phase 1 sample records once real ones exist.

The run prints one line per source with its tier, record count, and status, then names any
unavailable source and reminds the reader that the report will say so.

## 6. Known limitations

- No collection has been run against the live FRED API. The development sandbox's egress
  proxy rejects every data-source host — `api.stlouisfed.org`, `trends.google.com`,
  `api.census.gov`, `api.bls.gov`, `apps.bea.gov` — so every collector test runs against a
  mocked transport, written to the documented response shape rather than an observed one.
  `python -m app.check` exists for exactly this: it makes one real metadata call, one real
  observations call, and one real Trends collection, and names any field the collectors
  expect but did not get, so the first real run diagnoses itself instead of failing
  somewhere deeper.
- The automated Trends collector has likewise never run against live Google. Expect it to
  need adjustment, and expect it to break again later; the CSV path is what makes that
  survivable rather than blocking.
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
| v0.2 | 2026-08-23 | Added the Tier 3 automated Trends collector and the tier fallback chain, so the manual export is the exception rather than the weekly routine. |
