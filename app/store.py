"""SQLite evidence store.

Every record is validated before it is written, so an invalid record cannot reach the
report layer. `derived_from` references are checked against records already stored: a
finding that claims to rest on evidence which does not exist is a defect, and the cheapest
place to catch it is the write.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path

from .models import (
    AccessMethod,
    EvidenceRecord,
    InvalidRecord,
    RecordType,
    SourceType,
)
from . import sources

DEFAULT_DB = Path("data/evidence.db")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS evidence (
    record_id         TEXT PRIMARY KEY,
    record_type       TEXT NOT NULL,
    source_id         TEXT NOT NULL,
    source_type       TEXT NOT NULL,
    publisher         TEXT NOT NULL,
    access_method     TEXT NOT NULL,
    subject           TEXT NOT NULL,
    query_or_series_id TEXT NOT NULL,
    geography         TEXT NOT NULL,
    period_start      TEXT NOT NULL,
    period_end        TEXT NOT NULL,
    observed_at       TEXT,
    retrieved_at      TEXT NOT NULL,
    value             REAL,
    excerpt           TEXT,
    unit              TEXT,
    rights_note       TEXT NOT NULL,
    retention_rule    TEXT NOT NULL,
    limitation        TEXT NOT NULL,
    derived_from      TEXT NOT NULL DEFAULT '[]',
    is_sample         INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS evidence_subject_period
    ON evidence (subject, period_start, period_end);
CREATE INDEX IF NOT EXISTS evidence_source ON evidence (source_id);
"""


class EvidenceStore:
    def __init__(self, path: Path | str = DEFAULT_DB) -> None:
        self.path = Path(path)
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path, detect_types=0)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "EvidenceStore":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- writing ---------------------------------------------------------

    def add(self, record: EvidenceRecord) -> None:
        record.validate()
        sources.get(record.source_id)  # raises if the source is not registered

        missing = [r for r in record.derived_from if not self.exists(r)]
        if missing:
            raise InvalidRecord(
                f"{record.record_id} derives from records that are not stored: "
                f"{', '.join(missing)}"
            )

        self._conn.execute(
            """
            INSERT OR REPLACE INTO evidence VALUES (
                :record_id, :record_type, :source_id, :source_type, :publisher,
                :access_method, :subject, :query_or_series_id, :geography,
                :period_start, :period_end, :observed_at, :retrieved_at, :value,
                :excerpt, :unit, :rights_note, :retention_rule, :limitation,
                :derived_from, :is_sample
            )
            """,
            {
                "record_id": record.record_id,
                "record_type": record.record_type.value,
                "source_id": record.source_id,
                "source_type": record.source_type.value,
                "publisher": record.publisher,
                "access_method": record.access_method.value,
                "subject": record.subject,
                "query_or_series_id": record.query_or_series_id,
                "geography": record.geography,
                "period_start": record.period_start.isoformat(),
                "period_end": record.period_end.isoformat(),
                "observed_at": record.observed_at.isoformat() if record.observed_at else None,
                "retrieved_at": record.retrieved_at.isoformat(),
                "value": record.value,
                "excerpt": record.excerpt,
                "unit": record.unit,
                "rights_note": record.rights_note,
                "retention_rule": record.retention_rule,
                "limitation": record.limitation,
                "derived_from": json.dumps(list(record.derived_from)),
                "is_sample": int(record.is_sample),
            },
        )
        self._conn.commit()

    def add_all(self, records: list[EvidenceRecord]) -> None:
        for record in records:
            self.add(record)

    # -- reading ---------------------------------------------------------

    def exists(self, record_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM evidence WHERE record_id = ?", (record_id,)
        ).fetchone()
        return row is not None

    def get(self, record_id: str) -> EvidenceRecord | None:
        row = self._conn.execute(
            "SELECT * FROM evidence WHERE record_id = ?", (record_id,)
        ).fetchone()
        return _from_row(row) if row else None

    def query(
        self,
        *,
        subject: str | None = None,
        source_ids: list[str] | None = None,
        period_start: date | None = None,
        period_end: date | None = None,
    ) -> list[EvidenceRecord]:
        """Records overlapping the requested window.

        Overlap, not containment: a source that reports monthly must still surface in a
        one-month window whose edges do not line up with the release calendar.
        """
        clauses, params = [], []
        if subject:
            clauses.append("subject = ?")
            params.append(subject)
        if source_ids:
            clauses.append(f"source_id IN ({','.join('?' * len(source_ids))})")
            params.extend(source_ids)
        if period_start:
            clauses.append("period_end >= ?")
            params.append(period_start.isoformat())
        if period_end:
            clauses.append("period_start <= ?")
            params.append(period_end.isoformat())

        sql = "SELECT * FROM evidence"
        if clauses:
            sql += " WHERE " + " AND ".join(clauses)
        sql += " ORDER BY period_start, record_id"
        return [_from_row(r) for r in self._conn.execute(sql, params)]

    def delete_sample_records(self) -> int:
        """Drop Phase 1 sample data once real records exist.

        Records that derive from a sample record go with it: leaving them would create
        the dangling references the schema exists to prevent.
        """
        cursor = self._conn.execute(
            """
            DELETE FROM evidence WHERE is_sample = 1
               OR record_id IN (
                   SELECT e.record_id FROM evidence e, json_each(e.derived_from) d
                   WHERE d.value IN (SELECT record_id FROM evidence WHERE is_sample = 1)
               )
            """
        )
        self._conn.commit()
        return cursor.rowcount

    def subjects(self) -> list[str]:
        return [
            r[0]
            for r in self._conn.execute(
                "SELECT DISTINCT subject FROM evidence ORDER BY subject"
            )
        ]

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]


def _from_row(row: sqlite3.Row) -> EvidenceRecord:
    return EvidenceRecord(
        record_id=row["record_id"],
        record_type=RecordType(row["record_type"]),
        source_id=row["source_id"],
        source_type=SourceType(row["source_type"]),
        publisher=row["publisher"],
        access_method=AccessMethod(row["access_method"]),
        subject=row["subject"],
        query_or_series_id=row["query_or_series_id"],
        geography=row["geography"],
        period_start=date.fromisoformat(row["period_start"]),
        period_end=date.fromisoformat(row["period_end"]),
        observed_at=date.fromisoformat(row["observed_at"]) if row["observed_at"] else None,
        retrieved_at=datetime.fromisoformat(row["retrieved_at"]),
        value=row["value"],
        excerpt=row["excerpt"],
        unit=row["unit"],
        rights_note=row["rights_note"],
        retention_rule=row["retention_rule"],
        limitation=row["limitation"],
        derived_from=tuple(json.loads(row["derived_from"])),
        is_sample=bool(row["is_sample"]),
    )
