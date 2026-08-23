"""The evidence schema is the enforcement point for evidence-versus-interpretation."""

from datetime import date

import pytest

from app.models import InvalidRecord, RecordType
from tests.conftest import make_record


def test_observation_is_valid():
    assert make_record().record_type is RecordType.OBSERVATION


def test_interpretation_without_derived_from_is_rejected():
    with pytest.raises(InvalidRecord, match="empty derived_from is invalid"):
        make_record(record_type=RecordType.INTERPRETATION)


def test_derived_metric_without_derived_from_is_rejected():
    with pytest.raises(InvalidRecord, match="must name the records"):
        make_record(record_type=RecordType.DERIVED_METRIC)


def test_interpretation_with_derived_from_is_valid():
    record = make_record(
        record_type=RecordType.INTERPRETATION, derived_from=("r.0",)
    )
    assert record.derived_from == ("r.0",)


def test_observation_may_not_derive_from_anything():
    with pytest.raises(InvalidRecord, match="stored verbatim"):
        make_record(derived_from=("r.0",))


def test_record_cannot_derive_from_itself():
    with pytest.raises(InvalidRecord, match="cannot derive from itself"):
        make_record(
            "r.1", record_type=RecordType.INTERPRETATION, derived_from=("r.1",)
        )


def test_numeric_value_requires_a_unit():
    with pytest.raises(InvalidRecord, match="unit is required"):
        make_record(value=1.0, unit=None)


def test_record_needs_a_value_or_an_excerpt():
    with pytest.raises(InvalidRecord, match="either a value or an excerpt"):
        make_record(value=None, unit=None, excerpt="   ")


def test_excerpt_only_record_is_valid():
    record = make_record(value=None, unit=None, excerpt="People mention battery life.")
    assert record.display_value == "People mention battery life."


def test_blank_required_field_is_rejected():
    with pytest.raises(InvalidRecord, match="limitation is required"):
        make_record().__class__(
            **{**make_record().__dict__, "limitation": "  "}
        )


def test_period_order_is_enforced():
    with pytest.raises(InvalidRecord, match="period_start must not be after"):
        make_record(period_start=date(2026, 8, 1), period_end=date(2026, 7, 1))


def test_display_value_always_carries_its_unit():
    assert make_record(value=3.5, unit="percent").display_value == "3.5 percent"
