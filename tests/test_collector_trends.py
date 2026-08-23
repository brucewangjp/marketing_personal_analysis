"""The Trends importer must be tolerant of a real export and honest about what it read."""

from datetime import date

import pytest

from app.collectors.base import CollectionRequest
from app.collectors.trends_csv import TrendsCsvCollector
from app.config import load
from app.models import AccessMethod

REQUEST = CollectionRequest(
    "US technology", "United States", date(2026, 5, 24), date(2026, 8, 22)
)

EXPORT = """Category: All categories

Week,US technology: (United States)
2026-05-24,44
2026-05-31,46
2026-06-07,52
"""


@pytest.fixture
def import_dir(tmp_path):
    d = tmp_path / "trends"
    d.mkdir()
    return d


def _collect(import_dir, **kw):
    return TrendsCsvCollector(load(trends_import_dir=import_dir), **kw).collect(REQUEST)


def test_missing_directory_is_a_warning_not_a_failure(tmp_path):
    result = TrendsCsvCollector(load(trends_import_dir=tmp_path / "absent")).collect(
        REQUEST
    )
    assert not result.failed
    assert result.records == []
    assert any("No Trends export directory" in w for w in result.warnings)


def test_empty_directory_is_a_warning(import_dir):
    result = _collect(import_dir)
    assert not result.failed
    assert any("No CSV exports" in w for w in result.warnings)


def test_export_becomes_evidence_records(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    result = _collect(import_dir)
    assert len(result.records) == 3
    assert result.records[0].value == 44
    assert result.records[0].unit == "relative interest, 0-100"
    assert result.records[0].access_method is AccessMethod.MANUAL


def test_a_weekly_row_covers_seven_days(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    record = _collect(import_dir).records[0]
    assert record.period_start == date(2026, 5, 24)
    assert record.period_end == date(2026, 5, 30)


def test_below_one_is_kept_with_its_limitation_recorded(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT.replace("2026-05-31,46", "2026-05-31,<1"))
    result = _collect(import_dir)
    low = [r for r in result.records if r.value == 0.5]
    assert len(low) == 1
    assert "'<1'" in low[0].limitation
    assert any("<1" in w for w in result.warnings)


def test_manual_import_says_so_in_the_limitation(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    assert "Imported by hand" in _collect(import_dir).records[0].limitation


def test_a_downloaded_export_is_recorded_as_tier_two(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    result = _collect(import_dir, tier=AccessMethod.EXPORT)
    assert result.records[0].access_method is AccessMethod.EXPORT
    assert "Imported by hand" not in result.records[0].limitation


def test_query_is_preserved_for_reproducibility(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    query = _collect(import_dir).records[0].query_or_series_id
    assert 'query="US technology"' in query
    assert "geo=United States" in query
    assert "weekly" in query


def test_export_for_another_query_is_skipped(import_dir):
    (import_dir / "other.csv").write_text(
        EXPORT.replace("US technology:", "US healthcare:")
    )
    result = _collect(import_dir)
    assert result.records == []
    assert any("not 'US technology'" in w for w in result.warnings)


def test_rows_outside_the_window_are_excluded(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT + "2024-01-01,99\n")
    assert all(r.period_end >= REQUEST.period_start for r in _collect(import_dir).records)


def test_monthly_export_is_understood(import_dir):
    (import_dir / "m.csv").write_text(
        "Category: All categories\n\nMonth,US technology: (United States)\n2026-06-01,60\n"
    )
    record = _collect(import_dir).records[0]
    assert record.period_start == date(2026, 6, 1)
    assert record.period_end == date(2026, 6, 30)


def test_a_file_that_is_not_an_interest_export_is_reported(import_dir):
    (import_dir / "wrong.csv").write_text("Region,Interest\nCalifornia,100\n")
    result = _collect(import_dir)
    assert result.records == []
    assert any("Interest over time" in w for w in result.warnings)


def test_byte_order_mark_does_not_break_parsing(import_dir):
    (import_dir / "bom.csv").write_bytes(b"\xef\xbb\xbf" + EXPORT.encode())
    assert len(_collect(import_dir).records) == 3


def test_shipped_example_export_parses(import_dir):
    from pathlib import Path

    (import_dir / "example.csv").write_text(
        Path("examples/trends_interest_over_time_example.csv").read_text()
    )
    result = _collect(import_dir)
    assert len(result.records) == 13


def test_every_record_passes_schema_validation(import_dir):
    (import_dir / "tech.csv").write_text(EXPORT)
    for record in _collect(import_dir).records:
        record.validate()
        assert record.is_sample is False
