"""Source registry.

One entry per source named in a `docs/03_Data` source plan. The registry is what the
gating rule reads to decide whether a report section can be populated, and what the
confidence rubric reads to decide whether a source's methodology is documented.

`connected` is deliberately data, not code: Phase 1 ships with only the sources whose
collectors exist. Connecting a source later is a one-line change here plus a collector.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import AccessMethod, SourceType


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    publisher: str
    source_type: SourceType
    access_method: AccessMethod
    methodology_documented: bool
    proxy: bool
    connected: bool
    rights_note: str
    retention_rule: str
    default_limitation: str
    provides: str
    """What a report loses while this source is not connected. Shown in gated sections."""


REGISTRY: dict[str, Source] = {
    "fred": Source(
        source_id="fred",
        name="FRED",
        publisher="Federal Reserve Bank of St. Louis",
        source_type=SourceType.MACRO_INDICATOR,
        access_method=AccessMethod.API,
        methodology_documented=True,
        proxy=False,
        connected=True,
        rights_note="Attribution to FRED and the originating agency required.",
        retention_rule="Retain while the report referencing it is retained.",
        default_limitation=(
            "A macroeconomic indicator describes the environment, not any single "
            "industry or company."
        ),
        provides="macroeconomic and published aggregate sentiment context",
    ),
    "google_trends": Source(
        source_id="google_trends",
        name="Google Trends",
        publisher="Google",
        source_type=SourceType.SEARCH_INTEREST,
        access_method=AccessMethod.EXPORT,
        methodology_documented=True,
        proxy=True,
        connected=True,
        rights_note="Attribution to Google Trends required.",
        retention_rule="Retain the query configuration with every stored series.",
        default_limitation=(
            "Search interest is relative attention within the query and period. It is "
            "not search volume, sentiment, or a decision to buy."
        ),
        provides="search-attention trend",
    ),
    "public_discussion": Source(
        source_id="public_discussion",
        name="Public discussion",
        publisher="Not yet selected",
        source_type=SourceType.PUBLIC_DISCUSSION,
        access_method=AccessMethod.API,
        methodology_documented=False,
        proxy=False,
        connected=False,
        rights_note="Set when the platform is chosen.",
        retention_rule="Set when the platform is chosen.",
        default_limitation=(
            "Public discussion is a self-selected sample of people who choose to post, "
            "not a representative survey."
        ),
        provides=(
            "group-level attitudes, and the motivations and concerns people state in "
            "their own words"
        ),
    ),
}


def get(source_id: str) -> Source:
    try:
        return REGISTRY[source_id]
    except KeyError:
        raise KeyError(
            f"unknown source {source_id!r}; every source must be registered before "
            "its records can be stored or reported"
        ) from None


def is_connected(source_id: str) -> bool:
    return get(source_id).connected


def connected_sources() -> list[Source]:
    return [s for s in REGISTRY.values() if s.connected]


def unconnected_sources() -> list[Source]:
    return [s for s in REGISTRY.values() if not s.connected]
