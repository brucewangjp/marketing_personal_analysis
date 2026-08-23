"""Automated Trends collection, against mocked responses.

No test reaches Google. The parsing is verified against the response shape the Trends
interface returns; the first real run is the real test of that shape.
"""

from datetime import date

import httpx
import pytest

from app.collectors.base import CollectionRequest
from app.collectors.trends_api import HOST, TrendsApiCollector, window_code
from app.config import load
from app.models import AccessMethod

REQUEST = CollectionRequest(
    "US technology", "United States", date(2026, 5, 24), date(2026, 8, 22)
)

GUARD = ")]}',\n"
EXPLORE_BODY = GUARD + (
    '{"widgets":[{"id":"TIMESERIES","token":"tok-1",'
    '"request":{"time":"2026-05-24 2026-08-22"}},'
    '{"id":"GEO_MAP","token":"tok-2","request":{}}]}'
)
# Weekly rows, one week apart, one marked as having no data.
TIMELINE_BODY = GUARD + (
    '{"default":{"timelineData":['
    '{"time":"1779580800","value":[44],"hasData":[true]},'
    '{"time":"1780185600","value":[46],"hasData":[true]},'
    '{"time":"1780790400","value":[0],"hasData":[false]}'
    "]}}"
)


def _collector(handler):
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=HOST)
    return TrendsApiCollector(load(), client=client)


def _ok(request: httpx.Request) -> httpx.Response:
    if "explore" in request.url.path:
        return httpx.Response(200, text=EXPLORE_BODY)
    return httpx.Response(200, text=TIMELINE_BODY)


def test_window_maps_to_a_trends_code():
    assert window_code(date(2026, 5, 24), date(2026, 8, 22)) == "today 3-m"
    assert window_code(date(2026, 7, 23), date(2026, 8, 22)) == "today 1-m"


def test_timeline_becomes_evidence_records():
    result = _collector(_ok).collect(REQUEST)
    assert not result.failed
    assert len(result.records) == 2  # the hasData=false row is skipped, not stored as 0
    assert result.records[0].value == 44
    assert result.records[0].access_method is AccessMethod.WEB_COLLECTION


def test_row_spacing_is_inferred_as_weekly():
    record = _collector(_ok).collect(REQUEST).records[0]
    assert (record.period_end - record.period_start).days == 6


def test_query_configuration_is_preserved():
    query = _collector(_ok).collect(REQUEST).records[0].query_or_series_id
    assert 'query="US technology"' in query
    assert "geo=US" in query
    assert "today 3-m" in query


def test_limitation_names_the_undocumented_route():
    limitation = _collector(_ok).collect(REQUEST).records[0].limitation
    assert "no documented API" in limitation
    assert "Not search volume" in limitation


def test_rate_limiting_gives_up_rather_than_retrying():
    """Policy: when a source starts blocking, drop a tier — never work around it."""
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        return httpx.Response(429, text="")

    result = _collector(handler).collect(REQUEST)
    assert result.failed
    assert "429" in result.reason
    assert "fall back" in result.reason.lower()
    assert len(calls) == 1  # one attempt, no retry loop


def test_refusal_is_reported():
    result = _collector(lambda r: httpx.Response(403, text="")).collect(REQUEST)
    assert result.failed
    assert "403" in result.reason


def test_unreachable_host_is_reported_not_raised():
    def dead(request):
        raise httpx.ConnectError("no route")

    result = _collector(dead).collect(REQUEST)
    assert result.failed
    assert "unreachable" in result.reason


def test_a_changed_response_shape_is_a_failed_source_not_a_crash():
    def handler(request: httpx.Request) -> httpx.Response:
        if "explore" in request.url.path:
            return httpx.Response(200, text=GUARD + '{"widgets":[]}')
        return httpx.Response(200, text=TIMELINE_BODY)

    result = _collector(handler).collect(REQUEST)
    assert result.failed
    assert "does not understand" in result.reason
    assert "CSV export path" in result.reason


def test_missing_guard_prefix_still_parses():
    def handler(request: httpx.Request) -> httpx.Response:
        body = EXPLORE_BODY if "explore" in request.url.path else TIMELINE_BODY
        return httpx.Response(200, text=body[len(GUARD):])

    assert _collector(handler).collect(REQUEST).records


def test_the_collector_sends_no_credentials_and_no_cookies():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["cookie"] = request.headers.get("cookie")
        seen["auth"] = request.headers.get("authorization")
        return _ok(request)

    _collector(handler).collect(REQUEST)
    assert seen["cookie"] is None
    assert seen["auth"] is None


def test_every_record_passes_schema_validation():
    for record in _collector(_ok).collect(REQUEST).records:
        record.validate()
        assert record.is_sample is False
