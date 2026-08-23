# Decision Log

- Version: v0.1
- Status: Living document
- Updated: 2026-08-23

Decisions that are settled, so they are not re-litigated. Each row names where the
decision is specified in full. To reverse one, change the specifying document and add a
superseding row here — do not edit a decision in place.

| # | Date | Decision | Why | Specified in |
| --- | --- | --- | --- | --- |
| D1 | 2026-08-23 | The first release is a **personal workspace for the project owner**, not a multi-user or public product. | Narrows six user types to one, which makes the MVP buildable. | `docs/00_Vision.md` section 3 |
| D2 | 2026-08-23 | Two MVPs: **Industry Sentiment** (US technology and healthcare) and **Product Opportunity** (US categories). | Two decision contexts the owner actually has. | `docs/00_Vision.md` section 5 |
| D3 | 2026-08-23 | **US only, English only** for the first release. | Source availability and terms differ by jurisdiction; each new market needs its own review. | `docs/02_Research/01_Industry_Sentiment_MVP_Scope.md` section 4.1 |
| D4 | 2026-08-23 | **Weekly cadence**, with a one-month or three-month lookback window. | Matches how the owner would actually read the report. | `docs/01_Product/01_Industry_Sentiment_MVP.md` section 3.1 |
| D5 | 2026-08-23 | **Free sources first**, accessed in tier order: official API, official export, collection from public web pages, then manual import. A paid licence only after a free route has failed. | A free route exists for every source the MVPs need. Collection from public pages is permitted, not excluded. | `docs/01_Product/00_Shared_Research_Foundation.md` section 3.1 |
| D6 | 2026-08-23 | Three limits hold at every tier: **no login-walled content, no personal data, no stored full-text copies**. | These are what make collected evidence defensible and collectors durable. | `docs/01_Product/00_Shared_Research_Foundation.md` section 3.1 |
| D7 | 2026-08-23 | A single **shared contract** governs terminology, evidence schema, confidence rubric, report header, and gating. Where any document disagrees with it, it wins. | Two report templates were already drifting apart. | `docs/01_Product/00_Shared_Research_Foundation.md` |
| D8 | 2026-08-23 | A report section whose source is not connected renders as **insufficient evidence**, naming what is missing. Never omitted, never filled from an unrelated signal. | Both templates required sections that their first version could not populate. | `docs/01_Product/00_Shared_Research_Foundation.md` section 9 |
| D9 | 2026-08-23 | MVP2 reports **measured sales at the category level** from free official statistics, and **proxies at the product level**, where no free measured source exists. | Category sales are published free by Census, BEA, and BLS. Product-level unit sales are published by nobody, at any price. | `docs/03_Data/02_Product_Opportunity_MVP_Data_Sources.md` section 1 |
| D10 | 2026-08-23 | **MVP1 is built first. MVP2 reuses the same architecture and the same collection core** — it adds a collector and a report template, not a second system. | The two MVPs share three of four source types; a second stack would duplicate the collection, evidence, and analysis layers for no gain. | `docs/06_Development/00_Claude_Code_Implementation_Brief.md` section 1.1, `docs/04_Architecture/00_System_Architecture.md` section 1 |

## Still open

| # | Question | Blocks |
| --- | --- | --- |
| O1 | Which three to five US categories are used for MVP2's first demonstration reports? | MVP2's category-to-statistics mapping |
| O2 | Which public-discussion platform is integrated first? | The attitude and motivation sections of both reports |
| O3 | Which marketplace publishes a usable free API for the chosen categories? | MVP2's product-level view |
| O4 | Should the interface open on a topic page or a research-question page? | MVP1's first screen |
| O5 | Data storage and retention policy for the evidence store. | Phase 2 |

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Recorded the ten decisions settled so far and the five questions still open. |
