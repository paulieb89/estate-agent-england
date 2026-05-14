---
name: Market Comparable Summary
description: >
  This skill should be used when the user asks to "summarise comparables", "comparable sold prices",
  "sold price analysis", "market comparison for this property", "what have similar properties sold for",
  "analyse HMLR price paid data", "comparables for a valuation", "sold evidence", "comparable evidence
  summary", "recent sales near this property", or "price paid data analysis". Summarises comparable
  sold-price evidence using live HMLR Price Paid Data via the property-shared MCP server or a
  user-supplied CSV file, clearly distinguishing sold prices from asking prices, and including data
  range, sample size, and limitations.
version: 0.1.0
---

# Market Comparable Summary

Summarise comparable sold-price evidence for England residential property. For postcode-based queries
use the live `property_comps` MCP tool (property-shared server). For user-supplied CSV files fall back
to the `summarise_price_paid.py` script. Always distinguish sold prices from asking prices and include
data-range, sample-size, and data-lag caveats.

## Input Requirements

Expect one of:
- A postcode (or address + postcode) — use the MCP tools path
- A path to a user-supplied HMLR Price Paid CSV/TXT file — use the script path
- A list of comparable addresses and prices pasted into the conversation — summarise directly

If no data is provided, explain how to obtain it (see `$PLUGIN_ROOT/references/data-sources.md`).
Do not fabricate comparable prices.

---

## Path A — Postcode Query (MCP tools, live data)

Use this path whenever a postcode is available. No CSV file required.

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/data-sources.md` for HMLR data limitations (lag, no STC/asking prices,
search_level scope). Note that `property_comps` defaults to sector-level search — check `search_level`
in the response.

### Step 2 — Call `property_comps`

```
property_comps(
  postcode = "<postcode>",
  property_type = "<D|S|T|F|null>",   # null = all residential
  months = 24,                         # extend to 36 on thin markets
  enrich_epc = true,                   # adds floor_area_m2 and price_per_sqm
  filter_outliers = false,             # set true for IQR-trimmed stats if n >= 4
  search_level = "sector"              # default; widens to "district" on thin market
)
```

The response includes: `sample_size`, `median_price`, `mean_price`, `p25`, `p75`, `min_price`,
`max_price`, `date_range`, `search_level`, and a `transactions` list (up to `limit`, default 50).

If `sample_size < 5`, widen `search_level` to `"district"` or extend `months` before reporting.
Always state the `search_level` used in the output.

### Step 3 — Optional enrichment

For investment or rental context, also call:
- `property_yield(postcode, property_type)` — gross yield combining HMLR sales and Rightmove rents
- `rental_analysis(postcode)` — achievable rent estimate with thin-market escalation
- `ppd_transactions(postcode, property_type)` — raw recent transactions if the user wants the
  full transaction list rather than statistics

### Step 4 — Classify the data

State for each figure whether it is:
- **Registered sold price** (HMLR PPD — completed, lodged transactions)
- **Asking/listed price** — only if user has supplied portal data; never blend with sold prices
- **Stale** — transactions > 18 months old; flag prominently
- **Small sample** — n < 5; flag at the top of the output

---

## Path B — CSV File (script fallback)

Use this path only when the user has supplied a downloaded HMLR Price Paid CSV.

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/data-sources.md` for CSV format notes and streaming guidance.

### Step 2 — Run the summariser script

```
uv run $PLUGIN_ROOT/scripts/summarise_price_paid.py \
  --file <filepath> \
  [--outcode SW9] \
  [--property-type T] \
  [--from-date 2022-01-01] \
  [--to-date 2024-12-31] \
  [--min-price 200000] \
  [--max-price 700000]
```

Property type codes: D=Detached, S=Semi-Detached, T=Terraced, F=Flat/Maisonette, O=Other.
The script streams the file — do not attempt to load large HMLR files into memory.

---

## Output Format

Use the comparable-evidence-summary template in `$PLUGIN_ROOT/references/output-templates.md`
(Section 3) for both paths.

```
## Comparable Evidence Summary

### Subject Property
[Address / postcode / type — as supplied]

### Data Source
[property-shared / HMLR Price Paid Data — live via property_comps, sector SW9, 24 months]
[or: User-supplied CSV file — <filename>]

### Filters Applied
- Geography: [search_level: sector / district / postcode — and scope e.g. SW9]
- Property type: [code + description, or "all residential"]
- Date range: [from] to [to]
- Tenure: [if filtered]
- Outlier filtering: [IQR applied / not applied]

### Statistics
| Metric | Value |
|---|---|
| Sample size | N transactions |
| Median sold price | £X |
| Mean sold price | £X |
| Lower quartile (P25) | £X |
| Upper quartile (P75) | £X |
| Minimum | £X |
| Maximum | £X |
| Date range of sample | [from] — [to] |
| Price per sq m (median, EPC-enriched) | £X / m² [if enrich_epc used] |

### Recent Comparable Transactions (up to 10)
| Address | Date | Price | Type | Floor area | £/m² |
|---|---|---|---|---|---|
| ... | | | | | |

### Yield and Rental Context (if called)
- Gross yield: X% (median sale price £X, median monthly rent £X)
- Achievable monthly rent: £X–£X [rental_analysis result]

### Limitations
- HMLR data lag: typically 2–3 months from registration to publication
- [Sample size caveat if n < 10]
- [Search level caveat: sector-level includes all postcodes in the sector, not just the subject street]
- [Stale data caveat if any transaction > 18 months]
- EPC floor-area enrichment: not all transactions have a matched EPC certificate

### Interpretation Notes
[Brief narrative. Do not state or imply a property's value. Use: "The median of £X for [type] in
[area] over [period] provides a range of £X–£X as a broad guide, subject to individual condition,
floor area, and features. This is sold-price evidence only."]

### Caveat
This summary is based on HMLR Price Paid Data (completed, lodged transactions). It does not include
unsold properties, listings for sale, or properties under offer. This is not a formal valuation and
does not constitute an estate agent's market appraisal or surveyor's opinion. Human review is
required before using this summary for pricing decisions.
```

### Final Step — Invoke the Compliance Reviewer Agent

Pass the draft summary to `uk-property-compliance-reviewer` to check for data mischaracterisation,
unwarranted conclusions, and stale-data risks before finalising.

---

## Red Lines

Do not:
- Fabricate comparable transactions
- Present asking prices as sold prices or blend the two without clear labelling
- Draw conclusions from samples smaller than 3 without prominent caveats
- State or imply a property's value, valuation, or likely sale price
- Quote yield or investment return figures unless sourced from `property_yield` or `rental_analysis`

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
