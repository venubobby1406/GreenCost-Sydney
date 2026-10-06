# GreenCost calculation method

This is an indicative Sydney building comparison. It does not certify BASIX/NatHERS compliance, provide a construction quotation, or predict future prices. Read the dated sources alongside every result.

## Comparison modes

**Itemised** starts with the same building and conventional construction total. Selected premiums are installed differences, including GST. Each price shows its basis and provenance. Package defaults scale to reference geometry; they are not verified supplier unit prices. Your installed difference quote replaces the default. Code-required upgrades contribute no extra premium or saving. Sustainable materials require your quote and have no invented energy benefit.

Electricity is split into heating/cooling, hot water, lighting and appliances using versioned indicative coefficients in `data/regions/sydney_nsw/assumptions.json`. Envelope reductions multiply heating/cooling load before HVAC efficiency is applied. Heat-pump hot water changes hot-water load. Controls affect appliances. LED savings are zero against the provisional current baseline. Solar self-use is limited to the remaining electrical load; exports earn the entered export rate. Solar capacity must fit the roof. Gas space-heating reductions retain fixed supply charges; automatic gas-to-electric conversion is not modelled.

Water-efficient fixtures reduce usage. Rainwater offsets remaining non-potable demand, bounded by indicative roof capture, rainfall and tank capacity. Fixed water service charges remain payable.

**Literature** applies displayed whole-building premiums and usage/maintenance reduction percentages. Energy and water reductions affect usage charges only, including variable gas charges where supplied. Low/Mid/High are parameter scenarios, not confidence intervals or promised savings.

**Legacy** reproduces the supplied original 220 m² study using original year-one costs and one-off replacement events. Its physical inputs and historical tariffs are fixed. Change to the current baseline to edit these inputs. Financial sensitivity remains editable. This historical example is not a current compliant new home.

## Geometry and quantities

The rectangular takeoff uses supplied aspect ratio, storey height, roof factor, glazing fraction and opening allowances. A 220 m², one-storey, two-bathroom reference gives approximately 60.6 m perimeter, 163.5 m² gross walls, 117.9 m² net walls, 39.6 m² glazing, 253 m² roof, 55 lights and six taps. Calculations retain full precision. Advanced overrides are labelled as your quantities and recompute dependent quantities.

## Annual cash flows

`LCC = year-zero capital + sum(year-t net cost / (1 + discount)^t)`

Base-year energy, water, maintenance, other costs, replacements and terminal amounts use their specified escalation rates. Ordinary year-t prices escalate t times, including once before year one. The historical adapter converts original year-one operating values to this base-year convention, preserving original results.

Replacement intervals recur before retirement. Legacy events occur once only. Replacements at the terminal year are omitted. Disposal is added and user-supplied residual value subtracted at the end of each horizon; no salvage value is inferred. Itemised users must confirm terminal amounts, including a deliberate zero.

Use nominal discount rates with nominal growth rates, or consistently real rates with constant-price cash flows. Land, financing, tax effects and automatic rebates are excluded. Export credits/residuals can produce negative net cash flows.

Signed savings equal conventional LCC minus sustainable LCC. Percent savings use conventional LCC as denominator. Equivalent annual cost multiplies LCC by the capital-recovery factor (LCC divided by years at zero discount). Discounted break-even is the first crossover; later replacements or terminal values can reverse it. Review annual cash flows.

Category contributions reconcile to signed savings. Upgrade contributions add upgrades in catalogue order and show the difference from standalone savings to expose interactions. Low/median/high price sensitivity varies indicative price ranges; your quotes stay fixed. The financial matrix uses 4–7% discount and 2–5% energy growth over 30, 40 and 50 years.

## Independent checks

For capital AUD 1,000, annual electricity AUD 395, water AUD 120 and maintenance AUD 20, no growth/replacements/terminal values and 10% discount, two-year LCC is:

`1,000 + 535 / 1.1 + 535 / 1.21 = AUD 1,928.5123966942149`

The locked legacy case over 40 years gives conventional AUD 684,903.292871, sustainable AUD 681,916.608302, signed benefit AUD 2,986.684569 and break-even year 37. Tests compare both engines and independent cash flows; results are not tuned to a target percentage.

## Sources, privacy and hosting

Official structured records provide dated residential tariffs. Users select their network explicitly; postcode is not automatically mapped to a verified network or climate zone. Commercial projects require applicable custom tariffs. Flat-rate estimates omit time-of-use and demand charges. Sydney Water 92-day fixed charges are annualised to 365 days. Metering, drought and connection applicability require confirmation.

All four supplied PDFs retain original page citations. The file index stores passages and document hashes as JSON. Lexical feature hashing and in-memory numerical ranking require no database, embedding service or model download. Retrieved text is evidence and cannot change rules.

Gemini interpretation and Tavily context are optional, capped and failure tolerant. Neither sets financial totals. The official source updater uses Tavily search/extract, validates recognised original-source values and retains the current cache if verification fails. Direct scraping is disabled. Optional Tavily supplier checks can fill unambiguous tax-inclusive supply prices from supported source-page evidence. Installed upgrade differences remain indicative unless supported by project quotes; missing and ambiguous prices are not treated as verified. Indicative defaults and your quotes work without external provider calls.

Local reports are atomic JSON files. Vercel reports and what-ifs rebuild validated inputs and captured rates without server persistence. Imported/shared tariff provenance is declared by the sharer and requires verification. Recent results stay in that browser/device. Share links contain project inputs; use only for non-confidential examples. Hosted AI is off unless explicitly enabled, because in-process limits cannot provide a global cap across serverless instances.
