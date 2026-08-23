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

Specification stage. No application code yet. The directories `apps/`, `services/`,
`packages/`, `infra/`, `scripts/`, `tests/`, and `data/` are placeholders for the
implementation described in the brief above.

## Credentials

Data-source API keys are never committed. Keep them in a local `.env`, which `.gitignore`
excludes.
