# GreenCost Sydney: Start Here (instructions for the AI coding agent)

You are building **GreenCost Sydney**, a public web application that compares a **code-minimum new home** with a **sustainable (beyond-code) home** in Greater Sydney over 30, 40 and 50 years using life cycle costing. It is also the analysis tool for an academic study (UTS Engineering Project Preparation 42908). Accuracy, honesty and traceable sources matter more than polish.

The owner is not a developer. **Make sensible decisions yourself, record each one in `DECISIONS.md`, and only stop to ask when something is listed under "Ask the owner" below.**

---

## 1. Read in this order
1. `docs/GreenCost-Sydney-Agent-Build-Brief.md`: what to build, rules, ordered tasks with "done when" checks. **Highest priority.**
2. `docs/GreenCost-Sydney-Pricing-and-Takeoff-Spec.md`: postcode zones, house takeoff, cost build-up, Tavily cached-live pricing. **Wins on anything about pricing.**
3. `docs/GreenCost-Sydney-Project-Document.md`: background, modules, formulas, risks.
4. `docs/research/*.pdf`: the owner's study documents. Context only; do not copy claims into the app as facts.
5. `greencost/`: existing code (backend engine, three endpoints, tests; Next.js frontend scaffold). **Extend it; do not rewrite the engine.**
6. `greencost/backend/app/data/regions/sydney_nsw/*.json`: seed data (see section 4).

Precedence if files disagree: **Build Brief > Pricing Spec (for pricing) > Project Document > everything else.**

---

## 2. Decisions already made (do not reopen)
- Public site, **no accounts or logins**. Share results by link; keep recent analyses on the device.
- **Itemised by measure** (each option has its own cost and effects) plus a **Literature mode** using the study proposal's percentage ranges.
- **Conventional = code-minimum new build** (provisional, owner confirming with supervisor). The old pre-2023 6-star house is a labelled **Legacy preset** and regression fixture only.
- Sydney only now; all city data lives in `data/regions/<region>/` so cities can be added later.
- **Prices are cached-live via Tavily**, never searched on each click. Gemini explains results and extracts text; it never calculates.
- Disposal and salvage are required inputs. Every assumption needs a citation or a visible "placeholder/indicative" label.
- Results are worded "under the stated assumptions". Never tune inputs to reproduce the literature's 10-20% saving.

## 3. Defaults the owner has delegated to you
Use these unless the owner says otherwise; log them in `DECISIONS.md`.
| Item | Default |
|------|---------|
| Hosting | An Australian region (for example AWS Sydney, ap-southeast-2) with a persistent disk for SQLite |
| Pricing zones | The six zones in pricing spec section 3.2 |
| Margin, labour, waste, delivery | Seed placeholders in `assumptions.json` |
| Supplier allow-list | Candidates in `suppliers.json` (owner must verify terms) |
| Price sanity bounds | 0.4× to 2.5× default until a quantity surveyor sets real bounds |
| API caps and refresh limits | Values in `assumptions.json` under `price_pipeline` |
| Installed systems | Shown as indicative price ranges |
| Language and format | Australian English, AUD, `en-AU` formatting |
| Tech stack | As listed in the Build Brief, section 3 |

## 4. Seed data (read the status fields)
| File | Contents | Trust level |
|------|----------|-------------|
| `assumptions.json` | Financial settings, tariffs, efficiency, solar, water, disposal, allowances, pipeline settings, legacy fixture | Mixed: each block has `status` (`from_spec` unverified, `placeholder` invented) |
| `measures.json` | 11 measures with options, quantity drivers, price keys, default premiums | Placeholder |
| `takeoff_assumptions.json` | Geometry parameters and a worked 220 m² example | Placeholder (the example arithmetic is correct) |
| `suppliers.json` | Candidate domains per category | Owner must verify |

Not provided, you must create from official sources and cite: **`postcode_zones.json`** (every Greater Sydney postcode to zone, electricity network, climate zone, water authority; use ABS concordances and official network and NatHERS data), **incentive schemes** (federal and NSW, dated), **a verified tariff set**, and **per-item default unit prices** where `measures.json` has `null`.

## 5. Facts to preserve exactly
- Legacy fixture: 220 m², $528,000 vs $580,800, 40 years, 5% discount, 3% energy escalation (water 2%, maintenance 1.5%). Year 1 operating cost $6,546.66 vs $4,278.94 (saving $2,267.72). **Break-even Year 37; net benefit about +$2,987** (engine-verified). The old documents' "Year 33, +$7,741" are **wrong**.
- At that baseline, whole-life cost is $684,903 vs $681,917 (0.44% difference); operating costs are about 23% of the total. The literature's claims (60-80% operating share, 10-20% saving) do not hold for this house. This is a finding to report, not a bug.
- Known spec weaknesses to fix, not copy: itemised upgrade costs sum to $29,800 (not $52,800); the sustainable home's implied electricity use exceeds the conventional home's and gas is ignored; disposal is missing; the sensitivity grid is 4 × 4 per horizon.

## 6. How to work
1. Do tasks **in order** (T0, T1, T2, T3, T3A, T3B, T4, T5A to T5E, T6 to T10). Do not start the next task until the current "done when" check passes.
2. Write tests with each task. Use tight tolerances (never 10%). Keep the legacy fixture green at all times.
3. Commit after every task with a clear message.
4. Keep secrets in `.env` (see `greencost/.env.example`); never expose them to the browser.
5. The app must work with **Tavily and Gemini switched off** (defaults, with correct badges).
6. Never hard-code results in text; generate numbers from computed values.
7. Update `README.md` (setup, tests, env vars, adding a region) as you go.

**First commands**
```
cd greencost/backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pytest
uvicorn app.main:app --port 8000
cd ../frontend && npm install && npm run dev      # http://localhost:3000
```
The existing frontend and `pytest` have **never been run**. Expect to fix issues in T0.

## 7. Ask the owner (stop and ask only for these)
1. Final approval of the conventional baseline definition (after the supervisor decides).
2. API keys (`GEMINI_API_KEY`, `TAVILY_API_KEY`) and the real monthly caps.
3. Supplier terms-of-use approval and any suppliers to add or remove.
4. Real margin, labour and waste values, or a quantity surveyor's sanity bounds.
5. Final wording for the disclaimer, privacy policy and terms.
6. The production domain and hosting account.

## 8. Do not
- Do not change the engine's numbers without a before-and-after test.
- Do not present literature ranges or placeholder values as verified findings.
- Do not scrape websites directly; use Tavily.
- Do not store copies of web pages (price, title, link and date only).
- Do not claim NatHERS or BASIX compliance; show the notice in pricing spec section 10.
- Do not add user accounts, a user database, machine-learning cost prediction or other cities in version 1.

## 9. Definition of done
All tasks pass their checks; the legacy fixture still gives Year 37 and about +$2,987; both modes and both presets are tested; every number shown is computed, sourced or labelled indicative; the site works with Tavily and Gemini off; `README.md` and `DECISIONS.md` are complete.

## 10. Package map
```
00-START-HERE.md
docs/  Build Brief, Pricing and Takeoff Spec, Project Document, research/ (4 PDFs)
greencost/
  .env.example
  backend/  app/main.py, app/calculations/lcc.py, tests/, requirements.txt,
            app/data/regions/sydney_nsw/ (assumptions, measures, takeoff_assumptions, suppliers)
  frontend/ Next.js 15 scaffold (home, calculator, methodology)
```
