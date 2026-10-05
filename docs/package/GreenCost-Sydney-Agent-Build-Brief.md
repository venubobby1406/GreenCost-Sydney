# GreenCost Sydney: Agent Build Brief

**Read first.** This brief tells you what to build, in what order, and what "done" means for each step. Also read `GreenCost-Sydney-Project-Document.md` for background, and start from the existing code in `greencost/` (backend engine, API and frontend scaffold). Where this brief and the project document disagree, **this brief wins**.

**Context:** this is an academic research project (UTS Engineering Project Preparation 42908: *A Comparative Life Cycle Cost Analysis of Sustainable and Conventional Buildings*). The website is the analysis tool for that study and also a public tool for people planning a new home. Academic rigour (cited assumptions, honest wording, reproducibility) is a requirement, not an extra.

---

## 1. Resolved decisions

| # | Decision |
|---|----------|
| D1 | **Audience:** anyone planning a new building in Greater Sydney who wants to compare a normal (conventional) build with a sustainable one. Plain language, no jargon without explanation. |
| D2 | **No accounts or logins in v1.** Anyone can visit the site and run an analysis. |
| D3 | **Itemised by measure.** The user selects individual sustainability measures. Each measure has its own cost and its own effects. There is no single flat percentage premium in the main flow. |
| D4 | **Item prices are fetched with Tavily** from supplier, retailer and industry websites, then validated, cached and shown with sources (section 7). Dated default prices always exist as a fallback. |
| D5 | **Sydney only** at launch, but all city-specific data lives in data files so other cities can be added later without changing the engine. |
| D6 | AI (Gemini) explains results only. It never calculates or changes numbers. |
| D7 | Sensitivity grids are 4 × 4 (discount rates 4, 5, 6, 7%; energy escalation 2, 3, 4, 5%) for each of 30, 40 and 50 years. |
| D8 | **Academic context.** The study answers five research sub-questions (section 6, T6). The app must produce the outputs needed to answer them. |
| D9 | **Two calculation modes:** **Itemised mode** (selected measures, section 5) and **Literature mode** (the proposal's percentage ranges, T3A). Both use the same discounting engine. |
| D10 | **"Conventional" means a code-minimum new build** under current NSW requirements (7-star NatHERS; provisions to be verified and cited), and "sustainable" means measures that go beyond code. The old pre-2023 6-star house stays as a labelled **Legacy preset** and regression fixture. *Provisional: owner to confirm with supervisor.* |
| D11 | **Disposal/demolition and salvage are required inputs** with cited defaults. **Every assumption carries a citation** (author, year, link, date accessed) or is labelled placeholder. |
| D12 | **Honest results.** Never tune inputs to reach the literature's 10-20% saving. Wording: "Under the stated assumptions, the sustainable case has an X% lower (or higher) modelled LCC." Literature ranges are background, not results. |
| D13 | **Cached-live pricing.** Prices are refreshed in the background and cached; users see them instantly with a badge, age and sources. Tavily is **not** called on every click. A rate-limited "Refresh price" button exists. |
| D14 | **Postcode drives location, not exact pricing.** A Greater Sydney postcode resolves to a pricing zone, electricity network and climate zone. Supply prices are per zone; installed systems are shown as metro-wide ranges labelled indicative. |
| D15 | **Cost = quantity × price + labour + allowances**, using a house takeoff. The premium is the upgrade cost minus the code-minimum cost. Users may enter their own price or quantity. Full rules: `GreenCost-Sydney-Pricing-and-Takeoff-Spec.md` (which wins on pricing). |

---

## 2. Rules for the agent

1. **Never change calculation outputs silently.** Engine changes need a test that shows the before and after.
2. **Do not invent data.** Any number without a source is a *placeholder*: mark it `"status": "placeholder"` in the data file and label it "indicative" in the UI.
3. **Do not hard-code results in text.** Break-even years, savings and percentages shown to users must come from computed values.
4. **The legacy baseline is a regression fixture only.** Preserve it exactly (section 4) but do not present it as the default user experience.
5. Ask before making product decisions that are not in section 1. If you cannot ask, choose the simplest option and record it in `DECISIONS.md`.
6. Keep secrets in `.env`, never in code or in the browser bundle.
7. Every task below must pass its "done when" check before you start the next.
8. Never present literature ranges as the app's own findings, and never tune inputs to reproduce them.

---

## 3. Stack and structure

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11, FastAPI, Uvicorn, Pydantic v2, NumPy `>=2.4,<2.5`, httpx, python-dotenv, pytest |
| Frontend | Node 20+, Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 3.4, Recharts, Lucide-react |
| Storage (v1) | SQLite (price cache and price history) or JSON files; **no user database** |
| AI | Gemini API, model `gemini-2.5-flash`, text explanation only |
| Search | Tavily API |
| Env vars | `GEMINI_API_KEY`, `TAVILY_API_KEY`, `PORT=8000`, `NEXT_PUBLIC_API_URL` |

```
greencost/
  DECISIONS.md
  backend/
    app/
      main.py
      calculations/lcc.py          # discounting engine (pure, NumPy)
      calculations/energy.py       # end-use energy model
      models/                      # Pydantic request/response models
      data/regions/sydney_nsw/
        assumptions.json           # tariffs, rates, escalation (sourced, dated)
        measures.json              # measure catalogue (section 5)
        price_defaults.json        # fallback item prices (may be derived from measures.json)
        takeoff_assumptions.json   # house geometry parameters
        suppliers.json             # Tavily domain allow-list
        postcode_zones.json        # postcode to zone, network, climate zone (create from official data)
      services/prices.py           # Tavily pipeline
      services/narrative.py        # Gemini
      services/report.py           # PDF
    tests/
  frontend/
    src/app/ (home, calculator, methodology, assumptions, share)
    src/components/
    src/lib/
```

**Run:**
`cd backend && pip install -r requirements.txt && pytest && uvicorn app.main:app --port 8000`
`cd frontend && npm install && npm run dev` (port 3000)

---

## 4. Legacy baseline (regression fixture)

The original specification's reference case. Keep as a test fixture named `spec_baseline_legacy`.

Inputs: 220 m², capex $528,000 conventional and $580,800 sustainable (premium $52,800), 40 years, r = 5%, e = 3%, water escalation 2%, maintenance escalation 1.5%.
Year 1 operating cost: conventional $2,237.50 energy + $1,669.16 water + $2,640.00 maintenance = **$6,546.66**; sustainable $808.75 + $1,379.31 + $2,090.88 = **$4,278.94**; saving **$2,267.72**.
Replacements: conventional Y12 $1,800, Y15 $3,500; sustainable Y10 $750, Y12 $2,200, Y15 $3,800.

**Engine results that must remain stable:** break-even **Year 37**, 40-year net benefit about **+$2,987**, sustainable EAUC about $39,700.

> The original document claimed Year 33 and +$7,741. Those figures are wrong. Do not use them anywhere.

### Check against the research literature (verified from the engine)
At the legacy baseline the engine gives whole-life cost of **$684,903** (conventional) and **$681,917** (sustainable): a difference of $2,987, or **0.44%**. Operating costs (energy, water, maintenance, replacements) are only about **23%** of conventional whole-life cost, not the 60-80% quoted in the project's literature review. Applying the literature's own percentage ranges directly to this house (rough check, see T3A) gives between about **-8.5% and +4.2%**, not 10-20% lower. This is a finding to report honestly, not a bug to hide (see D12). Do not tune inputs to force a 10-20% result.

### Two known weaknesses in the legacy baseline (resolved by the new model)
1. **Premium mismatch.** The itemised upgrade costs in the legacy spec sum to **$29,800** (glazing 5,500; insulation 3,200; HVAC 4,500; hot water 2,800; solar 5,800; rainwater 4,200; airtightness and shading 3,800), not $52,800. The remaining $23,000 is unexplained. In itemised mode, the premium is the **sum of the selected measures**, so results will differ from the legacy baseline. This is expected.
2. **Energy comparison is not like-for-like.** The legacy numbers imply the sustainable home uses *more* grid electricity (about 6,650 kWh) than the conventional home (5,200 kWh), and ignore the conventional home's possible gas use. The new energy model (task T3) must model electricity **and gas** by end use.

---

## 5. Measure catalogue (itemised model)

Each measure in `measures.json` has:

```json
{
  "id": "solar_pv",
  "name": "Rooftop solar PV",
  "category": "generation",
  "options": [{"id": "6.6kw", "label": "6.6 kW array", "size": 6.6, "unit": "kW"}],
  "cost": {"basis": "installed", "unit": "per_kW", "default": null, "price_key": "solar_pv_installed_per_kw"},
  "effects": {"energy": "...", "water": "...", "maintenance": "..."},
  "replacements": [{"year": 12, "cost_key": "solar_inverter"}],
  "life_years": 25,
  "interacts_with": ["smart_controls", "heat_pump_hot_water"],
  "status": "placeholder"
}
```

**Baseline option per measure.** Because "conventional" is a code-minimum new build (D10), every measure has a `baseline_option` (what a code-compliant home already has) and one or more `beyond_code` options. Costs are the **difference** between the beyond-code option and the baseline option. A measure that is already required by code has zero premium and must not be counted as a sustainability saving. Keep the legacy 6-star specification as a separate preset (`legacy_6star`).

**Measures to include:** enhanced wall and ceiling insulation; high-performance glazing; airtightness and passive shading; efficient HVAC (inverter heat pump); heat pump hot water; solar PV (size selectable, 0 to 13.2 kW); efficient lighting; smart controls and load shifting; water-efficient fixtures (WELS); rainwater harvesting (5,000 L plumbed); sustainable material alternatives.

**Quantities and prices.** Each measure's quantity comes from the takeoff and its price from the catalogue (`GreenCost-Sydney-Pricing-and-Takeoff-Spec.md`). The figures below are only the *defaults* used until live prices pass validation, and are scaled by quantity ratio.

**Starting costs** from the legacy spec (placeholders until Tavily or sourcing replaces them): glazing $5,500; insulation $3,200; HVAC $4,500; hot water $2,800 (net of STCs); solar $5,800 for 6.6 kW; rainwater $4,200; airtightness and shading $3,800. Costs for lighting, controls, fixtures and materials are **not provided**: create them as placeholders flagged for sourcing.

**Cost basis must be explicit.** Every price states whether it is *supply only* or *installed*, whether it includes GST, and the unit (per m², per kW, each, per tank). Do not mix bases.

**Interactions.** Measures affect each other (better insulation reduces the HVAC saving; solar value depends on how much load exists to self-consume). The engine must:
- compute the **combined** result for the selected set using the end-use model (not by summing standalone savings), and
- report each measure's **marginal contribution** by adding measures in a fixed, documented order, with an explicit "interaction adjustment" line so contributions reconcile to the total.

---

## 6. Build tasks (in order)

### T0. Baseline and tooling
Install dependencies, run existing tests, fix whatever fails, add GitHub-style CI (lint, tests).
**Done when:** `pytest` passes locally; the frontend installs, builds and runs; `/health` returns OK.

### T1. Harden the engine
- Keep `calculate_discounted_lcc` pure and deterministic.
- Add disposal/demolition and salvage as **required** inputs with cited defaults (zero only by explicit user choice), discounted at year N.
- Use `Literal[30, 40, 50]`, `pattern=` for regex fields (Pydantic v2).
- Add tests: Year 1 figures; schedule consistency; NPV identity; break-even correctness; property tests (higher discount rate never raises discounted savings; zero premium breaks even in Year 1); legacy fixture (Year 37, about +$2,987, tolerance `rel=0.001`).
**Done when:** all tests pass and the legacy fixture is locked.

### T2. Measure catalogue and selection model
- Create the schema and loader for `measures.json` with validation.
- Request model accepts a list of selected measures and options.
- Premium = sum of selected measure costs (beyond-code option minus code-minimum option), plus any replacement schedules from the measures.
- Provide two presets: `code_minimum_7star` (default) and `legacy_6star` (regression and comparison).
**Done when:** selecting no measures gives identical conventional and sustainable results (zero premium, zero savings); selecting each measure alone gives plausible, sign-correct results; an unknown measure ID returns a clear 422 error.

### T3. End-use energy model (electricity and gas)
- Model annual energy by end use: heating and cooling, hot water, lighting, appliances. Support both electricity and gas, including gas supply charges.
- Measures change specific end uses (for example heat pump hot water changes fuel and efficiency; envelope measures reduce heating and cooling demand).
- Solar: generation from capacity and a Sydney yield factor; self-consumption depends on load and the load-shifting setting; exports are credited at the feed-in tariff.
- All parameters live in `assumptions.json` with source or `placeholder` status.
**Done when:** energy results change sensibly as measures are toggled; a worked example is documented in `docs/energy-model.md`; no result is hard-coded.

### T3A. Literature mode
Implements the proposal's secondary-data method alongside itemised mode.
- Inputs (with ranges and defaults): capital premium 5-15% (default 10%); energy saving 20-40% (30%); water saving 30-50% (40%); maintenance saving 10-25% (20%).
- Apply the percentages only to the **reducible** parts of the conventional year-1 costs (energy usage charges, water usage charges, maintenance), not to fixed supply or service charges. Document this choice in the methodology page.
- Same discounting, escalation, horizons and sensitivity grids as itemised mode; disposal and replacements included.
- Always show **Low / Mid / High** scenarios (low savings with high premium; mid; high savings with low premium).
- Show the literature's claim (10-20% lower total LCC) beside the modelled result.
- *Indicative check from a simplified calculation* (percentages applied to whole bills, replacements and disposal excluded, 40-5-3): low -$57,700 (-8.5%), no break-even; mid -$12,800 (-1.9%), no break-even; high +$28,600 (+4.2%), break-even Year 15. Negative means the sustainable case costs more. **Recompute with the real rules above; do not hard-code these.**
**Done when:** the mode switch works; the three scenarios compute; a hand calculation of one scenario matches to the cent; outputs are labelled "literature-parameter scenario", not "prediction".

### T3B. Cost-category contribution (research sub-question d)
For each category (initial cost, energy, water, maintenance, replacements, disposal less salvage) output present value for each scenario, the difference, and each category's share of the total LCC difference (shares can be negative or exceed 100%; handle and explain). Also output the operating-cost share of total LCC and the percentage operating-cost reduction by category (sub-question a). Works in both modes.
**Done when:** category differences sum exactly to the total LCC difference; tests cover both modes.

### T4. API
Endpoints: `GET /health`, `GET /api/v1/measures`, `GET /api/v1/assumptions`, `POST /api/v1/calculate/lcc`, `POST /api/v1/sensitivity/matrix`, `POST /api/v1/narrative/explain`, `POST /api/v1/report/pdf`, `POST /api/v1/prices/refresh` (protected by a server-side token).
Responses include the assumption-set version and, per measure, the price source and date.
**Done when:** OpenAPI docs render; validation errors are clear; API tests pass.

### T5. Local pricing and takeoff (see `GreenCost-Sydney-Pricing-and-Takeoff-Spec.md`)
Build in this order; each sub-task has its own check.

**T5A. Location resolver.** `GET /api/v1/location/{postcode}` returns zone, suburbs, network, climate zone and water authority from cited data files. **Done when:** sample postcodes resolve correctly and invalid or out-of-area postcodes return a friendly message.

**T5B. Takeoff engine.** Convert floor area, storeys, bedrooms and bathrooms into quantities per measure, with feasibility checks (for example solar roof capacity) and user overrides. **Done when:** the 220 m² worked example in the pricing spec (section 4.2) is reproduced exactly and tests cover two-storey and override cases.

**T5C. Catalogue and cost build-up.** Price catalogue with reference specs, units, basis flags (`includes_labour`, `includes_margin`, `gst_included`), dated defaults, sanity bounds, incentives as a separate line, and the premium formula (upgrade minus code-minimum). **Done when:** the reference-house premium is reproducible from defaults, installed prices are not double counted, and a code-required measure shows zero premium.

**T5D. Tavily pipeline, cache and jobs.** Search, extract (Gemini, schema only), normalise, match the spec, validate, aggregate (median, low, high), change guard, SQLite cache and history, nightly scheduler, stale-while-revalidate, single-flight, rate limits, daily and monthly caps, fallback ladder. **Done when:** a test run refreshes the starter items from live sources, bad data is rejected in tests, and the app works fully with Tavily and Gemini switched off.

**T5E. Price API and picker UI.** `GET /api/v1/prices`, `POST /api/v1/prices/refresh`, price badges, sources drawer, own-price field, price scenario (low / median / high) in sensitivity. **Done when:** a cached price appears in under one second, badges are correct, and the picker works on a phone.

### T6. Frontend
- Pages: Home, Calculator, Methodology, Assumptions (all inputs with source and date), Share.
- Calculator: progressive disclosure in four stages. Stage 1 takes the **postcode** and shows the resolved zone and network. Stage 2 is the **measure picker**: each option card shows name, plain-language description, the quantity for this house, unit price, total as a range, the difference versus code-minimum, a price badge (Live / Cached / Default / Indicative / Your price), age, a sources drawer, a refresh button and a field for the user's own quote. Prices load from the cache and never block the page.
- Results: KPI ribbon; cumulative net position chart with break-even marker; annual outflows stacked bar; **per-measure contribution chart**; **cost-category contribution chart**; 4 × 4 sensitivity heatmap; AI advisory panel; CSV and PDF export.
- **Literature vs model panel:** the literature ranges (with citations) beside the modelled values, marking whether each modelled value falls inside or outside the range.
- **Research answers tab** mapping the study's sub-questions to computed outputs: (a) operating-cost saving by category; (b) effect of discount rate, escalation and horizon (range sentence generated from the grid); (c) percentage LCC difference; (d) category contribution; (e) planning implications and limitations as templated text.
- Mode switch: Itemised / Literature, and preset switch: Code-minimum / Legacy 6-star.
- Clear "estimate, not advice" notice on every results view.
**Done when:** a first-time user completes an analysis on a phone without help; all numbers come from the API; the app handles API failures gracefully.

### T7. Gemini explanation
- Send only the computed JSON (summary, year 1, sensitivity, per-measure contributions).
- System prompt: senior quantity surveyor and building economist in Sydney, three paragraphs, Australian English, **no calculating or inventing numbers**.
- Stream the response to the UI.
- Check that every number in the output appears in the input; if not, drop the paragraph or fall back to a template.
**Done when:** the narrative works, streams, and the numeric check catches a deliberately wrong test output. The rest of the app works with no Gemini key.

### T8. Reports and export
- PDF: building details; assumptions with sources and dates; selected measures and costs; cash-flow schedule; comparison; sensitivity; charts; AI explanation; methodology and limitations.
- CSV: raw annual cash flows.
**Done when:** a PDF generated from the baseline example opens correctly and its figures match the on-screen results.

### T9. Sharing and recent analyses (no accounts)
- Encode the analysis inputs in a shareable URL; opening it re-runs the calculation with the same assumption version where available.
- Keep "Recent analyses on this device" in browser storage.
**Done when:** a shared link reproduces the same results; clearing browser data does not break the site.

### T10. Quality and launch
- Accessibility pass (keyboard, contrast, labels).
- End-to-end test of the full flow.
- Rate limiting, CORS restricted to the frontend origin, error logging.
- Legal pages: disclaimer, privacy, terms. (Wording to be reviewed by the owner.)
**Done when:** CI is green and the launch checklist in `DECISIONS.md` is complete.

---

## 7. Tavily price pipeline: specification

> This section is extended and, where different, superseded by `GreenCost-Sydney-Pricing-and-Takeoff-Spec.md` (zones, takeoff, cost build-up, cache rules, badges, fallbacks).

**Goal:** keep item costs current using live web sources, while keeping results trustworthy.

### 7.1 Flow
1. **Query:** for each item, run targeted Tavily searches (for example, installed price of a 6.6 kW solar system in Sydney; supply price of R2.5 wall batts per pack; heat pump hot water unit price in NSW; 5,000 L rainwater tank price). Prefer Australian supplier, retailer and industry pages.
2. **Extract:** pull prices from the returned content into a structured record. Gemini may be used **for extraction only**, with a strict JSON schema.
3. **Normalise:** convert to AUD, a standard unit and a stated basis (supply only or installed; GST included or not).
4. **Validate:** reject records that fail checks (7.3).
5. **Aggregate:** with at least three valid sources, use the **median** after removing outliers.
6. **Store:** save the price, sources and timestamp in the cache and in the price history.
7. **Use:** the calculation reads cached prices; the user sees the source badge and links.

### 7.2 Price record

```json
{
  "item_key": "solar_pv_installed_per_kw",
  "value": 1050.0,
  "unit": "AUD_per_kW",
  "basis": "installed",
  "gst_included": true,
  "sources": [{"url": "...", "retailer": "...", "price": 1099.0, "retrieved_at": "..."}],
  "method": "median_of_3",
  "confidence": "medium",
  "updated_at": "..."
}
```

### 7.3 Validation rules
- Each item has a plausible min and max range; values outside are rejected.
- Unit and basis must match the item definition.
- Minimum three independent valid sources for "Live"; fewer gives "Indicative".
- A change of more than 25% from the previous value is flagged for review and not applied automatically.
- Out-of-date pages or pages without a visible price are ignored.
- If anything fails, the **default price** is used and labelled "Default".

### 7.4 Operations
- Refresh on a schedule (for example weekly) and on demand through the protected refresh endpoint.
- Cache results. A user's calculation or page load never waits for a Tavily search. Searches run on a schedule, for stale items in the background (single-flight), or from the rate-limited refresh button. Enforce daily and monthly caps.
- Budget guard: a maximum number of searches per run and per month, logged.
- Respect website terms; use Tavily's API rather than your own scraping.
- Keep price history so past analyses and reports can state which prices they used.

### 7.5 What the pipeline must not do
- It must not override tariffs or financial assumptions automatically. Electricity, water and feed-in rates come from `assumptions.json` (regulator sources: AER, IPART, Sydney Water) and may be *suggested* for update, with review.
- It must not present a price without its basis, unit, source and date.

---

## 8. Cross-cutting requirements

- **Plain language:** explain terms (discount rate, break-even, EAUC) where they appear.
- **Honesty about uncertainty:** show ranges and the sensitivity grid prominently; avoid a single headline promise.
- **Academic rigour:** every assumption on the Assumptions page has a citation (author, year, title, link, date accessed) or is flagged placeholder. Provide an export of the method and assumptions table suitable for a thesis appendix.
- **Result wording:** "Under the stated assumptions, ..." Never "sustainable buildings save X%" as a universal claim.
- **Formatting:** Australian English, AUD, `en-AU` number formatting.
- **Region-ready:** all rates, measure costs and rules loaded from `data/regions/<region>/`. The API accepts a `region` field defaulting to `sydney_nsw`; no UI selector until a second region exists.
- **Reproducibility:** every result stores the assumption-set version and the price snapshot date.

---

## 9. Out of scope for v1

User accounts, saved server-side analyses, builder dashboards, machine-learning cost prediction, a project catalogue, multi-city UI, payments, native apps.

---

## 10. Definition of done (whole project)

1. All tasks T0 to T10 meet their "done when" checks.
2. Legacy fixture still passes (Year 37, about +$2,987), and both modes, both presets and the category contribution outputs are tested.
3. Every figure shown to users is computed, sourced or clearly marked indicative.
4. The site works without Gemini or Tavily keys (using defaults) and says so.
5. `README.md` explains setup, tests, environment variables and how to add a region.
6. `DECISIONS.md` lists every assumption you made.

---

## 11. Items the project owner must still supply or confirm

- Review of the method and numbers by the academic supervisor and, ideally, a quantity surveyor or energy assessor before public launch or submission.
- Confirmation of the conventional baseline definition (D10) with the supervisor.
- Approval of the pricing zones, margins, labour rates, supplier allow-list, incentive schemes and sanity bounds (pricing spec, section 14), and Tavily and Gemini monthly caps.
- Verification of citations in the literature documents: Zuo & Zhao (listed as 2017 but the journal volume suggests 2014); whether Cabeza et al. (2014, an LCA review) supports the "15-20% decision accuracy" claim; GBCA dated 2020 in the table but 2023 in the references; the "75% of new NSW homes at 7-star" and "$4,300 uplift" figures; the "6-10% annual construction cost growth" figure; and inconsistent ranges (maintenance saving 10-25% vs 10-20%; energy saving 20-40% vs 25-40%).
- Source and sign-off for placeholder values (lighting, controls, fixtures, materials, end-use energy splits).
- Hosting choice (an Australian region is preferred).
- Final wording for the disclaimer, privacy policy and terms.
- Tavily and Gemini API keys and monthly usage limits.
