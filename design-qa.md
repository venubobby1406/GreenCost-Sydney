# GreenCost interface refresh — design QA

Date: 9 October 2026

## Scope and reference

Adapt the typography, neutral surfaces, green accents, theme control and graph treatment of [TensorTonic](https://www.tensortonic.com/) to GreenCost. This is a visual adaptation: GreenCost retains its own identity, calculator content, research, financial model, reports and interactive building. TensorTonic's logo, artwork, code and machine-learning interactions were not copied.

Reference and implementation were inspected in light and dark modes at comparable desktop sizes, with additional phone checks at 390 × 844 and 320 × 740. Satoshi loaded successfully from the official Fontshare CDN. Bundled Inter remains available as a fallback.

## Final assessment

Pass for the requested refresh. The hierarchy, font treatment and restrained surfaces follow the reference direction. Both themes cover Home, Compare, the dashboard and Method & evidence. Charts retain actual calculated values and use theme-aware axes, grids, legends and full-value tooltips. No outstanding blocking visual defects were observed in the checked screens.

Intentional differences from the reference:

- GreenCost's building illustration replaces the reference's ML demonstration; its independent day/night cycle remains intact.
- The homepage uses GreenCost's shorter two-line headline and existing explanation, rather than the reference's content.
- Cost charts retain linear currency scales and add a dashed orange conventional-design series for comparison. They do not imitate unrelated mathematical data.
- The calculator keeps the existing accessible controls and disclosure arrows. Very narrow phones omit the duplicate header call to action; the main start button stays available.

## Issues found and corrected

| Priority | Observation | Correction | Verification |
| --- | --- | --- | --- |
| P1 | Older white methodology disclosure surfaces were unreadable in dark mode. | Shared surface, border and foreground variables. | Reopened the assumptions panel and captured the corrected screen. |
| P1 | Some form disclosure labels retained an older important dark-green declaration. | Applied the shared foreground at the required specificity. | Production budget disclosure and nested material editor reviewed after the correction. |
| P2 | Toast, guide icons, table values and help surfaces retained older colours. | Theme-aware foreground, backgrounds and borders. | Form, evidence, assumptions, helper and upgrade-table checks in dark mode. |
| P2 | Mobile charts spent too much width on full-currency axis labels. | Compact axis values, smaller axis allocation and preserved first/last year labels. | Light and dark phone chart captures; tooltips still show full amounts. |
| P2 | Upgrade chart labels were angled and crowded. | Horizontal contributions with shortened axis labels; full names remain in tables and tooltips. | Reviewed the contribution graph and horizontally scrollable table. |
| P2 | Area unit controls crowded the selected unit and arrow. | Increased the unit control width. | Opened the m²/ft² selector and dismissed it with Escape. |
| P2 | The header overflowed at 320 px. | Removed the duplicate header action at widths up to 360 px. | Document scroll width equals client width at 320 px. |

## Interaction and functional checks

- Manual light/dark switching, persistence after reload, cross-tab synchronisation and device-default behaviour.
- Eight bootstrap cases: light/dark saved preferences, missing/corrupt preferences and unavailable browser storage.
- Phone navigation menu, Escape dismissal and focus return.
- Building-type choices, apartment total/per-floor area, editable floor count and automatic occupant estimate. A 10,000 m², 20-floor apartment input produced the existing estimate of 219 occupants.
- Budget breakdown, feature categories, review screen, local sample calculation and all five result tabs.
- 30/40/50-year selection, keyboard chart tooltip and full-currency values.
- Existing apartment, building-switch, preview-retry and report-export regression checks.
- Type checking, lint and optimized Next.js production build.

The offline 40-year sample retains conventional cost $961,153, sustainable cost $936,347, displayed saving $24,805 and additional initial cost $12,981, with first recovery in year 10. The 50-year view retains $985,899 and $955,715. These are illustrative model outputs, not project quotations.

Testing used an isolated local backend with outbound research requests blocked and captured reference rates. No OpenRouter, Groq, Gemini or Tavily requests were made. The test stream returns the completed calculation directly; provider connectivity and the eight-stage live research stream were not revalidated by this appearance-only change. Calculation code and PDF layout were not changed.

## Visual evidence

Screenshots are local review artifacts in `output/tensor-refresh/` (ignored by Git):

- `comparison-light-production.png` and `comparison-dark-production.png`: reference and production implementation side by side, inspected together.
- `reference-graph-final.png`: the reference's green graph, neutral grid and low-emphasis axis labels.
- `home-light-production.png` and `home-dark-production.png`: completed production homepage themes.
- `mobile-light.png`, `mobile-dark.png`, `home-320-final.png`: responsive homepage checks.
- `mobile-charts-light-final.png` and `mobile-charts-dark-final.png`: final phone axis spacing and contrast.
- `charts-dark-production.png`, `tooltip-dark-production.png`, `contributions-dark-mobile.png`: graph and full-value tooltip checks.
- `method-dark-final.png` and `method-assumptions-dark-final.png`: methodology and corrected disclosure surfaces.
- `budget-dark-production.png`, `material-editor-dark-final.png`, `evidence-dark-production.png`: corrected calculator, nested material editor and evidence surfaces.

Font delivery depends on the official CDN; the interface falls back to the bundled font when it is unavailable. The completed changes are local and have not been committed, pushed or deployed.
