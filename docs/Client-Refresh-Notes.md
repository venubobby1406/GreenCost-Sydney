# GreenCost client refresh

Updated 7 October 2026. Local review build; public deployment has not been performed.

## What changed

- Clean Inter typography, near-white surfaces, forest-green actions, responsive feature cards and visible keyboard focus.
- House, apartment building and commercial choices replace the building-type dropdown. Houses show area first; optional details retain floor count and editable suggested occupants. Existing single-unit saves retain a separate Apartment unit (saved) choice.
- Apartment building comparisons require a floor count and offer per-floor or total building area entry. The occupancy estimate uses editable illustrative 75 m² apartment size and 80% residential share assumptions with the dated BASIX dwelling energy relationship. Manual count overrides persist. Area, budgets, use and aggregate meter charges must describe the same building. Generic upgrade coefficients are indicative; drawings and project quotes must cover lifts, central plant and other common systems. Legacy unit comparisons retain shared-system exclusions.
- Water inputs use litres and display million litres. Backend JSON retains `water_kl` and tariff rates in AUD/kL for compatibility; do not change the API’s units when importing a file.
- Automatic browser drafts preserve inputs and the current step across refresh, page navigation and Back. Explicitly opening a sample or imported project replaces the active draft. Start fresh has a confirmation step. Analysis results are separate from unfinished drafts.
- Feature categories: comfort and design, clean energy, water saving, lower-impact materials. Familiar equipment can improve efficiency, but an already-included feature is not counted again. Heat-pump hot water is conditional on the baseline. No unmodelled battery, greywater or carbon savings have been invented.
- Real stage-start and stage-completion events drive the eight-stage timeline. Optional providers report their own outcomes. A response failing content checks is shown as a fallback, not an API success.
- Results prominently compare initial construction, maintenance and total costs. Replacements remain separate from maintenance. Future expenses use discounted present value; amounts are not a prediction of future cash bills. Investment recovery is the first discounted crossover and can reverse after replacements.

## Occupancy assumption

For a house, the suggested count is the rounded, bounded NSW BASIX energy-modelling assumption: `1.525 × ln(dwelling floor area in m²) − 4.533`, bounded to one through six occupants. Use all dwelling floors combined, excluding garage. This is a dated modelling assumption, not city density, an occupancy limit or a prediction of water use. Actual occupants can override it; actual entered consumption remains the basis for utility costs.

Source: [NSW BASIX standard occupancy, August 2022](https://www.planningportal.nsw.gov.au/sites/default/files/documents/2022/BASIX%20standard%20occupancy%20-%20version%204%20-%2023.08.22%20LMv5.pdf).

## Sustainable feature guidance

Official Australian [Your Home](https://www.yourhome.gov.au/) guidance supports choosing appropriate insulation, glazing, shading, solar, water efficiency and material alternatives. These sources support the design rationale; they do not validate the app’s seed installed prices or project savings. Replace indicative prices and performance with project evidence.

- [Insulation](https://www.yourhome.gov.au/passive-design/insulation)
- [Glazing](https://www.yourhome.gov.au/passive-design/glazing)
- [Shading](https://www.yourhome.gov.au/passive-design/shading)
- [Rooftop solar](https://www.yourhome.gov.au/energy/rooftop-solar)
- [Hot-water systems](https://www.yourhome.gov.au/energy/hot-water-systems)
- [Rainwater](https://www.yourhome.gov.au/water/rainwater)
- [Reducing water use](https://www.yourhome.gov.au/water/reducing-water-use)
- [Embodied energy](https://www.yourhome.gov.au/materials/embodied-energy)

## Removal and recovered materials

Default: the building stays in use and there is no demolition cash flow at the study horizon. Property resale is outside this comparison. Demolition of an existing building today belongs in the initial construction budget.

The optional estimate uses the midpoint of a [Direct Demolition March 2026 contractor guide](https://directdemolition.com.au/blog/demolition-cost-sydney-2026.html): one-storey under 150 m² AUD 15,000–22,000; one-storey 150–250 m² AUD 20,000–32,000; one-storey over 250–350 m² AUD 28,000–42,000; two-storey 200–350 m² AUD 32,000–55,000. GST included, reasonable access, no asbestos. Additional slab/footing removal and site work are excluded. This is one contractor’s indicative range, not an official government rate or project quote. No extrapolation to apartments, commercial or larger buildings.

Both designs receive the same amount. Recovered-material income defaults to zero unless there is a payable recovery quote. Changing size recalculates the estimate and requires review again. Manual edits switch to manual mode. Costs are base-year estimates and follow the terminal escalation assumption. Review timing and pricing basis with a contractor.

## Public-launch limits

Removing “Sydney” from the logo and postcode label does not add new regions: reference utility data still supports the stated NSW networks and Sydney Water coverage. Apartment buildings use project-specific aggregate rates, not single-house reference charges. Other regions and formal BASIX/NatHERS assessments require separate reviewed data and scope. No database was added. Vercel deployment remains a later step.
