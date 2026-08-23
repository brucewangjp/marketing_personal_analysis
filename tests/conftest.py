from datetime import date, datetime

import pytest

from app.models import AccessMethod, EvidenceRecord, RecordType, SourceType
from app.store import EvidenceStore


@pytest.fixture
def store():
    with EvidenceStore(":memory:") as s:
        yield s


def make_record(
    record_id: str = "r.1",
    *,
    record_type: RecordType = RecordType.OBSERVATION,
    source_id: str = "fred",
    source_type: SourceType = SourceType.MACRO_INDICATOR,
    subject: str = "US technology",
    period_start: date = date(2026, 7, 1),
    period_end: date = date(2026, 7, 31),
    geography: str = "United States",
    value: float | None = 61.7,
    unit: str | None = "index",
    excerpt: str | None = None,
    derived_from: tuple[str, ...] = (),
) -> EvidenceRecord:
    return EvidenceRecord(
        record_id=record_id,
        record_type=record_type,
        source_id=source_id,
        source_type=source_type,
        publisher="Publisher",
        access_method=AccessMethod.API,
        subject=subject,
        query_or_series_id="SERIES",
        geography=geography,
        period_start=period_start,
        period_end=period_end,
        retrieved_at=datetime(2026, 8, 23, 9, 0),
        rights_note="Attribution required.",
        retention_rule="Retain with the report.",
        limitation="Describes the economy, not this industry.",
        value=value,
        unit=unit,
        excerpt=excerpt,
        derived_from=derived_from,
    )


@pytest.fixture
def record_factory():
    return make_record
