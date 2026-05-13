---
name: Property Listing Draft
description: >
  This skill should be used when the user asks to "draft a property listing", "write a sales listing",
  "create a property description", "write listing copy from seller notes", "generate a property advert",
  "write an estate agent description", "turn these property notes into a listing", or "help me write
  up a property". Drafts a professional residential sales listing for England from structured seller
  notes or property details, separating confirmed facts from assumptions and using restrained
  UK estate-agency prose.
version: 0.1.0
---

# Property Listing Draft

Draft a professional residential sales listing for England from seller notes, property details, or a
structured fact sheet. Produce UK-English copy that is accurate, non-hype-heavy, and appropriate for
portal submission.

## Input Requirements

Expect any of:
- A free-form set of seller notes or a filled-in property fact sheet
- A structured JSON file (same schema as `fixtures/listing_valid.json`)
- A list of property attributes provided in conversation

If input is sparse, ask for the missing required fields before drafting. Required fields are: address,
property type, bedrooms, tenure, guide price or price. EPC rating and council tax band are strongly
preferred.

## Drafting Process

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/red-lines.md` before writing any copy to know what claims and phrases
are forbidden.

Read `$PLUGIN_ROOT/references/output-templates.md` (Section 4 — listing rewrite) for the expected
output structure.

### Step 2 — Classify Each Input Field

Before writing, classify every piece of information provided as:

- **Confirmed fact** — stated explicitly in the input (e.g., "3 bedrooms", "freehold", "EPC D")
- **Inferred / likely** — reasonable assumption from context (e.g., gas central heating implied by
  "gas boiler present") — these must be flagged in the output
- **Unknown / not stated** — absent from input — do not invent these

### Step 3 — Write the Listing

Write in UK English. Follow these style rules:

**Do:**
- Use clear, professional estate-agency prose appropriate for Rightmove or OnTheMarket
- Lead with the strongest confirmed facts: location, property type, size, tenure
- Describe rooms and features concisely without padding
- Note any distinguishing features that are confirmed (e.g., "Victorian terrace", "private rear garden")
- Include a brief location paragraph drawing only on factual or well-known area characteristics
  (transport links if verifiable, character of the area)
- Use present tense for property descriptions

**Do not:**
- Use the words: guaranteed, best, perfect, immaculate, no issues, stunning, outstanding school,
  planning potential, investment opportunity, must-see, rarely available (unless genuinely rare and
  stated)
- Claim structural condition ("sound", "damp-free", "solid construction") without a survey source
- Claim flood risk, knotweed status, school catchment grade unless stated in input with a source
- Bury negative or uncertain information
- Add rooms, features, or attributes not present in the input
- Quote rental yields or capital growth projections
- Imply planning consent exists without stated planning permission reference

### Step 4 — Structure the Output

```
## Listing: [Address]

### Key Details
- Type: [Property type]
- Bedrooms: [N] | Bathrooms: [N]
- Tenure: [Freehold / Leasehold — and if leasehold: lease length, ground rent, service charge]
- EPC: [Band] | Council Tax: Band [X]
- Guide Price: £[X]

### Description
[2–4 paragraph listing copy]

### Features
- [Confirmed feature 1]
- [Confirmed feature 2]
...

---

### Drafting Notes
**Confirmed facts used:** [list]
**Assumed / inferred (flag for seller verification):** [list, or "None"]
**Fields not provided — omitted from listing:** [list]
**Seller questions before publishing:** [list of items to verify]
```

### Step 5 — Invoke the Compliance Reviewer Agent

Pass the draft listing to the `uk-property-compliance-reviewer` agent to check for unsupported claims,
missing material information, and compliance overreach. Incorporate feedback before presenting the
final draft.

### Step 6 — Append Caveats

Append to the output:
> This draft is based solely on the information supplied. Claims marked as assumed require seller
> confirmation before publication. EPC, council tax, tenure, and leasehold details must be verified
> against original certificates and title documentation. This output is not legal advice.

## Red Lines

Do not:
- Invent or infer EPC ratings, lease length, ground rent, service charges, structural condition,
  flood risk, knotweed status, planning permissions, school catchment grades, or title restrictions
- Write copy that implies legal, structural, or financial certainty the input does not support
- Add features not present in the input to make the listing sound better
- Use pressure-selling language ("act quickly", "won't last", "rare opportunity") without factual basis

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
