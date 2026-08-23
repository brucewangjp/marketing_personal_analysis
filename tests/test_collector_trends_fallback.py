"""Tier 3 first, Tier 4 when Google declines. The fallback must always be reachable."""

from datetime import date

import pytest

from app.collectors.base import CollectionRequest, CollectionResult
from app.collectors import trends as trends_module
from app.collectors.trends import TrendsCollector
from app.config import load
from app.models import AccessMethod

REQUEST = CollectionRequest(
    "US technology", "United States", date(2026, 5, 24), date(2026, 8, 22)
)

EXPORT = """Category: All categories

Week,US technology: (United States)
2026-06-07,52
2026-06-14,58
"""


@pytest.fixture
def settings(tmp_path):
    d = tmp_path / "trends"
    d.mkdir()
    (d / "tech.csv").write_text(EXPORT)
    return load(trends_import_dir=d)


def _stub_api(monkeypatch, result: CollectionResult):
    class Stub:
        def __init__(self, *a, **kw):
            pass

        def collect(self, request):
            return result

    monkeypatch.setattr(trends_module, "TrendsApiCollector", Stub)


def test_automated_result_is_used_when_it_works(monkeypatch, settings):
    from app.collectors.trends_api import TrendsApiCollector  # noqa: F401
    from tests.conftest import make_record

    record = make_record(
        "trends.x", source_id="google_trends",
        source_type=__import__("app.models", fromlist=["x"]).SourceType.SEARCH_INTEREST,
    )
    _stub_api(
        monkeypatch,
        CollectionResult("google_trends", AccessMethod.WEB_COLLECTION, [record]),
    )
    result = TrendsCollector(settings).collect(REQUEST)
    assert result.tier is AccessMethod.WEB_COLLECTION
    assert len(result.records) == 1


def test_blocked_automated_collection_falls_back_to_csv(monkeypatch, settings):
    _stub_api(
        monkeypatch,
        CollectionResult("google_trends", reason="Trends rate-limited this collector (HTTP 429)."),
    )
    result = TrendsCollector(settings).collect(REQUEST)
    assert result.tier is AccessMethod.MANUAL
    assert len(result.records) == 2
    assert "Fell back to CSV import" in result.warnings[0]
    assert "429" in result.warnings[0]


def test_fallback_can_be_forced(settings):
    result = TrendsCollector(settings, allow_automated=False).collect(REQUEST)
    assert result.tier is AccessMethod.MANUAL
    assert "disabled" in result.warnings[0]


def test_both_tiers_failing_is_reported_as_an_unavailable_source(monkeypatch, tmp_path):
    _stub_api(monkeypatch, CollectionResult("google_trends", reason="Trends blocked."))
    result = TrendsCollector(load(trends_import_dir=tmp_path / "absent")).collect(REQUEST)
    assert result.failed
    assert "No CSV export was available either" in result.reason
