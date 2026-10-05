# GreenCost Sydney: Project Document

**AI-assisted Conventional vs Sustainable Building Life-Cycle Cost (LCC) Analysis Web Application**

| | |
|---|---|
| Version | 1.1 (draft for review) |
| Scope | Greater Sydney, NSW, Australia (other cities designed for later) |
| Status | Planning complete; backend engine and frontend scaffold exist; frontend untested |
| Commercial terms | Intentionally excluded from this document |
| Context | Academic research project (UTS Engineering Project Preparation 42908); the website is the study's analysis tool and a public tool |
| Companion files | `GreenCost-Sydney-Agent-Build-Brief.md` (wins where the two differ) |

---

## Table of contents
1. Purpose and vision
2. Scope
3. Users and use cases
4. Functional requirements (modules)
5. Non-functional requirements
6. Domain data and baseline
7. Calculation methodology
8. System architecture
9. API specification
10. Data model
11. User interface design
12. AI (Gemini) and live research (Tavily) design
13. Reporting
14. Multi-city extensibility
15. Quality assurance and validation
16. Security, privacy and legal
17. Risks and mitigations
18. Delivery roadmap
19. Current status
20. Open decisions
21. Glossary
22. Appendix: known issues in earlier drafts

---

## 1. Purpose and vision

### 1.1 Problem
Residential buyers and builders concentrate on the construction quote and underweight 30 to 50 years of electricity, water, maintenance and replacement costs. Upfront construction typically represents only 20% to 40% of whole-life cost, so decisions based on day-one price can be financially poor.

### 1.2 Solution
A web application that takes a building description and produces two scenarios, a **Conventional Build** and a **Sustainable / High-Performance Build**. It calculates the whole-life cost of each, the difference, the break-even year and the sensitivity of the answer to financial assumptions, and explains the result in plain language.

### 1.3 Design principles
1. **Deterministic maths.** Financial results come only from the calculation engine. The same inputs always give the same outputs.
2. **AI explains, never calculates.** Gemini receives computed results and writes the explanation. It cannot change or invent figures.
3. **Transparent assumptions.** Every input has a source and an effective date, and is visible to the user.
4. **Ranges over single numbers.** Results are shown with sensitivity so users see uncertainty.
5. **Estimates, not advice.** The tool supports decisions; it does not replace a certified quantity surveyor.

### 1.4 Research context
The app supports a secondary-data comparative study of sustainable and conventional buildings in Sydney (baseline 40 years, 5% discount rate, 3% energy escalation). It must help answer the study's sub-questions:

| Sub-question | App output |
|--------------|-----------|
| (a) How much operating cost do sustainable buildings save? | Operating-cost saving by category (energy, water, maintenance) |
| (b) How do discount rate and energy escalation affect results? | 4 × 4 sensitivity grids for 30, 40, 50 years |
| (c) What is the percentage difference in total LCC? | Headline percentage, always worded "under the stated assumptions" |
| (d) Which cost elements drive long-term savings? | Cost-category and per-measure contribution charts |
| (e) How can LCC aid planning? | Templated planning implications and limitations |

---

## 2. Scope

### 2.1 In scope (Ready Client Prototype, "Option 1" modules)
Responsive dashboard; building input and validation; conventional construction cost engine; LCC calculator; sustainable scenario analysis; comparison; sensitivity analysis; live research integration with visible sources; Gemini explanation; charts; downloadable report; literature mode; research-question outputs.

### 2.2 Later scope (Advanced ML and Data Prototype, "Option 2" modules)
Project catalogue with search and filters; structured dataset preparation and feature engineering; machine-learning construction cost prediction (regression models with MAE, RMSE and R² evaluation); multi-configuration sustainable optimisation; expanded sensitivity variables; advanced analytics dashboard. This depends on obtaining enough project-level cost data. The system must not claim accuracy that the data cannot support.

### 2.3 Out of scope
Certified cost estimates, construction tenders, engineering certification, regulatory approval, professional financial advice, and unlimited third-party API usage.

### 2.4 Geographic scope
Greater Sydney only at launch.

---

## 3. Users and use cases

| User | Goal | Key needs |
|------|------|-----------|
| Homeowner / owner-builder | Decide whether to pay for sustainability upgrades | Simple inputs, clear answer, plain English |
| Builder / designer | Show clients the lifetime value of options | Custom prices, client-ready report |
| Quantity surveyor | Check or support an estimate | Transparent formulas, exportable data |
| Student / researcher | Demonstrate LCC methodology | Documented method, sources, limitations |

**Recommended launch audience:** homeowners and owner-builders, with a "show workings" mode for professionals (to be confirmed, see section 20).

### Primary use cases
- UC1: Run a new analysis for a proposed building.
- UC2: Change financial assumptions and see results update.
- UC3: Compare individual sustainability measures.
- UC4: Read an AI explanation of results.
- UC5: Export a report and raw cash-flow data.
- UC6: Reopen a previous analysis (needs accounts or saved storage).

---

## 4. Functional requirements (modules)

### M1. User interface and dashboard
- Responsive layout with header or sidebar navigation.
- Pages: Home, New Analysis, Results Dashboard, Previous Analyses, Methodology, Assumptions.
- Project overview cards and a Conventional vs Sustainable comparison view.
- Clean presentation suitable for client or academic demonstration.

### M2. Building input and configuration
**Inputs:** location (Sydney suburb or postcode), building category and type, floor area (120 to 450 m² slider; engine accepts a wider range), storeys, bedrooms, bathrooms, kitchens, parking, construction quality, structural system, wall system, roof system, glazing, HVAC, hot water, insulation, solar system, rainwater system, water-efficient fixtures, lighting, other sustainable features.

**Progressive disclosure in four stages:**
1. Geometry and quality
2. Envelope and active systems
3. Tariffs and operation
4. Financial assumptions

**Validation:** type, range and consistency checks (for example postcode must be four digits and in the service area; solar size 0 to 13.2 kW) with clear error messages before any calculation runs.

### M3. Conventional construction cost engine
Estimates initial cost with a **component-level breakdown**: site preparation, structural works, flooring, roofing, external walls, windows and doors, electrical, plumbing, HVAC, internal finishes, fixtures, other. Uses configurable cost rules and dated Sydney/NSW rate assumptions, not a trained model, in the prototype.

### M4. Life-cycle cost calculator
Computes for each scenario: initial construction and installation, annual energy, annual water, maintenance, replacement of components at milestone years, disposal or demolition allowance (required input with a cited default, with salvage), and present-value discounting. Supports 30, 40 and 50-year horizons.

### M5. Sustainable building analysis
Generated from the same building description. Each measure has **its own** cost premium and its own effect on energy, water, maintenance and replacements. The system must not apply a single flat percentage reduction. Measures:
- Enhanced insulation
- High-performance glazing
- Efficient HVAC
- Efficient hot water (heat pump)
- Solar PV
- Efficient lighting
- Smart controls
- Water-efficient fixtures
- Rainwater harvesting
- Sustainable material alternatives

Interactions between measures (for example better insulation reduces the HVAC saving) must be modelled or explicitly flagged as a limitation.

### M6. Comparison
Outputs: initial investment difference, whole-life cost for each scenario (broken into energy, water, maintenance, replacement, end-of-life), LCC difference, percentage saving, break-even year, long-term advantage, and Equivalent Annual Uniform Cost.

### M7. Sensitivity analysis
Variables: horizon (30, 40, 50 years), discount rate (4%, 5%, 6%, 7%), energy escalation (2%, 3%, 4%, 5%). Results recalculate automatically when assumptions change. Displayed as a heatmap per horizon (4 × 4 grid).

### M8. Live research integration
Retrieves current reference information (electricity and water rates, construction indices, standards, regulations) through a search API such as Tavily. Sources are displayed. Live data **supplements** the dated assumptions table and never silently overrides calculation inputs; the user or an administrator approves any change.

### M9. Gemini explanation
Explains results, major cost drivers, sustainable advantages, break-even behaviour and sensitivity. Three paragraphs: (1) capital delta, first-year saving, lifetime saving; (2) cost drivers; (3) sensitivity risks. Australian English. Uses only provided figures.

### M10. Charts and visualisation
Total cost comparison; construction cost comparison; energy, water and maintenance comparisons; cumulative LCC with the break-even crossover; cost distribution; annual outflows stacked by category.

### M11. Report generation
Downloadable report (see section 13), plus raw CSV of the cash flows.

### M12. Literature mode
A second calculation mode that applies the study proposal's percentage ranges (capital premium 5-15%; energy saving 20-40%; water saving 30-50%; maintenance saving 10-25%) to the conventional year-1 costs, reducible parts only. Always shows Low / Mid / High scenarios side by side with the literature's stated 10-20% total-LCC reduction. Outputs are labelled "literature-parameter scenarios", not predictions.

### M13. Research outputs
Cost-category contribution (initial, energy, water, maintenance, replacements, disposal less salvage), operating-cost share of LCC, a literature-versus-model comparison panel, and a "Research answers" tab mapping sub-questions (a) to (e) to computed results. Exports of the method and assumptions table for use in a thesis appendix.

### M14. Local pricing and quantity takeoff
The user enters a Greater Sydney postcode, which resolves to a pricing zone, electricity network and climate zone. A takeoff converts the house description into quantities per measure (for example wall insulation area from perimeter, wall height and glazing share). Measure costs are quantity × price plus labour and allowances, and the premium is the upgrade minus the code-minimum cost. Prices come from a **cached-live** pipeline: Tavily searches run on a schedule and in the background, results are validated and cached, and the user sees each price instantly with a badge (Live, Cached, Default, Indicative, Your price), its age and its sources. Installed systems are shown as indicative ranges. Users may enter their own quote or quantity. Full rules are in `GreenCost-Sydney-Pricing-and-Takeoff-Spec.md`.

---

## 5. Non-functional requirements

| Area | Requirement |
|------|-------------|
| Performance | Calculation under 100 ms for a standard run; sensitivity grids under 1 s |
| Accuracy | Baseline reproduces an independent spreadsheet to the cent |
| Reproducibility | Each result stores the assumption-set version used |
| Usability | Works on phones; usable without technical knowledge |
| Accessibility | Keyboard navigation, sufficient contrast, labelled inputs |
| Reliability | Graceful errors if Gemini or search services are unavailable; the calculator still works |
| Maintainability | Typed code (TypeScript, Pydantic), tests in CI, documented modules |
| Portability | City data separate from code (section 14) |

---

## 6. Domain data and baseline

### 6.1 Reference house
220 m² gross floor area, single storey, 4 bedrooms, 2 bathrooms, double lock-up garage, detached, Greater Sydney.

### 6.1a Definition of "conventional" (provisional; confirm with supervisor)
The original specification used a pre-2023 6-star house (single glazing, R1.5 walls) as the conventional case. The project's own literature review states that over 75% of new NSW homes already meet 7-star, at an uplift of about $4,300, so that comparator risks being a straw man. This document therefore defines **Conventional = a code-minimum new build** meeting the current minimum energy requirement for new NSW homes (7-star NatHERS under the current NCC/BASIX; exact provisions to be verified and cited) and **Sustainable = the same house with selected measures that go beyond code**. The old specification is kept as a **Legacy preset** for regression tests and for users who want "old build versus high performance". Both presets are selectable and clearly labelled. The table in 6.2 describes the Legacy preset.

### 6.2 Specification comparison

| Component | Conventional | Sustainable |
|-----------|--------------|-------------|
| Build rate | $2,400/m² ($528,000) | $2,640/m² ($580,800), +$52,800 (+10%) |
| Glazing | Single clear aluminium (Uw about 5.8, SHGC about 0.72) | Double-glazed Low-E argon, thermally broken (Uw about 1.8, SHGC about 0.38) |
| Insulation | R1.5 wall, R3.5 ceiling | R2.5 wall, R5.0 ceiling plus reflective sarking |
| HVAC | Fixed-speed ducted split (EER about 3.1) | Inverter multi-zone heat pump (EER 4.6 or higher) |
| Hot water | Electric storage or instant gas | CO₂ air-source heat pump (COP 4.2 or higher) |
| Solar PV | None | 6.6 kW with 5 kW inverter |
| Water | Mains, 3-star WELS | 5,000 L plumbed tank, 5-star WELS |
| Airtightness | About 10 to 12 ACH at 50 Pa | About 3 to 4 ACH at 50 Pa, passive shading |

Indicative upgrade components from the earlier specification (to be re-sourced): glazing about $5,500, insulation about $3,200, HVAC about $4,500, hot water about $2,800, solar about $5,800, rainwater about $4,200, airtightness and shading about $3,800.

### 6.3 Tariffs and rates (to be verified and dated)
- Electricity: 32.5 ¢/kWh import plus 150 ¢/day supply charge ($547.50/year).
- Solar feed-in: 5.0 ¢/kWh.
- Water: $3.41/kL plus $987.16/year fixed charges.

### 6.4 Year 1 operating costs

| Item | Conventional | Sustainable |
|------|-------------:|------------:|
| Net energy | $2,237.50 | $808.75 |
| Water | $1,669.16 | $1,379.31 |
| Maintenance | $2,640.00 (0.50% of capex) | $2,090.88 (0.36% of capex) |
| **Total** | **$6,546.66** | **$4,278.94** |

Year 1 saving: **$2,267.72** (34.6%).

Energy detail: conventional imports 5,200 kWh; sustainable imports 1,450 kWh and exports 4,200 kWh. Water: 200 kL versus 115 kL.

### 6.5 Replacements (fixed real amounts)

| Year | Conventional | Sustainable |
|------|--------------|-------------|
| 10 | none | Rainwater pump $750 |
| 12 | Hot water unit $1,800 | Solar inverter $2,200 |
| 15 | Ducted AC compressor $3,500 | Heat pump core $3,800 |

### 6.6 Escalation (real, above CPI)
Energy 3%, water 2%, maintenance 1.5%.

---

## 7. Calculation methodology

Follows ISO 15686-5 (life-cycle costing of constructed assets).

### 7.1 Framework
"40-5-3": 40-year horizon, 5.0% real discount rate, 3.0% real energy escalation. Alternative horizons 30 and 50 years. Real rates, so general inflation is excluded.

### 7.2 Formulas
- Discount factor: `DF_t = 1 / (1 + r)^t`
- Energy cost: `E_t = E_1 × (1 + e)^(t−1)`
- Water cost: `W_t = W_1 × (1 + 0.02)^(t−1)`
- Maintenance cost: `M_t = M_1 × (1 + 0.015)^(t−1)`
- Whole-life cost: `LCC = C_init + Σ DF_t × (E_t + W_t + M_t) + Σ DF_tk × R_k + DF_N × (Disposal − Salvage)`
- LCC difference: `ΔLCC = LCC_conv − LCC_sust`
- Break-even year `t*`: first year where cumulative discounted savings (operating plus replacement) are at least the capital premium
- Equivalent Annual Uniform Cost: `EAUC = LCC × r(1+r)^N / ((1+r)^N − 1)`

### 7.3 Baseline result (from the engine)
At 40-5-3 with the reference house:

| Metric | Result |
|--------|--------|
| Capital premium | $52,800 |
| Year 1 saving | $2,267.72 |
| **Break-even year** | **37** |
| **40-year net lifecycle benefit** | **about +$2,987** |
| Sustainable EAUC | about $39,700/year |

The earlier specification stated Year 33 and +$7,741. Those figures cannot be reproduced from the specification's own formulas and inputs and should not be used (see appendix).

**Interpretation:** the sustainable build wins at the baseline but narrowly. The result is sensitive to discount rate and energy escalation, so the product leads with ranges and scenarios.

### 7.3a Comparison with the literature (verified from the engine)
| Item | Result |
|------|--------|
| Conventional whole-life cost (legacy baseline) | $684,903 |
| Sustainable whole-life cost | $681,917 |
| Difference | $2,987 (0.44%) |
| Operating share of conventional LCC | about 23% |

The literature review states that operating costs are 60-80% of LCC and that sustainable buildings reduce total LCC by 10-20%. Applying the literature's own percentage ranges to this house gives a very different picture. Rough check (simplified: percentages applied to whole bills, replacements and disposal excluded, 40-5-3):

| Scenario | Premium | Energy / water / maintenance saving | Net LCC difference | Break-even |
|----------|--------:|------------------------------------|-------------------:|-----------|
| Low savings, high premium | 15% | 20 / 30 / 10% | -$57,700 (-8.5%) | not reached |
| Mid | 10% | 30 / 40 / 20% | -$12,800 (-1.9%) | not reached |
| High savings, low premium | 5% | 40 / 50 / 25% | +$28,600 (+4.2%) | Year 15 |

Negative means the sustainable case costs more. Even the most favourable literature case gives about 4% for this house, below the 10-20% cited.

**Possible reasons (to investigate, not conclusions):** the 60-80% operating share probably comes from commercial or institutional buildings; a house has a large capital cost and a small operating-cost stream; percentages applied to bills that include large fixed charges overstate savings; studies use different system boundaries and real versus nominal rates. **Handling:** report the result honestly, explain the differences in the methodology and limitations, and discuss with the supervisor. Do not tune inputs to match the literature.

### 7.4 Modelling notes and limitations
- Replacements are fixed real amounts in the milestone year.
- Disposal and salvage are in the formula but are not yet in the engine.
- The solar model is calibrated to the specification's $808.75 net energy figure; its underlying basis (generation, self-consumption, export) needs documenting.
- Tariff structures are assumed constant over decades.
- Measure interactions are not yet modelled.

---

## 8. System architecture

```
Browser (Next.js App Router, TypeScript, Tailwind, Recharts, Lucide)
      │ HTTPS / JSON
      ▼
FastAPI gateway (Pydantic v2, CORS, rate limiting, structured logging)
  ├─ Calculation engine   NumPy, pure functions, no I/O
  ├─ Region and assumptions service   versioned, dated, sourced data
  ├─ Pricing service      Postcode zones, house takeoff, Tavily cached-live prices (see pricing spec)
  ├─ Narrative service    Gemini 2.5 Flash, figures passed in
  └─ Report service       HTML to PDF
      │
PostgreSQL (accounts, saved analyses, assumption sets, audit log)
```

### Technology
| Layer | Choice |
|-------|--------|
| Frontend | Next.js 14/15, React, TypeScript, Tailwind CSS, Recharts, Lucide-react |
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2, NumPy (2.4.x) |
| AI | Google Gemini API (gemini-2.5-flash) |
| Research | Tavily API or equivalent |
| Database | PostgreSQL (for example Supabase) |
| Reporting | HTML templates rendered to PDF |
| Config | `.env`: `GEMINI_API_KEY`, `TAVILY_API_KEY`, `PORT=8000` |

### Key rules
1. The engine is pure and deterministic and has no knowledge of the city or the web.
2. API keys stay on the server.
3. The AI receives numbers and returns text only.
4. Every result records the assumption-set version.

---

## 9. API specification

| Method and path | Purpose |
|-----------------|---------|
| `GET /health` | Liveness check |
| `POST /api/v1/calculate/lcc` | Year-by-year cash flows, LCC totals, break-even, EAUC |
| `POST /api/v1/sensitivity/matrix` | 4 × 4 grids for 30, 40 and 50 years |
| `POST /api/v1/narrative/explain` | Gemini explanation from computed results |
| `POST /api/v1/report/pdf` | PDF report (later phase) |
| `GET /api/v1/assumptions` | Current dated assumptions and sources (later phase) |
| `GET/POST /api/v1/analyses` | Saved analyses (later phase) |

### Calculation request (key fields)
`postcode`, `floor_area`, `storeys`, `quality_tier` (`project_home` | `custom_mid` | `architectural`), `capex_premium_pct`, `solar_capacity_kw`, `has_rainwater_tank`, `lifespan_years` (30 | 40 | 50), `real_discount_rate`, `real_energy_escalation`, optional `custom_electricity_tariff`, `custom_water_tariff`.

### Calculation response (key fields)
`initial_capex_conv`, `initial_capex_sust`, `initial_capex_premium`, `total_lcc_conv`, `total_lcc_sust`, `net_lifecycle_savings`, `percentage_savings`, `break_even_year`, `eauc_conv`, `eauc_sust`, and `annual_schedules[]` with per-year energy, water, maintenance and replacement amounts for both builds, nominal savings, discount factor, discounted savings, cumulative discounted savings and net financial position.

### Conventions
Validated with Pydantic v2 (`pattern=` for regex; `Literal[...]` for fixed choices). Errors return clear messages. Rate limiting and CORS restricted to the frontend origin.

---

## 10. Data model (from the accounts phase)

| Table | Key fields |
|-------|-----------|
| `users` | id, email, created_at |
| `analyses` | id, user_id, name, inputs (JSON), results (JSON), assumption_set_id, created_at |
| `assumption_sets` | id, region_id, version, valid_from, data (JSON) |
| `assumption_items` | id, set_id, key, value, unit, source, source_date |
| `regions` | id (for example `sydney_nsw`), name, status |
| `research_snapshots` | id, query, results, retrieved_at |
| `audit_log` | id, actor, action, detail, timestamp |

---

## 11. User interface design

### Pages
- **Home:** value statement and call to action.
- **Calculator:** four-stage input panel and results dashboard.
- **Previous analyses:** list of saved runs (later phase).
- **Methodology:** how the calculation works.
- **Assumptions:** every input with source and date.

### Results dashboard
1. KPI ribbon: capital delta, net lifetime benefit, break-even year, EAUC.
2. Cumulative net position chart with break-even marker.
3. Annual outflows stacked bar chart (energy, water, maintenance, replacements).
4. Sensitivity heatmap with the selected horizon.
5. AI advisory panel (streamed text).
6. Export: PDF and CSV.

### UX rules
- Defaults pre-filled from the reference house so a first run needs few clicks.
- Show units everywhere; format money for Australia.
- Colour is never the only signal (for example surplus and deficit also carry text).
- Show a clear "estimate" notice on results.

---

## 12. AI (Gemini) and live research (Tavily) design

### 12.1 Gemini
- System role: senior quantity surveyor and building economist, Sydney.
- Strict constraints: do not recalculate or invent figures; exactly three paragraphs; Australian English.
- Input: computed JSON (summary and Year 1 detail, plus sensitivity).
- Safeguards: numbers in the output should be checked against the input; if unavailable, the app still shows all results.

### 12.2 Live research
- Purpose: keep reference data current and show evidence.
- Sources to prefer: AER, IPART, Sydney Water, NSW Government, ABS, Rawlinsons-type indices.
- Behaviour: results are cached with timestamps; sources are shown; proposed changes to assumptions need approval before they affect calculations.

---

## 13. Reporting

Sections of the downloadable report:
1. Header and building metadata
2. Executive summary (KPIs)
3. Side-by-side specification
4. Assumptions with sources and dates
5. Conventional cost breakdown
6. Sustainable cost breakdown
7. Discounted cash flow schedule
8. Comparison and break-even
9. Sensitivity grid
10. Charts
11. AI explanation
12. Methodology, references and limitations
13. Research answers (sub-questions a to e) and literature-versus-model comparison

CSV export contains the raw annual cash flows.

---

## 14. Multi-city extensibility

Launch is Sydney only. All city-specific facts are data, not code.

| Area | Varies by city |
|------|----------------|
| Energy rules | BASIX / NatHERS (NSW) versus other states |
| Electricity | Networks, tariffs, supply charges, feed-in |
| Water | Authority, rates, rebates |
| Construction | Cost per m², trade premiums, site conditions |
| Climate | Solar yield, heating and cooling load, rainfall |
| Incentives | State and federal schemes |

**Approach:** a `Region` record (for example `sydney_nsw`) with versioned, dated, sourced data. Requests carry a `region` field defaulting to Sydney; the selector is hidden until a second region exists. Postcode resolves to region and network. Adding a city means adding a data set and baseline tests, with no engine change.

---

## 15. Quality assurance and validation

- **Unit tests** for the engine: Year 1 figures, schedule consistency, NPV identity, break-even correctness (tight tolerances, never 10%).
- **Regression test** on the stored baseline.
- **Independent verification:** reproduce the baseline in a spreadsheet to the cent.
- **Property tests:** higher discount rate never raises discounted savings; zero premium breaks even immediately; a longer horizon never reduces cumulative savings when annual savings are positive.
- **API tests** for validation and error handling.
- **End-to-end test** from browser to API to result.
- **Professional and academic review** of method and baseline by the supervisor and, ideally, a quantity surveyor or energy assessor before public launch or submission.
- **Literature-mode tests:** hand-calculated scenario matches the engine to the cent; low, mid and high ordering is correct.
- **CI** runs all tests on every change.

---

## 16. Security, privacy and legal

- API keys and secrets only in server environment variables.
- Input validation on both client and server; rate limiting on public endpoints.
- Personal data (accounts, saved analyses) stored in an Australian region where practical; privacy policy required.
- Clear disclaimer on every result and report: this is an AI-assisted research and decision-support tool. It is not a certified quantity surveyor estimate, a construction tender, engineering certification, regulatory approval or professional financial advice.
- Third-party API usage (Gemini, Tavily, hosting, database, domain) is subject to provider limits and costs, not unlimited.
- Legal review of terms and disclaimers before launch.

---

## 17. Risks and mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Stale or incorrect inputs | Misleading results | Assumptions register with source and date; scheduled review |
| Thin baseline result | Over-promising | Lead with ranges; show worst and best cases |
| AI states wrong numbers | Loss of trust | Figures supplied as data; output checked against inputs |
| Live search returns poor data | Wrong prices | Search supplements only; approval before use |
| Measure interactions ignored | Overstated savings | Model interactions or state the limitation |
| Insufficient ML data (later phase) | Poor predictions | Do not claim accuracy; report evaluation honestly |
| Scope creep | Delays | Phase gates with exit criteria |
| Untested frontend | Late surprises | Install and run early; end-to-end test in CI |
| Liability for estimates | Legal exposure | Disclaimers; legal review |
| Model result differs from the literature (0.4% vs 10-20%) | Questions from supervisor or markers | Report honestly; explain operating share, system boundary and fixed charges; show literature mode alongside |
| "Conventional" baseline seen as a straw man | Weakens credibility | Code-minimum default; legacy 6-star only as a labelled preset |
| Citation errors in source documents | Academic integrity issue | Verify each citation before submission (see appendix) |
| Wrong price extracted from a web page | Misleading premium | Spec matching, sanity bounds, at least three sources, change guard, default fallback |
| Search cost or rate limits | Budget overrun, slow site | Cached-live design, single-flight, rate limits, daily and monthly caps |
| Store website terms | Legal exposure | Use Tavily's API, store prices and links only, curated supplier list |
| Users read results as a NatHERS or BASIX rating | Compliance misunderstanding | Clear notice that this is not an assessment; recommend a NatHERS assessor |

---

## 18. Delivery roadmap

### Phase 0: Foundations
- Agree the corrected baseline and regenerate all tables from the engine.
- Build the assumptions register (value, unit, source, date).
- Decide audience, itemised-versus-flat premium, and disposal treatment.
- Confirm hosting region.

**Exit:** signed-off assumptions register and baseline.

### Phase 1: Core calculator (MVP)
- Engine hardening, disposal and salvage option, tests in CI.
- Four-stage input flow with validation.
- Results dashboard: KPIs, trajectory chart, stacked outflows, sensitivity.
- Methodology and assumptions pages; CSV export.
- Literature mode (Low / Mid / High), Legacy and code-minimum presets, cost-category contribution, literature-versus-model panel, research answers tab.
- Disposal and salvage as required inputs; citations on every assumption.

**Exit:** a first-time user completes a run on a phone; results match the independent spreadsheet.

### Phase 2: Full prototype scope
- Component-level conventional costing (M3).
- Postcode resolver, house takeoff, cost build-up, cached-live Tavily pricing with badges and fallbacks (M14).
- Measure-by-measure sustainable analysis with interactions (M5).
- Gemini advisory with streaming; live research with visible sources.
- PDF report; accounts, saved and previous analyses; postcode to network mapping.

**Exit:** all Ready Client Prototype modules working end to end.

### Phase 3: Advanced data and ML
- Dataset collection, cleaning, feature engineering.
- Regression models with MAE, RMSE and R² evaluation.
- Multi-configuration sustainable optimisation.
- Project catalogue, filters and advanced analytics.

**Exit:** model performance reported honestly; best model integrated only if data supports it.

### Phase 4: Growth
- Builder dashboards and white-label reports.
- Additional building types and cities.
- Scheduled data refresh with change history.

---

## 19. Current status

| Item | State |
|------|-------|
| Single-page prototype (published) | Working; one bug fixed (sustainable maintenance base) |
| Backend engine, three endpoints, tests, requirements, `.env.example` | Written; engine reproduces all Year 1 figures; `pytest` not yet run |
| Frontend (home, calculator, methodology) | Scaffolded; never installed or run |
| Project plan (`GreenCost-Sydney-Project-Plan.md`) | Delivered |
| Agent build brief (`GreenCost-Sydney-Agent-Build-Brief.md`) | Delivered; updated with literature mode, research outputs and academic rules |
| Gemini screen, PDF, accounts, database, Tavily, multi-city, disposal | Not built |

---

## 20. Open decisions

| # | Decision | Recommendation |
|---|----------|----------------|
| 1 | Main launch audience | Homeowners, with a professional mode |
| 2 | Nature of the project (client product, academic, portfolio) | Decide before Phase 2 |
| 3 | Independent review of numbers | Yes, before launch |
| 4 | Confirm 4 × 4 sensitivity grids and Standard ($2,400/m²) default tier | Accept |
| 5 | Include disposal and salvage | Optional inputs, Phase 1 |
| 6 | Itemised upgrade costs or a single premium percentage | Itemised, Phase 2 |
| 7 | Hosting region | Australian region |
| 8 | Saved analyses and accounts in the prototype | **Resolved:** no accounts in v1; shareable links and device-local recent analyses |
| 9 | Conventional baseline: code-minimum new build or legacy 6-star | Code-minimum default, legacy as preset; confirm with supervisor |
| 10 | Handling a result that differs from the literature | Report honestly with explanation; raise with supervisor |
| 11 | Add literature mode alongside itemised mode | **Resolved:** yes |
| 12 | Verify citations (Zuo & Zhao year; Cabeza claim; GBCA date; 75% and $4,300 figures) | Verify before submission |

**Resolved since v1.1 (pricing):** cached-live pricing (not search-on-click); postcode resolves to zone, network and climate zone; installed items shown as indicative ranges; users may enter their own price or quantity.

**Resolved since v1.0:** audience is anyone planning a new building (public site); no accounts; costs itemised by measure; item prices fetched with Tavily; the project is an academic study (UTS 42908).

---

## 21. Glossary

| Term | Meaning |
|------|---------|
| LCC | Life-Cycle Cost: present value of all costs over the analysis period |
| NPV / PV | Net present value / present value |
| EAUC | Equivalent Annual Uniform Cost, LCC spread as an equal yearly amount |
| CapEx / OpEx | Capital expenditure / operating expenditure |
| Real rate | A rate excluding general inflation |
| GFA | Gross Floor Area |
| BASIX | NSW Building Sustainability Index |
| NatHERS | Nationwide House Energy Rating Scheme (star ratings) |
| AER / DMO | Australian Energy Regulator / Default Market Offer |
| IPART | Independent Pricing and Regulatory Tribunal (NSW) |
| WELS | Water Efficiency Labelling and Standards scheme |
| STC | Small-scale Technology Certificate (renewable energy rebate) |
| EER / COP | Energy efficiency ratio / coefficient of performance |
| SHGC / Uw | Solar heat gain coefficient / window U-value |
| ACH50 | Air changes per hour at 50 Pa (airtightness) |

---

## 22. Appendix: known issues in earlier drafts

1. Spec headline results (Year 33, +$7,741) do not reconcile with its formulas; engine gives Year 37, about +$2,987.
2. The original unit test asserted Year 33 and used a 10% tolerance; both are wrong.
3. Sensitivity grid described as both 4×3 and 16 cells; this document uses 4 × 4 per horizon.
4. Advisory text claimed profitability "up to 5.8%" without support; narrative must be generated from computed values only.
5. Disposal and salvage appear in the formula but not in the engine.
6. Pydantic v2: use `pattern=`, and `Literal[30, 40, 50]` for fixed integer choices.
7. Solar figures are slightly inconsistent (4,200 kWh export versus 40% of 9,400 kWh generation); engine is calibrated to the stated net energy cost.
8. Claims about the "pre-2023 6-star" baseline, STC rebates and the IPART feed-in need verification and dates.
9. The quotation's "Previous analyses" feature implies accounts and a database that its Option 1 module list does not include.
10. The quotation's component-level costing and measure-by-measure savings need data that does not yet exist and are the largest hidden effort.
11. The model's baseline gives a 0.44% LCC saving with operating costs about 23% of LCC, versus the literature's 10-20% and 60-80%; applying the literature percentages directly gives -8.5% to +4.2% (section 7.3a).
12. The legacy conventional house (pre-2023 6-star) is likely to be seen as a straw man given the literature's own 7-star statistics.
13. Source-document inconsistencies: maintenance savings 10-25% versus 10-20%; energy savings 20-40% versus 25-40%; Zuo & Zhao year; GBCA 2020 versus 2023; the proposal's LCC formula omits replacements.
