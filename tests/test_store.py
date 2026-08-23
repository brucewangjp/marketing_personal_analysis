"""The store rejects what the schema forbids, and resolves what reports need."""

from datetime import date

import pytest

from app.models import InvalidRecord, RecordType
from tests.conftest import make_record


def test_round_trip(store):
    record = make_record("obs.1")
    store.add(record)
    assert store.get("obs.1") == record


def test_dangling_derived_from_is_rejected(store):
    with pytest.raises(InvalidRecord, match="not stored"):
        store.add(
            make_record(
                "int.1",
                record_type=RecordType.INTERPRETATION,
                derived_from=("missing.1",),
            )
        )


def test_derived_from_resolves_once_the_base_record_exists(store):
    store.add(make_record("obs.1"))
    store.add(
        make_record(
            "int.1", record_type=RecordType.INTERPRETATION, derived_from=("obs.1",)
        )
    )
    assert store.count() == 2


def test_unregistered_source_is_rejected(store):
    with pytest.raises(KeyError, match="unknown source"):
        store.add(make_record("obs.1", source_id="mystery_blog"))


def test_query_returns_overlapping_records_not_only_contained_ones(store):
    # A monthly indicator must still surface in a window whose edges cut across it.
    store.add(
        make_record("obs.1", period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))
    )
    found = store.query(
        subject="US technology",
        period_start=date(2026, 7, 15),
        period_end=date(2026, 8, 15),
    )
    assert [r.record_id for r in found] == ["obs.1"]


def test_query_excludes_records_outside_the_window(store):
    store.add(
        make_record("old.1", period_start=date(2026, 1, 1), period_end=date(2026, 1, 31))
    )
    found = store.query(
        subject="US technology",
        period_start=date(2026, 7, 1),
        period_end=date(2026, 7, 31),
    )
    assert found == []


def test_query_filters_by_subject(store):
    store.add(make_record("tech.1", subject="US technology"))
    store.add(make_record("health.1", subject="US healthcare"))
    assert [r.record_id for r in store.query(subject="US healthcare")] == ["health.1"]
