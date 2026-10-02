# Audit notes

## Manual independent example

For a two-year building scenario:

- Capital: 1,000 AUD
- Annual electricity: 100 kWh × 0.30 AUD/kWh + 365 × 1 AUD/day = 395 AUD
- Annual water: 10 kL × 2 AUD/kL + 100 AUD fixed = 120 AUD
- Annual maintenance: 20 AUD
- All escalation: zero; discount: 10%; no replacements, disposal or residual

Annual expense = 535 AUD. The independently calculated LCC is:

`1,000 + 535 / 1.1 + 535 / 1.21 = 1,928.5123966942149 AUD`

`test_manual_example` compares this expression with the engine, rather than mirroring its annual loop.

## Scenario boundaries

Same floor area, floors, occupancy and project use in both scenarios. Only declared capital, package consumption reductions, maintenance adjustment, replacements and terminal amounts differ. Quality and system names are descriptive. Selected features never silently generate a construction price or savings percentage.

Total construction input takes priority over rate per square metre. Detailed construction equals the sum of material quantities × unit prices plus the entered remaining scope. Material maintenance is additional to annual building maintenance. A sustainable total quote takes priority over the percentage premium.

The conventional maintenance basis is used before applying a single sustainable reduction. This is a comparison convention, not an engineering service-life model. Explicit maintenance totals and service lives should come from project evidence.

## Data hierarchy

Project inputs determine geometry and costs. Verified official JSON records determine selected residential tariff values. Project PDFs inform fallback research assumptions only. No RAG passage can override the source register or formulas.

Confidence is qualitative: demo inputs → low/indicative; actual declared project capital/consumption and performance plus applicable official prices → high; remaining cases → medium. This is provenance confidence, not a statistical confidence interval.

## Timing and terminal treatment

The model uses nominal price growth and nominal discount rates. Escalation occurs once before year-one expenditure. Constant-price studies can set escalation to zero and use a consistently real discount rate. Water, maintenance, other expenses and terminal values have independent growth assumptions. Editable discount and escalation rates are labelled user assumptions, including when they start at literature defaults.

Replacement at the retirement date is omitted. Disposal and residual values occur at the end of each selected horizon. No residual fraction of a recently replaced component is inferred. A positive residual input can materially change results and needs independent support.

The first crossover is reported even when later replacement/terminal cash flows reverse it. Review reversal years and the complete discounted series.

## Metering and tariff scope

AER flat-rate caps cover residential supply in the selected zone. Time-of-use, demand charges, controlled loads and commercial tariffs require a different tariff model or an explicitly supplied equivalent project rate. Do not model a whole apartment development as one residential meter without validating the billing boundary.

Sydney Water inputs assume metered drinking water. Standard versus drought pricing, wastewater connection and stormwater catchment must be confirmed from project evidence. Fixed charges do not scale down with water savings. Provider maximum quarterly charges use 92 days; the model annualises to 365 days.

## Evidence lifecycle

All three PDFs are retained locally with the original page numbering. Chroma persists document text, embeddings, page numbers and document hashes. Structured official metadata is indexed separately, and source dates/categories accompany retrieved chunks. Feature hashing is lexical retrieval; an optional local Sentence Transformers model enables semantic retrieval after an explicit installation and re-index. Uploaded PDFs are added to the same knowledge base.

Analysis optionally adds one domain-restricted Tavily search to the PDF context, then sends retrieved excerpts and non-identifying scenario facts to Gemini for interpretation. Web snippets are context, not verified tariff updates. No retrieved instruction can modify calculations. Financial summaries remain deterministic; model-generated monetary claims are rejected. Missing keys and provider failures are explicitly reported with local/template fallback.

Saved results capture selected rates. Chat what-ifs reuse those rates so later cache changes do not alter the financial baseline. Questions containing multiple percentages are not silently interpreted as a single change.

The update command performs at most three restricted Tavily searches and checks original official pages. Failed verification cannot overwrite the current cache. Adopting a new financial-year table needs a reviewed extraction rule and an effective date, not an LLM answer.
