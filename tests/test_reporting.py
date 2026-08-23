"""Gating: a section without its source says so, and is never filled from elsewhere."""

from datetime import date

from app.confidence import INSUFFICIENT, Window
from app.models import RecordType
from app.reporting import Section, build_finding
from tests.conftest import make_record

WINDOW = Window(date(2026, 6, 1), date(2026, 8, 31), "United States")


def test_section_without_a_source_requirement_is_never_gated():
    assert Section("summary", "Executive summary").is_gated is False


def test_section_is_gated_when_its_only_source_is_unconnected():
    section = Section("attitude", "Group attitude", requires=("public_discussion",))
    assert section.is_gated is True


def test_section_is_open_when_its_source_is_connected():
    assert Section("attention", "Attention", requires=("google_trends",)).is_gated is False


def test_section_is_open_when_any_required_source_is_connected():
    section = Section("mixed", "Mixed", requires=("public_discussion", "fred"))
    assert section.is_gated is False


def test_gate_message_names_the_source_and_what_it_would_add():
    section = Section("attitude", "Group attitude", requires=("public_discussion",))
    message = section.gate_message
    assert "Insufficient evidence" in message
    assert "Public discussion" in message
    assert "motivations and concerns" in message


def test_build_finding_assigns_confidence_from_the_rubric():
    finding = build_finding(
        "Attention is rising.",
        RecordType.DERIVED_METRIC,
        [make_record("fred.1")],
        WINDOW,
    )
    assert finding.confidence == "Medium"
    assert finding.confidence_reason


def test_finding_without_evidence_is_insufficient_not_silently_dropped():
    finding = build_finding("Tone cannot be assessed.", RecordType.OBSERVATION, [], WINDOW)
    assert finding.confidence == INSUFFICIENT


def test_findings_split_into_reportable_and_gaps():
    section = Section("summary", "Executive summary")
    section.findings = [
        build_finding("Supported.", RecordType.OBSERVATION, [make_record("fred.1")], WINDOW),
        build_finding("Unsupported.", RecordType.OBSERVATION, [], WINDOW),
    ]
    assert len(section.reportable_findings) == 1
    assert len(section.gap_findings) == 1
