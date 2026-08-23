"""Load the Phase 1 sample evidence into the store.

Run: .venv/bin/python -m app.seed
"""

from __future__ import annotations

import sys

from .sample import all_records
from .store import DEFAULT_DB, EvidenceStore


def main() -> int:
    records = all_records()
    with EvidenceStore(DEFAULT_DB) as store:
        store.add_all(records)
        total = store.count()
    print(f"Loaded {len(records)} sample records into {DEFAULT_DB} ({total} stored).")
    print("Every record is flagged is_sample=1; reports built from them say so.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
