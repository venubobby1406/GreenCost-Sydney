# GreenCost component refresh

The component choices were reviewed against [EasyUI](https://easyui.site/). The application keeps its green identity and existing Three.js scene.

## Component choices

| Reference | GreenCost use |
| --- | --- |
| Animated Tabs / Pill Navigation | Animated upgrade-category selector and accessible dashboard tabs; pill styling for entry modes, study periods and the main navigation. |
| DrawCheckbox | Animated check marks for connections, research, baseline features and confirmations. Native checkbox semantics remain intact. |
| OriginDropdown / Form | Styled selection menus throughout the form, including inline area units. Native controls retain validation; the visible combobox supports arrows, Home, End, Escape and typeahead. |
| UnfoldAccordion | Native disclosure panels with consistent chevrons and restrained opening transitions. |
| Selection Basket | Selected-upgrade summary, removal actions and feature cards with a clear selection state and installed price. |
| Smart Comparison | Separate conventional and sustainable cards, prominent whole-life totals, initial cost and maintenance. |
| Interactive Timeline | Existing backend stage timeline gains a progress bar driven by the completed-stage count. Research connections are expandable. |
| PressButton | Consistent rounded actions with gentle press feedback and visible keyboard focus. |

AnimatedTabs and DrawCheckbox are source adaptations with MIT attribution in `frontend/THIRD_PARTY_NOTICES.md`. Other components implement the published interaction patterns independently, using existing project dependencies. No additional package was installed.

## Preserved behaviour

Calculation formulas, provider order, source fetching, saved drafts, input units, building scopes, result data and report exports are unchanged. Reduced-motion preferences are respected. The mobile navigation supports Escape and returns focus to its trigger.

## Verification

- Frontend lint, TypeScript and production build.
- Existing apartment/scope, preview-error and report-export regression scripts.
- Browser checks of blank required fields, selection errors and focus, keyboard unit selection, confirmation checkboxes, saved-draft reload, category selection and dashboard tab navigation.
- Responsive checks at 1280 px and 390 px, including mobile cards, menu and horizontal overflow.
- Dashboard rendered with a temporary deterministic local harness, with outbound HTTP requests blocked. No OpenRouter, Groq, Gemini or Tavily request was made for verification. The normal backend was restored afterward.

Screenshots are saved under `output/ui-refresh/`. The changes are local; they were not committed, pushed or deployed.
