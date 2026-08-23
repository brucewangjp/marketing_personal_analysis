"""The Industry Sentiment report.

Builds every section of `docs/05_Design/01_Industry_Sentiment_Report_Template.md` from
stored evidence. Sections 6 and 7 are gated on the public-discussion source: while it is
not connected they render as insufficient evidence, because attention and macro data
measure the environment, not what people think or why.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

from .. import charts, sources
from ..confidence import INSUFFICIENT, Window
from ..models import EvidenceRecord, Finding, RecordType, SourceType
from ..reporting import Report, ReportHeader, Section, build_finding
from ..store import EvidenceStore

SUBJECTS = ("US technology", "US healthcare")

WINDOWS: dict[str, tuple[str, int]] = {
    "1m": ("most recent one month", 30),
    "3m": ("most recent three months", 90),
}

CADENCE = "Weekly"


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
    def period_start(self) -> date:
        return self.as_of - timedelta(days=WINDOWS[self.window][1])

    @property
    def period_end(self) -> date:
        return self.as_of


def default_question(subject: str) -> str:
    return f"Is attention toward {subject} rising or falling, and what does the evidence not show?"


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

    attention = _attention_section(trends, window)
    macro_section = _macro_section(macro, window)
    attitude = Section(
        "group_attitude", "Group attitude", requires=("public_discussion",)
    )
    motivations = Section(
        "motivations", "Motivations and concerns", requires=("public_discussion",)
    )
    change = _change_section(trends, window)
    summary = _summary_section(trends, macro, attention, window)
    monitoring = _monitoring_section(request, attention, [attitude, motivations])

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
            "It does not measure what any individual thinks, and it is not investment advice."
        ),
        contains_sample_data=any(r.is_sample for r in records),
    )

    return Report(
        header=header,
        sections=[
            summary,
            attention,
            macro_section,
            attitude,
            motivations,
            change,
            monitoring,
        ],
    )


# -- sections ------------------------------------------------------------


def _points(records: list[EvidenceRecord]) -> list[charts.Point]:
    return [(r.period_end, r.value) for r in records if r.value is not None]


def _attention_section(trends: list[EvidenceRecord], window: Window) -> Section:
    section = Section("attention", "Attention trend", requires=("google_trends",))
    section.note = (
        "Search interest measures relative attention within this query and period. "
        "It is not a count of people, their sentiment, or a decision to buy."
    )
    if not trends:
        section.findings.append(
            build_finding(
                "No search-interest series covers this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )
        return section

    points = _points(trends)
    section.chart_svg = charts.line_chart(
        points, label="Search interest", unit="relative interest, 0-100"
    )
    heading = charts.direction(points)
    first, last = points[0][1], points[-1][1]

    section.findings.append(
        build_finding(
            f"Search interest is {heading} over the window, from {first:g} to {last:g} "
            "on the relative interest scale.",
            RecordType.DERIVED_METRIC,
            trends,
            window,
        )
    )
    return section


def _macro_section(macro: list[EvidenceRecord], window: Window) -> Section:
    section = Section(
        "macro", "Macro and aggregate sentiment context", requires=("fred",)
    )
    section.note = (
        "A macroeconomic correlation does not prove why people feel or act a certain way."
    )
    if not macro:
        section.findings.append(
            build_finding(
                "No macroeconomic indicator covers this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )
        return section

    by_series: dict[str, list[EvidenceRecord]] = {}
    for record in macro:
        by_series.setdefault(record.query_or_series_id, []).append(record)

    for series_id, series in sorted(by_series.items()):
        series.sort(key=lambda r: r.period_start)
        latest = series[-1]
        statement = f"{series_id} stands at {latest.display_value} for {latest.period_label}."
        if len(series) > 1:
            move = latest.value - series[0].value
            word = "up" if move > 0 else "down" if move < 0 else "flat"
            statement += f" That is {word} {abs(move):.2f} across the window."
        section.findings.append(
            build_finding(statement, RecordType.OBSERVATION, series, window)
        )
    return section


def _change_section(trends: list[EvidenceRecord], window: Window) -> Section:
    section = Section("change", "Change over time", requires=("google_trends",))
    points = _points(trends)
    if len(points) < 2:
        section.findings.append(
            build_finding(
                "Not enough observations to describe change over this window.",
                RecordType.OBSERVATION,
                trends,
                window,
            )
        )
        return section

    heading = charts.direction(points)
    peak = max(points, key=lambda p: p[1])
    trough = min(points, key=lambda p: p[1])
    section.findings.append(
        build_finding(
            f"Attention is {heading}. It peaked at {peak[1]:g} in the week ending "
            f"{peak[0].isoformat()} and was lowest at {trough[1]:g} in the week ending "
            f"{trough[0].isoformat()}.",
            RecordType.DERIVED_METRIC,
            trends,
            window,
        )
    )
    section.note = (
        "A change in attention is not a change in tone. Whether sentiment moved with it "
        "cannot be established from this evidence."
    )
    return section


def _summary_section(
    trends: list[EvidenceRecord],
    macro: list[EvidenceRecord],
    attention: Section,
    window: Window,
) -> Section:
    section = Section("summary", "Executive summary")
    points = _points(trends)

    if points:
        heading = charts.direction(points)
        section.findings.append(
            build_finding(
                f"Overall attention is {heading} across the window.",
                RecordType.DERIVED_METRIC,
                trends,
                window,
            )
        )
    else:
        section.findings.append(
            build_finding(
                "Overall attention cannot be assessed: no search-interest series covers "
                "this window.",
                RecordType.OBSERVATION,
                [],
                window,
            )
        )

    # Tone is deliberately not inferred. Stating it as a gap is the correct output
    # while the only source that could support it is unconnected.
    section.findings.append(
        build_finding(
            "Overall group tone cannot be assessed. Attention and macroeconomic "
            "indicators measure the environment, not what people think.",
            RecordType.OBSERVATION,
            [],
            window,
        )
    )

    if macro:
        latest = max(macro, key=lambda r: r.period_end)
        section.findings.append(
            build_finding(
                f"The broader environment is described by {len(macro)} macroeconomic "
                f"observations, most recently {latest.query_or_series_id} at "
                f"{latest.display_value} for {latest.period_label}.",
                RecordType.OBSERVATION,
                macro,
                window,
            )
        )
    return section


def _monitoring_section(
    request: ReportRequest, attention: Section, gated: list[Section]
) -> Section:
    section = Section("monitoring", "Monitoring list")
    section.note = "Carried into the next weekly run."

    items = [
        f'Search interest for "{request.subject}" — whether the current direction holds '
        "into the next run.",
        "The macroeconomic indicators in this report, at their next release.",
    ]
    for gated_section in gated:
        for missing in gated_section.missing_sources:
            items.append(
                f"Data gap: {missing.name} is not connected, so {gated_section.title.lower()} "
                f"cannot be reported. It would provide {missing.provides}."
            )

    # Monitoring items are instructions to the reader, not claims about the world. They
    # carry no record type and no confidence level, because neither would mean anything.
    section.findings = [
        Finding(statement=text, record_type=None, evidence=[], confidence="")
        for text in items
    ]
    return section
