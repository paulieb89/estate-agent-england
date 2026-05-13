---
name: Market Comparable Summary
description: >
  This skill should be used when the user asks to "summarise comparables", "comparable sold prices",
  "sold price analysis", "market comparison for this property", "what have similar properties sold for",
  "analyse HMLR price paid data", "comparables for a valuation", "sold evidence", "comparable evidence
  summary", "recent sales near this property", or "price paid data analysis". Summarises comparable
  sold-price evidence using HMLR Price Paid Data files or user-supplied data, clearly distinguishing
  sold prices from asking prices, and including data range, sample size, and limitations.
version: 0.1.0
---

# Market Comparable Summary

Summarise comparable sold-price evidence for England residential property using HMLR Price Paid Data
or user-supplied comparable data. Produce a clear, limitation-aware summary that distinguishes sold
prices from asking prices and agent opinion.

## Input Requirements

Expect one of:
- A path to an HMLR Price Paid Data CSV/TXT file (pass to the summariser script)
- A user-supplied CSV or table of comparable sales
- A list of comparable addresses and prices pasted into the conversation
- A request for a summary when the user has already uploaded or referenced a data file

If no data file is provided, explain what data is needed and how to obtain it (see data-sources
reference). Do not fabricate comparable prices.

## Summary Process

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/data-sources.md` before proceeding. Note the limitations of each source,
especially HMLR lag (typically 2–3 months from registration to publication) and the absence of
unsold/STC listings from Price Paid Data.

### Step 2 — Run the Summariser Script (CSV/TXT input)

If the input is an HMLR Price Paid CSV or a similarly structured file, run:
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

Property type codes (HMLR): D=Detached, S=Semi-Detached, T=Terraced, F=Flat/Maisonette, O=Other.
Duration codes: F=Freehold, L=Leasehold.

The script streams the file — do not attempt to load large HMLR files entirely into memory.

Use the script output as the statistical foundation for the narrative summary.

### Step 3 — Classify the Data

For each data point, clearly state whether it is:
- **Registered sold price** (HMLR PPD — the price at which the transaction completed and was lodged)
- **Asking/listed price** (only if user has supplied portal data)
- **Agent opinion** (only if agent has provided a verbal CMA figure)
- **Stale data** (transactions > 18 months old should be flagged)
- **Small sample** (n < 5 comparable transactions — flag prominently)

Never blend these categories without clearly labelling each.

### Step 4 — Apply Comparability Filters

When selecting comparables, match on as many of the following as the data allows:
- Postcode district or sector (e.g., SW9, SE24 0)
- Property type (D/S/T/F)
- Tenure (F=Freehold, L=Leasehold) — where available
- Approximate size or bedroom count (if provided in supplementary data)
- Date range (prefer last 12 months; flag if extending to 24 months)

State which filters were applied and which could not be applied due to data limitations.

### Step 5 — Produce the Output

Use the comparable-evidence-summary template in `$PLUGIN_ROOT/references/output-templates.md`
(Section 3).

```
## Comparable Evidence Summary

### Subject Property
[Address / postcode / type — as supplied]

### Data Source
[HMLR Price Paid Data / user-supplied / other — with file name or retrieval date]

### Filters Applied
- Geography: [outcode/sector]
- Property type: [code + description]
- Date range: [from] to [to]
- Tenure: [if filtered]
- Price range: [if filtered]
- Excluded: [any anomalies or exclusions with reason]

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

### Recent Comparable Transactions (up to 10)
| Address | Date | Price | Type | Duration |
|---|---|---|---|---|
| ... | | | | |

### Limitations
- [HMLR data lag caveat]
- [Sample size caveat if n < 10]
- [Comparability caveat if type/tenure mix is impure]
- [Stale data caveat if any transaction > 18 months]
- [Any other limitation]

### Interpretation Notes
[Brief narrative — e.g., "The median of £X for freehold terraced houses in SW9 over the 24-month
period to [date] suggests a broad range of £X–£X for the subject property, subject to condition,
floor area, and individual features. This is sold-price evidence only; asking prices and market
conditions at time of instruction may differ. Human review by the instructed agent is required."]

### Caveat
This summary is based solely on the data supplied. HMLR Price Paid Data records completed and lodged
transactions and does not include unsold properties, listings currently for sale, or properties under
offer. This is not a formal valuation and does not constitute an estate agent's market appraisal or
surveyor's opinion. Human review is required before using this summary for pricing decisions.
```

### Step 6 — Invoke the Compliance Reviewer Agent

Pass the draft summary to `uk-property-compliance-reviewer` to check for data mischaracterisation,
unwarranted conclusions, and stale-data risks before finalising.

## Red Lines

Do not:
- Fabricate comparable transactions
- Present asking prices as sold prices
- Blend sold-price and asking-price data without clear labelling
- Draw conclusions from samples smaller than 3 without prominent caveats
- State or imply a property's value, valuation, or likely sale price
- Quote yield or investment return figures unless explicitly in the supplied data

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
