# GreenCost Sydney: Local Pricing and Quantity Takeoff Specification

Companion to `GreenCost-Sydney-Agent-Build-Brief.md` and `GreenCost-Sydney-Project-Document.md`. Where this file and the brief differ on pricing, **this file wins**.

**Purpose:** when a user enters a Sydney postcode and chooses materials or systems, the app shows a believable local price for *their* house, with its source and age, without making the page slow or the search bill unpredictable.

---

## 1. Rules a builder and a developer would both insist on

1. **A price is not a cost.** A shelf price for one pack of batts says nothing about the cost of insulating a house. Cost = quantity × price, plus labour, plus allowances.
2. **Compare like with like.** Every price states its unit, whether it is supply-only or installed, and whether it includes GST. The code-minimum option is priced the same way as the upgrade.
3. **Only price the difference.** The sustainable premium is the upgrade cost minus the code-minimum cost, never the full cost of the item.
4. **Do not double count.** Installed prices already include labour and margin. Supply prices do not. The build-up adds only what is missing.
5. **Be honest about what is live.** Only supply prices and installed price ranges come from the web. Labour rates, margins, GST, rebates and energy figures are dated assumptions, and are labelled that way.
6. **Never search on every click.** Prices are cached, refreshed in the background, and shown instantly with their age.
7. **Always fall back.** If a live price cannot be found or fails validation, the app uses a dated default and says so.
8. **A real quote beats everything.** Let users type their own price. It is marked "Your price".

---

## 2. User journey

```
Stage 1  Enter postcode ──► app shows: "Parramatta area, Western Sydney zone,
          floor area, storeys,    electricity network: Endeavour Energy"
          bedrooms, bathrooms     (zone drives nearby stores and network)
              │
              ▼
Stage 2  Pick materials/systems ──► each option card shows, for THIS house:
          (measure picker)           quantity, price per unit, total (range),
              │                       difference vs code-minimum, price badge,
              │                       "see sources", "refresh price"
              ▼
Stage 3  Tariffs and operation
Stage 4  Financial assumptions ──► results (premium = sum of selected differences)
```

---

## 3. Location resolver (postcode to zone)

### 3.1 What a postcode gives us
`GET /api/v1/location/{postcode}` returns:
- `valid`: whether it is in the Greater Sydney service area (data file, cited).
- `suburbs[]`: names used in store searches.
- `zone`: one of the pricing zones below.
- `network`: electricity distributor (Ausgrid, Endeavour Energy or Essential Energy) from the official network maps.
- `climate_zone`: NatHERS climate zone for the postcode (look up and cite; do not guess).
- `water_authority`: for water tariffs (look up and cite).

Invalid or out-of-area postcodes return a clear message ("This version covers Greater Sydney only"), and never an error page.

### 3.2 Proposed pricing zones (owner to approve)
| Zone | Rough coverage |
|------|---------------|
| Inner and Eastern | CBD, inner west, eastern suburbs |
| North Shore and Northern Beaches | Lower and upper north shore, beaches |
| Hills and North-West | The Hills, Hornsby, Ryde to north-west |
| Western Sydney | Parramatta west to Penrith, Blacktown |
| South-West | Liverpool, Campbelltown, Camden |
| South and Sutherland | St George, Sutherland Shire |

Zones are data in `postcode_zones.json` (postcode to zone), so they can be changed without code. Start with six; fewer zones means fewer searches.

### 3.3 Honest limits
Sydney prices vary little between postcodes. What really changes is which suppliers are nearby, delivery cost and the electricity network. The UI must **not** claim exact per-postcode pricing. It says "prices from suppliers serving your area".

---

## 4. House takeoff (turning a house into quantities)

`POST /api/v1/takeoff` converts the user's house description into quantities. All parameters below are **placeholders** until sourced; they live in `takeoff_assumptions.json`, can be overridden in an "Advanced" panel, and are shown on the Assumptions page.

### 4.1 Geometry model (rectangular plan)
| Parameter | Default | Note |
|-----------|---------|------|
| Plan aspect ratio (length : width) | 1.5 : 1 | placeholder |
| Wall height per storey | 2.7 m | placeholder |
| Glazing area as share of floor area | 18% | consistent with the legacy spec (about 39 m² on 220 m²) |
| External door area | 6 m² | placeholder |
| Roof area factor (pitch and eaves) | footprint × 1.15 | placeholder |
| Usable solar roof share | 40% | placeholder |
| Solar panel area | 5 m² per kW | placeholder |
| Rainwater catchment | footprint × 1.1 | placeholder |
| Light points | 1 per 4 m² of floor area | placeholder |
| Waste allowance | 5-10% by material | placeholder |

Formulas:
- `footprint = GFA / storeys`
- `width = sqrt(footprint / 1.5)`, `length = 1.5 × width`, `perimeter = 2 × (length + width)`
- `gross_wall = perimeter × wall_height × storeys`
- `glazing = 0.18 × GFA`
- `net_wall = gross_wall − glazing − doors`
- `ceiling = footprint` (top storey), `roof = footprint × 1.15`
- `envelope = gross_wall + ceiling`

### 4.2 Worked example (220 m², single storey, 4 bed, 2 bath)
| Quantity | Value |
|----------|------:|
| Footprint | 220 m² |
| Width × length | 12.1 m × 18.2 m |
| Perimeter | 60.6 m |
| Gross external wall | 163.5 m² |
| Glazing | 39.6 m² |
| Net insulated wall | 117.9 m² |
| Ceiling | 220 m² |
| Roof | 253 m² |
| Envelope (walls + ceiling) | 383.5 m² |
| Solar panel area at 6.6 kW | 33 m² (needs usable roof of at least 33 m²; available about 101 m²) |
| Rainwater catchment | 242 m² |
| Fixtures (2 bathrooms) | 2 showers, 2 toilets, 6 taps |
| Light points | 55 |

### 4.3 Measure to quantity driver
| Measure | Quantity driver | Reference value (220 m² house) |
|---------|-----------------|-------------------------------:|
| Wall insulation | net wall area | 117.9 m² |
| Ceiling insulation | ceiling area | 220 m² |
| Reflective sarking | roof area | 253 m² |
| Glazing | glazing area | 39.6 m² |
| Airtightness | envelope area, plus 1 blower-door test | 383.5 m² |
| Passive shading | shaded glazing (about 50% of glazing) | 19.8 m² |
| HVAC | conditioned floor area × load density (placeholder, about 70 W/m²) | 220 m², about 15 kW |
| Heat pump hot water | 1 unit, size by bedrooms | 1 unit |
| Solar PV | selected kW (roof capacity check) | 6.6 kW |
| Rainwater | tank size, catchment | 5 kL, 242 m² |
| Water fixtures | fixture counts | 2 / 2 / 6 |
| Efficient lighting | light points | 55 |
| Smart controls | per dwelling | 1 |

### 4.4 Feasibility checks (what a builder would flag)
- **Solar:** `max_kW = usable_roof_area / 5 m² per kW`. A double-storey house has a smaller roof, so the slider maximum drops (about 10 kW on a 220 m² two-storey house). Show a message, don't silently cap.
- **Rainwater:** the tank only helps if roof yield and indoor non-potable demand justify it; show the assumed offset and how it is limited by tank size.
- **Heat pump hot water:** one unit per dwelling; size by bedrooms.

### 4.5 When the geometry is wrong
Real plans are not rectangles. Advanced users may override perimeter, glazing area, roof area or any quantity directly. Overridden quantities are marked "Your quantity".

---

## 5. Price catalogue

Prices are keyed by `item_key` and `zone`. **Refresh class:** **A** = unit supply price, zone-specific, refresh daily; **B** = installed price range, metro-wide, refresh weekly; **C** = assumption (not live), reviewed by a person.

| Item (code-minimum and upgrade pairs) | Reference specification | Unit | Basis | Source types | Class |
|---------------------------------------|-------------------------|------|-------|--------------|:-----:|
| Wall batts (baseline and R2.5) | glasswool wall batts of stated R-value and thickness | $/m² | supply | building-supply and hardware stores | A |
| Ceiling batts (baseline and R5.0) | glasswool ceiling batts of stated R-value | $/m² | supply | building-supply and hardware stores | A |
| Reflective sarking | foil sarking roll | $/m² | supply | building-supply stores | A |
| Rainwater tank | 5,000 L poly tank | $/unit | supply | tank suppliers, hardware stores | A |
| Rainwater pump system | auto-switching pressure pump | $/unit | supply | plumbing suppliers | A |
| WELS fixtures | showerhead, toilet, tap of stated WELS rating | $/unit | supply | plumbing suppliers | A |
| LED lighting | dimmable LED downlight | $/unit | supply | electrical suppliers | A |
| Glazing (baseline and double Low-E argon, thermally broken) | window supply-and-install by area | $/m² window | installed | window makers and installers (price guides) | B |
| HVAC (baseline and inverter multi-split) | by capacity | $/kW | installed | HVAC suppliers, installers | B |
| Heat pump hot water (baseline and CO₂ or air-source) | unit with installation | $/unit | installed | plumbing suppliers, installers | B |
| Solar PV | 6.6 kW tier-1 panels with inverter | $/kW | installed | solar price indices, installers | B |
| Solar inverter replacement | string inverter | $/unit | installed | suppliers, installers | B |
| Smart controls | home energy management unit | $/unit | supply plus install | suppliers | B |
| Labour rates (carpenter, plumber, electrician, insulation installer) | published trade rates | $/hour | n/a | published schedules | C |
| Builder margin and overheads, GST, rebates, replacement lives | assumptions | % or $ | n/a | regulator and industry sources | C |

**Defaults until live prices pass validation** (placeholders from the legacy spec, scaled by quantity ratio): glazing +$5,500 (about $140/m² of glazing), insulation package +$3,200, HVAC +$4,500, hot water +$2,800 (net of incentives), solar +$5,800 for 6.6 kW (about $880/kW), rainwater tank and plumbing +$4,200, airtightness and shading +$3,800. Scale each by `quantity / reference_quantity` from section 4.3.

**Sanity bounds** per item start at **0.4× to 2.5× the default** unit price (placeholder). A quantity surveyor should replace these with real bounds before live updates are switched on.

---

## 6. Cost build-up per measure

```
option_cost =  Σ over materials [ quantity × (1 + waste) × unit_price ]      (Class A, B)
             + labour allowance (hours × rate)                               (Class C; skip if price is installed)
             + delivery / site allowance                                      (Class C)
             × (1 + builder margin and overheads)                             (Class C; skip if price is installed)
             × (1 + GST)                                                      (only if prices are ex-GST)

premium(measure) = option_cost(upgrade) − option_cost(code_minimum)
net premium      = premium − incentives (shown as a separate line)
```

Rules:
- Each price record carries flags: `includes_labour`, `includes_margin`, `gst_included`. The build-up adds only what is missing.
- **Incentives** (for example federal STCs for solar and heat pump hot water, and NSW schemes) are a separate, dated table, applied explicitly and shown on screen. Never bake them silently into a price. Verify and date each scheme at every update.
- **Ranges:** each price has low, median and high. The engine runs on the median. The sensitivity panel adds a **price scenario** (low / median / high) so users see how price uncertainty moves break-even.
- **Replacement costs** (inverter, pumps, heat pump, lighting) read from the same catalogue, in real terms.
- Contingency is **not** applied by default (optional input).
- A measure already required by code has zero premium and must not be shown as a saving.

---

## 7. Price pipeline (cached-live)

### 7.1 Flow
1. **Select what to refresh:** by schedule, by stale price, or by user request (section 7.4).
2. **Search (Tavily):** use query templates such as `"{reference spec} price {zone suburbs} Sydney"`. Use Tavily's domain filtering against a curated allow-list of Australian suppliers per category (`suppliers.json`, reviewed by the owner). Check the current Tavily API documentation for parameters.
3. **Extract:** a Gemini call with a **strict JSON schema** pulls `product_title`, `price_aud`, `gst_included`, `unit_text`, `pack_quantity`, `pack_unit`, `spec_matches`, `url`. Gemini extracts text only. It does not do arithmetic.
4. **Normalise (in code):** convert to the catalogue unit, for example pack price divided by pack coverage in m² (batts), dollars per kW (solar), dollars per unit.
5. **Match the product:** the extracted spec must match the reference spec (R-value, thickness, tank volume, WELS rating). Otherwise discard.
6. **Validate:** within sanity bounds, correct unit, correct basis, price visible and current. Reject the rest.
7. **Aggregate:** with at least three independent domains, `median` of valid prices, `low` and `high` as min and max after outlier removal. Fewer than three means "Indicative" and the default is used.
8. **Change guard:** a move of more than 25% from the previous median is held for review and not applied automatically.
9. **Store:** save the result and source records. Keep history.

### 7.2 Price record
```json
{
  "item_key": "insulation_wall_r2_5",
  "zone": "western_sydney",
  "unit": "AUD_per_m2",
  "basis": "supply",
  "gst_included": true,
  "includes_labour": false,
  "includes_margin": false,
  "low": 11.8, "median": 13.6, "high": 16.2,
  "sources": [{"url": "...", "retailer": "...", "price": 13.5, "seen_at": "..."}],
  "confidence": "medium",
  "status": "live",
  "computed_at": "2026-10-05T02:00:00+11:00",
  "expires_at": "2026-10-06T02:00:00+11:00"
}
```
Store the price, title, URL and timestamp only. Do not store copies of web pages.

### 7.3 Freshness, speed and cost control
| Mechanism | Rule |
|-----------|------|
| Cache | Prices are read from the cache. A user's page never waits for a search. |
| TTL | Class A: 24 hours. Class B: 7 days. |
| Scheduled refresh | A nightly job (Sydney time) refreshes class A items per zone and class B items metro-wide. |
| Stale-while-revalidate | A stale price is shown immediately with "updating…", a background refresh starts, and the UI updates when it finishes. |
| Single-flight | Only one refresh per `(item, zone)` at a time; others wait or reuse the result. |
| Refresh button | Allowed per item, rate-limited (placeholder: 5 per IP per hour, 200 per day overall). Over the limit, the cached price is shown with a message. |
| Budget caps | `TAVILY_DAILY_CAP` and `TAVILY_MONTHLY_CAP` counters. At the cap, refreshing stops and the cache serves everything. Log and surface it. |
| Planning estimate | Roughly 8 class A items × 6 zones × 2 queries a day is about 100 searches a day, or about 3,000 a month, before class B and manual refreshes. Check against the Tavily plan and reduce zones or queries if needed. |

### 7.4 Fallback ladder
1. Live price for the user's zone.
2. Live price for metro Sydney.
3. Last good price within a maximum age (placeholder: 30 days), labelled "Cached".
4. Dated default, labelled "Default".
5. Placeholder, labelled "Indicative".
The user's own price overrides all of these.

### 7.5 Badges
| Badge | Meaning |
|-------|---------|
| Live | At least 3 sources, fresh, passed validation. Shows "checked 6 h ago, 3 sources". |
| Cached | Last good live price, older than its TTL. |
| Default | Dated default from the catalogue. |
| Indicative | Placeholder or range, not verified. |
| Your price | Entered by the user. |

### 7.6 Storage and jobs
SQLite (WAL mode) for version 1 with tables `price_current`, `price_history`, `refresh_log`, `review_queue`, `usage_counters`. No user data. Move to Postgres only if a second server is needed. Use a scheduler (APScheduler or an operating-system cron job) to run `python -m app.jobs.refresh_prices`. Hosting needs a persistent disk.

---

## 8. API additions

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/location/{postcode}` | Zone, suburbs, network, climate zone, water authority |
| `POST /api/v1/takeoff` | House description to quantities, with formulas and overrides |
| `GET /api/v1/prices?zone=&items=` | Cached prices with badges, ages and sources; may mark `refreshing: true` |
| `POST /api/v1/prices/refresh` | Rate-limited refresh for one item and zone |
| `POST /api/v1/calculate/lcc` | Adds `zone`, `geometry`, `price_overrides`, `quantity_overrides`, `price_scenario` |

Each measure in the calculation response returns: quantity and unit, unit price (low/median/high), labour, margin, GST, incentives, premium versus code-minimum, badge, age and sources.

---

## 9. UI specification (measure picker)

- Every option card shows: plain-language name, a one-line "what it is", **quantity for this house** ("about 39 m² of windows"), unit price, **total as a range**, **difference versus code-minimum**, badge, **See sources** drawer, **Refresh price** button.
- Skeletons while loading. Never block the page on a price.
- A running total of the selected premium at the top of the picker.
- "Use my own quote" field on each card.
- A clear note: "Prices are indicative and not an offer. Confirm with your builder or supplier."
- Mobile first, keyboard accessible, colour never the only signal (badges carry text).
- The Assumptions page lists every takeoff parameter, price source, rebate and date.

---

## 10. Engineering cautions (to show in the app and in the report)

1. **This is not a NatHERS or BASIX assessment.** Thermal performance depends on orientation, window placement, shading and thermal mass. Picking measures does not guarantee a star rating. A NatHERS assessor must confirm compliance.
2. **Base build cost excludes site conditions** (sandstone excavation, reactive soil, bushfire or flood requirements). Measure premiums are separate from these.
3. **The takeoff is an estimate** for a simple rectangular plan. Irregular plans differ.
4. **Performance assumes correct installation.** Gaps in insulation or poor sealing reduce savings.
5. **Solar:** roof orientation and shading, network approval and export limits may apply. Verify with the installer and the distributor.
6. **Rainwater:** council and BASIX requirements, maintenance and first-flush devices apply.
7. **Prices change over time.** Reports state the price snapshot date.

---

## 11. Testing and acceptance

- **Takeoff:** the 220 m² example reproduces the table in section 4.2 exactly; two-storey and non-default inputs behave sensibly; overrides work.
- **Location:** valid, invalid and out-of-area postcodes; zone, network and climate zone correct for a sample of postcodes.
- **Extraction and normalisation:** pack-size parsing (for example a pack of batts covering 10.9 m²), GST handling, wrong-spec products rejected.
- **Validation:** out-of-range, wrong unit, fewer than three sources, and a more than 25% jump are all handled as specified.
- **Cache behaviour:** stale-while-revalidate, single-flight (two simultaneous requests cause one search), rate limits, budget caps.
- **Fallbacks:** with Tavily and Gemini both unavailable, the app still calculates, using defaults with correct badges.
- **No double counting:** an installed price does not get labour and margin added again.
- **Premium logic:** a code-required measure shows zero premium.
- **Speed:** a cached price shows in under one second; no user action triggers a blocking search.
- **Reproducibility:** each result and report records the price snapshot date and the source list.

---

## 12. Operations, ethics and legal

- Use Tavily's API. Do not scrape websites directly.
- Store only prices, titles, links and dates. Link to the source on screen.
- Keep a log of refreshes, failures, cap usage and held changes. Provide a simple private review list for held prices.
- Show clear wording that prices are indicative, may differ in store, and are not an offer to sell.
- Academic use: the price history and snapshot dates support reproducibility. Cite the method and sources in the thesis.

---

## 13. Build order (maps to the build brief)

| Task | Content | Done when |
|------|---------|-----------|
| T5A | Location resolver and zone data | Sample postcodes resolve correctly; invalid postcodes return friendly messages |
| T5B | Takeoff engine, feasibility checks, overrides | Section 4.2 example matches; tests pass |
| T5C | Price catalogue, defaults, sanity bounds, build-up logic | Premium for the reference house is reproducible from defaults; no double counting |
| T5D | Tavily pipeline, cache, scheduler, caps, fallbacks | Test run refreshes starter items; bad data rejected; app works with Tavily off |
| T5E | Price API and picker UI with badges, sources, refresh, own price | Cached price under 1 second; badges correct; works on a phone |

---

## 14. Owner decisions and inputs needed

1. Approve the six pricing zones, or choose different groupings.
2. Provide or approve the builder margin, labour rates, delivery allowance and waste factors (all placeholders now).
3. Review the supplier allow-list per category and check each site's terms.
4. Confirm incentive schemes to include and keep them dated.
5. Set sanity bounds with a quantity surveyor before turning on live updates.
6. Set the Tavily and Gemini monthly caps.
7. Confirm that installed items may be shown as price ranges labelled "indicative".
