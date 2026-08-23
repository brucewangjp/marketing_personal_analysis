# US Product Opportunity Report Template

- Version: v0.2
- Status: Draft
- Updated: 2026-08-23

## 1. Purpose

Define the final report for the US Product Opportunity MVP. The report helps the project owner make product-development and product-selling decisions.

It must compare two views:

1. Products or categories with evidence of selling well now.
2. Emerging needs and product opportunities that may not yet be crowded.

The report must never present interest, discussion, or marketplace rank as verified national sales unless the source directly supports that claim.

## 1.1 Shared contract

The report header, terminology, evidence schema, confidence rubric, presentation rules,
and the gating rule for unavailable sources are defined once in
`docs/01_Product/00_Shared_Research_Foundation.md`. This template does not restate them.

Sections marked **Gated** below depend on a source that may not be connected for a given
category. Under the shared gating rule they render as *Insufficient evidence*, naming the
missing source and what it would have added.

## 2. Report header

The shared report header (shared foundation, section 7), with these subject-specific values:

- Subject: US category or product idea researched.
- Market scope: United States.
- Selected time range.

## 3. Executive summary

Answer these questions in a short, source-backed overview:

- What appears to be selling well now?
- Which customer need or conversation theme is emerging?
- Is the category mature, crowded, growing, or uncertain?
- What product direction is worth investigating next?
- What is the most important risk or evidence gap?

## 4. Current sales reality — **Gated: marketplace source**

### User-facing view

- Current products or categories with reliable sales or marketplace evidence.
- Signal type: direct sales evidence, marketplace ranking, review volume, search attention, or other.
- Time period and market coverage.
- Apparent competitive density and signs of saturation.

### Required limitation

Every value in this section is a **proxy**. Label which one it is — platform ranking,
review volume, listing density, or price spread — and state the period it covers and the
marketplace it came from. The report never presents any of them as national sales,
revenue, or market share, because no source in the first version measures those.

When no marketplace source is available for the category, this section renders as
insufficient evidence. Search interest is attention, not sales, and must not be
substituted here.

## 5. Emerging customer opportunity

### User-facing view

- Growing search or discussion topics.
- Recurring customer pain points, unmet needs, and desired improvements.
- Customer language that may suggest a product concept, feature, positioning, or sales message.
- Whether the opportunity is early, growing, mature, crowded, or too uncertain to assess.

### Required limitation

An emerging topic is a lead for further research, not proof that a product will sell.

## 6. Customer insight

For each important opportunity, show:

- Likely target customer group, only where evidence supports it.
- Desired outcomes and purchase motivations.
- Frustrations, objections, and reasons not to buy.
- Price, quality, convenience, trust, or differentiation themes where visible.
- Direct evidence summary and source limitations.

## 7. Competition and saturation — **Partly gated: marketplace source**

Classify the opportunity using evidence rather than intuition:

| State | Meaning | Needs |
| --- | --- | --- |
| Established demand | Strong evidence that the category sells, with known competition. | Marketplace source |
| Crowded | Demand exists, but many similar offers or repeated customer complaints indicate weak differentiation. | Marketplace source |
| Emerging | Attention or discussion is rising, but sales validation is still limited. | Search or discussion signals |
| Uncertain | Too little or conflicting evidence to classify. | — |

Without a marketplace source, only **Emerging** and **Uncertain** are assignable. The
report must not infer that a category is crowded from discussion volume alone.

## 8. Product and sales recommendation

The report should recommend an investigation direction, not claim certainty. It may suggest:

- Product concept to test.
- Feature or positioning angle to investigate.
- Customer group to research further.
- Differentiation hypothesis.
- Sales message to test.
- Evidence that must be collected before committing resources.

## 9. Evidence, confidence, and limits

Every material finding carries the fields and the confidence level defined by the shared
evidence schema and confidence rubric (shared foundation, sections 5 and 6).

Category-specific notes:

- A finding supported only by marketplace proxies cannot exceed **Low** confidence for any
  claim about demand, because rank and review count measure neither.
- A rising search term without corroboration is a lead, reported at **Low** confidence.
- An opportunity enters the ranked list at **Medium** or above; anything below is listed
  as a lead.

## 10. Monitoring list

End with items to monitor in the next report:

- Product categories or terms with changing attention.
- New customer pain points or feature requests.
- Signs of rising competition or market saturation.
- Missing sales, review, or discussion evidence.

## 11. Implementation instruction

This template, together with the shared contract it references, is the output contract for
the second MVP. Data sources are already fixed by
`docs/03_Data/02_Product_Opportunity_MVP_Data_Sources.md`; Claude Code designs the
evidence layout, analysis rules, and user interface backward from this report.

The second MVP reuses the collection, evidence store, analysis, and report shell built for
the first. See `docs/06_Development/00_Claude_Code_Implementation_Brief.md` for the
sequencing.

## Change log

| Version | Date | Change |
| --- | --- | --- |
| v0.1 | 2026-08-23 | Initial report template for the US product opportunity MVP. |
| v0.2 | 2026-08-23 | Referenced the shared contract instead of restating the header and confidence levels; marked section 4 gated and section 7 partly gated on the marketplace source; stated that marketplace values are proxies. |
