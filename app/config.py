"""Settings, read from the environment.

Credentials never live in the repository. `.env` is gitignored; `.env.example` records
which keys exist without their values.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ENV_FILE = Path(".env")


def _load_env_file(path: Path | None = None) -> None:
    """Read KEY=value lines into the environment without overwriting real env vars.

    A tiny parser rather than a dependency: the file holds a handful of API keys.

    `path` is resolved at call time, not bound as a default, so ENV_FILE stays the single
    authority over where the file lives.
    """
    path = path or ENV_FILE
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    fred_api_key: str | None
    trends_import_dir: Path
    db_path: Path
    request_timeout: float

    @property
    def has_fred_key(self) -> bool:
        return bool(self.fred_api_key)


def load(**overrides: object) -> Settings:
    _load_env_file()
    settings = Settings(
        fred_api_key=os.environ.get("FRED_API_KEY") or None,
        trends_import_dir=Path(
            os.environ.get("TRENDS_IMPORT_DIR", "data/imports/trends")
        ),
        db_path=Path(os.environ.get("EVIDENCE_DB", "data/evidence.db")),
        request_timeout=float(os.environ.get("REQUEST_TIMEOUT", "20")),
    )
    if overrides:
        return Settings(**{**settings.__dict__, **overrides})  # type: ignore[arg-type]
    return settings
