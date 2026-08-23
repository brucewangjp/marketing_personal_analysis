"""Google Trends automated collector — Tier 3, collection from the public interface.

Google publishes no documented API for Trends. The Trends web interface calls an internal
endpoint, and this collector calls the same one, which is the Tier 3 route the source
selection policy permits when no API and no export exist.

Three properties follow from that policy and are not optional:

- It is unauthenticated and reads only what a signed-out visitor sees.
- It stores a metric and the query configuration, never a page copy or anything personal.
- **When Google blocks it, it gives up rather than working around the block.** A 429 or a
  changed response is a failed result, and `TrendsCollector` falls back to the CSV import
  path. Rotating identities or hammering through a rate limit is out of scope by policy,
  and would lose the source permanently in practice.

This code has never run against live Google: the sandbox it was written in cannot reach
trends.google.com. The parsing is covered by tests against the documented response shape.
Treat the first real run as the real test, and expect the endpoint to change over time —
that is why the CSV path stays.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timezone

import httpx

from ..config import Settings
from ..models import AccessMethod, EvidenceRecord, SourceType
from .base import CollectionRequest, CollectionResult, build_record, period_for

HOST = "https://trends.google.com"
EXPLORE = "/trends/api/explore"
MULTILINE = "/trends/api/widgetdata/multiline"
UNIT = "relative interest, 0-100"

# Google prefixes these JSON responses with an anti-JSON-hijacking guard.
_GUARD = ")]}'"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
)

WINDOW_CODES = {30: "today 1-m", 90: "today 3-m"}


def window_code(period_start: date, period_end: date) -> str:
    """Trends takes a named window, not arbitrary dates."""
    days = (period_end - period_start).days
    return WINDOW_CODES.get(days) or f"{period_start.isoformat()} {period_end.isoformat()}"


class TrendsApiCollector:
    source_id = "google_trends"

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self._client = client

    def collect(self, request: CollectionRequest) -> CollectionResult:
        result = CollectionResult(
            source_id=self.source_id, tier=AccessMethod.WEB_COLLECTION
        )
        client = self._client or httpx.Client(
            base_url=HOST,
            timeout=self.settings.request_timeout,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
            follow_redirects=True,
        )
        owns_client = self._client is None
        try:
            token, widget_request = self._timeseries_widget(client, request)
            rows = self._timeline(client, token, widget_request)
            result.records = self._to_records(rows, request)
            if not result.records:
                result.warnings.append("Trends returned no rows for this window.")
        except _Blocked as exc:
            result.reason = str(exc)
        except httpx.HTTPError as exc:
            result.reason = f"Trends is unreachable: {type(exc).__name__}: {exc}"
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            # The endpoint is undocumented and does change. A shape we do not recognise
            # is a failed source, not a crash, and the CSV path takes over.
            result.reason = (
                f"Trends returned a response this collector does not understand "
                f"({type(exc).__name__}: {exc}). Use the CSV export path."
            )
        finally:
            if owns_client:
                client.close()
        return result

    # -- steps -----------------------------------------------------------

    def _timeseries_widget(
        self, client: httpx.Client, request: CollectionRequest
    ) -> tuple[str, dict]:
        payload = {
            "comparisonItem": [
                {
                    "keyword": request.subject,
                    "geo": "US",
                    "time": window_code(request.period_start, request.period_end),
                }
            ],
            "category": 0,
            "property": "",
        }
        response = client.get(
            EXPLORE,
            params={"hl": "en-US", "tz": "0", "req": json.dumps(payload)},
        )
        data = _decode(response)
        for widget in data.get("widgets", []):
            if widget.get("id") == "TIMESERIES":
                return widget["token"], widget["request"]
        raise ValueError("no TIMESERIES widget in the explore response")

    def _timeline(
        self, client: httpx.Client, token: str, widget_request: dict
    ) -> list[dict]:
        response = client.get(
            MULTILINE,
            params={
                "hl": "en-US",
                "tz": "0",
                "req": json.dumps(widget_request),
                "token": token,
            },
        )
        return _decode(response)["default"]["timelineData"]

    def _to_records(
        self, rows: list[dict], request: CollectionRequest
    ) -> list[EvidenceRecord]:
        retrieved_at = datetime.now()
        records: list[EvidenceRecord] = []
        for row in rows:
            if not any(row.get("hasData", [True])):
                continue  # Trends marks a period with no data; it is not a zero.
            values = row.get("value") or []
            if not values:
                continue
            observed = datetime.fromtimestamp(
                int(row["time"]), tz=timezone.utc
            ).date()
            frequency = _frequency(rows)
            period_start, period_end = period_for(observed, frequency)
            if period_end < request.period_start or period_start > request.period_end:
                continue
            records.append(
                build_record(
                    source_id=self.source_id,
                    record_id=f"trends.{request.subject_slug}.{observed.isoformat()}",
                    request=request,
                    source_type=SourceType.SEARCH_INTEREST,
                    access_method=AccessMethod.WEB_COLLECTION,
                    query_or_series_id=(
                        f'query="{request.subject}", geo=US, '
                        f'{window_code(request.period_start, request.period_end)}, '
                        f"{frequency.lower()}"
                    ),
                    period_start=period_start,
                    period_end=period_end,
                    observed_at=observed,
                    retrieved_at=retrieved_at,
                    value=float(values[0]),
                    unit=UNIT,
                    limitation=(
                        "Relative attention within this query and period. Not search "
                        "volume, sentiment, or purchase intent. Collected from the "
                        "public Trends interface, which publishes no documented API."
                    ),
                )
            )
        return records


def _frequency(rows: list[dict]) -> str:
    """Infer the row spacing, since Trends changes it with the window length."""
    if len(rows) < 2:
        return "Daily"
    gap = (int(rows[1]["time"]) - int(rows[0]["time"])) // 86400
    if gap >= 28:
        return "Monthly"
    if gap >= 6:
        return "Weekly"
    return "Daily"


def _decode(response: httpx.Response) -> dict:
    if response.status_code == 429:
        raise _Blocked(
            "Trends rate-limited this collector (HTTP 429). Policy is to fall back to "
            "the CSV export rather than work around a block."
        )
    if response.status_code in (401, 403):
        raise _Blocked(
            f"Trends refused this collector (HTTP {response.status_code}). Falling back "
            "to the CSV export."
        )
    if response.status_code != 200:
        raise _Blocked(f"Trends returned HTTP {response.status_code}.")

    body = response.text.lstrip()
    if body.startswith(_GUARD):
        body = body[len(_GUARD) :].lstrip("\n\r ,")
    return json.loads(body)


class _Blocked(RuntimeError):
    """Google declined to serve this collector. Fall back; do not push through."""
