"""Google Trends importer — Tier 4 manual import, and Tier 2 for a downloaded export.

Google Trends publishes no stable public API, so the implementation brief requires this
path to ship: the owner exports "Interest over time" from the Trends interface and drops
the CSV into the import directory. A run must be able to proceed without it, so a missing
directory is a normal outcome, not an error.

The export looks like:

    Category: All categories

    Week,US technology: (United States)
    2026-05-24,44
    2026-05-31,46

The parser is deliberately tolerant of the leading preamble, of Day/Week/Month columns,
and of the "<1" value Trends uses for interest below one.
"""

from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path

from ..config import Settings
from ..models import AccessMethod, EvidenceRecord, SourceType
from .base import CollectionRequest, CollectionResult, build_record, period_for

UNIT = "relative interest, 0-100"

_PERIOD_COLUMNS = {"week": "Weekly", "day": "Daily", "month": "Monthly"}
_HEADER_QUERY = re.compile(r"^(?P<query>.+?):\s*\((?P<geo>.+?)\)\s*$")
# Trends writes "<1" for interest below one. Treated as 0.5 with the limitation recorded,
# because dropping it would misrepresent a real low reading as no reading at all.
_BELOW_ONE = 0.5


class TrendsCsvCollector:
    source_id = "google_trends"

    def __init__(
        self,
        settings: Settings,
        *,
        tier: AccessMethod = AccessMethod.MANUAL,
    ) -> None:
        self.settings = settings
        self.tier = tier

    def collect(self, request: CollectionRequest) -> CollectionResult:
        result = CollectionResult(source_id=self.source_id, tier=self.tier)
        directory = self.settings.trends_import_dir

        if not directory.exists():
            result.warnings.append(
                f"No Trends export directory at {directory}. Export 'Interest over time' "
                "from Google Trends and save the CSV there."
            )
            return result

        files = sorted(directory.glob("*.csv"))
        if not files:
            result.warnings.append(f"No CSV exports found in {directory}.")
            return result

        retrieved_at = datetime.now()
        for path in files:
            try:
                records, note = self._read_file(path, request, retrieved_at)
            except ValueError as exc:
                result.warnings.append(f"{path.name}: {exc}")
                continue
            if note:
                result.warnings.append(f"{path.name}: {note}")
            result.records.extend(records)

        if not result.records and not result.warnings:
            result.warnings.append(
                "Exports were found but none covered this subject and window."
            )
        return result

    # -- parsing ---------------------------------------------------------

    def _read_file(
        self, path: Path, request: CollectionRequest, retrieved_at: datetime
    ) -> tuple[list[EvidenceRecord], str]:
        rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
        header_index = _find_header(rows)
        if header_index is None:
            raise ValueError(
                "no 'Week', 'Day', or 'Month' header row found; is this an "
                "'Interest over time' export?"
            )

        header = rows[header_index]
        frequency = _PERIOD_COLUMNS[header[0].strip().lower()]
        query, geography = _parse_query_column(header[1] if len(header) > 1 else "")

        if not _matches_subject(query, request.subject):
            return [], f"skipped: query {query!r} is not {request.subject!r}"

        records: list[EvidenceRecord] = []
        below_one = 0
        for row in rows[header_index + 1 :]:
            if len(row) < 2 or not row[0].strip():
                continue
            try:
                observed = date.fromisoformat(row[0].strip())
            except ValueError:
                continue

            raw = row[1].strip()
            if not raw:
                continue
            if raw == "<1":
                value, below_one = _BELOW_ONE, below_one + 1
            else:
                try:
                    value = float(raw)
                except ValueError:
                    continue

            period_start, period_end = period_for(observed, frequency)
            if period_end < request.period_start or period_start > request.period_end:
                continue

            limitation = (
                "Relative attention within this query and period. Not search volume, "
                "sentiment, or purchase intent."
            )
            if raw == "<1":
                limitation += " Reported by the source as '<1'; stored as 0.5."
            if self.tier is AccessMethod.MANUAL:
                limitation += " Imported by hand, so it is current only to the export."

            records.append(
                build_record(
                    source_id=self.source_id,
                    record_id=(
                        f"trends.{request.subject_slug}.{observed.isoformat()}"
                    ),
                    request=request,
                    source_type=SourceType.SEARCH_INTEREST,
                    access_method=self.tier,
                    query_or_series_id=(
                        f'query="{query}", geo={geography}, {frequency.lower()}'
                    ),
                    period_start=period_start,
                    period_end=period_end,
                    observed_at=observed,
                    retrieved_at=retrieved_at,
                    value=value,
                    unit=UNIT,
                    limitation=limitation,
                )
            )

        note = ""
        if below_one:
            note = f"{below_one} value(s) reported as '<1' and stored as 0.5"
        return records, note


def _find_header(rows: list[list[str]]) -> int | None:
    for index, row in enumerate(rows):
        if row and row[0].strip().lower() in _PERIOD_COLUMNS:
            return index
    return None


def _parse_query_column(column: str) -> tuple[str, str]:
    match = _HEADER_QUERY.match(column.strip())
    if match:
        return match.group("query").strip(), match.group("geo").strip()
    return column.strip() or "unknown", "unknown"


def _matches_subject(query: str, subject: str) -> bool:
    """Exports are named by the query, which may differ in case or spacing."""
    normalise = lambda text: re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    return normalise(query) == normalise(subject)
