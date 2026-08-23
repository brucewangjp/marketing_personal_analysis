"""A direction is only claimed when the move is larger than the series' own noise."""

from datetime import date, datetime, timedelta

import pytest

from app.analysis import (
    Direction,
    MIN_POINTS_FOR_DIRECTION,
    analyse_series,
    derived_metric,
)
from app.models import AccessMethod, EvidenceRecord, RecordType, SourceType


def series(values, start=date(2026, 5, 24), source_id="google_trends"):
    records = []
    for i, value in enumerate(values):
        week = start + timedelta(days=7 * i)
        records.append(
            EvidenceRecord(
                record_id=f"obs.{i}",
                record_type=RecordType.OBSERVATION,
                source_id=source_id,
                source_type=SourceType.SEARCH_INTEREST,
                publisher="Google",
                access_method=AccessMethod.WEB_COLLECTION,
                subject="US technology",
                query_or_series_id="q",
                geography="United States",
                period_start=week,
                period_end=week + timedelta(days=6),
                retrieved_at=datetime(2026, 8, 23),
                rights_note="r",
                retention_rule="k",
                limitation="l",
                value=float(value),
                unit="relative interest, 0-100",
            )
        )
    return records


RISING = [44, 46, 43, 48, 52, 51, 57, 60, 58, 64, 69, 72, 71]
FALLING = list(reversed(RISING))
NOISY_FLAT = [50, 58, 44, 61, 47, 55, 49, 60, 45, 57, 52, 48, 53]
TINY_DRIFT = [50, 50, 51, 50, 51, 52, 51, 52, 51, 52, 52, 53, 52]


def test_a_clear_rise_is_reported():
    analysis = analyse_series(series(RISING), "trends")
    assert analysis.direction is Direction.RISING
    assert "clearing both bars" in analysis.reason


def test_a_clear_fall_is_reported():
    assert analyse_series(series(FALLING), "trends").direction is Direction.FALLING


def test_noise_larger_than_the_move_is_not_a_direction():
    """The series swings 44 to 61 and ends where it started. That is not a trend."""
    analysis = analyse_series(series(NOISY_FLAT), "trends")
    assert analysis.direction is Direction.STABLE
    assert "inside its own week-to-week variation" in analysis.reason


def test_a_small_move_in_a_quiet_series_is_not_a_direction():
    analysis = analyse_series(series(TINY_DRIFT), "trends")
    assert analysis.direction is Direction.STABLE
    assert "10% of the opening level" in analysis.reason


def test_too_few_observations_is_indeterminate_not_stable():
    """Absence of evidence for a direction is not evidence of stability."""
    analysis = analyse_series(series([50, 60, 70]), "trends")
    assert analysis.direction is Direction.INDETERMINATE
    assert str(MIN_POINTS_FOR_DIRECTION) in analysis.reason


def test_a_single_observation_cannot_describe_change():
    analysis = analyse_series(series([50]), "trends")
    assert analysis.direction is Direction.INDETERMINATE
    assert "At least two" in analysis.reason


def test_an_empty_series_does_not_crash():
    analysis = analyse_series([], "trends")
    assert analysis.direction is Direction.INDETERMINATE
    assert analysis.count == 0
    assert analysis.peak is None


def test_records_without_values_are_ignored():
    records = series(RISING)
    text_only = EvidenceRecord(
        record_id="excerpt.1",
        record_type=RecordType.OBSERVATION,
        source_id="public_discussion",
        source_type=SourceType.PUBLIC_DISCUSSION,
        publisher="p",
        access_method=AccessMethod.API,
        subject="US technology",
        query_or_series_id="q",
        geography="United States",
        period_start=date(2026, 6, 1),
        period_end=date(2026, 6, 7),
        retrieved_at=datetime(2026, 8, 23),
        rights_note="r",
        retention_rule="k",
        limitation="l",
        excerpt="People are talking about it.",
    )
    assert analyse_series([*records, text_only], "trends").count == len(records)


def test_peak_and_trough_carry_their_dates():
    analysis = analyse_series(series(RISING), "trends")
    assert analysis.peak[1] == 72
    assert analysis.trough[1] == 43
    assert isinstance(analysis.peak[0], date)


def test_out_of_order_records_are_sorted_before_analysis():
    shuffled = list(reversed(series(RISING)))
    assert analyse_series(shuffled, "trends").direction is Direction.RISING


def test_an_unusual_jump_is_flagged():
    spiky = [50, 51, 50, 52, 51, 50, 95, 51, 50, 52, 51, 50, 51]
    notable = analyse_series(series(spiky), "trends").notable
    assert notable
    assert notable[0].change > 40


def test_a_smooth_series_flags_nothing():
    assert analyse_series(series(range(40, 66, 2)), "trends").notable == []


def test_percent_change_is_relative_to_the_opening_average():
    analysis = analyse_series(series(RISING), "trends")
    assert analysis.percent_change == pytest.approx(52.6, abs=1.0)


def test_a_derived_metric_names_every_observation_behind_it():
    analysis = analyse_series(series(RISING), "trends")
    metric = derived_metric(
        record_id="derived.change.1",
        analysis=analysis,
        subject="US technology",
        geography="United States",
        value=analysis.change,
        unit="change in relative interest",
        limitation="A change in relative interest.",
    )
    metric.validate()
    assert metric.record_type is RecordType.DERIVED_METRIC
    assert set(metric.derived_from) == {r.record_id for r in analysis.records}
    assert metric.period_start == analysis.records[0].period_start
    assert metric.period_end == analysis.records[-1].period_end


def test_a_derived_metric_inherits_the_sample_flag():
    records = series(RISING)
    sampled = [
        EvidenceRecord(**{**r.__dict__, "is_sample": True}) for r in records
    ]
    analysis = analyse_series(sampled, "trends")
    metric = derived_metric(
        record_id="derived.change.2",
        analysis=analysis,
        subject="US technology",
        geography="United States",
        value=1.0,
        unit="u",
        limitation="l",
    )
    assert metric.is_sample is True


def test_a_derived_metric_needs_evidence_behind_it():
    with pytest.raises(ValueError, match="at least one observation"):
        derived_metric(
            record_id="derived.empty",
            analysis=analyse_series([], "trends"),
            subject="US technology",
            geography="United States",
            value=0.0,
            unit="u",
            limitation="l",
        )


def test_direction_has_a_past_tense_for_narrative_sentences():
    assert Direction.RISING.past_tense == "rose"
    assert Direction.FALLING.past_tense == "fell"
    assert Direction.STABLE.past_tense == "held steady"
