# Apartment building update — 7 October 2026

The new Apartment building choice represents the whole residential building. Legacy Apartment saves still represent one unit. Changing scope clears the previous single-property budgets, consumption, tariff rates and upgrades; new inputs must represent the building.

## Calculation checks

- Per-floor area 500 m² × 20 floors gives 10,000 m² and 219 estimated occupants.
- Per-floor area 500 m² × 50 floors gives 25,000 m² and 547 estimated occupants.
- Total-area mode does not multiply an already combined area by floors.
- Equivalent ft² input produces the same count.
- Manual counts remain unchanged when geometry changes.
- Cleared area, floors or occupancy assumptions stay blank and prevent incomplete calculations.
- The server verifies canonical area, recalculates automatic occupancy and rejects mismatched area or single-house reference tariffs for whole buildings.
- Saved analysis replay reproduces financial results, with area basis and occupancy assumptions retained in results and PDF exports.

## Browser checks

Checked the local production build in a separate localhost browser origin, preserving the user's 127.0.0.1 draft. The whole-building example reaches the review step with 20 floors and 219 estimated people. Refresh and browser Back preserve the stage, area, budget and utility inputs. Missing assumptions show inline validation. Desktop and 390 px mobile layouts checked; no horizontal overflow or browser console errors observed.

Screenshots: `output/apartment-building/desktop.png` and `output/apartment-building/mobile.png`.

## Automated verification

- Full backend suite: 102 tests passed.
- Frontend type checking and ESLint passed.
- Production build completed successfully.
- `node scripts/check-apartment.cjs` passed area-mode, blank-editing, override, unit and draft regressions.
- Tests isolate provider keys and do not consume external API quotas.

## Estimate basis and limits

The assumed apartment interior size of 75 m² and apartment share of 80% are illustrative and editable, not official density standards. The per-dwelling relationship is the dated NSW BASIX energy-modelling equation, bounded to 1–6 people **per dwelling**; the building total is not capped at six. The estimate is not legal capacity, a resident forecast, predicted water use or a formal BASIX assessment.

Budgets, usage and fixed meter charges must describe the same whole building. Occupants describe the scenario; measured/design utility usage drives running costs. Generic rectangular quantities, dwelling upgrade coefficients and capped small-system solar/tank defaults are indicative and do not model a complete tower. Include lifts, central plant, parking, fire systems and applicable common-system maintenance/replacements using drawings and project quotes. Ordinary-house removal-guide estimates do not apply to an apartment block.

Source: [NSW BASIX standard occupancy, August 2022](https://www.planningportal.nsw.gov.au/sites/default/files/documents/2022/BASIX%20standard%20occupancy%20-%20version%204%20-%2023.08.22%20LMv5.pdf).
