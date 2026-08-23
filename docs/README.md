# Documentation map

This repository is a document-first project. Product decisions are documented before
implementation tasks are handed to Claude Code.

**Start here:** `06_Development/00_Claude_Code_Implementation_Brief.md` is the entry point
for implementation. `01_Product/00_Shared_Research_Foundation.md` is the binding contract
that every other document defers to.

## Current documents

| Document | What it fixes |
| --- | --- |
| `00_Vision.md` | Product vision, the two MVPs, scope, and success criteria. |
| `01_Product/00_Shared_Research_Foundation.md` | **The shared contract**: terminology, source access policy, evidence schema, confidence rubric, report header, gating rule. |
| `01_Product/01_Industry_Sentiment_MVP.md` | MVP1 requirements: US technology and healthcare sentiment. |
| `01_Product/02_US_Product_Opportunity_MVP.md` | MVP2 requirements: US product opportunity, two-view model. |
| `02_Research/01_Industry_Sentiment_MVP_Scope.md` | MVP1 industry scope, themes, and exclusions. |
| `03_Data/01_Industry_Sentiment_MVP_Data_Sources.md` | MVP1 sources, access tiers, and safeguards. |
| `03_Data/02_Product_Opportunity_MVP_Data_Sources.md` | MVP2 sources, marketplace proxies, and category criteria. |
| `04_Architecture/00_System_Architecture.md` | Shared core, modules, data flow, development order. |
| `05_Design/01_Industry_Sentiment_Report_Template.md` | MVP1 output contract. |
| `05_Design/02_US_Product_Opportunity_Report_Template.md` | MVP2 output contract. |
| `06_Development/00_Claude_Code_Implementation_Brief.md` | Build order, boundaries, phases, definition of done. |

## Folders

| Folder | Purpose |
| --- | --- |
| `00_Foundation` | Reserved for foundation documents. `00_Vision.md` sits at the `docs` root as the project-level starting point. |
| `01_Product` | Product requirements, user journeys, and feature definitions. |
| `02_Research` | Target users, market research, data-source research, and assumptions. |
| `03_Data` | Data model, source inventory, collection rules, quality, privacy, and rights. |
| `04_Architecture` | System architecture, APIs, security, and technical decisions. |
| `05_Design` | Information architecture, UX flows, and interface specifications. |
| `06_Development` | Implementation plans, Claude Code task briefs, and acceptance criteria. |
| `07_Operations` | Testing, release, monitoring, and operating procedures. |

## Conventions

**File naming** — `NN_Subject.md`, where `NN` marks which product the document belongs to:

| Prefix | Meaning |
| --- | --- |
| `00_` | Shared across both MVPs, or project-level. |
| `01_` | Industry Sentiment MVP. |
| `02_` | Product Opportunity MVP. |

**Document header** — every document starts with `Version`, `Status`, and `Updated`.

**Versioning** — every content change adds a change-log row *and* bumps the `Version` in
the header. The two must always agree; a header that lags its change log has caused real
confusion in this repository before.

**Status values** — `Draft`, `Approved for MVP`, `Ready for implementation planning`,
`Deferred`, `Superseded by <path>`.

**Precedence** — where any document disagrees with
`01_Product/00_Shared_Research_Foundation.md`, the shared foundation wins.
