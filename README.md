# GreenCost

Compare the whole-life cost of a conventional and upgraded building over **30, 40 and 50 years**. GreenCost uses Python for all financial calculations and Three.js for the animated building. Gemini and Tavily are optional.

**No SQL, NoSQL, vector database, database account, or database installation is required.** Research is kept in ordinary files. Recent comparisons stay in your browser. Local installations can also save JSON reports.

The **Home** page introduces GreenCost and its interactive building. **Compare** opens the three-step calculator and results at `/compare`. **Method & evidence** is a supporting reference page; `/sources` redirects there.

For a complete nontechnical walkthrough, technology explanation and five-minute presentation script, read the [Client Presentation and Execution Guide](docs/GreenCost-Client-Guide.md).

## Run it on Windows

Install [Python 3.12+](https://www.python.org/downloads/) and [Node.js 22 LTS or newer](https://nodejs.org/). Open PowerShell in this project folder, then run:

```powershell
.\scripts\start-local.ps1
```

The first run installs dependencies and prepares the supplied research PDFs. Later runs reuse them. Open **http://127.0.0.1:3000**. Keep the terminal open; press **Ctrl+C** to stop both services.

For the optimised production build:

```powershell
.\scripts\start-local.ps1 -Production
```

The same script accepts `-SetupOnly` to install without starting, or `-Python 'C:\path\to\python.exe'` if Python is not on your PATH. If PowerShell blocks scripts, run `powershell -ExecutionPolicy Bypass -File .\scripts\start-local.ps1` for this invocation.

No API key is needed to calculate, inspect evidence, compare scenarios, or export reports. Tavily is required for optional live supplier searches. A configured key is distinct from a successful provider request; the interface reports the last analysis status.

## Example 1: explore the supplied house

1. Choose **Explore a sample** or **Try an example**.
2. Continue through **Building details**, **Budget & bills**, and **Sustainable design**.
3. Inspect the selected insulation, solar and rainwater upgrades. Prices say **Indicative** because they are not verified builder quotes.
4. Choose what happens at the end of the study, choose **Review comparison**, check the summary, then choose **Compare my building**.
5. Read the initial building cost, maintenance, total cost and investment recovery. Switch between 30, 40 and 50 years; expand charts or research details when needed, and download PDF, HTML or CSV.

The sample is an illustration. Do not reuse its costs or consumption as measurements of your own house.

## Example 2: use a budget range

Choose **Start fresh**. Enter postcode **2000**, a **220 m²** house. Optional building details let you confirm floors and edit suggested occupants. In **Budget & bills**, choose **Budget range** and enter **AUD 600,000–800,000**. The main comparison uses the **AUD 700,000 midpoint**; low and high budgets are recalculated separately.

Choose **Review & edit cost breakdown** to inspect the generated categories. Quantities and category shares are explicitly labelled estimates. **Find prices for this breakdown** checks up to five material categories through Tavily. A clear tax-inclusive per-unit source-page price can fill automatically when there is one match. Multiple products need selection; ambiguous or missing prices remain **Quote required**. This does not fetch installed builder quotes or guarantee Sydney delivery. The entered budget remains the calculation baseline until you choose **Use edited breakdown as construction total**.

Enter **5,200 kWh** electricity and **200,000 L (0.2 million litres)** water annually, or choose **Monthly average** and enter your average month; the app multiplies it by twelve. Select **Ausgrid** as the distributor for this practice example. Use the distributor printed on your own bill for a real project.

Continue to upgrades and select insulation and solar. Review their installed cost differences; use **Compare two installed quotes** if you know both conventional and sustainable costs for the same scope. Keep **Remains in use** for no end-of-period demolition, or choose a supported house removal estimate / manual costs and review them. Choose **Review comparison**, check the three summary sections and use their **Edit** buttons if needed. Choose **Compare my building** to calculate.

Required fields have an **asterisk (*)**. Missing or invalid values show a reason beside the field and focus the first problem. Select the **ⓘ** beside a label for help; it also works with keyboard focus and hover. Numbers can be erased completely; blank and zero have different meanings. Utility reference charges appear before calculation for your selected distributor, water connections and reference date.

Every value above is illustrative, not a Sydney construction benchmark or prediction for your house. A positive signed saving means sustainable costs less; a negative saving means it costs more. Correct consumption and realistic quotes do not guarantee savings.

## Save, reopen and share

- **Save project** downloads a JSON file containing inputs, captured rates and results. On the Compare page, choose **My projects → Import saved project** to reload the inputs and recalculate.
- **Save draft** sits in the form action bar. It downloads unfinished inputs, including empty number fields. Choose **My projects → Import saved project** to resume, then complete the inputs before calculating.
- **Share** copies a URL containing inputs and captured utility rates. The recipient opens it and chooses **Compare my building**. This reproduces financial results for assumption version `2026-10-v1`; optional AI wording may differ.
- **My projects → Saved on this device** lists the last three completed comparisons with names and dates when browser storage is available. Opening one restores validated inputs for review and recalculation. **Clear device history** removes these browser copies.

Downloads and successful actions use a temporary notice at the top right. Calculator connection failures stay beside the form with **Retry connection** and connection help. **Research connections** and the results' research-status section distinguish configured keys from successful calls, provider busy, quota limits and unavailable services. Financial calculations remain available without optional research APIs.

Share links and downloaded files contain project details. Do not put private information in the project name or share a link publicly unless you intend to disclose its inputs. With browser storage disabled or full, calculations and downloads still work.

## Use free Gemini and Tavily keys

The setup script creates `.env` only if it does not already exist. Add keys to that file, not frontend files:

```dotenv
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-3.5-flash-lite
TAVILY_API_KEY=your-key
TAVILY_DAILY_CAP=10
TAVILY_MONTHLY_CAP=200
GEMINI_DAILY_CAP=20
GEMINI_MONTHLY_CAP=400
```

Restart after editing. Choose a model available in your Gemini account. Free services have quotas; timeouts, quota errors and unavailable models fall back to calculated explanations. A normal online comparison makes at most one context search and one explanation call. Supplier pricing is separate: a full breakdown refresh makes up to five search requests, and an individual refresh makes at most one. Successful price checks are reused for up to a day; rapid repeated attempts have a cooldown. Follow-up qualitative questions may make an additional explanation call. Financial what-ifs and exports make no external calls.

Gemini sees non-identifying scenario facts and selected research excerpts. Tavily receives a general building-feature search. Neither provider controls arithmetic or official tariff values. Administrators should exclude confidential research from the bundled library when optional AI is enabled.

Local caps count requests, not credits, and are persisted as JSON. **Serverless instances cannot share a global counter without shared storage.** Hosted AI is therefore off by default. Keep account-level quotas in place before enabling it.

Official references: [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [Tavily pricing](https://help.tavily.com/articles/8816424538-pricing), [Vercel Hobby rules](https://vercel.com/docs/plans/hobby).

## Deploy on Vercel

Vercel Hobby is for personal, non-commercial use and is subject to limits. It can suit an academic demo. Commercial use requires a suitable paid plan. The project is configured for **two Vercel projects from the same repository**; no database service is involved.

**1. Backend project**

- Import the repository into Vercel.
- Use the repository root as the Root Directory and **FastAPI** as the framework. Root `vercel.json` and `pyproject.toml` identify `backend.app.main:app` and build the research index.
- Set `SAVE_LOCAL_ANALYSES=false` and `ENABLE_HOSTED_AI=false`.
- Set `ALLOWED_ORIGINS` to the exact frontend URL once it is available, such as `https://greencost-example.vercel.app`. Multiple explicit URLs can be comma separated; wildcards are not accepted.
- Deploy and check `https://YOUR-BACKEND.vercel.app/api/health`. It should show `status: ok`, `rag_ready: true` and `vector_db: none`.
- In both projects, choose deployment protection settings appropriate for a public app. A backend protected by a login wall cannot serve the frontend's public API proxy.

**2. Frontend project**

- Import the same repository a second time. Set Root Directory to **frontend**, framework **Next.js**, and Node.js **22** or newer.
- Add `GREENCOST_API_URL=https://YOUR-BACKEND.vercel.app` without a trailing slash. This is a server-side proxy setting, not an API key.
- Deploy. Add the resulting frontend URL to the backend's `ALLOWED_ORIGINS`, then redeploy the backend.
- Run the sample comparison and test PDF export, a share link and the methodology page.

To use optional free APIs on Vercel, add the two keys and `GEMINI_MODEL` to the **backend project only**. Set `ENABLE_HOSTED_AI=true` only after configuring provider quotas and host abuse protection. Per-instance rate limits and counters are not a distributed spending guarantee. Preview frontend domains must also be explicitly allowed.

Vercel has no durable local filesystem. PDF uploads have been removed from the public UI and API. Administrators can maintain the included research files locally, run `scripts/ingest_knowledge.py`, and redeploy. Results are retained in the browser or exported files. Server-side report/chat routes rebuild validated inputs with captured rates, rather than relying on a saved server ID. No hosted deployment has been performed or verified against your account.

Official deployment guide: [FastAPI on Vercel](https://vercel.com/docs/frameworks/backend/fastapi).

## What the model includes

- Capital at year zero; base-year annual costs escalated and discounted at year end.
- Electricity usage and fixed supply, water usage and fixed service charges, maintenance, replacements, other annual costs, disposal and salvage.
- Itemised envelope/HVAC/hot-water interactions; indicative solar self-use and exports; gas space-heating consumption with user tariffs. Literature mode applies energy reductions to variable electricity/gas costs only.
- Rectangular-plan quantity estimates, roof feasibility, drawing-quantity overrides, individual quotes and already-required measures.
- Three horizons, 48 discount/escalation sensitivity cases, indicative price ranges, category and marginal measure contributions, equivalent annual cost.
- A separate legacy regression preset, preserving the original engine's Year 37 break-even and $2,986.68 net benefit. Its historical assumptions are not current official prices.

The current app's base-year escalation convention and the package's legacy year-one convention differ. They are explicitly separated and tested. First break-even may reverse later. See [docs/METHODOLOGY.md](docs/METHODOLOGY.md) and the method page for formulas and limits.

## Review before public launch

The software runs and is tested, but it is **not a certified cost or energy model**. The package includes placeholder assumptions. Public launch as an authoritative planning tool still requires the owner/supervisor and appropriate building professionals to review them.

The supplied package's **full official Greater Sydney postcode/network/climate concordance and comprehensive paired supplier catalogue remain incomplete**. The interface asks users to select the actual electricity distributor from their bill, uses clearly labelled indicative upgrade differences, and accepts project quotes. It does not guess climate zones. A bounded Tavily supplier-check pipeline is implemented for six budget categories; only unambiguous tax-inclusive source-page prices qualify for filling, and many categories need quotes. Comparable installed baseline/upgrade quotes can be entered separately. The complete paired product specifications, supplier terms, quantity allowances and incentive eligibility still need review before an authoritative public launch. These outstanding requirements are recorded in `DECISIONS.md`.

The provisional code-minimum baseline and public disclaimer/privacy/terms wording also need owner sign-off. Selecting upgrades is not a BASIX or NatHERS assessment. Site conditions, orientation, shading, code requirements, installation quality and network approvals need project-specific review.

## Verify the project

From the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check backend scripts
cd frontend
npm run lint
npm run typecheck
npm run build
npm audit
```

Stop the frontend before rebuilding; development and production share `.next`. GitHub Actions runs backend and frontend checks on pushes and pull requests. Automated provider tests use mocked contracts. The 6 October verification records 81 passing backend tests and the production/browser checks. Live Tavily checks returned research context, while supplier prices can remain unresolved; Gemini has returned both provider-busy and unusable-text conditions, with calculated fallback explanations. See `docs/PRODUCTION_VERIFICATION.md` for the evidence and limits.

## Project structure

```text
backend/app/calculations/   financial engine, legacy fixture, energy and takeoff
backend/app/schemas/        validated input models
backend/app/services/       analysis, JSON files, PDF/HTML reports, API budgets
backend/app/rag/            local PDF passage retrieval (not a database)
frontend/app/               comparison and method/evidence pages
frontend/components/        guided form, upgrade picker, Three.js and charts
data/regions/sydney_nsw/    supplied region catalogue and indicative assumptions
data/verified/             dated official tariff/index records
data/knowledge/            all four supplied research PDFs and context
data/research_index/        generated JSON passage files
docs/package/              original ZIP instructions, preserved as reference
scripts/                   setup, knowledge ingestion, explicit tariff verification
```

Legacy `data/faiss/` and earlier verification documents are retained as historical artifacts and are not application storage. SQLite/Chroma are not imported, installed by the lockfile, or used.

To update official tariff records, run `scripts/update_sources.py --offline` for validation, or its normal Tavily mode for conservative verification. Direct scraping is disabled; no new page copies are saved. A new financial year requires reviewed dated records rather than extrapolating an expired official tariff.

To add a region later, create a new `data/regions/<region>/` folder with reviewed assumptions, catalogue and location data, then explicitly add a supported region identifier and tariff loader. The current release intentionally supports Sydney only; copying a folder alone does not enable another city.

## Troubleshooting

**Backend not connected:** keep the startup terminal open. Check `backend-error.log`, then restart the script.

**Port already in use:** stop the previous GreenCost terminal with Ctrl+C, or close the application using port 3000/8000. The script does not terminate unrelated programs.

**Tariffs expired:** choose your own utility rates and enter a bill reference, or have the administrator review a new dated official record.

**Solar too large:** the warning shows stored total area, area units, floors, roof area and selected solar size. Choose **Review area, units & floors**, **Edit solar size**, or **Edit measured roof area** to correct the relevant input. If an unintended roof override is present, **Use estimated roof area** removes it. The estimate rechecks automatically after a change. Retrying unchanged inputs cannot fix a sizing constraint; **Retry estimate** is reserved for connection/server failures and now visibly enters the calculating state. A 250 m², single-storey house without a roof override accepts the default 6.6 kW system in this model. Drawing overrides remain estimates, not network approval.

**Changing building type:** switching between House, Apartment building and Commercial starts a fresh building scope, including area, floors, occupants, budgets, bills and upgrades. Project name, postcode and financial study settings remain. Back navigation and clicking the already selected type preserve your inputs. House floor count is shown below the area field; use **Edit floors** for a multi-storey house or **Use one floor** to correct a previously saved count.

**No supplier price:** many products have variant-dependent, pack-based or quote-only pricing. The app retains the labelled estimate and links to the supplier. Check the source and confirm installation, delivery and product suitability before using a price.

**Gemini busy / quota reached:** the provider status identifies temporary demand, quota or model-access errors where available. Financial calculations still finish with built-in explanations.

**Blank number fields:** Backspace now clears values. Complete required inputs before continuing. A zero utility value requires confirmation and models no usage savings.

**Report or chat fails on Vercel:** verify the backend URL, origin allow-list, deployment protection and backend function logs. Do not put provider keys in the frontend.

## Client refresh — 7 October 2026

The calculator automatically saves an unfinished draft and its current step in this browser. Refreshing or leaving Compare and coming back restores it. **My projects** opens saved comparisons and imports a project JSON file; **Save draft** downloads your inputs. Start fresh asks you to confirm before replacing the current draft. Avoid sharing a browser profile for private projects; browser data is not an online account or cross-device backup.

Water consumption uses **litres**, with a million-litre equivalent below the field. Enter 500,000 for half a million litres. Utility rates stay in AUD/kL to match bills; the app converts internally. Monthly values are annualised once.

**House** needs total dwelling floor area in the main size section. Its optional occupancy suggestion uses the dated NSW BASIX energy-modelling assumption, with a manual override. **Apartment building** now compares a whole building: enter **Area per floor** or **Total building area**, and a required floor count. Total area is stored once, so total-area entry is never multiplied again. Previously saved **Apartment unit** projects retain their single-flat scope; they are not silently converted into a building.

For example, select **Apartment building → Area per floor**, enter **500 m²** and **20 floors**. The building total is **10,000 m²**, with **219 estimated occupants** using the illustrative defaults of **75 m² per apartment** and **80% apartment space**. With 50 floors and the same per-floor area, it becomes 25,000 m² and 547 estimated occupants. Alternatively, enter **10,000 m²** using **Total building area** and 20 floors: the estimate remains 219. Changing floors in total-area mode does not change an already combined area. Select **Enter actual number** to override the count; manual counts stay fixed when geometry changes.

The estimate divides gross residential-floor area by assumed apartment size after removing assumed common/service space, then applies the NSW BASIX August 2022 dwelling-level energy occupancy relationship. Review both editable assumptions under **Review the occupancy assumptions**. These defaults are illustrative, not official city density standards, legal capacity, actual resident forecasts, a water prediction or a BASIX assessment. See the [NSW occupancy guidance](https://www.planningportal.nsw.gov.au/sites/default/files/documents/2022/BASIX%20standard%20occupancy%20-%20version%204%20-%2023.08.22%20LMv5.pdf).

Use whole-building budgets and measured/design consumption for this scope. Enter your applicable utility rates with **combined supply charges for all included meters**; single-house reference charges are disabled for apartment buildings. Occupants describe the scenario and do not automatically generate utility bills. Choosing a building clears previous single-property budget, consumption, rates and upgrades so they cannot be mistaken for tower inputs. Generic quantities and upgrade coefficients remain indicative: enter project quotes, actual bathroom totals, maintenance and replacement allowances for lifts, central plant, car parks and other common systems. Solar/tank defaults are capped small systems, not an automatically sized tower design. Ordinary-house demolition guide prices do not apply; use project quotes if removal is assumed.

**Sustainable design** groups features into comfort, clean energy, water and materials. Australian guidance is linked on each card. Heat-pump hot water is offered for a less efficient baseline; already-included features receive no extra benefit. Supply-price lookup remains in the budget breakdown. Installed upgrades still need comparable quotes; a supply price is not an installed quote.

The eight-stage timeline shows actual start/completion events. Gemini and Tavily have separate request outcomes; a configured key alone is not a successful request. Rejected or unavailable Gemini responses use a calculated explanation and say so. Python financial results do not depend on an AI response.

Removal estimates are restricted to supported ordinary house scopes from a dated contractor guide. Both designs use the same allowance, recovered-material income defaults to zero, and manual quotes can override it. End-of-study demolition is optional, not automatic. The initial cost, maintenance present value and total present value are prominent in results and reports. See [client refresh notes](docs/Client-Refresh-Notes.md) for sources and scope.

## Automatic AI fallback

Set server-side keys in `.env` (never `NEXT_PUBLIC_` variables):

```dotenv
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openrouter/free
```

Keep your existing `GEMINI_API_KEY` and `GEMINI_MODEL`. Restart the server after editing keys. Order: **OpenRouter → Groq → Gemini → calculated explanation**. Missing keys are skipped. A usable first or second reply stops the chain: later APIs receive no request. Quota, permission, connection, incomplete-text and content-check failures permit the next provider. Each provider has one attempt, bounded HTTP timeouts and its own daily/monthly application caps. These caps are not a shared serverless quota. OpenRouter is restricted to `openrouter/free` or a model ID ending in `:free`; account limits still apply. The free router may choose different available models. Optional AI receives the explanation context/evidence; Python remains responsible for every calculation. The interface identifies the successful provider and reports failures.


## Client decision report

PDF and printable HTML reports start with initial building cost, routine maintenance and total cost, then explain savings, investment recovery, selected upgrades, important assumptions and next steps in everyday language. Technical inputs stay available in the project JSON and annual cash-flow CSV instead of being printed as raw records. Maintenance is included in the total, not added to it again.

Downloads contain project-specific paragraphs built from validated inputs, selected upgrades and calculated results. Provider/request diagnostics and metadata replies are kept out of client reports. Reports use the project name in the download filename, with a GreenCost fallback when no name is entered. Exporting makes no new AI request and never accepts browser-supplied financial totals.

The landing-page Three.js preview includes an illustrative 36-second day/night cycle. The sun and moon appear in separate phases, with changing scene light and sky colour. Its pause control freezes the animation; reduced-motion settings and offscreen visibility limit animation. This is a decorative preview, not a local sunrise forecast.
Traffic disappears at night and returns in daylight, resuming its motion without a jump. The moon advances through eight illustrative phases across successive nights, and soft clouds drift slowly with day/night colours. This accelerated cycle does not follow the real lunar calendar.

