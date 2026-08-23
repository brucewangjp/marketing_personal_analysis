"""FRED collector — Tier 1, free API.

Fetches series metadata and observations, and normalizes both into evidence records. The
series' own frequency decides the period each observation covers, so a monthly indicator
is never reported as if it described a single day.
"""

from __future__ import annotations

from datetime import date, datetime

import httpx

from ..config import Settings
from ..models import AccessMethod, EvidenceRecord, SourceType
from .base import CollectionRequest, CollectionResult, build_record, period_for

BASE_URL = "https://api.stlouisfed.org/fred"

# Series that describe the US economy as a whole. Every one of these is a long-standing
# FRED series id, but ids do change: an unknown id is reported as a warning on the run
# rather than crashing it, so a rename never costs a whole report.
SHARED_SERIES: tuple[str, ...] = (
    "FEDFUNDS",   # Federal Funds Effective Rate
    "CPIAUCSL",   # CPI, All Urban Consumers
    "UNRATE",     # Unemployment Rate
    "UMCSENT",    # University of Michigan Consumer Sentiment
    "INDPRO",     # Industrial Production Index
)

# Sector context. Left empty until the ids are verified against FRED on a real run;
# `docs/02_Research/01_Industry_Sentiment_MVP_Scope.md` section 4 names what belongs here.
SUBJECT_SERIES: dict[str, tuple[str, ...]] = {
    "US technology": (),
    "US healthcare": (),
}


def series_for(subject: str) -> tuple[str, ...]:
    return SHARED_SERIES + SUBJECT_SERIES.get(subject, ())


class FredCollector:
    source_id = "fred"

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self._client = client

    def collect(self, request: CollectionRequest) -> CollectionResult:
        result = CollectionResult(source_id=self.source_id, tier=AccessMethod.API)

        if not self.settings.has_fred_key:
            result.reason = (
                "FRED_API_KEY is not set. Get a free key at "
                "https://fredaccount.stlouisfed.org/apikeys and put it in .env"
            )
            return result

        client = self._client or httpx.Client(
            base_url=BASE_URL, timeout=self.settings.request_timeout
        )
        owns_client = self._client is None
        try:
            for series_id in series_for(request.subject):
                try:
                    result.records.extend(
                        self._collect_series(client, series_id, request)
                    )
                except _SeriesUnavailable as exc:
                    result.warnings.append(str(exc))
        except httpx.HTTPError as exc:
            # The host is unreachable or timing out: the whole source is unavailable,
            # not just one series.
            result.reason = f"FRED is unreachable: {type(exc).__name__}: {exc}"
        finally:
            if owns_client:
                client.close()
        return result

    # -- internals -------------------------------------------------------

    def _params(self, **extra: object) -> dict[str, object]:
        return {
            "api_key": self.settings.fred_api_key,
            "file_type": "json",
            **extra,
        }

    def _collect_series(
        self, client: httpx.Client, series_id: str, request: CollectionRequest
    ) -> list[EvidenceRecord]:
        meta = self._series_metadata(client, series_id)
        response = client.get(
            "/series/observations",
            params=self._params(
                series_id=series_id,
                observation_start=request.period_start.isoformat(),
                observation_end=request.period_end.isoformat(),
            ),
        )
        if response.status_code != 200:
            raise _SeriesUnavailable(
                f"{series_id}: observations request returned HTTP {response.status_code}"
            )

        retrieved_at = datetime.now()
        records: list[EvidenceRecord] = []
        for observation in response.json().get("observations", []):
            value = observation.get("value")
            if value in (None, "", "."):
                continue  # FRED marks a missing observation with "."; it is not a zero.
            try:
                numeric = float(value)
                observed = date.fromisoformat(observation["date"])
            except (TypeError, ValueError):
                continue

            period_start, period_end = period_for(observed, meta["frequency"])
            records.append(
                build_record(
                    source_id=self.source_id,
                    record_id=(
                        f"fred.{series_id.lower()}.{observed.isoformat()}"
                        f".{request.subject_slug}"
                    ),
                    request=request,
                    source_type=SourceType.MACRO_INDICATOR,
                    access_method=AccessMethod.API,
                    query_or_series_id=series_id,
                    period_start=period_start,
                    period_end=period_end,
                    observed_at=observed,
                    retrieved_at=retrieved_at,
                    value=numeric,
                    unit=meta["units"],
                    limitation=(
                        f"{meta['title']} describes the US economy as a whole, not "
                        f"{request.subject}."
                    ),
                )
            )
        return records

    def _series_metadata(self, client: httpx.Client, series_id: str) -> dict[str, str]:
        response = client.get("/series", params=self._params(series_id=series_id))
        if response.status_code != 200:
            raise _SeriesUnavailable(
                f"{series_id}: metadata request returned HTTP {response.status_code}"
            )
        entries = response.json().get("seriess") or []
        if not entries:
            raise _SeriesUnavailable(f"{series_id}: no such series in FRED")
        entry = entries[0]
        return {
            "title": entry.get("title", series_id),
            # The unit is required by the schema, so a series without one is unusable
            # rather than silently stored as a bare number.
            "units": entry.get("units") or entry.get("units_short") or "",
            "frequency": entry.get("frequency", ""),
        }


class _SeriesUnavailable(RuntimeError):
    """One series could not be collected. The rest of the run continues."""
