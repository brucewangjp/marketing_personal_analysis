"""End-to-end: the report contains every template section, populated or gated."""

from datetime import date

import pytest

from app.confidence import INSUFFICIENT
from app.reports import industry_sentiment as sentiment
from app.sample import all_records
from app.store import EvidenceStore

AS_OF = date(2026, 8, 22)


@pytest.fixture
def seeded():
    with EvidenceStore(":memory:") as store:
        store.add_all(all_records())
        yield store


def _request(subject="US technology", window="3m"):
    return sentiment.ReportRequest(
        subject=subject,
        window=window,
        research_question=sentiment.default_question(subject),
        as_of=AS_OF,
    )


def test_every_template_section_is_present(seeded):
    report = sentiment.build(seeded, _request())
    assert [s.section_id for s in report.sections] == [
        "summary",
        "attention",
        "macro",
        "group_attitude",
        "motivations",
        "change",
        "monitoring",
    ]


def test_header_states_period_geography_and_cadence(seeded):
    report = sentiment.build(seeded, _request())
    assert report.header.geography == "United States"
    assert report.header.cadence == "Weekly"
    assert report.header.period_end == AS_OF
    assert report.header.period_start == date(2026, 5, 24)


def test_header_lists_missing_sources(seeded):
    report = sentiment.build(seeded, _request())
    assert [s.source_id for s in report.header.sources_missing] == ["public_discussion"]


def test_sample_data_is_declared_in_the_header(seeded):
    assert sentiment.build(seeded, _request()).header.contains_sample_data is True


def test_attitude_and_motivation_sections_are_gated(seeded):
    report = sentiment.build(seeded, _request())
    assert report.section("group_attitude").is_gated
    assert report.section("motivations").is_gated
    assert [s.section_id for s in report.gated_sections] == [
        "group_attitude",
        "motivations",
    ]


def test_gated_sections_carry_no_fabricated_findings(seeded):
    report = sentiment.build(seeded, _request())
    assert report.section("group_attitude").findings == []
    assert report.section("motivations").findings == []


def test_tone_is_reported_as_a_gap_rather_than_inferred(seeded):
    report = sentiment.build(seeded, _request())
    tone = [f for f in report.section("summary").findings if "tone" in f.statement.lower()]
    assert len(tone) == 1
    assert tone[0].confidence == INSUFFICIENT


def test_attention_section_has_a_chart_and_a_finding(seeded):
    section = sentiment.build(seeded, _request()).section("attention")
    assert section.chart_svg.startswith("<svg")
    assert len(section.findings) == 1
    assert "rising" in section.findings[0].statement


def test_every_finding_with_evidence_carries_a_confidence_level(seeded):
    report = sentiment.build(seeded, _request())
    for section in report.sections:
        if section.section_id == "monitoring":
            continue  # monitoring items are instructions, not claims
        for finding in section.findings:
            assert finding.confidence, f"{section.section_id}: {finding.statement}"


def test_evidence_table_is_deduplicated(seeded):
    records = sentiment.build(seeded, _request()).all_evidence
    assert len(records) == len({r.record_id for r in records})


def test_latest_observation_is_reported(seeded):
    assert sentiment.build(seeded, _request()).latest_observation == AS_OF


def test_one_month_window_is_narrower_than_three_months(seeded):
    one = sentiment.build(seeded, _request(window="1m"))
    three = sentiment.build(seeded, _request(window="3m"))
    assert len(one.all_evidence) < len(three.all_evidence)
    assert one.header.period_start > three.header.period_start


def test_both_subjects_build(seeded):
    for subject in sentiment.SUBJECTS:
        report = sentiment.build(seeded, _request(subject=subject))
        assert report.header.subject == subject


def test_healthcare_attention_is_falling_in_the_sample(seeded):
    section = sentiment.build(seeded, _request("US healthcare")).section("attention")
    assert "falling" in section.findings[0].statement


def test_empty_store_produces_a_report_of_gaps_not_a_crash():
    with EvidenceStore(":memory:") as empty:
        report = sentiment.build(empty, _request())
    assert report.all_evidence == []
    assert report.header.sources_included == []
    for finding in report.section("summary").findings:
        assert finding.confidence == INSUFFICIENT
    assert report.section("attention").findings[0].confidence == INSUFFICIENT


def test_unknown_subject_is_rejected(seeded):
    with pytest.raises(ValueError, match="unknown subject"):
        sentiment.build(
            seeded,
            sentiment.ReportRequest("US energy", "1m", "why?", AS_OF),
        )


def test_unknown_window_is_rejected(seeded):
    with pytest.raises(ValueError, match="unknown window"):
        sentiment.build(
            seeded,
            sentiment.ReportRequest("US technology", "5y", "why?", AS_OF),
        )


def test_monitoring_items_are_not_labeled_as_observations(seeded):
    """They are instructions to the reader, and carry no evidence standard."""
    section = sentiment.build(seeded, _request()).section("monitoring")
    assert section.findings
    for item in section.findings:
        assert item.record_type is None
        assert item.is_claim is False
        assert item.confidence == ""


def test_monitoring_list_names_each_data_gap(seeded):
    section = sentiment.build(seeded, _request()).section("monitoring")
    gaps = [f.statement for f in section.findings if f.statement.startswith("Data gap")]
    assert len(gaps) == 2
    assert all("Public discussion" in g for g in gaps)
