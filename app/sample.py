"""Sample evidence for Phase 1.

Phase 1 ships no collectors, so the report is exercised against sample records. Every
record here carries `is_sample=True`, the store keeps that flag, and the report marks
itself as containing sample data. Nothing in the pipeline treats sample data as real:
the flag exists so it can never be mistaken for a collected observation.

The shapes mirror what the real collectors will produce — a FRED monthly indicator, a
Google Trends weekly series — so Phase 2 replaces the source of these records without
changing anything downstream.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .models import AccessMethod, EvidenceRecord, RecordType, SourceType

RETRIEVED = datetime(2026, 8, 23, 9, 0, 0)

SUBJECTS = ("US technology", "US healthcare")

_TRENDS_SERIES: dict[str, list[float]] = {
    # Weekly relative search interest, 0-100, as Google Trends reports it.
    "US technology": [44, 46, 43, 48, 52, 51, 57, 60, 58, 64, 69, 72, 71],
    "US healthcare": [58, 57, 59, 56, 55, 57, 54, 53, 55, 52, 51, 53, 50],
}

_FRED_SERIES: dict[str, tuple[str, str, list[tuple[date, float]]]] = {
    "UMCSENT": (
        "University of Michigan: Consumer Sentiment",
        "index 1966:Q1=100",
        [
            (date(2026, 5, 1), 62.8),
            (date(2026, 6, 1), 60.4),
            (date(2026, 7, 1), 61.7),
        ],
    ),
    "FEDFUNDS": (
        "Federal Funds Effective Rate",
        "percent",
        [
            (date(2026, 5, 1), 3.88),
            (date(2026, 6, 1), 3.63),
            (date(2026, 7, 1), 3.62),
        ],
    ),
    "CPIAUCSL": (
        "Consumer Price Index for All Urban Consumers",
        "index 1982-1984=100",
        [
            (date(2026, 5, 1), 322.1),
            (date(2026, 6, 1), 323.4),
            (date(2026, 7, 1), 324.6),
        ],
    ),
}


def _trends_records(subject: str, end: date, weeks: int) -> list[EvidenceRecord]:
    series = _TRENDS_SERIES[subject]
    values = series[-weeks:]
    slug = subject.lower().replace(" ", "_")
    records = []
    for i, value in enumerate(values):
        week_end = end - timedelta(days=7 * (len(values) - 1 - i))
        week_start = week_end - timedelta(days=6)
        records.append(
            EvidenceRecord(
                record_id=f"sample.trends.{slug}.{week_start.isoformat()}",
                record_type=RecordType.OBSERVATION,
                source_id="google_trends",
                source_type=SourceType.SEARCH_INTEREST,
                publisher="Google",
                access_method=AccessMethod.EXPORT,
                subject=subject,
                query_or_series_id=f'query="{subject}", geo=US, weekly',
                geography="United States",
                period_start=week_start,
                period_end=week_end,
                retrieved_at=RETRIEVED,
                value=float(value),
                unit="relative interest, 0-100",
                rights_note="Attribution to Google Trends required.",
                retention_rule="Retain the query configuration with the series.",
                limitation=(
                    "Relative attention within this query and period. Not search "
                    "volume, sentiment, or purchase intent."
                ),
                is_sample=True,
            )
        )
    return records


def _fred_records(subject: str, window_start: date) -> list[EvidenceRecord]:
    records = []
    for series_id, (name, unit, observations) in _FRED_SERIES.items():
        for observed, value in observations:
            # A monthly indicator covers its whole month.
            period_end = (observed.replace(day=28) + timedelta(days=4)).replace(
                day=1
            ) - timedelta(days=1)
            if period_end < window_start:
                continue
            records.append(
                EvidenceRecord(
                    record_id=(
                        f"sample.fred.{series_id.lower()}.{observed.isoformat()}"
                        f".{subject.lower().replace(' ', '_')}"
                    ),
                    record_type=RecordType.OBSERVATION,
                    source_id="fred",
                    source_type=SourceType.MACRO_INDICATOR,
                    publisher="Federal Reserve Bank of St. Louis",
                    access_method=AccessMethod.API,
                    subject=subject,
                    query_or_series_id=series_id,
                    geography="United States",
                    period_start=observed,
                    period_end=period_end,
                    observed_at=observed,
                    retrieved_at=RETRIEVED,
                    value=value,
                    unit=unit,
                    rights_note="Attribution to FRED and the originating agency required.",
                    retention_rule="Retain while the report referencing it is retained.",
                    limitation=(
                        f"{name} describes the US economy as a whole, not this industry."
                    ),
                    is_sample=True,
                )
            )
    return records


def records_for(subject: str, window_start: date, window_end: date) -> list[EvidenceRecord]:
    """Sample evidence covering one subject and window."""
    weeks = max(2, ((window_end - window_start).days // 7) + 1)
    return _trends_records(subject, window_end, weeks) + _fred_records(
        subject, window_start
    )


def all_records() -> list[EvidenceRecord]:
    """Every sample record, for seeding the store."""
    end = date(2026, 8, 22)
    start = end - timedelta(days=90)
    records: list[EvidenceRecord] = []
    for subject in SUBJECTS:
        records.extend(records_for(subject, start, end))
    return records
