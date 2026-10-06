# GreenCost local verification — 6 October 2026

The agreed Sydney interface rebuild is implemented and checked locally. This records evidence for this revision; it does not certify real construction estimates or a hosted deployment.

## Automated checks

- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp tmp/pytest-client-final`: **81 passed**. Includes the original financial regression suite and independent budget-range recalculations, editable allocation reconciliation, incomplete draft validation, comparable installed quotes (including cheaper upgrades), removed PDF upload, safe supplier URLs, GST/unit/ambiguity rejection, mocked Tavily raw-page extraction and metadata-only caching. New tests verify the utility-rate preview against the calculation engine and reject truncated or oversized Gemini responses while retaining calculated explanations.
- Python Ruff: passed. Python dependency check: no broken requirements.
- Frontend ESLint and TypeScript: passed.
- Final `npm run build`: passed after the refinement; home, comparison and methodology routes prerendered. Production server starts successfully on port 3000, FastAPI on port 8000.
- Next prints a non-fatal framework ESLint plugin configuration notice. Explicit TypeScript, React and hooks lint checks pass.

## Browser and report evidence

- Home contains the introduction, interactive building and a Start comparison link. The calculator and results are on `/compare`; imports and browser history are grouped under My projects.
- Missing required fields show inline reasons and focus the first invalid input. A reversed budget range focuses its upper bound. Field help works through a selectable info button. The review summary provides Edit links before calculation.
- The Three.js model visibly renders different three- and four-floor buildings; its roof and camera follow the floor count. Floor controls disable at their bounds.
- The selected Ausgrid reference rates were shown before calculation: electricity AUD 0.3314/kWh and AUD 1.66/day, water AUD 3.41/kL and AUD 859.06/year for the tested residential water/wastewater connections, without stormwater. These match the backend tariff function, not a retailer quotation.
- PDF and Save project actions produce separate temporary success notices. My projects and the review/results flow were checked at 390 × 844; the page has no horizontal overflow.
- The optimized production build restored the saved comparison through My projects and reproduced AUD 22,851 savings and Year 8 crossover for the checked scenario. Its final provider call used the calculated explanation after Gemini text failed validation; Tavily succeeded. The provider status and research retry control were visible. No browser warnings or errors were recorded. Fast scrolling to the bottom and back to the top kept hero content visible (opacity 1) and the four-floor canvas rendered.

- The three-step form completes a 220 m², AUD 600,000–800,000 budget-range comparison with 5,200 kWh/year and 200 kL/year. Low, midpoint and high results are independently calculated for all three horizons.
- The observed 40-year headline for the tested form is conventional AUD 980,995, sustainable AUD 958,143, signed saving AUD 22,851 and first discounted crossover year 8 (rounded). These are scenario outputs, not a building quotation.
- A number field can be cleared with Backspace and stays blank on blur. Intentional zero remains a separate value; zero utility use requires confirmation.
- Monthly values are converted to annual consumption. An incomplete imported draft restores successfully with blank floor-area/occupant values and nullable material costs; it cannot be submitted as a completed analysis.
- Desktop at 1280 × 900 and mobile at 390 × 844 were visually checked. Chart tooltip containment and wrapping controls fixed mobile horizontal overflow. Document widths do not exceed viewport widths.
- Rapid jumps from top to bottom and back leave content visible, with hero opacity 1. The new Three.js architectural scene renders with solar, wood screens, trees and rainwater tank. Reduced-motion and WebGL fallback paths are implemented.
- Final production browser console check returned no warnings or errors. The methodology page loads its sources and calculation boundaries.
- PDF button reports a successful download. PDF and HTML report endpoints return 200 from captured validated inputs/rates without AI calls. An eleven-page report with the new six-category breakdown and budget-range table was rendered and every page inspected: repeated table headers and footers, no clipped or overlapping rows or blank pages. Material input records are split into separate rows so a large material list does not become one oversized row.

Current client-review screenshots (ignored by Git): `output/GreenCost-client-production-home.png`, `output/GreenCost-client-production-results.png`, `output/GreenCost-client-review.png`, `output/GreenCost-client-results.png`, `output/GreenCost-client-3floors.png`, `output/GreenCost-client-4floors.png`, `output/GreenCost-client-mobile-results.png`, `output/GreenCost-client-mobile-projects.png`. The earlier report render remains at `output/pdf/GreenCost-rebuild-report.pdf`, with its full-page review at `output/pdf/rebuild-report-review.png`.

## Provider verification and practical limits

A real Tavily insulation search completed and returned three sources from the configured Australian supplier domains. None provided an unambiguous, tax-inclusive per-square-metre supply price; all correctly stayed **Quote required**, without overwriting estimates. Supplier results are cached for 24 hours; price checks are bounded by provider budgets and a retry cooldown. Automatic pricing is conditional on usable source evidence, not guaranteed for every material. Edited/deleted material rows retain category-correct lookup rather than using row position.

During the 6 October browser flow, Gemini and Tavily requests both completed. The Gemini output exposed an unfinished-text case; the adapter now rejects non-STOP finishes and oversized text rather than displaying a cut-off paragraph, with regression tests. Explanation prompts request fewer words and allow a larger token budget for completion. Earlier diagnostics also observed provider HTTP 503. The app distinguishes provider busy, quota, permissions, incomplete output and model errors and keeps deterministic financial results available. A successful call does not establish consistent provider availability. The sandboxed local server may restrict outbound networking; a provider failure there is not proof of invalid keys.

No Vercel deployment, supplier terms acceptance, public authentication/protection setup or professional validation was performed. The complete official postcode/distributor concordance and comprehensive paired supplier/labour catalogue remain outside this bounded implementation; users select their distributor and can supply comparable installed quotes. Budget allocations and rectangular-plan quantities are explicitly editable placeholders. Public launch requirements and host limits are described in the README and DECISIONS.
