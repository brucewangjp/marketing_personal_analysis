# marketing_personal_analysis

A personal market and consumer research workspace. It collects free public signals,
preserves the evidence behind every claim, and produces source-backed weekly reports for
two decision contexts:

- **Industry Sentiment** — how attention and group sentiment around US technology and
  healthcare are changing.
- **Product Opportunity** — what is selling in a US product category, what unmet need is
  emerging, and how crowded it is.

Its defining rule: a conclusion is either traceable to evidence with a stated period,
source, and confidence level, or the report says *insufficient evidence* instead.

This repository is document-first. The product is specified in `docs/` before any code is
written.

- **Documentation map:** [`docs/README.md`](docs/README.md)
- **Vision:** [`docs/00_Vision.md`](docs/00_Vision.md)
- **The binding contract:** [`docs/01_Product/00_Shared_Research_Foundation.md`](docs/01_Product/00_Shared_Research_Foundation.md)
- **Where implementation starts:** [`docs/06_Development/00_Claude_Code_Implementation_Brief.md`](docs/06_Development/00_Claude_Code_Implementation_Brief.md)

## Status

Phase 1 implemented: the report shell, the evidence store, the confidence rubric, and the
gating rule, running against clearly labeled sample evidence. No collectors yet — Phase 2
replaces the sample module with a FRED collector without changing anything downstream.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m app.seed        # load sample evidence into ./data/evidence.db
.venv/bin/uvicorn app.main:app      # http://127.0.0.1:8000
.venv/bin/python -m pytest
```

See [`docs/06_Development/01_Phase1_Technical_Design.md`](docs/06_Development/01_Phase1_Technical_Design.md)
for the stack choice, module map, and known limitations.

## Credentials

Data-source API keys are never committed. Keep them in a local `.env`, which `.gitignore`
excludes.
