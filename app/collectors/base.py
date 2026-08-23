"""The collector contract.

Every source implements this, so a source can move between access tiers — or be replaced
entirely — without the analysis or report layers changing.

A collector that cannot run does not raise. It returns a failed result, the store gains no
records for that source, and the report's gating rule turns that into an honest
"insufficient evidence" section. A crash would instead lose the whole run, including the
sources that did work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Protocol, runtime_checkable

from ..models import AccessMethod, EvidenceRecord, RecordType, SourceType
from .. import sources


@dataclass(frozen=True)
class CollectionRequest:
    subject: str
    geography: str
    period_start: date
    period_end: date

    @property
    def subject_slug(self) -> str:
        return self.subject.lower().replace(" ", "_")


@dataclass
class CollectionResult:
    source_id: str
    tier: AccessMethod | None = None
    records: list[EvidenceRecord] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    reason: str = ""
    """Why the collector could not run at all. Empty when it ran."""

    @property
    def failed(self) -> bool:
        return bool(self.reason)

    @property
    def status(self) -> str:
        if self.failed:
            return "unavailable"
        if not self.records:
            return "no data"
        return "ok"


@runtime_checkable
class Collector(Protocol):
    source_id: str

    def collect(self, request: CollectionRequest) -> CollectionResult: ...


def build_record(
    *,
    source_id: str,
    record_id: str,
    request: CollectionRequest,
    source_type: SourceType,
    access_method: AccessMethod,
    query_or_series_id: str,
    period_start: date,
    period_end: date,
    limitation: str,
    value: float | None = None,
    unit: str | None = None,
    excerpt: str | None = None,
    observed_at: date | None = None,
    retrieved_at: datetime | None = None,
    publisher: str | None = None,
) -> EvidenceRecord:
    """Build an observation, filling rights and retention from the source registry.

    Centralised so every collector's records carry the same rights metadata, rather than
    each collector remembering to attach it.
    """
    source = sources.get(source_id)
    return EvidenceRecord(
        record_id=record_id,
        record_type=RecordType.OBSERVATION,
        source_id=source_id,
        source_type=source_type,
        publisher=publisher or source.publisher,
        access_method=access_method,
        subject=request.subject,
        query_or_series_id=query_or_series_id,
        geography=request.geography,
        period_start=period_start,
        period_end=period_end,
        observed_at=observed_at,
        retrieved_at=retrieved_at or datetime.now(),
        value=value,
        unit=unit,
        excerpt=excerpt,
        rights_note=source.rights_note,
        retention_rule=source.retention_rule,
        limitation=limitation,
        is_sample=False,
    )


def end_of_month(day: date) -> date:
    from calendar import monthrange

    return day.replace(day=monthrange(day.year, day.month)[1])


def period_for(observation: date, frequency: str) -> tuple[date, date]:
    """The span a single observation actually covers.

    A monthly indicator dated the first of the month describes the whole month. Reporting
    it as a single day would misstate what the source measured.
    """
    freq = (frequency or "").strip().lower()
    if freq.startswith("m"):
        return observation, end_of_month(observation)
    if freq.startswith("q"):
        month = observation.month + 2
        year = observation.year + (month - 1) // 12
        month = (month - 1) % 12 + 1
        return observation, end_of_month(observation.replace(year=year, month=month))
    if freq.startswith("a") or freq.startswith("y"):
        return observation, observation.replace(month=12, day=31)
    if freq.startswith("w"):
        from datetime import timedelta

        return observation, observation + timedelta(days=6)
    return observation, observation
