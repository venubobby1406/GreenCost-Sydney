# GreenCost — Client Presentation and Execution Guide

The interface was refreshed on 7 October 2026. See [Client refresh notes](Client-Refresh-Notes.md) for draft recovery, occupant assumptions, end-of-life estimates and the new results labels. The financial model still uses canonical kL internally. **Apartment building** now covers the whole building; previously saved **Apartment unit** projects keep their original single-flat scope.

For an apartment building, enter **Area per floor** or **Total building area** and a required floor count. For example, 500 m² per floor × 20 floors gives 10,000 m² and 219 estimated occupants with the editable illustrative defaults of 75 m² per apartment and 80% apartment space. Total-area mode stores the already combined area without multiplying it again. **Enter actual number** provides a manual resident count, which stays fixed when area or floors change. The estimate uses a dated dwelling-level BASIX energy relationship; there is no claimed universal Sydney area-per-person standard. These assumptions are not legal capacity or predicted water consumption.

Keep budgets, annual usage and meter charges on the same whole-building scope. Use aggregate bill rates instead of single-house reference charges. Confirm room/bathroom totals under optional details. Generic upgrade coefficients are indicative and do not model a complete tower specification; include lifts, central plant, parking and common-system costs through project quotes, maintenance and replacement allowances. Occupancy does not automatically replace measured/design electricity or water usage. See the [README apartment example](../README.md) for additional details.


**Prepared: 6 October 2026**  
**Audience:** the project owner, client and anyone who wants to understand GreenCost without reading code.  
**Scope:** the current local application, based on its implementation and recorded verification.

## Quick briefing

GreenCost compares the long-term cost of the same building with a conventional specification and a sustainable upgrade specification. It combines construction costs, utility use, maintenance, replacements and end-of-life costs over **30, 40 and 50 years**.

The website collects your inputs. **Python calculates the numbers.** Included research supports the explanation. **Tavily** optionally searches for web context and supplier prices. **Gemini** optionally adds a plain-language interpretation.

The project runs without a database. It has a Home page, a Compare page and a supporting Method & evidence page.

For the client, say:

> “GreenCost helps us compare building choices over their whole life, rather than looking only at construction cost. We can see the extra upfront investment, possible running-cost benefits and when the two options cross over. The result depends on the inputs and assumptions, which we can inspect and edit.”

The current release is suitable for a **local software demonstration and scenario discussion**. It is an indicative planning tool, not a builder quotation, energy simulation or regulatory certificate.

## Contents

1. [What GreenCost does](#1-what-greencost-does)
2. [Start the project locally](#2-start-the-project-locally)
3. [Walk through the website](#3-walk-through-the-website)
4. [Budget estimation and supplier pricing](#4-budget-estimation-and-supplier-pricing)
5. [What happens after Compare](#5-what-happens-after-compare)
6. [How the calculations work](#6-how-the-calculations-work)
7. [Read the results correctly](#7-read-the-results-correctly)
8. [Gemini, Tavily and the research library](#8-gemini-tavily-and-the-research-library)
9. [Save, reopen, share and export](#9-save-reopen-share-and-export)
10. [Technology and architecture](#10-technology-and-architecture)
11. [A complete worked example](#11-a-complete-worked-example)
12. [A five-minute client demo script](#12-a-five-minute-client-demo-script)
13. [Common questions and troubleshooting](#13-common-questions-and-troubleshooting)
14. [Verification and public-launch boundaries](#14-verification-and-public-launch-boundaries)
15. [Technical reference and glossary](#15-technical-reference-and-glossary)

## 1. What GreenCost does

The main question is:

> “If we spend more or less on these building improvements now, what happens to our total cost over the years?”

GreenCost compares the **same building geometry** under two specifications:

| Scenario | Meaning |
|---|---|
| Conventional building | The baseline building cost, consumption and specification supplied by the user. |
| Sustainable building | The baseline plus selected upgrades, or a research package with stated cost and consumption assumptions. |

The app can explore a home, apartment or another building type. Its current regional focus is **Sydney, New South Wales, Australia**, with amounts in Australian dollars.

Selecting a postcode does not automatically establish the correct electricity distributor or climate zone. The user selects the distributor from their bill. Commercial/other projects need applicable custom utility rates.

The app compares financial scenarios. It does not currently produce a verified carbon-footprint assessment or decide which building is environmentally best.

## 2. Start the project locally

### Open the project

In VS Code, choose **File → Open Folder** and open:

~~~text
D:\Project A\GreenCost
~~~

Open a PowerShell terminal in that folder. The project needs **Python 3.12 or newer** and **Node.js 22 or newer**.

### Start the optimized build

If GreenCost is already running, open the website directly. Start one server session at a time.

~~~powershell
.\scripts\start-local.ps1 -Production
~~~

When startup completes, open:

**http://127.0.0.1:3000/**

For development while editing code, use:

~~~powershell
.\scripts\start-local.ps1
~~~

### What the startup script does

1. Checks that ports **3000** and **8000** are available.
2. Checks the Node.js and Python versions.
3. Creates the Python environment if needed.
4. Installs or reuses the locked dependencies.
5. Creates the root **.env** file from the example only if it is missing.
6. Prepares the included research documents and their local passage index.
7. Builds the optimized frontend when **-Production** is selected.
8. Starts the Python backend on **127.0.0.1:8000**.
9. Waits for the backend health check, then starts the website on **127.0.0.1:3000**.

Keep the startup terminal running. **Ctrl+C** in that terminal stops the services started by the script. Closing browser tabs does not stop the servers.

The address starts with 127.0.0.1 because the app is running on your computer. It is not a public client-access link.

### API configuration

The root **.env** file holds backend settings such as:

~~~dotenv
GEMINI_API_KEY=your-key
GEMINI_MODEL=model-available-in-your-account
TAVILY_API_KEY=your-key
~~~

Actual keys stay out of this guide and out of the frontend. Restart the backend after changing them. The cost engine, included evidence and exports work without these provider keys.

## 3. Walk through the website

### Home

The landing page introduces GreenCost, explains the basic process and shows an animated Three.js building.

- **Start comparison** opens the calculator.
- **Explore a sample** opens the calculator with illustrative inputs.
- Floor controls display one to four storeys.
- The solar control changes the preview.
- **Method & evidence** explains assumptions and sources.

The animated building is a **visual preview**. Its floor and solar buttons do not fill or change your actual project inputs. Enter the real building details in the calculator.

### Compare — Step 1: Building details

| Input | What it means |
|---|---|
| Project name | An optional name for saved files and reports. |
| Postcode | The location you are describing; check actual service coverage. |
| Building type | House, one apartment unit or commercial/other premises. |
| Total floor area | Combined area of all floors, not just the ground floor. |
| Area unit | Square metres or square feet; square feet are converted for calculations. |
| Number of floors | Optional house detail; shown for commercial premises. Not the entire apartment building. |
| Number of occupants | Suggested for a house using a dated BASIX energy assumption, with manual override in optional details. Enter the actual unit/premises occupants for other types. Bill consumption determines utility costs. |
| Optional details | Rooms, bathrooms, build quality and whether inputs are estimates, actual inputs or demo assumptions. |

Required fields are marked with an asterisk (*). The **ⓘ** beside a label explains the field through hover, keyboard focus or a click/tap.

A missing or invalid value gets a reason beside that field. Continuing focuses the first problem. A number can be cleared completely; blank does not silently become zero.

### Compare — Step 2: Budget & bills

First choose how to enter construction cost:

| Option | Use it when |
|---|---|
| Exact budget | You know the complete construction budget. |
| Budget range | You know a lower and upper estimate. |
| Cost per m² | You know an approximate construction rate. |
| Detailed costs | You want the baseline calculated from item quantities, prices and remaining construction scope. |

Construction cost excludes land and finance. Review whether your quote includes all construction scope.

Next enter electricity and water **consumption**, not the bill amount:

- Electricity: **kWh**.
- Water: **litres (L)**, with a **million-litre equivalent**. 500,000 L is 0.5 million litres. The tariff calculation converts litres to kL internally.
- Annual use: enter the whole-year total.
- Monthly average: enter an average month; the app multiplies it by twelve. A single seasonal month may not represent a full year.
- Deliberate zero use needs confirmation. Fixed service charges can still apply.

Then choose the utility price source:

- **Sydney reference rates:** select the electricity distributor and review the dated reference charges.
- **My bill rates:** enter usage rates, fixed charges and a bill/contract reference.

Reference-rate previews use the same backend tariff function as the final calculation. They are dated residential reference charges, not a guaranteed retail offer.

Connection settings determine which fixed water services apply. Review the price-reference date, wastewater, stormwater and drought settings where relevant.

### Compare — Step 3: Sustainable design

**Choose upgrades** is the itemised comparison. Available choices include insulation, glazing, air sealing/shading, heating and cooling, hot water, solar, rainwater, water-efficient fixtures, lighting, smart controls and sustainable materials.

For each selected upgrade, inspect the installed cost difference and its source. Use your own installed difference or comparable baseline/upgrade quotes when available. Sustainable material alternatives require a project price; the app does not invent a default benefit for them.

Mark an upgrade **already included / required in my baseline** when appropriate. It then gets no additional upgrade cost or modelled benefit, avoiding a second claim for something already present.

**Research scenarios** is the alternative package approach. It applies stated construction premiums and usage/maintenance reductions instead of calculating an individual upgrade package. Research percentages are assumptions, not promised savings.

Advanced sections let you review:

- Financial growth and discount rates.
- Maintenance and component replacements.
- Gas use and solar export credit.
- System sizes and drawing quantities.
- Disposal costs and salvage credits.

Choose **Remains in use**, a supported house removal estimate, or manual costs. Estimated removal uses the same allowance for both designs and no unquoted material-sale income; review scope before confirming. Ending a study does not automatically mean demolition.

### Review before calculating

Choose **Review comparison**. Check the Building, Budget & bills and Upgrades & assumptions summaries. Their **Edit** buttons return to the relevant inputs.

Choose **Compare my building** to start the calculation.

## 4. Budget estimation and supplier pricing

Entering a budget can generate an editable category breakdown. This makes the first comparison easier without requiring dozens of manual material entries.

The breakdown is a **budget allocation estimate**, not a measured bill of quantities or verified Sydney market price.

The initial allocation is:

| Category | Share of entered budget |
|---|---:|
| Concrete & foundations | 8% |
| Structural timber | 6% |
| Roof covering | 5% |
| Windows & external glazing | 6% |
| Wall insulation | 2.5% |
| Internal finishes & fittings | 12.5% |
| Labour & installation allowance | 25% |
| Services, site work, fees & remaining allowance | 35% |
| **Total** | **100%** |

The six material rows total 40%. The form combines the remaining 60% in an editable remaining-scope field. Quantities use simplified building geometry; drawings and quotes take priority.

### What live supplier checks do

**Find prices for this breakdown** uses Tavily to check up to five supported material categories. An individual row also has a price-check option.

The pipeline looks for evidence from supported supplier pages. A price needs a clear matching unit and explicit GST inclusion. Search snippets alone are insufficient.

- A single usable matching price can fill the supply-price field.
- Multiple products need user selection.
- Ambiguous, missing, pack-based or quote-only prices stay unresolved.
- Your price and intervening edits are protected from an automatic overwrite.
- Recent checks are cached for up to a day; retries have a cooldown.

Supply prices do not establish installation costs, delivery to the project or product suitability. Whole-building installed prices are not automatically obtained from a supplier search.

**Important:** in exact/range/rate mode, the entered budget remains the calculation baseline. Editing a material allowance does not silently change that baseline. Choose **Use edited breakdown as construction total** to adopt the detailed sum.

For an installed upgrade, the comparison uses:

~~~text
Installed upgrade difference = comparable upgraded quote − comparable baseline quote
~~~

Use quotes for the same scope and GST basis. A negative difference is allowed when the upgraded option is cheaper. Installed upgrade differences already include labour, margin and GST; those amounts are not added again.

## 5. What happens after Compare

The browser sends the project through the frontend API proxy to FastAPI. The backend runs these **eight stages in order**:

| Stage | What happens |
|---|---|
| 1. Validate inputs | Pydantic checks types, supported choices, ranges and consistency. Browser validation is supported by server validation. |
| 2. Retrieve local evidence | Relevant passages are selected from the included project research files, with source/page information. |
| 3. Research online | If enabled and available, Tavily adds bounded web context from supported official domains. |
| 4. Check utility data | The backend uses applicable dated reference rates, custom bill rates or a supplied captured-rate snapshot. |
| 5. Prepare both scenarios | It assembles baseline and sustainable capital, consumption, maintenance, replacements and terminal values. |
| 6. Calculate life-cycle costs | Python builds annual cash flows for both buildings over 30, 40 and 50 years. |
| 7. Test sensitivity | It calculates 48 discount/electricity-growth combinations across the three horizons. |
| 8. Generate explanation | Built-in text explains the calculated totals. Gemini may add a validated qualitative explanation for the chosen main horizon. |

The app then assembles the detailed outputs, sources, assumptions and provider statuses. It returns progress messages and the final result through a **server-sent event stream**.

The browser displays the result and stores the last three completed comparisons when browser storage is available. Local installations can also save ordinary JSON analysis files. No database is involved.

Optional provider failures leave the cost calculation available with included evidence and a calculated explanation. Invalid required inputs or a failed backend connection still need correction.

## 6. How the calculations work

### Capital and usage

In quick cost mode:

~~~text
Baseline construction = exact budget
                     OR floor area × cost per m²
                     OR midpoint of the budget range
~~~

In detailed mode:

~~~text
Baseline construction = sum(quantity × unit price) + remaining construction scope
~~~

In itemised upgrade mode:

~~~text
Sustainable construction = baseline construction + selected installed upgrade differences
~~~

Itemised operating effects use indicative end-use assumptions. Insulation and equipment changes are applied together rather than adding overlapping percentage savings independently. Solar accounts for indicative self-use and exports; rainwater savings are constrained by the modelled system and demand.

These are simplified scenario models, not a physical simulation of a completed building.

### Annual operating costs

~~~text
Base electricity cost = grid kWh × usage rate + 365 × daily supply charge
Base water cost       = mains kL × usage rate + annual fixed water charges
~~~

Applicable gas costs and solar export credits are included when configured. Lower usage does not automatically remove fixed service charges.

For example, using the tested residential reference snapshot:

~~~text
Electricity: 5,200 × 0.3314 + 365 × 1.66 = AUD 2,329.18
Water:      200 × 3.41 + 859.06         = AUD 1,541.06
~~~

These are **base-year conventional utility amounts**, before future escalation and discounting. The reference charges depend on the selected date and connections.

### Growth and discounting

**Price growth** increases or decreases a base-year cost in future years.

**Discounting** expresses future costs in today's equivalent value. A higher discount rate usually gives less weight to distant operating savings.

~~~text
Year-t cost = base-year cost × (1 + annual growth rate)^t
Present value of year-t cost = year-t cost ÷ (1 + discount rate)^t

Life-cycle cost = upfront construction
                + discounted operating and replacement costs
                + discounted disposal
                − discounted salvage
~~~

Capital occurs at year zero. Ordinary annual expenses occur at year end. Prices escalate once before year one under the current base-year convention.

Replacements occur at their entered intervals **before retirement**, not at the terminal year. Disposal and salvage occur at the end of each selected study period.

The separate legacy study fixture uses an explicitly preserved historical convention. It exists for regression checks, not as a current compliant-house example.

## 7. Read the results correctly

| Result | Meaning |
|---|---|
| Sustainable / conventional life-cycle cost | Total present-value cost for the selected horizon, including upfront construction. |
| Initial construction | The year-zero cost, shown separately from the long-term total. |
| Upfront difference | Sustainable capital minus conventional capital. Positive means more upfront investment. |
| Whole-life difference / signed savings | Conventional life-cycle cost minus sustainable life-cycle cost. Positive means sustainable costs less; negative means it costs more. |
| First break-even | First year sustainable cumulative discounted cost is no higher than conventional cost. Year zero can occur if it starts cheaper. |
| Not reached | No crossover within that selected horizon. It does not establish what happens beyond it. |
| Confidence | A rule-based description of input quality/model assumptions. It is not a statistical probability or professional certification. |

The **30 / 40 / 50-year selector** shows results already calculated for each horizon. A different retirement year also changes terminal cash flows.

Expand the low/midpoint/high budget section for range comparisons. These are separately recalculated costs, not merely a decorative price range.

The results tabs provide:

- **Overview:** headline comparison, expandable charts and explanation.
- **Sensitivity:** 16 discount/growth combinations for the selected horizon; 48 across all three.
- **Cash flows:** annual costs, cumulative present values and replacement events.
- **Evidence & sources:** research passages and dated reference links.
- **Assumptions:** the inputs and their stated basis.

Detailed upgrade contributions account for interactions and catalogue order. A percentage contribution can be negative or exceed 100% when one category offsets savings in another.

### Why sustainable can cost more

A sustainable option may have a higher initial cost, insufficient usage savings, expensive replacements or an unfavourable study horizon. Low electricity/water use leaves less usage cost to save. Discounting can also reduce the value of distant savings.

A higher sustainable total does **not by itself** prove the inputs are wrong. GreenCost does not force a particular savings percentage.

Break-even can reverse later after replacement or terminal costs. Inspect annual cash flows, not only the first crossover.

## 8. Gemini, Tavily and the research library

### Who does what?

| Component | Job | Effect on arithmetic |
|---|---|---|
| Python cost engine | Calculates capital, annual costs, discounting, sensitivity and break-even. | Produces the numerical results. |
| Included research library | Supplies relevant evidence passages and page references. | Does not overwrite calculation rules. |
| Gemini API | Adds optional qualitative interpretation and some question answers. | Does not calculate or set financial totals. |
| Tavily API — context search | Finds optional supported web context. | Does not silently replace utility tariffs. |
| Tavily API — supplier checks | Finds candidate supply-price evidence. | A usable price affects the baseline only when the edited breakdown is adopted. |

**Add web research** controls the Tavily context search. It is not a master switch for Gemini; Gemini can still be attempted when its key is configured and request limits permit it.

### What RAG means here

RAG means **retrieval-augmented generation**: locate relevant evidence before asking an AI to interpret it.

At setup, the app reads included PDFs and structured reference files, splits them into passages and stores them in ordinary JSON files. Passages retain source names and page numbers.

At runtime, lightweight word-based hashing and NumPy similarity ranking retrieve passages. The current implementation uses **local-hash-v1**, with no embedding API, downloaded language model or vector database. It is lexical retrieval, not a pretrained semantic embedding model.

The recorded library contains **8 documents and 73 passages**, including four supplied research PDFs and structured context/reference records. This count changes if an administrator updates the library.

The official reference records include Australian Energy Regulator electricity references, Sydney Water charges and an Australian Bureau of Statistics construction price index. The ABS index supports historical-cost indexation; it is not an absolute Sydney construction price per square metre. These dated records are separate from a fresh Tavily context search.

There is no public PDF-upload feature. Administrators maintain the bundled research files and rebuild the index.

### Provider status and fallback

“Key configured” means a key exists. It does not prove that a provider request succeeded.

Statuses can distinguish success, a missing/rejected key, model permissions, provider busy, quota reached, app request limits, incomplete output or text that failed validation.

Incomplete or unusable Gemini output is not appended to the explanation. Calculated text remains available, with a status and retry option where appropriate.

The latest production check recorded successful Tavily context retrieval and a calculated fallback after Gemini text failed validation. This was a handled provider-output condition; the financial result still completed.

Local default app caps are Tavily **10 requests/day and 200/month**, and Gemini **20/day and 400/month**, unless configured differently. They count attempts, not currency or provider credits.

A normal online comparison uses at most one context search and one Gemini explanation attempt. Supplier checks and qualitative follow-up questions are separate. Exports and supported numerical what-ifs do not make external AI/search calls.

## 9. Save, reopen, share and export

| Action | What it does |
|---|---|
| Save draft | Downloads unfinished inputs as JSON, including blank values. |
| Save project | Downloads inputs, captured utility rates and completed results as JSON. |
| My projects → Import saved project | Imports a GreenCost JSON draft/project; inputs are validated before use. |
| My projects → Saved on this device | Restores inputs from one of the last three browser-local comparisons for review and recalculation. |
| Clear device history | Removes those browser copies; downloaded files remain. |
| Share | Copies a URL containing encoded inputs and captured rates, not an account-based shared project. |
| PDF | Downloads a generated report for the selected horizon. |
| Report | Downloads an HTML report. |
| Cash flows → Download CSV | Downloads annual rows for use in a spreadsheet. |

The date shown in device history is the project's price-reference date.

Reports rebuild validated inputs and captured utility rates on the backend without making external provider calls. They use the calculated explanation; optional AI wording seen onscreen may not appear in the exported report.

Share recipients review the inputs and calculate again. Matching assumptions/data versions matter; a future software or catalogue revision is not guaranteed to reproduce an older result.

Recent history belongs to that browser/device. It is not cloud sync or automatic draft autosave. Download **Save draft** before leaving an unfinished form.

Share links are encoded, **not encrypted**. They and exported files contain project details. Use non-confidential examples in a client demonstration.

### Questions and what-ifs

**Ask about this analysis** can explain costs, sources and assumptions using included evidence.

Supported numerical questions such as “What if electricity rises 5% per year?” or “What if the discount rate is 7%?” rerun Python calculations using captured rates. They do not overwrite the main saved comparison.

For other numerical changes, edit the form and compare again. The chat is not a general automatic redesign tool.

## 10. Technology and architecture

### The technologies actually used

| Technology | Purpose |
|---|---|
| Next.js 15 and React 19 | Frontend pages, interactive form and server-side API proxy. |
| TypeScript | Checks frontend data shapes and component types. |
| CSS and Tailwind CSS | Layout, responsive styling and reusable visual styles. |
| Three.js | The animated architectural preview. |
| React Three Fiber and Drei | React integration, camera and orbit controls for Three.js. |
| Framer Motion | Interface and decorative motion, with reduced-motion support. |
| Recharts | Financial charts and tooltips. |
| Lucide React and reusable UI components | Icons, buttons and controls. |
| Python | Calculation logic, research processing and reports. |
| FastAPI and Uvicorn | Backend HTTP API and local server. |
| Pydantic | Server-side validation of inputs and snapshots. |
| NumPy | In-memory passage similarity calculations. |
| pypdf | Reading included research PDFs and verifying generated PDFs in tests. |
| ReportLab | Generating downloadable PDF reports. |
| HTTPX | Backend calls to Gemini and Tavily. |
| python-dotenv | Loading backend settings from .env. |
| JSON files and browser localStorage | File-based research/configuration/cache and device history. |
| pytest, Ruff, ESLint and TypeScript checks | Automated tests, Python/frontend linting and type validation. |

The current runtime uses a sequential Python workflow. It does not use LangGraph/LangChain orchestration or a LangSmith tracing integration. Setting a LangSmith environment variable alone does not add tracing.

SQL, NoSQL, SQLite and Chroma are not application storage. Historical FAISS artifacts are not used by the current retrieval path.

### Request flow

~~~mermaid
flowchart TD
    A["User enters building details"] --> B["Next.js website"]
    B --> C["Frontend API proxy"]
    C --> D["FastAPI backend"]
    D --> E["Validate inputs"]
    E --> F["Local evidence and utility records"]
    F --> G["Python cost engine"]
    G --> H["Results and calculated explanation"]
    D -. "Optional web context and supplier checks" .-> T["Tavily"]
    T -. "Context or candidate price evidence" .-> D
    H -. "Optional qualitative interpretation" .-> M["Gemini"]
    M -. "Validated text or fallback status" .-> H
    H --> B
    B --> I["Browser history and downloads"]
~~~

The diagram may appear as text in Markdown viewers without Mermaid support; the execution table in Section 5 explains the same process.

### Data and protection

Backend keys are not sent to the browser. Gemini receives selected scenario facts and research excerpts, without the project name/postcode in the explanation payload. Tavily receives a general research or material query.

The app has input validation, bounded request sizes, origin checks, per-instance request limits and provider budgets. These are safeguards, not authentication or a complete public-host abuse-protection system.

Local research, analyses and price/cache counters are ordinary files. Hosted execution is designed to rebuild reports from inputs rather than depend on durable server-local files.

Vercel deployment is planned but has not been performed or verified. The repository describes separate frontend and backend Vercel projects. Hosted optional AI defaults to off; per-instance counters do not provide a shared global quota across serverless instances.

## 11. A complete worked example

Use this reproducible **practice scenario**, not as a quotation for a real home.

Start with **Start comparison → Start fresh**.

| Setting | Practice input |
|---|---|
| Postcode / building type | 2000 / Residential House |
| Floor area / storeys / occupants | 220 m² / 1 / 3 |
| Optional rooms / bathrooms | Keep 3 rooms and 2 bathrooms |
| Construction budget | Range: AUD 600,000–800,000 |
| Electricity / water use | 5,200 kWh/year / 200,000 L/year (0.2 million litres) |
| Distributor / price source | Ausgrid / Sydney reference rates |
| Price-reference date | 6 October 2026 |
| Water settings | Water and wastewater connected; stormwater and drought options off |
| Upgrades | Extra wall/ceiling insulation and rooftop solar |
| Installed differences | Keep indicative defaults: AUD 3,200 insulation + AUD 5,800 solar |
| Solar size / export credit | Keep 6.6 kW / AUD 0.05 per kWh |
| Main horizon / discount | 40 years / 5% |
| Electricity growth | 3% per year |
| Other growth settings | Keep the 2.5% defaults |
| Annual maintenance | Keep blank explicit maintenance; 1% capital-based maintenance |
| Gas / extra replacements | Zero gas; no extra replacements |
| Disposal / salvage | Zero in both scenarios; explicitly confirm review |

Review the generated category breakdown, but retain the entered midpoint budget for this example. Do not adopt edited prices if you want to reproduce the recorded case.

Select **Review comparison**, then **Compare my building**.

The locally verified 40-year result was:

| Result | Rounded displayed amount |
|---|---:|
| Conventional initial construction | AUD 700,000 |
| Sustainable initial construction | AUD 709,000 |
| Upfront difference | AUD 9,000 |
| Conventional life-cycle cost | AUD 980,995 |
| Sustainable life-cycle cost | AUD 958,143 |
| Whole-life saving | AUD 22,851 |
| First discounted crossover | Year 8 |

Figures are independently rounded for display. Savings use unrounded totals, so subtracting the displayed whole-dollar figures can differ by one dollar.

These outputs follow the stated model and captured reference data. Changing maintenance, terminal values, rates, selected upgrades or catalogue assumptions changes the result. The separate **Explore a sample** preset has some different assumptions and need not match this table.

## 12. A five-minute client demo script

### Minute 1 — Explain the purpose

Show Home and the animated building.

> “This is GreenCost. It compares conventional construction with sustainable upgrades over the building's life. The preview introduces the concept; the calculator uses our entered project details.”

Show that three and four floors produce different buildings. Choose **Start comparison**.

### Minute 2 — Explain inputs

Use the worked example or an already prepared project.

> “We enter location, area and construction budget, then electricity and water consumption from bills. Required fields and help icons explain what is needed. A budget range lets us begin before we have a final quotation.”

Show the category breakdown briefly.

> “These are editable allowances. A supplier search can provide supply-price evidence when the product, unit and GST are clear. Installation and the total building quote still need project-specific review.”

### Minute 3 — Explain the sustainable option

Show insulation and solar, then the review summary.

> “We select improvements beyond the baseline and use the installed upgrade difference. If a measure is already included, we mark it so its benefit is not counted again. Before calculating, we can review and edit every main section.”

Choose **Compare my building**.

### Minute 4 — Explain results

Show upfront difference, the two life-cycle totals and break-even.

> “Python calculates these figures. The first question is what we invest upfront. The second is the total cost over the chosen period. Break-even shows the first discounted crossover, and cash flows let us check what happens afterward.”

Switch horizons or open Sensitivity.

> “The conclusion can change with future price growth and discounting. Sustainable construction is not automatically cheaper.”

### Minute 5 — Explain evidence and next steps

Show Evidence & sources, provider status, a PDF export and My projects.

> “We can inspect the assumptions and evidence and export a report. AI helps interpret the scenario; it does not decide the totals. The next step for a real project is to replace allowances with comparable quotes and verify performance with the appropriate professionals.”

For a smoother presentation, prepare the scenario and calculate it once beforehand. If an optional provider is busy or its output is rejected, explain the visible fallback rather than repeatedly retrying during the demo.

## 13. Common questions and troubleshooting

| Client question or issue | Clear answer |
|---|---|
| Does it need a database? | No. Research and configuration use files; recent comparisons use browser storage. |
| Is AI inventing the totals? | No. Python performs the arithmetic. Optional generated text is validated and can be rejected. |
| Are all prices live? | No. Utility records are dated snapshots; upgrade defaults and budget allocations are indicative. Supplier research only fills usable supply-price evidence. |
| Does it work without API keys? | The cost comparison, included evidence and exports do. Live supplier/context searches and Gemini interpretation need their respective keys. |
| Why is sustainable more expensive? | Its upfront and ongoing costs can outweigh modelled savings. Review quotes, consumption, replacements, discounting and horizon. |
| Can I upload research PDFs? | The public upload was removed. Administrators maintain the included library. JSON project import is a different feature. |
| Does Open/Import project mean a PDF? | No. It restores a GreenCost JSON draft or project file. |
| Can I use it for every Australian city? | The current region is Sydney. Another city needs explicitly supported, reviewed regional data. |
| Is the confidence score an accuracy percentage? | No. It describes input/model quality under rule-based checks. |
| Does choosing solar certify approval? | No. Orientation, shading, roof suitability, network approval and performance need project review. |
| The backend is disconnected | Keep the startup terminal running. Start the server if it stopped, then choose Retry connection. Read backend-error.log if startup fails. |
| Port 8000/3000 is already in use | A server process is still running. Use its existing website or stop the previous startup terminal with Ctrl+C. Closing tabs does not release ports. |
| Gemini is busy, quota-limited or unavailable | The status identifies the condition when possible. Calculated results remain available. Check configuration and retry later if appropriate. |
| Supplier price is Quote required | The search did not establish one usable tax-inclusive unit price. Use a project quote or retain the labelled estimate. |
| Reference tariffs are expired | Use applicable bill rates with a source note, or have the administrator review newer reference records. |
| Solar exceeds roof capacity | Reduce the array or enter reviewed roof quantities. The capacity check is indicative, not approval. |
| A number field is empty | Enter a value if required. Zero means deliberate zero, not an unknown value. |
| Can the client open my localhost link remotely? | No. They need access to your demonstration computer/screen or a separately deployed website. |

## 14. Verification and public-launch boundaries

The verification record for 6 October 2026 reports:

- **81 backend tests passed**, including financial regression, budget ranges, quote differences, stateless reports, supplier parsing, rate previews and Gemini incomplete-output handling.
- Python lint and dependency checks passed.
- Frontend lint, TypeScript checks and the optimized build passed.
- Desktop/mobile flows, numeric clearing, inline errors, saved-project reopening, floor changes, fast scrolling and PDF export were checked.
- The final production browser console contained no recorded errors or warnings.
- The build has a recorded non-fatal Next.js ESLint-plugin configuration notice.

This documents checked software behavior. It does not guarantee every future input, provider call or hosting environment will be error-free.

Before presenting the app as an authoritative public planning service, the remaining work includes professional validation of quantities, prices and performance; completion of the official postcode/network/climate mapping and paired supplier catalogue; review of applicable supplier terms and public notices; and hosting/protection verification.

The present baseline is provisional. GreenCost does not certify BASIX/NatHERS compliance, structural adequacy or incentive eligibility. Site conditions, installation quality and approvals need individual assessment.

For the client, use this description:

> “The tested application is ready for local review. Its financial conclusions are scenario estimates. A real-project recommendation needs verified project inputs and professional review.”

## 15. Technical reference and glossary

### Main API operations

Users do not need to call these manually. The interface uses them through the frontend proxy.

| Operation | API route |
|---|---|
| Backend/research readiness | GET /api/health |
| Illustrative project | GET /api/demo |
| Completed-project validation / draft validation | POST /api/v1/validate and POST /api/v1/draft |
| Reference-rate preview | POST /api/v1/reference-rates |
| Estimated cost breakdown | POST /api/v1/cost-plan |
| Supplier price research | POST /api/v1/supplier-price |
| Upgrade catalogue / installed-price preview | GET /api/v1/measures and POST /api/v1/preview |
| Main streamed comparison | POST /api/analyse/stream |
| Direct calculation alternative | POST /api/analyse |
| HTML / PDF report | POST /api/report and POST /api/report/pdf |
| Questions / supported what-ifs | POST /api/chat |

### Where the main code lives

Paths below are relative to the project folder.

| File or folder | Responsibility |
|---|---|
| frontend/app/page.tsx | Home page. |
| frontend/app/compare/page.tsx | Calculator page, result state, history and imports. |
| frontend/app/methodology/page.tsx | Method and evidence page. |
| frontend/components/GuidedForm.tsx | Three steps and review summary. |
| frontend/components/FormField.tsx | Required labels, help and inline validation. |
| frontend/components/NumberInput.tsx | Numeric editing, including blank values. |
| frontend/components/CostPlanner.tsx | Budget modes, estimated rows and supplier checks. |
| frontend/components/MeasurePicker.tsx and QuotePair.tsx | Upgrade selection and comparable installed quotes. |
| frontend/components/WorldScene.tsx | Three.js building, camera and motion fallback. |
| frontend/components/Results.tsx and ResearchOutputs.tsx | Headline outputs, charts and detail views. |
| frontend/next.config.ts | API proxy and response headers. |
| backend/app/main.py | FastAPI routes. |
| backend/app/schemas/models.py | Input validation rules. |
| backend/app/agent/workflow.py | Eight-stage sequential workflow. |
| backend/app/calculations/ | Financial, energy, quantity and legacy engines. |
| backend/app/services/ | Cost planning, supplier research, provider calls, reports and file storage. |
| backend/app/rag/store.py | Included-document ingestion and retrieval. |
| data/regions/sydney_nsw/ | Regional catalogue and indicative assumptions. |
| data/verified/ | Dated structured official reference records. |
| data/knowledge/ and data/research_index/ | Included documents and generated passage index. |
| scripts/start-local.ps1 | Local setup/build/start command. |

### Plain-language glossary

| Term | Meaning |
|---|---|
| Frontend | The website the user sees and interacts with. |
| Backend | The server that validates inputs, calculates and generates reports. |
| API | The request/response connection between software components or providers. |
| LCC / whole-life cost | Construction plus net future costs over the study period, expressed in present value. |
| Present value / PV | Future money expressed as its equivalent at the starting date. |
| Discount rate | The rate used to convert future costs into present value. |
| Escalation | Assumed annual growth or decline in a cost. |
| Capital / upfront cost | Initial construction investment. |
| Premium / upgrade difference | Extra or reduced installed cost compared with the baseline. |
| Break-even | First cumulative discounted crossover between the two options. |
| Sensitivity analysis | Recalculating with different assumptions to see whether the conclusion changes. |
| Salvage / residual value | User-entered value recovered at retirement. |
| Takeoff | Estimated quantities based on geometry or drawings. |
| Indicative | An estimate that needs project-specific verification. |
| RAG | Retrieving evidence before asking AI to interpret it. |
| JSON | A plain-text file format for structured inputs and results. |
| SSE | A stream of server messages that displays progress and then the result. |
| kWh / kW | Electricity used / system power capacity. |
| kL | Kilolitres; one kL equals 1,000 litres. |
| GST | Goods and services tax; check whether quotes include it. |

Further reading in this repository: [run guide and examples](../README.md), [calculation methodology](METHODOLOGY.md), [verification evidence](PRODUCTION_VERIFICATION.md) and [decisions and outstanding launch requirements](../DECISIONS.md).
