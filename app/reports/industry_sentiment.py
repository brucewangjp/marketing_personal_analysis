"""The Industry Sentiment report.

Builds every section of `docs/05_Design/01_Industry_Sentiment_Report_Template.md` from
stored evidence, via `app.analysis`. Sections 6 and 7 are gated on the public-discussion
source: while it is not connected they render as insufficient evidence, because attention
and macro data measure the environment, not what people think or why.

Building a report never writes to the store. The derived metrics it states are computed
here and attached to their findings, so the same stored evidence always produces the same
report.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .. import charts, sources
from ..analysis import Direction, SeriesAnalysis, analyse_series, derived_metric
from ..confidence import Window
from ..models import EvidenceRecord, Finding, RecordType, SourceType
from ..reporting import Report, ReportHeader, Section, build_finding
from ..store import EvidenceStore

SUBJECTS = ("US technology", "US healthcare")

WINDOWS: dict[str, tuple[str, int]] = {
    "1m": ("most recent one month", 30),
    "3m": ("most recent three months", 90),
}

CADENCE = "Weekly"
TREND_UNIT = "relative interest, 0-100"


@dataclass(frozen=True)
class ReportRequest:
    subject: str
    window: str
    research_question: str
    as_of: date

    @property
    def window_label(self) -> str:
        return WINDOWS[self.window][0]

    @property
    def subject_slug(self) -> str:
        return self.subject.lower().replace(" ", "_")

    @property
    def period_start(self) -> date:
        return self.as_of - timedelta(days=WINDOWS[self.window][1])

    @property
    def period_end(self) -> date:
        return self.as_of


def default_question(subject: str) -> str:
    return (
        f"Is attention toward {subject} rising or falling, and what does the evidence "
        "not show?"
    )


def build(store: EvidenceStore, request: ReportRequest) -> Report:
    if request.subject not in SUBJECTS:
        raise ValueError(f"unknown subject {request.subject!r}")
    if request.window not in WINDOWS:
        raise ValueError(f"unknown window {request.window!r}")

    window = Window(request.period_start, request.period_end, "United States")
    records = store.query(
        subject=request.subject,
        period_start=request.period_start,
        period_end=request.period_end,
    )
    trends = [r for r in records if r.source_type is SourceType.SEARCH_INTEREST]
    macro = [r for r in records if r.source_type is SourceType.MACRO_INDICATOR]

    attention = analyse_series(trends, "search interest")
    macro_analyses = _analyse_macro(macro)

    attention_section = _attention_section(attention, request, window)
    macro_section = _macro_section(macro_analyses, request, window)
    attitude = Section("group_attitude", "Group attitude", requires=("public_discussion",))
    motivations = Section(
        "motivations", "Motivations and concerns", requires=("public_discussion",)
    )
    change = _change_section(attention, request, window)
    summary = _summary_section(attention, macro_analyses, request, window)
    monitoring = _monitoring_section(
        attention, macro_analyses, request, [attitude, motivations]
    )

    header = ReportHeader(
        subject=request.subject,
        research_question=request.research_question,
        geography="United States",
        period_start=request.period_start,
        period_end=request.period_end,
        cadence=CADENCE,
        generated_at=datetime.now(),
        window_label=request.window_label,
        sources_included=sorted(
            {sources.get(r.source_id) for r in records}, key=lambda s: s.name
        ),
        sources_missing=sources.unconnected_sources(),
        limitation=(
            "This report describes attention and macroeconomic context for an industry. "
            "It does not measure what any individual thinks, and it is not investment "
            "advice."
        ),
        contains_sample_data=any(r.is_sample for r in records),
    )

    return Report(
        header=header,
        sections=[
            summary,
            attention_section,
            macro_section,
            attitude,
            motivations,
            change,
            monitoring,
        ],
    )


# -- analysis helpers ----------------------------------------------------


def _analyse_macro(macro: list[EvidenceRecord]) -> list[SeriesAnalysis]:
    by_series: dict[str, list[EvidenceRecord]] = {}
    for record in macro:
        by_series.setdefault(record.query_or_series_id, []).append(record)
    return [analyse_series(rs, sid) for sid, rs in sorted(by_series.items())]


def _direction_evidence(
    analysis: SeriesAnalysis, request: ReportRequest, unit: str, limitation: str
) -> list[EvidenceRecord]:
    """The change metric plus the observations behind it."""
    if analysis.count < 2:
        return list(analysis.records)
    metric = derived_metric(
        record_id=(
            f"derived.change.{analysis.series_id.lower().replace(' ', '_')}"
            f".{request.subject_slug}"
            f".{request.period_start.isoformat()}"
        ),
        analysis=analysis,
        subject=request.subject,
        geography="United States",
        value=analysis.change,
        unit=f"change in {unit}",
        limitation=limitation,
    )
    return [metric, *analysis.records]


# -- sections ------------------------------------------------------------


def _attention_section(
    analysis: SeriesAnalysis, request: ReportRequest, window: Window
) -> Section:
    section = Section("attention", "Attention trend", requires=("google_trends",))
    section.note = (
        "Search interest measures relative attention within this query and period. "
        "It is not a count of people, their sentiment, or a decision to buy."
    )

    if not analysis.records:
        section.findings.append(
            build_finding(
                "No search-interest series covers this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )
        return section

    section.chart_svg = charts.line_chart(
        [(r.period_end, r.value) for r in analysis.records],
        label="Search interest",
        unit=TREND_UNIT,
    )

    limitation = (
        "A change in relative interest, not in the number of people searching. "
        "Computed from the observations listed with it."
    )
    evidence = _direction_evidence(analysis, request, TREND_UNIT, limitation)

    if analysis.direction is Direction.INDETERMINATE:
        section.findings.append(
            build_finding(
                f"The direction of attention cannot be established. {analysis.reason}",
                RecordType.OBSERVATION,
                analysis.records,
                window,
                limitation=limitation,
            )
        )
    else:
        percent = analysis.percent_change
        movement = f" ({percent:+.0f}%)" if percent is not None else ""
        section.findings.append(
            build_finding(
                f"Attention is {analysis.direction.value}: the window opens averaging "
                f"{analysis.baseline:.1f} and closes averaging {analysis.recent:.1f}"
                f"{movement}. {analysis.reason}",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )

    if analysis.peak and analysis.trough:
        section.findings.append(
            build_finding(
                f"The series ranges from {analysis.trough[1]:g} in the period ending "
                f"{analysis.trough[0].isoformat()} to {analysis.peak[1]:g} in the period "
                f"ending {analysis.peak[0].isoformat()}, with a week-to-week variation of "
                f"{analysis.volatility:.1f}.",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )
    return section


def _macro_section(
    analyses: list[SeriesAnalysis], request: ReportRequest, window: Window
) -> Section:
    section = Section("macro", "Macro and aggregate sentiment context", requires=("fred",))
    section.note = (
        "A macroeconomic correlation does not prove why people feel or act a certain way."
    )

    if not analyses:
        section.findings.append(
            build_finding(
                "No macroeconomic indicator covers this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )
        return section

    for analysis in analyses:
        latest = analysis.records[-1]
        statement = (
            f"{analysis.series_id} stands at {latest.display_value} for "
            f"{latest.period_label}."
        )
        record_type = RecordType.OBSERVATION
        evidence: list[EvidenceRecord] = list(analysis.records)
        limitation = latest.limitation

        if analysis.is_directional:
            statement += (
                f" It is {analysis.direction.value} across the window, from "
                f"{analysis.first:g} to {analysis.last:g}."
            )
            record_type = RecordType.DERIVED_METRIC
            evidence = _direction_evidence(
                analysis, request, latest.unit or "", limitation
            )
        elif analysis.direction is Direction.STABLE:
            statement += " It is broadly unchanged across the window."

        lag = (request.period_end - latest.period_end).days
        if lag > 7:
            statement += (
                f" Its latest observation is {lag} days before this report's end date."
            )

        section.findings.append(
            build_finding(statement, record_type, evidence, window, limitation=limitation)
        )
    return section


def _change_section(
    analysis: SeriesAnalysis, request: ReportRequest, window: Window
) -> Section:
    section = Section("change", "Change over time", requires=("google_trends",))
    section.note = (
        "A change in attention is not a change in tone. Whether sentiment moved with it "
        "cannot be established from this evidence."
    )

    if analysis.count < 2:
        section.findings.append(
            build_finding(
                "Not enough observations to describe change over this window.",
                RecordType.OBSERVATION,
                analysis.records,
                window,
            )
        )
        return section

    limitation = "A movement in relative interest, not in how many people searched."
    evidence = _direction_evidence(analysis, request, TREND_UNIT, limitation)

    if analysis.is_directional:
        section.findings.append(
            build_finding(
                f"Attention {analysis.direction.past_tense} over the window, a move of "
                f"{abs(analysis.change):.1f} against a week-to-week variation of "
                f"{analysis.volatility:.1f}. This is the change the evidence supports.",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )
    else:
        section.findings.append(
            build_finding(
                f"No change in attention is supported by this window. {analysis.reason}",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )

    for move in analysis.notable[:3]:
        section.findings.append(
            build_finding(
                f"An unusual move in the period ending {move.at.isoformat()}: "
                f"{move.change:+.1f}, about {move.z_score:.1f} standard deviations beyond "
                "this series' usual week-to-week movement. What caused it is not "
                "established by this evidence.",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )

    if not analysis.notable:
        section.findings.append(
            build_finding(
                "No single period moved unusually far against this series' own "
                "variation.",
                RecordType.DERIVED_METRIC,
                evidence,
                window,
                limitation=limitation,
            )
        )
    return section


def _summary_section(
    attention: SeriesAnalysis,
    macro: list[SeriesAnalysis],
    request: ReportRequest,
    window: Window,
) -> Section:
    section = Section("summary", "Executive summary")

    if not attention.records:
        section.findings.append(
            build_finding(
                "Overall attention cannot be assessed: no search-interest series covers "
                "this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )
    elif attention.direction is Direction.INDETERMINATE:
        section.findings.append(
            build_finding(
                f"Overall attention cannot be assessed. {attention.reason}",
                RecordType.OBSERVATION,
                attention.records,
                window,
            )
        )
    else:
        limitation = "A change in relative interest, not in the number of people."
        section.findings.append(
            build_finding(
                f"Overall attention is {attention.direction.value}.",
                RecordType.DERIVED_METRIC,
                _direction_evidence(attention, request, TREND_UNIT, limitation),
                window,
                limitation=limitation,
            )
        )

    # Tone is deliberately not inferred. Stating it as a gap is the correct output while
    # the only source that could support it is unconnected.
    section.findings.append(
        build_finding(
            "Overall group tone cannot be assessed. Attention and macroeconomic "
            "indicators measure the environment, not what people think.",
            RecordType.OBSERVATION,
            [],
            window,
        )
    )

    moving = [a for a in macro if a.is_directional]
    if moving:
        described = ", ".join(f"{a.series_id} {a.direction.value}" for a in moving)
        section.findings.append(
            build_finding(
                f"In the broader environment, {described}.",
                RecordType.DERIVED_METRIC,
                [r for a in moving for r in a.records],
                window,
                limitation=(
                    "Macroeconomic indicators describe the US economy, not this industry."
                ),
            )
        )
    elif macro:
        section.findings.append(
            build_finding(
                f"The broader environment is unchanged across the window, on "
                f"{len(macro)} indicator(s).",
                RecordType.DERIVED_METRIC,
                [r for a in macro for r in a.records],
                window,
                limitation=(
                    "Macroeconomic indicators describe the US economy, not this industry."
                ),
            )
        )
    return section


def _monitoring_section(
    attention: SeriesAnalysis,
    macro: list[SeriesAnalysis],
    request: ReportRequest,
    gated: list[Section],
) -> Section:
    """Built from what actually moved and what is actually missing."""
    section = Section("monitoring", "Monitoring list")
    section.note = "Carried into the next weekly run."
    items: list[str] = []

    if attention.is_directional:
        items.append(
            f'Whether search interest for "{request.subject}" is still '
            f"{attention.direction.value} next week, or the move of "
            f"{abs(attention.change):.1f} reverses."
        )
    elif attention.direction is Direction.STABLE:
        items.append(
            f'Whether search interest for "{request.subject}" breaks out of its current '
            f"range of {attention.trough[1]:g} to {attention.peak[1]:g}."
            if attention.peak and attention.trough
            else f'Search interest for "{request.subject}".'
        )
    elif attention.records:
        items.append(
            f'Search interest for "{request.subject}" — the window holds only '
            f"{attention.count} observation(s), too few to read a direction."
        )
    else:
        items.append(
            f'Search interest for "{request.subject}" — no series was collected for this '
            "window."
        )

    for move in attention.notable[:2]:
        items.append(
            f"Whether the unusual move in the period ending {move.at.isoformat()} "
            f"({move.change:+.1f}) was a one-off or the start of a shift."
        )

    for analysis in macro:
        if analysis.is_directional:
            items.append(
                f"{analysis.series_id}, {analysis.direction.value} across this window, "
                "at its next release."
            )
    if macro and not any(a.is_directional for a in macro):
        items.append(
            f"The {len(macro)} macroeconomic indicator(s) in this report, at their next "
            "release."
        )
    if not macro:
        items.append(
            "Data gap: no macroeconomic indicator was collected for this window, so the "
            "broader environment is unknown here."
        )

    for section_gated in gated:
        for missing in section_gated.missing_sources:
            items.append(
                f"Data gap: {missing.name} is not connected, so "
                f"{section_gated.title.lower()} cannot be reported. It would provide "
                f"{missing.provides}."
            )

    # Monitoring items are instructions to the reader, not claims about the world. They
    # carry no record type and no confidence level, because neither would mean anything.
    section.findings = [
        Finding(statement=text, record_type=None, evidence=[], confidence="")
        for text in items
    ]
    return section
