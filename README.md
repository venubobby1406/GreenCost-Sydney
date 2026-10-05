# GreenCost Sydney

Compare the whole-life cost of a conventional and upgraded building over **30, 40 and 50 years**. GreenCost uses Python for all financial calculations and Three.js for the animated building. Gemini and Tavily are optional.

**No SQL, NoSQL, vector database, database account, or database installation is required.** Research is kept in ordinary files. Recent comparisons stay in your browser. Local installations can also save JSON reports.

There are two main pages: **your comparison** and **method & evidence**. The existing `/sources` address redirects to the second page.

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

No API key is needed to calculate, inspect evidence, compare scenarios, or export reports.

## Example 1: explore the supplied house

1. Choose **Explore a sample** or **Fill sample**.
2. Continue through **Your building**, **Costs & consumption**, and **Your greener alternative**.
3. Inspect the selected insulation, solar and rainwater upgrades. Prices say **Indicative** because they are not verified builder quotes.
4. Review disposal and salvage, then choose **Analyse my building**.
5. Switch between 30, 40 and 50 years, examine the contribution chart and sensitivity table, and download PDF, HTML or CSV.

The sample is an illustration. Do not reuse its costs or consumption as measurements of your own house.

## Example 2: use your own project

Choose **Start fresh**, then enter your Greater Sydney postcode and the distributor shown on your bill. For a practice example, use 2000, Ausgrid, 220 m², one floor, a $600,000 construction budget, 5,200 kWh electricity and 200 kL water annually. These are **example inputs**, not construction benchmarks.

In itemised mode, select solar. Open **Price source & your quote** and enter your builder's installed **difference** versus the baseline, for example $6,500. Set the array size to 6.6 kW. Enter disposal costs, for example $33,000 in each case, and explicitly confirm any zero salvage amounts. These end-of-life values are also illustrative.

Choose **Analyse my building**. Use **Refine your inputs** to try another quote or discount rate. A positive signed saving means the upgraded scenario costs less; a negative saving means it costs more. The app does not force a sustainable-building saving.

Choose **Literature scenarios** to explore percentage assumptions instead. Low / Mid / High scenarios use the package's research ranges and reduce variable utility charges, while retaining fixed charges.

## Save, reopen and share

- **Save project** downloads a JSON file containing inputs, captured rates and results. Use **Open saved project** to reload the inputs and recalculate.
- **Save current inputs** works before analysis; unfinished inputs must be completed before they can be reanalysed.
- **Share** copies a URL containing inputs and captured utility rates. The recipient opens it and chooses **Analyse**. This reproduces financial results for assumption version `2026-10-v1`; optional AI wording may differ.
- **Recent comparisons on this device** retains the last three results when browser storage is available. **Clear device history** removes them.

Share links and downloaded files contain project details. Do not put private information in the project name or share a link publicly unless you intend to disclose its inputs. With browser storage disabled or full, calculations and downloads still work.

## Use free Gemini and Tavily keys

The setup script creates `.env` only if it does not already exist. Add keys to that file, not frontend files:

```dotenv
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
TAVILY_API_KEY=your-key
TAVILY_DAILY_CAP=10
TAVILY_MONTHLY_CAP=200
GEMINI_DAILY_CAP=20
GEMINI_MONTHLY_CAP=400
```

Restart after editing. Choose a model available in your Gemini account. Free services have quotas; timeouts, quota errors and unavailable models fall back to calculated explanations. A normal online comparison makes at most one search and one explanation call. Follow-up qualitative questions may make an additional explanation call. Financial what-ifs and exports make no external calls.

Gemini sees non-identifying scenario facts and selected research excerpts. Tavily receives a general building-feature search. Neither provider controls arithmetic or official tariff values. Do not upload confidential research when optional AI is enabled.

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

Vercel has no durable local filesystem. Uploaded PDFs are disabled there; add PDFs locally, run `scripts/ingest_knowledge.py`, and redeploy. Results are retained in the browser or exported files. Server-side report/chat routes rebuild validated inputs with captured rates, rather than relying on a saved server ID. No hosted deployment has been performed or verified against your account.

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

The supplied package's **full official Greater Sydney postcode/network/climate concordance and supplier price pipeline are not complete in this delivery**. The interface asks users to select the actual electricity distributor from their bill, uses clearly labelled indicative upgrade differences, and accepts project quotes. It does not guess a climate zone or claim live supplier prices. Supplier terms, paired baseline/upgrade product specifications, verified unit prices, and incentive eligibility must be approved before live price updates are implemented/enabled. These outstanding requirements are recorded in `DECISIONS.md`.

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

Stop the frontend before rebuilding; development and production share `.next`. GitHub Actions runs backend and frontend checks on pushes and pull requests. Live provider requests use mocked contracts in tests; no real key or supplier price was used to verify this delivery.

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

**Solar too large:** reduce the array or override roof area from your drawings. An override is an estimate, not network approval.

**PDF upload rejected:** use a readable, unlocked, text-based PDF, at most 10 MB and 200 pages. Scans need OCR. Hosted deployments use a read-only library.

**Report or chat fails on Vercel:** verify the backend URL, origin allow-list, deployment protection and backend function logs. Do not put provider keys in the frontend.
