"""The rubric must be applied by rule, so two runs of a report are comparable."""

from datetime import date

from app.confidence import HIGH, INSUFFICIENT, LOW, MEDIUM, Window, assess
from app.models import RecordType, SourceType
from tests.conftest import make_record

WINDOW = Window(date(2026, 6, 1), date(2026, 8, 31), "United States")


def _fred(record_id="fred.1", **kw):
    return make_record(record_id, source_id="fred", source_type=SourceType.MACRO_INDICATOR, **kw)


def _trends(record_id="tr.1", **kw):
    return make_record(
        record_id, source_id="google_trends", source_type=SourceType.SEARCH_INTEREST, **kw
    )


def test_no_evidence_is_insufficient():
    assert assess([], WINDOW).level == INSUFFICIENT


def test_evidence_outside_the_window_is_insufficient():
    outside = _fred(period_start=date(2025, 1, 1), period_end=date(2025, 1, 31))
    assert assess([outside], WINDOW).level == INSUFFICIENT


def test_evidence_from_another_geography_is_insufficient():
    elsewhere = _fred(geography="Japan")
    assert assess([elsewhere], WINDOW).level == INSUFFICIENT


def test_one_documented_source_is_medium():
    assert assess([_fred()], WINDOW).level == MEDIUM


def test_two_independent_documented_sources_are_high():
    assert assess([_fred(), _trends()], WINDOW).level == HIGH


def test_conflicting_sources_drop_to_low():
    result = assess([_fred(), _trends()], WINDOW, conflicting=True)
    assert result.level == LOW
    assert "conflict" in result.reason


def test_proxy_only_support_is_capped_at_low():
    # Google Trends is registered as a proxy: it measures attention, not the claim.
    result = assess([_trends()], WINDOW)
    assert result.level == LOW
    assert "proxy" in result.reason


def test_interpretation_only_support_is_capped_at_low():
    interpretation = _fred(
        "int.1", record_type=RecordType.INTERPRETATION, derived_from=("fred.1",)
    )
    result = assess([interpretation], WINDOW)
    assert result.level == LOW
    assert "only on interpretation" in result.reason


def test_unselected_public_discussion_source_is_low():
    """No platform is chosen yet, so its methodology is undocumented and it caps at Low."""
    discussion = make_record(
        "pd.1",
        source_id="public_discussion",
        source_type=SourceType.PUBLIC_DISCUSSION,
        value=None,
        unit=None,
        excerpt="People say setup is confusing.",
    )
    assert assess([discussion], WINDOW).level == LOW


def test_public_discussion_alone_cannot_exceed_medium(monkeypatch):
    """The cap binds once a platform is chosen and its methodology is documented.

    Two independent documented sources would otherwise be High; because both are public
    discussion — a self-selected sample — the rubric holds them to Medium.
    """
    from dataclasses import replace

    from app import sources

    chosen = replace(
        sources.REGISTRY["public_discussion"],
        methodology_documented=True,
        connected=True,
    )
    second = replace(chosen, source_id="public_discussion_2", name="Second platform")
    monkeypatch.setitem(sources.REGISTRY, "public_discussion", chosen)
    monkeypatch.setitem(sources.REGISTRY, "public_discussion_2", second)

    records = [
        make_record(
            f"pd.{i}",
            source_id=source_id,
            source_type=SourceType.PUBLIC_DISCUSSION,
            value=None,
            unit=None,
            excerpt="A recurring complaint about setup.",
        )
        for i, source_id in enumerate(("public_discussion", "public_discussion_2"))
    ]
    result = assess(records, WINDOW)
    assert result.level == MEDIUM
    assert "self-selected sample" in result.reason


def test_partial_coverage_demotes_two_sources_from_high_to_medium():
    """The rubric does not award High for a window the evidence only partly covers."""
    straggler = _fred(
        "fred.partial", period_start=date(2026, 5, 1), period_end=date(2026, 6, 15)
    )
    result = assess([_fred(), _trends(), straggler], WINDOW)
    assert result.level == MEDIUM
    assert "only partially" in result.reason


def test_single_source_reason_does_not_claim_sources_agree():
    """One source cannot agree with anything; the reason must say what actually held."""
    partial = _fred("fred.partial", period_start=date(2026, 5, 1), period_end=date(2026, 6, 15))
    result = assess([_fred(), partial], WINDOW)
    assert result.level == MEDIUM
    assert "One listed source" in result.reason
    assert "agree" not in result.reason


def test_full_coverage_by_two_sources_is_still_high():
    """Demotion applies to partial coverage only, not to every multi-source claim."""
    assert assess([_fred(), _trends()], WINDOW).level == HIGH


def test_every_level_carries_a_reason():
    for evidence in ([], [_fred()], [_fred(), _trends()]):
        assert assess(evidence, WINDOW).reason
