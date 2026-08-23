"""Report assembly and the gating rule.

Implements `docs/01_Product/00_Shared_Research_Foundation.md` sections 7 to 9. A section
whose source is not connected is never omitted and never filled from a source that does
not support it — it renders as insufficient evidence naming what is missing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from .confidence import INSUFFICIENT, Assessment, Window, assess
from .models import EvidenceRecord, Finding, RecordType
from . import sources


@dataclass
class Section:
    section_id: str
    title: str
    requires: tuple[str, ...] = ()
    """Source ids this section's findings can come from. Empty means no source gate."""
    findings: list[Finding] = field(default_factory=list)
    note: str = ""
    chart_svg: str = ""

    @property
    def missing_sources(self) -> list[sources.Source]:
        return [
            sources.get(sid) for sid in self.requires if not sources.is_connected(sid)
        ]

    @property
    def is_gated(self) -> bool:
        """True when no source that could populate this section is connected."""
        if not self.requires:
            return False
        return not any(sources.is_connected(sid) for sid in self.requires)

    @property
    def gate_message(self) -> str:
        missing = self.missing_sources
        if not missing:
            return ""
        names = ", ".join(s.name for s in missing)
        provides = "; ".join(s.provides for s in missing)
        return (
            f"Insufficient evidence. This section needs {names}, which is not connected. "
            f"It would provide {provides}."
        )

    @property
    def reportable_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.confidence != INSUFFICIENT]

    @property
    def gap_findings(self) -> list[Finding]:
        return [f for f in self.findings if f.confidence == INSUFFICIENT]


@dataclass
class ReportHeader:
    """The shared report header, section 7. Templates add values, never remove fields."""

    subject: str
    research_question: str
    geography: str
    period_start: date
    period_end: date
    cadence: str
    generated_at: datetime
    window_label: str
    sources_included: list[sources.Source] = field(default_factory=list)
    sources_missing: list[sources.Source] = field(default_factory=list)
    limitation: str = ""
    contains_sample_data: bool = False

    @property
    def period_label(self) -> str:
        return f"{self.period_start.isoformat()} to {self.period_end.isoformat()}"


@dataclass
class Report:
    header: ReportHeader
    sections: list[Section]

    def section(self, section_id: str) -> Section:
        for s in self.sections:
            if s.section_id == section_id:
                return s
        raise KeyError(section_id)

    @property
    def all_evidence(self) -> list[EvidenceRecord]:
        """Every record any finding rests on, de-duplicated, for the evidence table."""
        seen: dict[str, EvidenceRecord] = {}
        for section in self.sections:
            for finding in section.findings:
                for record in finding.evidence:
                    seen.setdefault(record.record_id, record)
        return sorted(seen.values(), key=lambda r: (r.source_id, r.period_start))

    @property
    def gated_sections(self) -> list[Section]:
        return [s for s in self.sections if s.is_gated]

    @property
    def latest_observation(self) -> date | None:
        """The freshest period any evidence covers.

        Shown so a lagging source cannot imply it is current to the report date.
        """
        records = self.all_evidence
        return max((r.period_end for r in records), default=None)


def build_finding(
    statement: str,
    record_type: RecordType,
    evidence: list[EvidenceRecord],
    window: Window,
    *,
    conflicting: bool = False,
    limitation: str = "",
) -> Finding:
    """Create a finding with its confidence assigned by the rubric, never by hand."""
    result: Assessment = assess(evidence, window, conflicting=conflicting)
    if not limitation:
        limitations = {sources.get(r.source_id).default_limitation for r in evidence}
        limitation = " ".join(sorted(limitations))
    return Finding(
        statement=statement,
        record_type=record_type,
        evidence=evidence,
        confidence=result.level,
        confidence_reason=result.reason,
        limitation=limitation,
    )
