"""The evidence record and its field rules.

Implements the shared evidence schema in
`docs/01_Product/00_Shared_Research_Foundation.md` section 5. The rules here are the
enforcement point for the project's central principle: an interpretation must name the
records it rests on, so "separate evidence from interpretation" is checkable rather than
a style guideline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class RecordType(str, Enum):
    OBSERVATION = "observation"
    DERIVED_METRIC = "derived_metric"
    INTERPRETATION = "interpretation"


class SourceType(str, Enum):
    MACRO_INDICATOR = "macro_indicator"
    SEARCH_INTEREST = "search_interest"
    PUBLIC_DISCUSSION = "public_discussion"
    MARKETPLACE = "marketplace"
    OFFICIAL_STATISTIC = "official_statistic"


class AccessMethod(str, Enum):
    """Access tiers from the shared source selection policy, section 3.1."""

    API = "api"
    EXPORT = "export"
    WEB_COLLECTION = "web_collection"
    MANUAL = "manual"


class InvalidRecord(ValueError):
    """A record that the evidence schema does not permit to be stored."""


_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_.:-]*$")

# Types that must name the records they rest on.
_DERIVED_TYPES = (RecordType.DERIVED_METRIC, RecordType.INTERPRETATION)


@dataclass(frozen=True)
class EvidenceRecord:
    record_id: str
    record_type: RecordType
    source_id: str
    source_type: SourceType
    publisher: str
    access_method: AccessMethod
    subject: str
    query_or_series_id: str
    geography: str
    period_start: date
    period_end: date
    retrieved_at: datetime
    rights_note: str
    retention_rule: str
    limitation: str
    value: float | None = None
    excerpt: str | None = None
    unit: str | None = None
    observed_at: date | None = None
    derived_from: tuple[str, ...] = ()
    is_sample: bool = False

    def __post_init__(self) -> None:
        self.validate()

    # -- validation ------------------------------------------------------

    def validate(self) -> None:
        for name in (
            "record_id",
            "source_id",
            "publisher",
            "subject",
            "query_or_series_id",
            "geography",
            "rights_note",
            "retention_rule",
            "limitation",
        ):
            if not str(getattr(self, name) or "").strip():
                raise InvalidRecord(f"{name} is required and must not be blank")

        if not _ID_RE.match(self.record_id):
            raise InvalidRecord(
                f"record_id {self.record_id!r} must be lowercase alphanumeric "
                "with . _ : - separators"
            )

        if self.value is None and not str(self.excerpt or "").strip():
            raise InvalidRecord("a record must carry either a value or an excerpt")

        if self.value is not None and not str(self.unit or "").strip():
            raise InvalidRecord("unit is required for any numeric value")

        if self.period_start > self.period_end:
            raise InvalidRecord("period_start must not be after period_end")

        if self.record_type in _DERIVED_TYPES and not self.derived_from:
            raise InvalidRecord(
                f"a {self.record_type.value} must name the records it rests on; "
                "an interpretation with an empty derived_from is invalid"
            )

        if self.record_type is RecordType.OBSERVATION and self.derived_from:
            raise InvalidRecord(
                "an observation is stored verbatim and cannot derive from other records"
            )

        if self.record_id in self.derived_from:
            raise InvalidRecord("a record cannot derive from itself")

    # -- presentation ----------------------------------------------------

    @property
    def period_label(self) -> str:
        if self.period_start == self.period_end:
            return self.period_start.isoformat()
        return f"{self.period_start.isoformat()} to {self.period_end.isoformat()}"

    @property
    def display_value(self) -> str:
        """What the reader sees. Never a bare number without its unit."""
        if self.value is None:
            return (self.excerpt or "").strip()
        shown = f"{self.value:g}"
        return f"{shown} {self.unit}".strip()


@dataclass
class Finding:
    """A claim in a report, with the evidence it rests on.

    `confidence` is assigned by `app.confidence`, never set by hand, so the rubric is
    applied uniformly rather than by the judgement of whoever wrote the section.

    `record_type` is None for text that is not a claim about the world — a monitoring
    instruction, for instance. Labelling such text as an observation would misuse the
    one distinction the whole report rests on.
    """

    statement: str
    record_type: RecordType | None
    evidence: list[EvidenceRecord] = field(default_factory=list)
    confidence: str = ""
    confidence_reason: str = ""
    limitation: str = ""

    @property
    def is_interpretation(self) -> bool:
        return self.record_type is RecordType.INTERPRETATION

    @property
    def is_claim(self) -> bool:
        """False for instructions and prompts, which carry no evidence standard."""
        return self.record_type is not None
