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

Phases 1 to 3 implemented: the report shell, the evidence store, the confidence rubric,
the gating rule, the collectors that feed them, and the analysis that turns collected
signals into findings. Weekly scheduling and the public-discussion source are Phase 4.

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env                # add your free FRED API key
.venv/bin/python -m app.check       # confirm this machine can reach the sources
.venv/bin/python -m app.collect --subject "US technology" --window 3m
.venv/bin/uvicorn app.main:app      # http://127.0.0.1:8000

.venv/bin/python -m app.seed        # or: load sample evidence instead of collecting
.venv/bin/python -m pytest
```

Google publishes no API for Trends, so that source is collected from its public interface
and falls back to a manual CSV export when Google declines. A source that cannot be
collected at all is never fatal: the run reports it, and the report sections that needed
it say *insufficient evidence* naming what is missing.

See [`docs/06_Development/01_Phase1_Technical_Design.md`](docs/06_Development/01_Phase1_Technical_Design.md)
[`docs/06_Development/02_Phase2_Collectors.md`](docs/06_Development/02_Phase2_Collectors.md),
and [`docs/06_Development/03_Phase3_Analysis.md`](docs/06_Development/03_Phase3_Analysis.md)
for the stack choice, the collector contract, the analysis rules, and known limitations.

## Credentials

Data-source API keys are never committed. Keep them in a local `.env`, which `.gitignore`
excludes.
