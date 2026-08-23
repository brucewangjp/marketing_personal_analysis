"""Run the collectors and write what they return into the evidence store.

    .venv/bin/python -m app.collect --subject "US technology" --window 3m

A collector that cannot run is reported, not fatal. The run continues with the sources
that did work, and the report's gating rule turns each missing source into an honest
"insufficient evidence" section rather than a silently thinner report.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta

from . import config
from .collectors.base import CollectionRequest, CollectionResult, Collector
from .collectors.fred import FredCollector
from .collectors.trends_csv import TrendsCsvCollector
from .models import InvalidRecord
from .reports.industry_sentiment import SUBJECTS, WINDOWS
from .store import EvidenceStore

GEOGRAPHY = "United States"


def build_collectors(settings: config.Settings) -> list[Collector]:
    return [FredCollector(settings), TrendsCsvCollector(settings)]


def run(
    request: CollectionRequest,
    settings: config.Settings,
    *,
    dry_run: bool = False,
    drop_sample: bool = False,
) -> list[CollectionResult]:
    results = [c.collect(request) for c in build_collectors(settings)]

    if dry_run:
        return results

    with EvidenceStore(settings.db_path) as store:
        if drop_sample:
            removed = store.delete_sample_records()
            print(f"Removed {removed} sample record(s).")
        for result in results:
            stored, rejected = 0, 0
            for record in result.records:
                try:
                    store.add(record)
                    stored += 1
                except (InvalidRecord, KeyError) as exc:
                    # A record the schema refuses is a collector defect. Report it
                    # against that collector instead of failing the whole run.
                    rejected += 1
                    result.warnings.append(f"rejected {record.record_id}: {exc}")
            if rejected:
                result.warnings.append(
                    f"{rejected} of {len(result.records)} record(s) failed validation"
                )
            result.records = result.records[:stored] if rejected else result.records
    return results


def report(results: list[CollectionResult], request: CollectionRequest) -> int:
    print(
        f"\n{request.subject} · {request.geography} · "
        f"{request.period_start} to {request.period_end}\n"
    )
    width = max(len(r.source_id) for r in results)
    for result in results:
        tier = result.tier.value if result.tier else "-"
        print(
            f"  {result.source_id:<{width}}  {result.status:<12} "
            f"tier={tier:<14} {len(result.records):>4} record(s)"
        )
        if result.reason:
            print(f"      ! {result.reason}")
        for warning in result.warnings:
            print(f"      - {warning}")

    unavailable = [r.source_id for r in results if r.failed]
    if unavailable:
        print(
            f"\n{len(unavailable)} source(s) unavailable: {', '.join(unavailable)}. "
            "Report sections that depend on them will say so."
        )
    print()
    # Sources being unavailable is a reported condition, not a failed run: the report is
    # designed to be correct with them missing.
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect evidence for a report.")
    parser.add_argument("--subject", default=SUBJECTS[0], choices=list(SUBJECTS))
    parser.add_argument("--window", default="3m", choices=list(WINDOWS))
    parser.add_argument(
        "--as-of", type=date.fromisoformat, default=date.today(), metavar="YYYY-MM-DD"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="collect but do not write to the store"
    )
    parser.add_argument(
        "--drop-sample",
        action="store_true",
        help="remove Phase 1 sample records before writing collected ones",
    )
    args = parser.parse_args(argv)

    settings = config.load()
    request = CollectionRequest(
        subject=args.subject,
        geography=GEOGRAPHY,
        period_start=args.as_of - timedelta(days=WINDOWS[args.window][1]),
        period_end=args.as_of,
    )
    results = run(
        request, settings, dry_run=args.dry_run, drop_sample=args.drop_sample
    )
    if args.dry_run:
        print("\n(dry run: nothing written)")
    return report(results, request)


if __name__ == "__main__":
    sys.exit(main())
