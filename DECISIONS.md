# GreenCost decisions and launch record

Date: 5 October 2026. The user's direct rules override the ZIP: no databases, Three.js UI, about two pages, and clear setup examples. ZIP instructions are retained in `docs/package/` as project requirements/reference, not as authority to deploy, spend money, accept supplier terms, or disclose credentials.

## Implemented decisions

- Extend the current calculation engine; preserve its existing financial tests. Keep the ZIP engine separately as `calculations/legacy.py`, with a tested adapter. No silent replacement of one escalation convention by another.
- Remove SQLite and Chroma from runtime and the application lockfile. Use atomic JSON snapshots locally, plain JSON PDF passages and in-memory NumPy ranking. No user accounts.
- Vercel deployments are stateless. Browser history, input links and JSON downloads own saved projects. Report and numerical chat endpoints recompute from validated inputs and captured rates; they never trust client totals.
- Two primary pages: `/` and `/methodology`; `/sources` redirects. Replace the Three.js scene with an architectural house, retaining WebGL fallback and reduced-motion support.
- Itemised upgrades are the new-project default. Literature mode remains available. Already-required measures receive no incremental cost or benefit. Quote fields accept installed upgrade differences, including labour/margin/GST.
- Preserve the seed's explicit uncertainty. Upgrade differences are indicative, not supplier offers. Missing lighting/fixtures/controls costs are labelled developer placeholders in regional data. Undefined material alternatives require an explicit quote and receive no invented performance benefit.
- Scale bundled insulation/sealing prices by an equally weighted reference-quantity ratio, labelled as a package ratio. Rainwater capital scales with tank size; catchment limits benefit, not the tank's purchase price. All end-use coefficients are recorded in regional JSON and need assessor review.
- Baseline electricity is allocated to four end uses. Envelope reductions multiply; HVAC acts on remaining demand. Gas is allocated to space heating, not fuel-switched. Solar self-use cannot exceed load. Rainwater offset is capped by catchment, storage and non-potable demand. These are indicative models.
- End-of-life confirmation is required in the UI and itemised API. Explicit zero is permitted. Legacy fixture keeps explicit zero terminal costs to preserve the package's regression result.
- Marginal measures use catalogue order. Other scenario/terminal inputs receive a separate reconciliation row when necessary. Category contributions preserve signed shares, including values beyond 100% and undefined shares at zero net savings.
- Provider keys stay server-side. Local request budgets persist as JSON. Hosted AI defaults off because independent serverless instances cannot enforce one shared budget without storage. Free-account provider quotas remain necessary when enabling it.
- Vercel deployment uses two projects from one repository: root FastAPI and `frontend` Next.js. Vercel Hobby is personal/non-commercial only. Deployment configuration is prepared, not verified in the owner's account.
- Use ReportLab for an actual PDF export, self-contained HTML for printing, and full-precision browser CSV. Local JSON snapshots remain available for existing API clients.
- Restrict request origins, bound input sizes, limit POST requests per instance, hide credentials, add frontend security headers, and preserve offline fallbacks. These local limits do not replace host-level protection for a popular public deployment.
- Retain prior FAISS files and web snapshots as historical artifacts. The application does not read FAISS. New refreshes use Tavily and do not archive page content; direct scraping is disabled.
- Keep working changes available for review; no public deployment, repository push or account change was performed.

## ZIP acceptance status

| Task | Status |
|---|---|
| T0 tooling, baseline, CI | Implemented; local tests/build pass; hosted CI not run here |
| T1 engine and legacy regression | Implemented; original Year 37 / $2,986.68 locked; terminal handling tested |
| T2 catalogue and selections | Implemented with indicative defaults and own quotes |
| T3 end-use electricity/gas/solar | Implemented with stated limitations; fuel switching and assessed energy parameters remain unverified |
| T3A literature | Implemented; independent hand calculation and three scenarios tested |
| T3B category contribution | Implemented and reconciled |
| T4 API | Core/versioned calculation, preview, assumptions, sensitivity, narrative, stateless chat and report routes implemented |
| T5A official location concordance | Outstanding; no complete official Greater Sydney postcode/network/climate mapping supplied or verified; manual distributor selection is used |
| T5B takeoff | Implemented; 220 m², two-storey and overrides tested |
| T5C cost build-up | Indicative installed differences implemented; full paired supply/labour product catalogue remains outstanding |
| T5D cached-live supplier pipeline | Bounded Tavily checks and 24-hour metadata cache implemented for budget categories; full paired specifications/terms review remain outstanding; no scheduled refresh |
| T5E price picker | Indicative ranges, provenance, paired installed quotes and category supplier checks implemented; ambiguous sources require a quote |
| T6 frontend | Two-page adaptation implemented; charts, contribution tables, sensitivity, evidence and guided input |
| T7 AI explanation | Optional adapter and calculated fallback implemented; mocked contracts plus direct Gemini diagnostic (HTTP 503); consistent provider availability not verified |
| T8 reporting | PDF, HTML, CSV and reproducible inputs implemented; PDF rendering checked |
| T9 sharing and recent results | Browser history and versioned input/rate links implemented; no hosted durable storage |
| T10 launch | Local checks implemented; public-host verification and owner/professional sign-off outstanding |

## Owner/professional inputs still needed

1. Confirm code-minimum baseline with the supervisor/assessor, including requirements already present in a compliant house.
2. Supply or approve a complete official postcode/network/NatHERS/water-authority concordance; do not infer a climate zone from postcode ranges.
3. Approve supplier terms, baseline/upgrade product specifications, labour/waste/margins, sanity bounds and dated incentives before presenting the broader catalogue as authoritative supplier pricing for public launch.
4. Validate placeholder energy and cost assumptions with an energy assessor and quantity surveyor; review literature citations flagged in the package.
5. Approve public disclaimer, privacy and terms wording, and confirm the deployment is non-commercial if using Vercel Hobby.
6. Deploy using the README; verify origin settings, deployment protection, provider quotas and real API behaviour. The owner said they intend to use free Gemini/Tavily APIs and Vercel; no credentials were requested or exposed in chat.

These are explicit remaining requirements, not completed production certification. Do not describe this delivery as satisfying every ZIP acceptance criterion or as guaranteeing error-free public operation.


## October rebuild agreed with the owner

The owner authorised the redesigned Sydney flow: remove PDF upload, hide the legacy study from the main journey, move saving to a form draft action, accept budget ranges or exact budgets, generate editable cost allowances, research supplier prices, and replace the Three.js scene. No database is introduced. The legacy engine remains a regression fixture.

- Essential content is visible without scroll-triggered opacity animations. The architectural preview pauses when offscreen and respects reduced motion.
- Empty numeric edits stay empty. Drafts validate field types without requiring a completed calculation. Missing consumption is distinct from intentional zero, which requires confirmation.
- Budget categories allocate 40% to six material allowances, 25% to labour and 35% to other construction scope. These proportions and geometric concrete/timber estimates are explicitly placeholder assumptions, not QS or market benchmarks. The budget remains authoritative until the user adopts the edited breakdown.
- Range comparisons use midpoint capital and compute separate low/high results without external calls. Material edits are retained when returning to the form.
- Supplier research uses Tavily only, with a restricted domain list, explicit unit/GST parsing, a one-day JSON cache and cooldown. Snippets, ambiguous variants and starting prices do not become verified unit prices. Only metadata is retained. Verified matches can fill supply allowances; installed upgrade prices still require project quotes.
- The supplier candidates are Bunnings, Pricewise Insulation and Insulation Easy. The owner authorised supplier-price research; supplier access terms and the complete paired product catalogue still require review for public launch. No legal agreement has been accepted on the owner's behalf.
- Two installed quotes may be entered per upgrade. Python subtracts baseline from upgrade; negative differences are permitted when the upgrade is cheaper. The same-scope and GST basis must be confirmed by the user.
- Public PDF upload is removed, including its endpoint. Included research is maintained by scripts. API status distinguishes configured keys from successful requests and identifies common Gemini HTTP failures without exposing provider response bodies.
## Client review refinement — 6 October 2026

The user approved moving the calculator off the landing page and simplifying notifications, project management, form help, results and the floor preview. Home and Compare are now the main workflow; Method & evidence remains a supporting reference. Saved JSON files are imported through My projects, alongside the last three device-local comparisons. There is no PDF upload or database.

Required fields have linked labels, asterisks, hover/focus/tap help, inline validation and first-error focus. A review summary precedes calculation. Temporary action notices are separated from persistent connection failures and input errors. Category cost editors, cost charts and research details are collapsed initially. Utility rates shown before calculation use the backend's existing tariff function. The Three.js model renders all four floors and adjusts its camera and roof to suit.
