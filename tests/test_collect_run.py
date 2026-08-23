"""The run must survive an unavailable source and hand the report real records."""

from datetime import date

import httpx
import pytest

from app import collect, config
from app.collectors.base import CollectionRequest, CollectionResult
from app.collectors.fred import BASE_URL, FredCollector
from app.collectors.trends_csv import TrendsCsvCollector
from app.reports import industry_sentiment as sentiment
from app.sample import all_records
from app.store import EvidenceStore

REQUEST = CollectionRequest(
    "US technology", "United States", date(2026, 5, 24), date(2026, 8, 22)
)

EXPORT = """Category: All categories

Week,US technology: (United States)
2026-06-07,52
2026-06-14,58
2026-06-21,64
"""

META = {
    "seriess": [
        {"id": "X", "title": "Federal Funds Effective Rate",
         "units": "Percent", "frequency": "Monthly"}
    ]
}
OBS = {"observations": [{"date": "2026-06-01", "value": "3.63"}]}


@pytest.fixture
def settings(tmp_path):
    import_dir = tmp_path / "trends"
    import_dir.mkdir()
    (import_dir / "tech.csv").write_text(EXPORT)
    return config.load(
        fred_api_key="test-key",
        trends_import_dir=import_dir,
        db_path=tmp_path / "evidence.db",
    )


def _with_fred(monkeypatch, handler):
    def build(settings):
        client = httpx.Client(transport=httpx.MockTransport(handler), base_url=BASE_URL)
        return [FredCollector(settings, client=client), TrendsCsvCollector(settings)]

    monkeypatch.setattr(collect, "build_collectors", build)


def _ok(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json=META if request.url.path.endswith("/series") else OBS)


def _dead(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("no route to host")


def test_records_reach_the_store(monkeypatch, settings):
    _with_fred(monkeypatch, _ok)
    collect.run(REQUEST, settings)
    with EvidenceStore(settings.db_path) as store:
        assert store.count() == 8  # 5 FRED series x 1 observation + 3 Trends weeks


def test_dry_run_writes_nothing(monkeypatch, settings):
    _with_fred(monkeypatch, _ok)
    results = collect.run(REQUEST, settings, dry_run=True)
    assert any(r.records for r in results)
    with EvidenceStore(settings.db_path) as store:
        assert store.count() == 0


def test_an_unavailable_source_does_not_stop_the_others(monkeypatch, settings):
    _with_fred(monkeypatch, _dead)
    results = collect.run(REQUEST, settings)
    by_id = {r.source_id: r for r in results}
    assert by_id["fred"].failed
    assert by_id["google_trends"].status == "ok"
    with EvidenceStore(settings.db_path) as store:
        assert store.count() == 3  # the Trends rows still landed


def test_an_unavailable_source_becomes_a_gated_report_not_a_crash(monkeypatch, settings):
    """The whole point of the contract: collection failure degrades, never breaks."""
    _with_fred(monkeypatch, _dead)
    collect.run(REQUEST, settings)
    with EvidenceStore(settings.db_path) as store:
        report = sentiment.build(
            store,
            sentiment.ReportRequest(
                "US technology", "3m", "why?", date(2026, 8, 22)
            ),
        )
    assert report.section("attention").findings[0].confidence != "Insufficient evidence"
    assert report.section("macro").findings[0].confidence == "Insufficient evidence"
    assert report.section("group_attitude").is_gated


def test_drop_sample_removes_phase_one_data(monkeypatch, settings):
    with EvidenceStore(settings.db_path) as store:
        store.add_all(all_records())
        assert store.count() == 44
    _with_fred(monkeypatch, _ok)
    collect.run(REQUEST, settings, drop_sample=True)
    with EvidenceStore(settings.db_path) as store:
        assert all(not r.is_sample for r in store.query())
        assert store.count() == 8


def test_collected_records_are_not_flagged_as_sample(monkeypatch, settings):
    _with_fred(monkeypatch, _ok)
    collect.run(REQUEST, settings)
    with EvidenceStore(settings.db_path) as store:
        report = sentiment.build(
            store,
            sentiment.ReportRequest("US technology", "3m", "why?", date(2026, 8, 22)),
        )
    assert report.header.contains_sample_data is False


def test_cli_reports_an_unavailable_source_without_failing(monkeypatch, settings, capsys):
    _with_fred(monkeypatch, _dead)
    monkeypatch.setattr(config, "load", lambda **kw: settings)
    exit_code = collect.main(
        ["--subject", "US technology", "--window", "3m", "--as-of", "2026-08-22"]
    )
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "unavailable" in output
    assert "will say so" in output


def test_cli_rejects_an_unknown_subject(settings, monkeypatch):
    monkeypatch.setattr(config, "load", lambda **kw: settings)
    with pytest.raises(SystemExit):
        collect.main(["--subject", "US energy"])
