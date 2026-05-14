---
name: Property Listing Review
description: >
  This skill should be used when the user asks to "review a property listing", "check a draft listing",
  "review listing for compliance", "check for material information", "audit listing copy", "check this
  property description for risks", "review my listing before it goes live", "flag compliance issues in
  a listing", "check whether a listing is misleading", or "review a listing for material information
  gaps". Provides a structured compliance review of a UK residential property listing for England,
  identifying missing material information, unsupported claims, risky language, and misleading omissions.
version: 0.1.0
---

# Property Listing Review

Review draft residential property listings for England to identify compliance risks, missing material
information, unsupported claims, and misleading language before portal submission or client circulation.

## Input Formats

Accept the listing in any of:
- Free-form text or marketing copy pasted into the conversation
- A structured JSON file of listing fields — pass it to the validation script:
  `uv run $PLUGIN_ROOT/scripts/validate_listing.py <filepath>`
- A numbered list of property details

## Review Process

### Step 1 — Load Reference Material

Before starting the review, read:
- `$PLUGIN_ROOT/references/material-information-checklist.md` — to check material-info completeness
- `$PLUGIN_ROOT/references/red-lines.md` — to identify forbidden claim categories

Read `$PLUGIN_ROOT/references/england-estate-agent-compliance.md` if compliance questions arise about
redress scheme obligations, AML registration, or Estate Agents Act 1979 requirements.

### Step 1.5 — Verify EPC Against the Register (if postcode available)

If the listing includes a postcode, call `property_epc` from the property-shared MCP server:

```
property_epc(postcode = "<postcode>", address = "<address if available>")
```

Compare the returned certificate against the listing's stated EPC rating/band. Flag in the output if:
- No certificate is found for the postcode — EPC may be missing or the property has never been
  assessed; this must be investigated before listing
- The stated rating/band differs from the register (e.g. listing says C, register shows D)
- The certificate is expired — `lodgement_date` more than 10 years before today; an expired EPC is
  not valid for a property listing in England and a new assessment is required
- The certificate has a different property address — may indicate a mismatched or stale record

If `property_epc` returns no result, note this in Missing Information; do not infer the EPC rating.

### Step 2 — Run the Validator (JSON input only)

If the input is a JSON file, run:
```
uv run $PLUGIN_ROOT/scripts/validate_listing.py <filepath>
```
The script outputs a structured JSON report. Use its findings as the starting point for the narrative
review. Do not stop at the script output alone — apply judgement over the results.

### Step 3 — Check Material Information

Cross-check the listing against the material-information-checklist for:

**Always required:**
- Tenure: freehold, leasehold, or commonhold. Must be stated.
- EPC rating or band. Flag if absent, expired, or marked "exempt".
- Council tax band.
- Property type and number of bedrooms.

**Required if leasehold:**
- Lease length remaining (years). High-risk if < 80 years.
- Ground rent amount and review terms. Flag escalating ground rent.
- Service charge (annual or monthly amount).
- Management company or freeholder name if known.
- Building safety/cladding status if the building is a higher-risk building.

**Disclose if known:**
- Parking provision (on-street, off-street, permit zone, garage).
- Utilities (gas, electric, water, drainage type).
- Restrictive covenants or rights of way if disclosed by seller.
- Flood risk zone if known.
- Planning consents or permitted development restrictions if known.
- Japanese knotweed status if disclosed.
- Any known disputes, enforcement notices, or complaints.

Mark each item as: **confirmed** / **unknown — needs verification** / **absent**.

### Step 4 — Check for Risky Claims

Flag any of the following if present without stated source evidence:

| Claim type | Examples |
|---|---|
| Guarantee/certainty | "guaranteed", "will sell for", "no chain guaranteed" |
| Investment claims | "best investment", "perfect buy-to-let", "guaranteed rental yield" |
| Unverified structural/survey | "structurally sound", "no damp", "immaculate throughout" |
| Unverified planning/legal | "planning potential", "planning permission obtainable", "development opportunity" |
| Unverified environmental | "flood-free", "no flood risk", "no Japanese knotweed" |
| Unverified school claims | "outstanding school catchment", "excellent schools nearby" |
| Absolute condition claims | "no issues", "nothing to do", "perfect condition", "move-in ready" |
| Financial advice adjacents | "rental yields of X%", "capital growth likely" |

For each flagged claim: state the claim verbatim, the risk category, and what evidence would be needed
to support it.

### Step 5 — Check for Misleading Omissions

Assess whether:
- Known adverse information is buried, minimised, or omitted
- Leasehold warnings are absent on a leasehold property
- Service charge or ground rent figures are missing for leaseholds
- Building safety or cladding issues are present but not flagged
- Lease length is short (< 80 years) and not disclosed
- Flood risk, subsidence, or structural concerns are known but absent

### Step 6 — Produce the Output

Use the listing-review-report template in `$PLUGIN_ROOT/references/output-templates.md` (Section 1).

Structure the output as:

```
## Compliance Risk Summary
[One-paragraph overall assessment. Do not state the listing is "compliant".]

## Risk Level: [low | medium | high]
[One sentence justification]

## Confirmed Facts
- [Fact 1, with source if stated]
- [Fact 2]

## Missing Information
- [Item 1 — why it matters]
- [Item 2]

## Unsupported Claims
- [Verbatim claim — risk category — what evidence is needed]

## Risky Phrases Detected
- [Verbatim phrase — risk category]

## Questions for Seller / Vendor
- [Specific question to resolve missing/uncertain item]

## Human Review Notes
[Anything requiring professional or legal review: title, planning, AML, building safety, EPC validity]

## Caveat
This review is not legal advice and does not constitute a compliance sign-off. The listing must be
reviewed by the responsible agent and, where legal or technical issues arise, by a qualified
conveyancer, solicitor, or surveyor. Source data may be incomplete.
```

### Step 7 — Invoke the Compliance Reviewer Agent

Before finalising: pass the draft output to the `uk-property-compliance-reviewer` agent for a
second-opinion check on compliance overreach, missing attribution, and whether human review is
required. Incorporate any changes before presenting the final report.

## Red Lines

Do not:
- Invent or infer EPC ratings, tenure, lease length, service charge, or structural condition
- State the listing is "compliant" as a final legal determination
- Remove or minimise adverse information present in the input
- Answer unknown questions as if they are confirmed facts
- Make AML/KYC determinations

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
