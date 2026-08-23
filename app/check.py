"""Check that this machine can actually reach the data sources.

    .venv/bin/python -m app.check

Written because the sandbox this project was built in cannot reach any data-source host,
so the FRED collector was only ever exercised against a mocked transport. This makes the
first real run diagnose itself instead of failing somewhere deeper.
"""

from __future__ import annotations

import sys
from datetime import date, timedelta

import httpx

from . import config
from .collectors.fred import BASE_URL, SHARED_SERIES

OK, WARN, BAD = "  ok  ", " warn ", " fail "


def _line(status: str, label: str, detail: str = "") -> None:
    print(f"[{status}] {label}" + (f"\n         {detail}" if detail else ""))


def check_fred(settings: config.Settings) -> bool:
    if not settings.has_fred_key:
        _line(
            BAD,
            "FRED API key",
            "FRED_API_KEY is not set. Get a free key at\n         "
            "https://fredaccount.stlouisfed.org/apikeys, then put it in .env",
        )
        return False
    _line(OK, "FRED API key", "found in the environment")

    series = SHARED_SERIES[0]
    try:
        with httpx.Client(base_url=BASE_URL, timeout=settings.request_timeout) as client:
            response = client.get(
                "/series",
                params={
                    "series_id": series,
                    "api_key": settings.fred_api_key,
                    "file_type": "json",
                },
            )
    except httpx.HTTPError as exc:
        _line(
            BAD,
            "FRED reachable",
            f"{type(exc).__name__}: {exc}\n         "
            "Check network access to api.stlouisfed.org",
        )
        return False

    if response.status_code == 400:
        _line(BAD, "FRED accepted the key", "HTTP 400 — the key is probably wrong")
        return False
    if response.status_code != 200:
        _line(BAD, "FRED reachable", f"HTTP {response.status_code}")
        return False

    entries = response.json().get("seriess") or []
    if not entries:
        _line(WARN, "FRED response shape", "no 'seriess' key — the API may have changed")
        return False

    entry = entries[0]
    missing = [f for f in ("title", "units", "frequency") if not entry.get(f)]
    if missing:
        _line(
            WARN,
            "FRED response shape",
            f"{series} is missing {', '.join(missing)}; the collector expects these",
        )
        return False

    _line(
        OK,
        "FRED reachable and understood",
        f"{series}: {entry['title']} ({entry['units']}, {entry['frequency']})",
    )
    return True


def check_observations(settings: config.Settings) -> bool:
    """One real observations call, since that is the response the collector normalizes."""
    if not settings.has_fred_key:
        return False
    end = date.today()
    try:
        with httpx.Client(base_url=BASE_URL, timeout=settings.request_timeout) as client:
            response = client.get(
                "/series/observations",
                params={
                    "series_id": SHARED_SERIES[0],
                    "api_key": settings.fred_api_key,
                    "file_type": "json",
                    "observation_start": (end - timedelta(days=120)).isoformat(),
                    "observation_end": end.isoformat(),
                },
            )
        observations = response.json().get("observations", [])
    except (httpx.HTTPError, ValueError) as exc:
        _line(BAD, "FRED observations", f"{type(exc).__name__}: {exc}")
        return False

    if not observations:
        _line(WARN, "FRED observations", "the call worked but returned no rows")
        return False
    first = observations[0]
    if "date" not in first or "value" not in first:
        _line(WARN, "FRED observations", f"unexpected row shape: {first}")
        return False
    _line(
        OK,
        "FRED observations",
        f"{len(observations)} row(s); newest {observations[-1]['date']} = "
        f"{observations[-1]['value']}",
    )
    return True


def check_trends(settings: config.Settings) -> bool:
    directory = settings.trends_import_dir
    if not directory.exists():
        _line(
            WARN,
            "Google Trends imports",
            f"{directory} does not exist. Google publishes no API, so export\n         "
            "'Interest over time' from trends.google.com and save the CSV there.\n"
            "         Format example: examples/trends_interest_over_time_example.csv",
        )
        return False
    files = sorted(directory.glob("*.csv"))
    if not files:
        _line(WARN, "Google Trends imports", f"no CSV files in {directory}")
        return False
    _line(OK, "Google Trends imports", f"{len(files)} file(s) in {directory}")
    return True


def main(argv: list[str] | None = None) -> int:
    settings = config.load()
    print("\nChecking data sources\n")
    fred_ok = check_fred(settings)
    if fred_ok:
        fred_ok = check_observations(settings)
    trends_ok = check_trends(settings)

    print()
    if fred_ok and trends_ok:
        print("Both sources are ready. Run:")
        print('  .venv/bin/python -m app.collect --subject "US technology" --window 3m\n')
        return 0
    if fred_ok or trends_ok:
        print(
            "One source is ready. Collection will run and the report will say\n"
            "'insufficient evidence' for the sections the other one feeds.\n"
        )
        return 0
    print("Neither source is ready. Fix the items above, then run this check again.\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
