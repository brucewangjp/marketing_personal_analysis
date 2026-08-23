"""The self-check must diagnose, not crash, whatever it finds."""

import httpx
import pytest

from app import check, config
from app.collectors.fred import BASE_URL

META = {
    "seriess": [
        {"id": "FEDFUNDS", "title": "Federal Funds Effective Rate",
         "units": "Percent", "frequency": "Monthly"}
    ]
}
OBS = {"observations": [{"date": "2026-07-01", "value": "3.62"}]}


@pytest.fixture
def settings(tmp_path):
    return config.load(fred_api_key="k", trends_import_dir=tmp_path / "trends",
                       db_path=tmp_path / "db.sqlite")


def _patch_client(monkeypatch, handler):
    real = httpx.Client

    def factory(*a, **kw):
        kw.pop("transport", None)
        return real(transport=httpx.MockTransport(handler), base_url=BASE_URL,
                    timeout=kw.get("timeout", 10))

    monkeypatch.setattr(check.httpx, "Client", factory)


def test_missing_key_is_reported(tmp_path, capsys):
    settings = config.load(fred_api_key=None, trends_import_dir=tmp_path)
    assert check.check_fred(settings) is False
    assert "FRED_API_KEY is not set" in capsys.readouterr().out


def test_unreachable_host_is_reported_not_raised(monkeypatch, settings, capsys):
    def dead(request):
        raise httpx.ConnectError("no route to host")

    _patch_client(monkeypatch, dead)
    assert check.check_fred(settings) is False
    assert "Check network access" in capsys.readouterr().out


def test_bad_key_is_named(monkeypatch, settings, capsys):
    _patch_client(monkeypatch, lambda r: httpx.Response(400, json={}))
    assert check.check_fred(settings) is False
    assert "the key is probably wrong" in capsys.readouterr().out


def test_changed_response_shape_is_flagged(monkeypatch, settings, capsys):
    """The reason this command exists: the collector was never run against live FRED."""
    _patch_client(
        monkeypatch,
        lambda r: httpx.Response(200, json={"seriess": [{"id": "FEDFUNDS"}]}),
    )
    assert check.check_fred(settings) is False
    out = capsys.readouterr().out
    assert "missing title, units, frequency" in out


def test_healthy_fred_passes(monkeypatch, settings, capsys):
    _patch_client(monkeypatch, lambda r: httpx.Response(200, json=META))
    assert check.check_fred(settings) is True
    assert "Federal Funds Effective Rate" in capsys.readouterr().out


def test_observations_shape_is_checked(monkeypatch, settings, capsys):
    _patch_client(monkeypatch, lambda r: httpx.Response(200, json=OBS))
    assert check.check_observations(settings) is True
    assert "newest 2026-07-01" in capsys.readouterr().out


def test_missing_trends_directory_explains_the_export(settings, capsys):
    assert check.check_trends(settings) is False
    assert "Google publishes no API" in capsys.readouterr().out


def test_trends_directory_with_a_file_passes(settings, capsys):
    settings.trends_import_dir.mkdir(parents=True)
    (settings.trends_import_dir / "a.csv").write_text("Week,x\n")
    assert check.check_trends(settings) is True


def test_exit_code_is_zero_when_one_source_works(monkeypatch, settings, capsys):
    settings.trends_import_dir.mkdir(parents=True)
    (settings.trends_import_dir / "a.csv").write_text("Week,x\n")
    monkeypatch.setattr(config, "load", lambda **kw: settings)

    def dead(request):
        raise httpx.ConnectError("down")

    _patch_client(monkeypatch, dead)
    assert check.main([]) == 0
    assert "insufficient evidence" in capsys.readouterr().out


def test_exit_code_is_one_when_nothing_works(monkeypatch, tmp_path, capsys):
    settings = config.load(fred_api_key=None, trends_import_dir=tmp_path / "absent",
                          db_path=tmp_path / "db")
    monkeypatch.setattr(config, "load", lambda **kw: settings)
    assert check.main([]) == 1
    assert "Neither source is ready" in capsys.readouterr().out
