"""Google Trends, tried in the order the source selection policy defines.

Tier 3 automated collection first; Tier 4 manual CSV import when that fails. This is the
policy's fallback rule made concrete: when a source starts blocking, drop a tier rather
than working around the block.

The fallback matters in practice, not just on paper. The Trends endpoint is undocumented
and rate-limits aggressively, so the CSV path is the one that always works — the automated
path just saves the owner from doing it by hand most weeks.
"""

from __future__ import annotations

from ..config import Settings
from ..models import AccessMethod
from .base import CollectionRequest, CollectionResult
from .trends_api import TrendsApiCollector
from .trends_csv import TrendsCsvCollector


class TrendsCollector:
    source_id = "google_trends"

    def __init__(self, settings: Settings, *, allow_automated: bool = True) -> None:
        self.settings = settings
        self.allow_automated = allow_automated

    def collect(self, request: CollectionRequest) -> CollectionResult:
        if self.allow_automated:
            automated = TrendsApiCollector(self.settings).collect(request)
            if automated.records:
                return automated
            fallback_note = automated.reason or "Automated collection returned no rows."
        else:
            fallback_note = "Automated collection disabled; using the CSV import."

        manual = TrendsCsvCollector(self.settings, tier=AccessMethod.MANUAL).collect(
            request
        )
        manual.warnings.insert(0, f"Fell back to CSV import. {fallback_note}")
        if not manual.records and not manual.failed:
            manual.reason = (
                f"{fallback_note} No CSV export was available either, so this source "
                "has no data for this run."
            )
        return manual
