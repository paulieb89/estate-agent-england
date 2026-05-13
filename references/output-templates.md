# Output Templates

Structured templates for the main output types produced by the estate-agent-england plugin.
Use these as the basis for all final reports and drafts. Fill in sections from confirmed facts;
mark unknowns explicitly.

---

## Template 1 — Listing Review Report

```markdown
# Property Listing Review Report

**Property:** [Address]
**Review date:** [Date]
**Reviewed by:** Claude Code (estate-agent-england plugin) — requires human agent sign-off

---

## Compliance Risk Summary

[One-paragraph overall assessment. State the main risks found. Do not state the listing is
"compliant" as a legal determination. Use: "No significant issues identified from the supplied
material" or "Several issues require attention before publication".]

## Risk Level

**[LOW | MEDIUM | HIGH]**

[One-sentence justification.]

---

## Confirmed Facts

The following facts were present and appear sourced or verifiable in the supplied input:

- [Fact 1 — source if stated]
- [Fact 2]
- ...

---

## Missing Information

The following material information was absent or unclear:

| Item | Why It Matters | Action Required |
|---|---|---|
| [Item] | [Reason] | [Confirm with seller / obtain documentation] |

---

## Unsupported Claims

The following claims appear in the listing without stated source evidence:

| Claim (verbatim) | Risk Category | Evidence Needed |
|---|---|---|
| "[quote]" | Structural / Planning / Environmental / Financial / Legal | [What would support this claim] |

---

## Risky Phrases Detected

| Phrase (verbatim) | Risk Category |
|---|---|
| "[phrase]" | [Category] |

---

## Questions for Seller / Vendor

1. [Specific question to resolve missing or uncertain item]
2. ...

---

## Human Review Notes

[Items that require review by a qualified professional before listing:]
- [ ] [Item — professional type required]

---

## Caveat

This review is not legal advice and does not constitute a compliance sign-off. The listing must be
reviewed by the responsible agent and, where legal or technical issues arise, by a qualified
conveyancer, solicitor, or surveyor. Source data and seller disclosures have not been independently
verified. Data may be incomplete or out of date.
```

---

## Template 2 — Seller Information Request

```markdown
# Seller Information Request

**Property:** [Address]
**Prepared for:** [Seller name or "The Vendor"]
**Prepared by:** [Agent name]
**Date:** [Date]

---

> **Important:** This form is prepared by your estate agent to help gather the information buyers
> will need. It is not legal advice. Your conveyancer will handle legal title matters. Items marked
> "needs verification" should be discussed with your conveyancer, surveyor, or other qualified
> professional as appropriate.

---

[Use the checklist structure from material-information-checklist.md, tailored to the property type]

---

## Documentation to Gather

| Document | Status | Notes |
|---|---|---|
| [Document] | [Available / To be obtained / N/A] | |

---

## Agent Notes

[Agent-specific notes about this property or instruction]

---

## Conveyancer / Professional Referral Notes

[Items to discuss with seller's conveyancer, surveyor, or other specialist before listing:]
- [Item]
```

---

## Template 3 — Comparable Evidence Summary

```markdown
# Comparable Evidence Summary

**Subject property:** [Address / postcode / type]
**Prepared:** [Date]
**Data source:** [HMLR PPD / user-supplied / other]

---

## Filters Applied

| Filter | Value |
|---|---|
| Geography | [outcode / sector] |
| Property type | [code + description] |
| Date range | [from] to [to] |
| Tenure | [freehold / leasehold / all] |
| Price range | [£X – £Y / none] |
| Excluded | [anomalies / exclusions with reason] |

---

## Statistics

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

---

## Recent Comparable Transactions (up to 10 most recent)

| Address | Completion Date | Price | Type | Dur |
|---|---|---|---|---|
| [Address] | [YYYY-MM-DD] | £[X] | [T/S/D/F] | [F/L] |

---

## Limitations

- [HMLR lag caveat — data typically 2–3 months behind completion]
- [Sample size caveat if n < 10]
- [Comparability caveat if type/tenure mix is impure]
- [Stale data caveat if transactions > 18 months]

---

## Interpretation Notes

[Brief narrative — context, market conditions, caveats on applying to the subject property]

---

## Caveat

This summary is based on the data supplied and is for agent / client information only. HMLR Price
Paid Data records completed and lodged transactions; it does not include unsold properties, listings
for sale, or properties under offer. This is not a formal valuation, an estate agent's market
appraisal, or a surveyor's opinion of value. Human review by the instructed agent is required before
using this summary for pricing or marketing decisions. Data sourced from HM Land Registry under the
Open Government Licence (OGL).
```

---

## Template 4 — Listing Rewrite

```markdown
# Listing Draft

**Property:** [Address]
**Date:** [Date]
**Status:** DRAFT — awaiting seller verification and agent sign-off

---

## Key Details

| | |
|---|---|
| Type | [Property type] |
| Bedrooms | [N] |
| Bathrooms | [N] |
| Tenure | [Freehold / Leasehold — and if leasehold: lease length, GR, SC] |
| EPC | Band [X] |
| Council Tax | Band [X] |
| Guide Price | £[X] |

---

## Description

[2–4 paragraph listing copy, UK English, professional and restrained]

---

## Key Features

- [Confirmed feature 1]
- [Confirmed feature 2]
- ...

---

## Drafting Notes

**Confirmed facts used:**
- [List]

**Assumed / inferred (flag for seller verification before publishing):**
- [List, or "None"]

**Fields not provided — omitted from listing:**
- [List]

**Seller questions before publishing:**
1. [Question]

---

> This draft is based solely on the information supplied. Claims marked as assumed require seller
> confirmation before publication. EPC, council tax, tenure, and leasehold details must be verified
> against original certificates and title documentation. This draft is not legal advice.
```

---

## Template 5 — Buyer Enquiry Response

```markdown
# Draft Reply to Buyer Enquiry

**Property:** [Address]
**Date:** [Date]
**Re:** [Summary of buyer's question]

---

[Response text — professional, clear, UK English]

---

## Drafting Notes (internal — do not send to buyer)

**Based on:** [Sources used]
**Items stated as unknown in response:** [List, or "None"]
**Referrals included:** [Yes / No — and which professional type if yes]
**Items to verify with seller before sending:** [List, or "None"]

---

> Before sending: verify all stated facts remain accurate and current. Do not send buyer responses
> containing unverified claims. This skill does not provide legal or financial advice.
```
