"""Analysis: turn collected observations into findings that the evidence supports.

Two rules shape everything here.

**A direction is only claimed when the move is larger than the series' own noise.** A
weekly attention series wanders. Calling every wander a trend would produce a report that
says something different each week while nothing has actually changed, which is worse than
saying "stable" — the reader would learn to distrust it, or worse, act on it.

**Every number the report states is a derived metric that names the observations it came
from.** The schema already requires that; this module is where it is honoured, so a reader
can go from "attention rose 27 points" to the exact rows that produced it.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import date
from enum import Enum

from .models import AccessMethod, EvidenceRecord, RecordType, SourceType
from . import sources

# A move must clear both bars to count as a direction: a tenth of the baseline, and one
# standard deviation of the series itself. The first stops trivial moves in a quiet
# series; the second stops ordinary wander in a noisy one.
RELATIVE_THRESHOLD = 0.10
MIN_POINTS_FOR_DIRECTION = 4
# Week-over-week moves this many standard deviations from the mean move are called out.
NOTABLE_Z = 2.0


class Direction(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    INDETERMINATE = "indeterminate"

    @property
    def past_tense(self) -> str:
        """For sentences describing what the window already did."""
        return {
            Direction.RISING: "rose",
            Direction.FALLING: "fell",
            Direction.STABLE: "held steady",
            Direction.INDETERMINATE: "moved indeterminately",
        }[self]


@dataclass(frozen=True)
class Move:
    """One period-over-period change, with how unusual it was for this series."""

    at: date
    change: float
    z_score: float


@dataclass(frozen=True)
class SeriesAnalysis:
    series_id: str
    records: list[EvidenceRecord]
    direction: Direction
    reason: str
    first: float
    last: float
    change: float
    baseline: float
    recent: float
    volatility: float
    peak: tuple[date, float] | None
    trough: tuple[date, float] | None
    notable: list[Move]

    @property
    def count(self) -> int:
        return len(self.records)

    @property
    def span(self) -> tuple[date, date] | None:
        if not self.records:
            return None
        return self.records[0].period_start, self.records[-1].period_end

    @property
    def is_directional(self) -> bool:
        return self.direction in (Direction.RISING, Direction.FALLING)

    @property
    def percent_change(self) -> float | None:
        if not self.baseline:
            return None
        return (self.recent - self.baseline) / abs(self.baseline) * 100


def analyse_series(records: list[EvidenceRecord], series_id: str) -> SeriesAnalysis:
    """Describe a single series, claiming a direction only when the move clears the noise."""
    usable = sorted(
        (r for r in records if r.value is not None), key=lambda r: r.period_start
    )
    values = [r.value for r in usable]

    if len(usable) < 2:
        return SeriesAnalysis(
            series_id=series_id,
            records=usable,
            direction=Direction.INDETERMINATE,
            reason=(
                f"{len(usable)} observation(s) in this window. At least two are needed "
                "to describe a change at all."
            ),
            first=values[0] if values else 0.0,
            last=values[-1] if values else 0.0,
            change=0.0,
            baseline=values[0] if values else 0.0,
            recent=values[-1] if values else 0.0,
            volatility=0.0,
            peak=None,
            trough=None,
            notable=[],
        )

    third = max(1, len(usable) // 3)
    baseline = statistics.fmean(values[:third])
    recent = statistics.fmean(values[-third:])
    change = recent - baseline
    volatility = statistics.stdev(values) if len(values) > 1 else 0.0

    peak_record = max(usable, key=lambda r: r.value)
    trough_record = min(usable, key=lambda r: r.value)

    direction, reason = _direction(
        len(usable), baseline, recent, change, volatility, third
    )

    return SeriesAnalysis(
        series_id=series_id,
        records=usable,
        direction=direction,
        reason=reason,
        first=values[0],
        last=values[-1],
        change=change,
        baseline=baseline,
        recent=recent,
        volatility=volatility,
        peak=(peak_record.period_end, peak_record.value),
        trough=(trough_record.period_end, trough_record.value),
        notable=_notable_moves(usable),
    )


def _direction(
    count: int,
    baseline: float,
    recent: float,
    change: float,
    volatility: float,
    third: int,
) -> tuple[Direction, str]:
    if count < MIN_POINTS_FOR_DIRECTION:
        return (
            Direction.INDETERMINATE,
            f"{count} observations is too few to separate a direction from noise; "
            f"{MIN_POINTS_FOR_DIRECTION} are needed.",
        )

    relative_bar = abs(baseline) * RELATIVE_THRESHOLD
    bar = max(relative_bar, volatility)
    word = "rose" if change > 0 else "fell"

    if abs(change) < bar:
        limit = "its own week-to-week variation" if volatility > relative_bar else (
            f"{RELATIVE_THRESHOLD:.0%} of the opening level"
        )
        return (
            Direction.STABLE,
            f"The average {word} {abs(change):.1f} between the first and last {third} "
            f"observation(s), which is inside {limit} ({bar:.1f}). A move smaller than "
            "the noise is not a direction.",
        )

    return (
        Direction.RISING if change > 0 else Direction.FALLING,
        f"The average {word} {abs(change):.1f} between the first and last {third} "
        f"observation(s), clearing both bars: {RELATIVE_THRESHOLD:.0%} of the opening "
        f"level ({relative_bar:.1f}) and the series' own variation ({volatility:.1f}).",
    )


def _notable_moves(records: list[EvidenceRecord]) -> list[Move]:
    """Period-over-period jumps that stand out against this series' usual movement."""
    if len(records) < 4:
        return []
    deltas = [
        (records[i].period_end, records[i].value - records[i - 1].value)
        for i in range(1, len(records))
    ]
    magnitudes = [abs(d) for _, d in deltas]
    mean = statistics.fmean(magnitudes)
    spread = statistics.stdev(magnitudes) if len(magnitudes) > 1 else 0.0
    if not spread:
        return []
    moves = [
        Move(at=at, change=delta, z_score=(abs(delta) - mean) / spread)
        for at, delta in deltas
    ]
    return sorted(
        (m for m in moves if m.z_score >= NOTABLE_Z),
        key=lambda m: m.z_score,
        reverse=True,
    )


# -- derived metric records ---------------------------------------------


def derived_metric(
    *,
    record_id: str,
    analysis: SeriesAnalysis,
    subject: str,
    geography: str,
    value: float,
    unit: str,
    limitation: str,
    query_or_series_id: str | None = None,
) -> EvidenceRecord:
    """A computed value that names the observations it rests on.

    Built from the analysed records, so `derived_from` can never drift out of step with
    what was actually measured.
    """
    if not analysis.records:
        raise ValueError("a derived metric needs at least one observation behind it")
    source = sources.get(analysis.records[0].source_id)
    return EvidenceRecord(
        record_id=record_id,
        record_type=RecordType.DERIVED_METRIC,
        source_id=source.source_id,
        source_type=analysis.records[0].source_type,
        publisher=source.publisher,
        access_method=analysis.records[0].access_method,
        subject=subject,
        query_or_series_id=query_or_series_id or analysis.series_id,
        geography=geography,
        period_start=analysis.records[0].period_start,
        period_end=analysis.records[-1].period_end,
        retrieved_at=max(r.retrieved_at for r in analysis.records),
        value=round(value, 2),
        unit=unit,
        rights_note=source.rights_note,
        retention_rule=source.retention_rule,
        limitation=limitation,
        derived_from=tuple(r.record_id for r in analysis.records),
        is_sample=any(r.is_sample for r in analysis.records),
    )
