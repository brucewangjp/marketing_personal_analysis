"""The confidence rubric, as executable rules.

Implements `docs/01_Product/00_Shared_Research_Foundation.md` section 6. Assigning
confidence by rule rather than by impression is what makes two runs of the same report
comparable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from .models import EvidenceRecord, RecordType, SourceType
from . import sources

HIGH = "High"
MEDIUM = "Medium"
LOW = "Low"
INSUFFICIENT = "Insufficient evidence"

_ORDER = {INSUFFICIENT: 0, LOW: 1, MEDIUM: 2, HIGH: 3}


@dataclass(frozen=True)
class Window:
    """The period and geography a report claims to cover."""

    period_start: date
    period_end: date
    geography: str

    def covers(self, record: EvidenceRecord) -> bool:
        """Whether a record falls inside what the report says it reports on."""
        return (
            record.geography == self.geography
            and record.period_start >= self.period_start
            and record.period_end <= self.period_end
        )

    def overlaps(self, record: EvidenceRecord) -> bool:
        return (
            record.geography == self.geography
            and record.period_start <= self.period_end
            and record.period_end >= self.period_start
        )


@dataclass(frozen=True)
class Assessment:
    level: str
    reason: str


def _cap(level: str, ceiling: str) -> str:
    return level if _ORDER[level] <= _ORDER[ceiling] else ceiling


def assess(
    evidence: list[EvidenceRecord],
    window: Window,
    *,
    conflicting: bool = False,
) -> Assessment:
    """Assign a confidence level to a claim supported by `evidence`.

    `conflicting` is set by the caller when listed sources disagree about the claim;
    the rubric cannot detect that from the records alone.
    """
    if not evidence:
        return Assessment(
            INSUFFICIENT, "No listed source covers this claim."
        )

    covering = [r for r in evidence if window.covers(r)]
    if not covering:
        return Assessment(
            INSUFFICIENT,
            "The available source's period or scope does not match the report window.",
        )

    if conflicting:
        return Assessment(LOW, "Listed sources conflict about this claim.")

    partial = [r for r in evidence if window.overlaps(r) and not window.covers(r)]
    documented = {
        r.source_id for r in covering if sources.get(r.source_id).methodology_documented
    }
    proxy_only = all(sources.get(r.source_id).proxy for r in covering)

    if len(documented) >= 2:
        if partial:
            # The rubric holds this at Medium: sources agree, but the window is not
            # fully covered, so the claim is not evidenced across the period it states.
            level = MEDIUM
            reason = (
                f"{len(documented)} independent sources agree, but at least one covers "
                "the report window only partially."
            )
        else:
            level = HIGH
            reason = (
                f"{len(documented)} independent sources with documented methodology "
                "cover the report period and geography."
            )
    elif len(documented) == 1:
        if partial:
            level = MEDIUM
            reason = (
                "One listed source with a documented methodology supports this, and "
                "part of its coverage falls outside the report window."
            )
        else:
            level = MEDIUM
            reason = (
                "One listed source with a documented methodology covers the report "
                "period and geography."
            )
    else:
        level = LOW
        reason = "No covering source publishes its methodology."

    if proxy_only:
        level = _cap(level, LOW)
        reason += " Support is limited to proxy signals, which measure attention rather than the claim itself."

    # -- the two caps from the rubric ------------------------------------
    if all(r.record_type is RecordType.INTERPRETATION for r in covering):
        level = _cap(level, LOW)
        reason += " Support rests only on interpretation, never on an observation."

    if all(
        r.source_type is SourceType.PUBLIC_DISCUSSION for r in covering
    ):
        level = _cap(level, MEDIUM)
        reason += (
            " Support rests only on public discussion, which is a self-selected sample."
        )

    return Assessment(level, reason)


def is_reportable(level: str) -> bool:
    """Whether a finding may be stated as a conclusion rather than as a gap."""
    return _ORDER[level] >= _ORDER[LOW]
