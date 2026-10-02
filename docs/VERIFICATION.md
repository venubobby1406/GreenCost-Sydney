# Prototype verification — 2 October 2026

Completed checks:

- Full Python suite: **33 tests passed**.
- Python lint: `ruff check backend scripts` passed.
- Frontend TypeScript: `npm run typecheck` passed.
- Frontend lint: `npm run lint` passed.
- Production build: `npm run build` passed with Next.js 15.5.27.
- Cached official source-policy checks: passed, zero Tavily calls.
- Browser workflow: seeded project → all seven wizard steps → analysis → results.
- Interactive 3D floor count and solar toggle verified in the browser.
- Horizon selector, sensitivity grid, annual cash-flow table and official/PDF source provenance verified in the browser.
- Chat what-if with a selected 30-year horizon verified; Python recalculation used that selected horizon.
- Mobile landing layout checked at 390px; wizard and result flow exercised in the narrow browser layout. Desktop landing, results and report visually inspected.
- Report and CSV response validation passed for 30, 40 and 50 years. CSV final cumulative present values match saved LCC totals. Each report contains two SVG cost charts and complete assumptions/input records.
- Browser download-inspection tooling failed while handling a paused download response. Actual export HTTP responses, attachment headers and file contents were checked directly and passed.
- Normal seeded analysis: **0 Tavily calls, 0 LLM calls**.
- Optional LLM connection/quota failure tested with a mocked failure; templates remain available. A live paid-provider request was not made.

Sample deliverables: `demo-report.html` and `demo-cashflows.csv` in this directory. The HTML report is self-contained; open it in a browser and use Print → Save as PDF if required.

The demonstration remains an indicative academic scenario with explicitly labelled construction, consumption, performance and replacement assumptions. It does not establish an actual construction quotation or certified building performance.
