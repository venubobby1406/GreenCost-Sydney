# GreenCost verification — 5 October 2026

This records checks of the local production build. It is not a claim that every ZIP acceptance item, professional validation or hosted launch is complete. Outstanding scope is listed in `../DECISIONS.md`.

## Automated checks

- `python -m pytest -q`: **71 passed**. Covers original financial behaviour, independent cash-flow examples, locked legacy fixture, takeoff, all eleven measures, interactions/contribution reconciliation, code-required and quote logic, gas fixed charges, captured rates, stateless Vercel reports/chat, input limits, origins, incremental file retrieval and mocked provider contracts.
- `python -m ruff check backend scripts`: passed.
- `python -m pip check`: no broken requirements.
- `npm run lint` and `npm run typecheck`: passed.
- `npm run build`: passed; comparison and methodology routes prerendered.
- Clean `npm ci`: 373 packages installed, **zero reported vulnerabilities**. `npm audit --audit-level=high` also reports zero known vulnerabilities. This is an advisory snapshot, not a guarantee against undiscovered issues.
- `scripts/start-local.ps1 -SetupOnly`: passed; locked dependencies and eight-document / 73-passage index prepared.
- `scripts/start-local.ps1 -Production`: built and started both services successfully. Ports are checked before dependency updates; existing servers are not terminated by the setup script.

Next prints a non-fatal notice that its framework ESLint plugin is not configured. The project runs explicit TypeScript/React/hooks checks; the old lint configuration dependency tree was removed to resolve its audit findings. npm also reports the pinned ESLint 9 version's support notice. These notices do not fail the checks, but future supported dependency updates should be reviewed.

## Browser and export checks

- Sample guided input completes and returns conventional AUD 961,152.550138, sustainable AUD 936,347.312021, signed savings AUD 24,805.238117 and first break-even year 10 at the sample's 40-year assumptions. Rounded values shown in the UI agree with server results.
- Upgrade estimates, dated indicative provenance, uncertainty ranges, category contributions and individual marginal contributions render.
- Arrow-key tab navigation selects sensitivity and displays its calculated matrix.
- Electricity-growth what-if at 5% returns a recalculated AUD 40,756 saving (rounded), agreeing with the matrix; the original result remains available.
- Desktop layout checked at 1280 × 900, mobile at 390 × 844. Mobile document width does not exceed viewport. Temporary viewport overrides were reset.
- Browser text checked for corrupted UTF-8 punctuation after repair. No console errors observed in the final preview.
- The second method/evidence page loads dated source records and regional assumptions, with model boundaries and privacy wording.
- Stateless HTML export verified with current upgrade/contribution sections. PDF export rebuilt validated inputs and captured rates, with no external calls.
- The browser PDF button confirms a completed download. Sharing confirms a copied-link status in the interface; financial snapshot reproduction is separately tested in the API suite.
- The ten-page sample PDF was rendered with Poppler and every page inspected. Tables repeat headers; source headings stay with content; no blank pages, clipping or overlapping text found. Full-precision input values are retained; summary amounts are rounded for presentation.

Local review artifacts (ignored by Git): `output/GreenCost-desktop.jpg`, `output/GreenCost-mobile.jpg`, `output/GreenCost-sample-report.html`, and `output/pdf/GreenCost-sample-report.pdf`.

## Limits of verification

No hosted Vercel account deployment, paid operation, supplier terms acceptance, live supplier extraction or real Gemini/Tavily call was performed. Provider tests mock API contracts and failures. Free-tier quotas and hosted protection must be checked by the owner.

The app uses manually selected distributors and indicative installed upgrade differences. The complete official location concordance, full paired supply/labour catalogue and cached-live supplier pipeline remain outstanding. The provisional building baseline, end-use assumptions and public-launch wording require owner/professional review. No error-free production guarantee or regulatory certification is made.
