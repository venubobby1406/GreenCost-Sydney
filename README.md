# GreenCost

Compare the whole-life cost of conventional and sustainable building designs over **30, 40 and 50 years**. GreenCost uses Python for all financial calculations, Three.js for the interactive building, and optional **OpenRouter → Groq → Gemini** explanations. Tavily supplies optional research context and supplier searches. AI does not set prices or calculate savings.

**No SQL, NoSQL, vector database, database account, or database installation is required.** Research is kept in ordinary files. Recent comparisons stay in your browser. Local installations can also save JSON reports.

The **Home** page introduces GreenCost and its interactive building. **Compare** opens the three-step calculator and results at `/compare`. **Method & evidence** is a supporting reference page; `/sources` redirects there.

For a complete nontechnical walkthrough, technology explanation and five-minute presentation script, read the [Client Presentation and Execution Guide](docs/GreenCost-Client-Guide.md).

## Appearance and charts

The interface follows [TensorTonic](https://www.tensortonic.com/)'s warm neutral light palette, near-black dark palette, green accents and Satoshi headings. The sun/moon button in the header switches themes across Home, Compare and Method & evidence. The first visit follows your device preference; a manual selection is saved under `greencost-theme` in this browser. It does not alter or reset a project draft. With browser storage unavailable, the toggle still works for the current page.

Cost charts use green for the sustainable design and a dashed orange line for the conventional design. Axes, legends and tooltips change with the theme. Axis amounts use compact labels such as `$750K`; tooltips and tables retain full amounts. The Overview opens with charts visible, and the study-period selector continues to compare 30, 40 and 50 years. Styling does not change the calculation model or exported PDF layout.

Satoshi is delivered by the official Fontshare CDN, with the bundled Inter font as its fallback. No font API key is required. The font license and visual-source attribution are recorded in `frontend/THIRD_PARTY_NOTICES.md`. The Three.js scene retains its own illustrative day/night cycle, independently of the website theme.

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

**After changing code while running production:** press **Ctrl+C** in the startup terminal, run the production command again to rebuild, then refresh the browser. Development and production share `.next`; stop the frontend before building. Do not run two instances on ports 3000/8000.

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

## Optional AI explanations and live research

The setup script creates `.env` only if it does not already exist. Add keys to that file, not frontend files:

```dotenv
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=openrouter/free
GROQ_API_KEY=your-key
GROQ_MODEL=openai/gpt-oss-20b
GEMINI_API_KEY=your-key
GEMINI_MODEL=gemini-2.5-flash
TAVILY_API_KEY=your-key
TAVILY_DAILY_CAP=10
TAVILY_MONTHLY_CAP=200
OPENROUTER_DAILY_CAP=20
OPENROUTER_MONTHLY_CAP=400
GROQ_DAILY_CAP=20
GROQ_MONTHLY_CAP=400
GEMINI_DAILY_CAP=20
GEMINI_MONTHLY_CAP=400
```

Restart after editing. Choose models available in your provider accounts; availability and quotas can change. Explanation order is **OpenRouter → Groq → Gemini → calculated explanation**. Missing keys are skipped. A usable reply stops the chain, so later providers receive no request. Failed or rejected replies allow the next provider, with one bounded attempt per provider. OpenRouter configuration accepts `openrouter/free` or a model ID ending in `:free`; this does not guarantee account availability.

A normal online comparison makes at most one context search and can attempt up to three explanation providers when earlier attempts fail. Supplier pricing is separate: a full breakdown refresh makes up to five search requests, and an individual refresh makes at most one. Successful price checks are reused for up to a day; rapid repeated attempts have a cooldown. Follow-up qualitative questions and explicit research retries can use additional requests. Financial what-ifs and exports make no external calls.

Explanation providers receive scenario context and selected research excerpts. Tavily receives research and supplier queries. These providers do not control arithmetic or official tariff values. Administrators should exclude confidential research from the bundled library when optional AI is enabled. Keep keys in backend configuration and out of Git.

Local caps count requests, not credits, and are persisted as JSON. **Serverless instances cannot share a global counter without shared storage.** Hosted AI is therefore off by default. Keep account-level quotas in place before enabling it.

Official references: [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing), [Tavily pricing](https://help.tavily.com/articles/8816424538-pricing), [Vercel Hobby rules](https://vercel.com/docs/plans/hobby).

## Deploy on Vercel

### Where environment variables belong

| Environment | Backend configuration | Frontend configuration |
| --- | --- | --- |
| Local VS Code | Project-root `.env`, loaded by FastAPI. | Normally none: the proxy defaults to `http://127.0.0.1:8000`. For an override, use `frontend/.env.local`. |
| Live Vercel | Backend project → Settings → Environment Variables. | Frontend project → Settings → Environment Variables. |

Vercel does not automatically copy your local `.env` to the deployment. Add variables to the correct project and select **Production** for the live site. Use **Preview** settings separately if you want preview deployments to work. Changes need a new deployment; see [Vercel environment variable guidance](https://vercel.com/docs/environment-variables/managing-environment-variables).

### Backend: required live settings

Start with these values in the **backend Vercel project**. Replace the example frontend domain with your actual frontend URL:

```dotenv
ALLOWED_ORIGINS=https://YOUR-FRONTEND.vercel.app
SAVE_LOCAL_ANALYSES=false
ENABLE_HOSTED_AI=false
REQUESTS_PER_MINUTE=120
```

| Variable | Purpose / value |
| --- | --- |
| `ALLOWED_ORIGINS` | Exact permitted frontend origins, including `https://`. Separate multiple origins with commas, without paths. Add your custom domain and explicit preview origins if used. Do not use `*`. |
| `SAVE_LOCAL_ANALYSES` | `false` for Vercel. Local JSON analysis files are not durable hosted project storage. Locally, the default is `true`. |
| `ENABLE_HOSTED_AI` | `false` for offline launch testing. On Vercel, `true` permits both explanation providers **and Tavily** when keys and caps are configured. This switch does not disable local research requests outside Vercel. |
| `REQUESTS_PER_MINUTE` | Positive integer; default `120`. Limits POST requests per client as seen by one backend instance. It is not a global distributed rate limit. |

The calculator, local evidence and report exports can work with hosted AI disabled. No database URL or login secret is required by the current application.

### Backend: optional provider settings

Add only the provider keys you intend to use. These are **backend-only secrets**. The following values are placeholders, not real keys:

```dotenv
OPENROUTER_API_KEY=replace-with-your-openrouter-key
OPENROUTER_MODEL=openrouter/free
OPENROUTER_DAILY_CAP=20
OPENROUTER_MONTHLY_CAP=400

GROQ_API_KEY=replace-with-your-groq-key
GROQ_MODEL=openai/gpt-oss-20b
GROQ_DAILY_CAP=20
GROQ_MONTHLY_CAP=400

GEMINI_API_KEY=replace-with-your-gemini-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_DAILY_CAP=20
GEMINI_MONTHLY_CAP=400

TAVILY_API_KEY=replace-with-your-tavily-key
TAVILY_DAILY_CAP=10
TAVILY_MONTHLY_CAP=200
```

| Provider | What it does | When it is used |
| --- | --- | --- |
| OpenRouter | Qualitative explanations. | First choice; free router or model ID ending in `:free`. |
| Groq | Qualitative explanations. | Second choice if OpenRouter is unavailable or its reply is unusable. |
| Gemini | Qualitative explanations. | Last provider fallback. |
| Tavily | Web research and supplier-price searches. | Separate from the explanation fallback chain. |

Choose model IDs accessible to your account. Leave unconfigured keys absent or blank. A successful earlier explanation stops the chain. If none succeeds, Python results still appear with a calculated explanation.

Caps are integer request counts, not money or credits; a cap of `0` prevents that provider's requests. Hosted counters are per instance and can reset, so they cannot guarantee account-wide quotas. Configure provider account limits and host abuse protection before changing **`ENABLE_HOSTED_AI=true`**, then redeploy the backend. Do not make live provider calls just to check that a key is present; Research connections reports configuration separately from request outcomes.

### Frontend: live settings

Add this to the **frontend Vercel project**, before its build:

```dotenv
GREENCOST_API_URL=https://YOUR-BACKEND.vercel.app
NEXT_TELEMETRY_DISABLED=1
```

| Variable | Required? | Purpose |
| --- | --- | --- |
| `GREENCOST_API_URL` | Yes for deployment. | Backend base URL, including `https://`, without `/api` or a trailing slash. Used server-side for the API proxy and streaming route. If missing, it defaults to localhost, which will not reach your deployed backend. |
| `NEXT_TELEMETRY_DISABLED` | Optional. | `1` disables Next.js telemetry. It is not an application credential. |

**Do not add OpenRouter, Groq, Gemini or Tavily keys to the frontend. No `NEXT_PUBLIC_` variables are needed.** The browser calls the frontend's `/api` paths; the server forwards them to the backend.

For a local proxy override only, `frontend/.env.local` can contain:

```dotenv
GREENCOST_API_URL=http://127.0.0.1:8000
NEXT_TELEMETRY_DISABLED=1
```

Restart development after editing it, or rebuild/restart production. Putting this override only in the project-root `.env` does not configure Next.js when it runs from `frontend`.

### Deployment order and checks

1. Deploy the backend with `ENABLE_HOSTED_AI=false` and the intended frontend origin. If its URL is not known yet, update the origin after creating the frontend.
2. Copy the backend base URL into the frontend's `GREENCOST_API_URL`, then deploy the frontend.
3. Set backend `ALLOWED_ORIGINS` to the actual frontend origin and redeploy the backend. Include the custom domain if applicable.
4. Open `https://YOUR-BACKEND.vercel.app/api/health`: check `status: ok`, `rag_ready: true` and provider configuration flags. Flags confirm configuration, not working credentials.
5. Open `https://YOUR-FRONTEND.vercel.app/api/health` to check the proxy. Test a sample calculation, PDF export, draft restoration and project import with hosted AI still disabled.
6. When ready for optional online research, add backend keys, account controls and caps, set `ENABLE_HOSTED_AI=true`, and redeploy the backend.

Keep `.env` and `.env.local` files out of Git; `.env.example` contains safe placeholders. Do not manually set Vercel's platform-provided `VERCEL` variable. `LANGSMITH_TRACING=false` in the local example is not required by the current execution path, and no LangSmith key is needed.

### Vercel project configuration

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

To use optional APIs on Vercel, add the configured provider keys, model settings and request caps to the **backend project only**. Set `ENABLE_HOSTED_AI=true` only after configuring provider quotas and host abuse protection. Per-instance rate limits and counters are not a distributed spending guarantee. Preview frontend domains must also be explicitly allowed.

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

Additional regression checks, run from the project root:

```powershell
node scripts/check-apartment.cjs
node scripts/check-preview-retry.cjs
node scripts/check-report-export.cjs
```

Stop the frontend before rebuilding; development and production share `.next`. GitHub Actions runs backend tests/lint and frontend lint, type checks, build and dependency audit on pushes and pull requests. A yellow **pending** commit indicator means checks are queued or running; open **Actions** to inspect the outcome. Automated provider tests use mocked contracts. Historical verification documents describe their recorded versions, not the current health of every provider. See [production verification](docs/PRODUCTION_VERIFICATION.md) and [UI verification notes](docs/UI-COMPONENT-REFRESH.md) for evidence and limits.

## Project structure

```text
backend/app/calculations/   financial engine, legacy fixture, energy and takeoff
backend/app/schemas/        validated input models
backend/app/services/       analysis, JSON files, PDF/HTML reports, API budgets
backend/app/rag/            local PDF passage retrieval (not a database)
frontend/app/               comparison and method/evidence pages
frontend/components/        guided form, upgrade picker, Three.js and charts
frontend/components/ui/     shared tabs, checkbox and keyboard-accessible select
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

**AI busy / quota reached:** the provider status identifies temporary demand, quota or model-access errors where available. OpenRouter is attempted first, followed by Groq and Gemini if needed. Financial calculations still finish with built-in explanations when no provider returns usable text.

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

The eight-stage timeline shows actual start/completion events with a completed-stage progress bar. OpenRouter, Groq, Gemini and Tavily have separate request outcomes; a configured key alone is not a successful request. The first usable explanation ends the fallback chain. If all available providers fail, a calculated explanation is used. Python financial results do not depend on an AI response.

Removal estimates are restricted to supported ordinary house scopes from a dated contractor guide. Both designs use the same allowance, recovered-material income defaults to zero, and manual quotes can override it. End-of-study demolition is optional, not automatic. The initial cost, maintenance present value and total present value are prominent in results and reports. See [client refresh notes](docs/Client-Refresh-Notes.md) for sources and scope.

## Client decision report

The PDF uses a **five-page report structure**. PDF and printable HTML reports include the project name, start with initial building cost, routine maintenance and total cost, then explain savings, investment recovery, selected upgrades, important assumptions and next steps in everyday language. Interactive cost charts are available in the dashboard. Technical inputs stay available in the project JSON and annual cash-flow CSV instead of being printed as raw records. Maintenance is included in the total, not added to it again.

Downloads contain project-specific paragraphs built from validated inputs, selected upgrades and calculated results. Provider/request diagnostics and metadata replies are kept out of client reports. Reports use the project name in the download filename, with a GreenCost fallback when no name is entered. Exporting makes no new AI request and never accepts browser-supplied financial totals.

## Interface and interactive building

The component refresh keeps the green visual identity and introduces:

- Animated upgrade-category and dashboard tabs, with keyboard navigation.
- Styled selection menus supporting arrows, Home, End, Escape and typeahead.
- Animated checkboxes with native input semantics, inline validation and accessible help.
- Expandable panels and dropdowns with larger, high-contrast circular chevrons.
- Stacked material editors that stay inside the form; fields use one column on mobile.
- Clear selected-upgrade cards and dashboard totals, initial construction cost and maintenance.
- Responsive navigation, saved-project access and a progress bar driven by completed analysis stages.

The component choices were reviewed against EasyUI. Animated tabs and checkboxes adapt MIT-licensed source; attribution is in [THIRD_PARTY_NOTICES.md](frontend/THIRD_PARTY_NOTICES.md). Other patterns use existing project dependencies without adding a package. See [component refresh notes](docs/UI-COMPONENT-REFRESH.md).

The landing-page Three.js preview has one to four distinct floors, optional solar panels, trees, a small road, a car and a cyclist on separate paths. Its illustrative **36-second day/night cycle** changes scene light, sky and control colours. The sun and moon appear in separate phases. Traffic disappears at night and returns in daylight, resuming its motion without a jump. The moon advances through eight illustrative phases across successive nights, and soft clouds drift with day/night colours. The decorative orbiting ring and dot above the solar panels have been removed.

The pause control freezes animation; reduced-motion preferences and offscreen visibility limit it. This is a decorative preview, not a local sunrise forecast, solar assessment or real lunar calendar.

## Technology and execution flow

| Layer | Technology and purpose |
| --- | --- |
| Frontend | Next.js, React, TypeScript and CSS/Tailwind tooling for pages and forms. |
| UI and motion | Shared local components, Framer Motion and Lucide icons. |
| Interactive building | Three.js, React Three Fiber and Drei. |
| Results charts | Recharts. |
| Backend | Python, FastAPI and Pydantic input validation. |
| Reports | ReportLab PDFs, printable HTML, CSV and JSON exports. |
| Research | Local PDF passage retrieval and optional Tavily searches. |
| Explanations | OpenRouter, Groq and Gemini with calculated fallback. |
| Storage | Browser drafts/history and ordinary JSON files; no database service. |

The browser sends project inputs through the Next.js API proxy to FastAPI. Python validates the scope, builds both designs, applies utility rates and calculates the horizons and sensitivity cases. Local evidence and optional online research support explanations. The frontend receives progress events and displays returned calculations and charts. Report routes rebuild validated inputs rather than accepting financial totals supplied by the browser.

The UI refresh does not change backend formulas or provider order. Example projects demonstrate the workflow; sustainable designs are not guaranteed to cost less.

