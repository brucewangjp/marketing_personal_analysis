"""FRED collector, against a mocked transport. No test makes a network call."""

from datetime import date

import httpx
import pytest

from app.collectors.base import CollectionRequest
from app.collectors.fred import BASE_URL, FredCollector
from app.config import load
from app.models import AccessMethod, RecordType

REQUEST = CollectionRequest(
    "US technology", "United States", date(2026, 5, 1), date(2026, 8, 1)
)

META = {
    "seriess": [
        {
            "id": "FEDFUNDS",
            "title": "Federal Funds Effective Rate",
            "units": "Percent",
            "frequency": "Monthly",
        }
    ]
}
OBSERVATIONS = {
    "observations": [
        {"date": "2026-05-01", "value": "3.88"},
        {"date": "2026-06-01", "value": "."},      # FRED's marker for missing
        {"date": "2026-07-01", "value": "3.62"},
    ]
}


def _collector(handler, **settings_overrides):
    settings = load(fred_api_key="test-key", **settings_overrides)
    client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE_URL)
    return FredCollector(settings, client=client)


def _ok(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/series"):
        return httpx.Response(200, json=META)
    return httpx.Response(200, json=OBSERVATIONS)


def test_missing_api_key_is_reported_not_raised():
    result = FredCollector(load(fred_api_key=None)).collect(REQUEST)
    assert result.failed
    assert result.status == "unavailable"
    assert "FRED_API_KEY" in result.reason
    assert result.records == []


def test_observations_become_evidence_records():
    result = _collector(_ok).collect(REQUEST)
    assert not result.failed
    records = [r for r in result.records if r.query_or_series_id == "FEDFUNDS"]
    assert len(records) == 2  # the "." observation is skipped, not stored as zero
    assert records[0].value == 3.88
    assert records[0].unit == "Percent"
    assert records[0].record_type is RecordType.OBSERVATION
    assert records[0].access_method is AccessMethod.API


def test_monthly_observation_covers_its_whole_month():
    record = _collector(_ok).collect(REQUEST).records[0]
    assert record.period_start == date(2026, 5, 1)
    assert record.period_end == date(2026, 5, 31)
    assert record.observed_at == date(2026, 5, 1)


def test_records_carry_rights_and_retention_from_the_registry():
    record = _collector(_ok).collect(REQUEST).records[0]
    assert "Attribution" in record.rights_note
    assert record.retention_rule
    assert "not US technology" in record.limitation


def test_api_key_is_sent_but_never_stored_on_a_record():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["key"] = request.url.params.get("api_key")
        return _ok(request)

    record = _collector(handler).collect(REQUEST).records[0]
    assert seen["key"] == "test-key"
    assert "test-key" not in repr(record)


def test_unknown_series_is_a_warning_not_a_failed_run():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params.get("series_id") == "UNRATE":
            return httpx.Response(400, json={"error_message": "Bad request"})
        return _ok(request)

    result = _collector(handler).collect(REQUEST)
    assert not result.failed
    assert result.records  # the other series still collected
    assert any("UNRATE" in w for w in result.warnings)


def test_empty_series_list_is_a_warning():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/series"):
            return httpx.Response(200, json={"seriess": []})
        return httpx.Response(200, json=OBSERVATIONS)

    result = _collector(handler).collect(REQUEST)
    assert not result.failed
    assert result.records == []
    assert any("no such series" in w for w in result.warnings)


def test_unreachable_host_fails_the_source_not_the_process():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    result = _collector(handler).collect(REQUEST)
    assert result.failed
    assert "unreachable" in result.reason


def test_malformed_observation_is_skipped():
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/series"):
            return httpx.Response(200, json=META)
        return httpx.Response(
            200,
            json={"observations": [{"date": "not-a-date", "value": "1"},
                                   {"date": "2026-05-01", "value": "abc"}]},
        )

    result = _collector(handler).collect(REQUEST)
    assert result.records == []
    assert not result.failed


def test_every_record_passes_schema_validation():
    for record in _collector(_ok).collect(REQUEST).records:
        record.validate()  # raises if the collector built something invalid
        assert record.is_sample is False
