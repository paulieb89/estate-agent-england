---
name: Seller Onboarding Checklist
description: >
  This skill should be used when the user asks to "create a seller checklist", "generate a vendor
  questionnaire", "onboard a new seller", "seller information request", "what information do I need
  from the vendor", "seller pack checklist", "what to ask a new seller", "seller onboarding form",
  "prepare a seller briefing", or "seller due diligence checklist". Creates a tailored property-specific
  seller/vendor information request checklist for England residential sales, covering all material
  information categories with unknown/needs-verification states and appropriate professional referral
  notes.
version: 0.1.2
---

# Seller Onboarding Checklist

Create a tailored seller/vendor information request checklist for England residential sales. The
checklist helps agents gather the material information required before listing and identifies items
needing professional verification.

## Input Requirements

Expect:
- Property address or postcode
- Property type (house/flat/maisonette, detached/semi/terraced)
- Tenure (freehold/leasehold/unknown) — if unknown, a leasehold section is included by default

If tenure is unknown, include both freehold and leasehold sections.

## Checklist Generation Process

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/material-information-checklist.md` — this is the canonical source for
every checklist category. Do not omit sections without reason.

Read `$PLUGIN_ROOT/references/england-estate-agent-compliance.md` for the regulatory context behind
why certain items are required.

### Step 2 — Tailor the Checklist

Adjust the standard checklist based on the property type:

- **Leasehold flat in a multi-storey building (6+ storeys or 11m+):** Include building safety, EWS1,
  and cladding section prominently.
- **Listed building:** Add planning and alterations section with listed building consent questions.
- **Rural property:** Add septic tank, private water supply, rights of way, access track questions.
- **New build or < 10 years old:** Add NHBC/warranty, snagging, estate charge questions.

### Step 3 — Produce the Checklist

Use the seller-info-request template in `$PLUGIN_ROOT/references/output-templates.md` (Section 2).

For each item, include three states: ✅ Confirmed | ❓ Unknown — needs verification | N/A

```
## Seller Information Request
### Property: [Address]
### Date: [Today's date]

---

> **Important notice to sellers:** This checklist is prepared by your estate agent to help gather
> information buyers will need. It is not legal advice. Your conveyancer will handle legal title
> matters and the conveyancing process. Items marked "needs verification" should be discussed with
> your conveyancer, surveyor, or other qualified professional as appropriate.

---

### 1. Property Basics
| Item | Status | Notes |
|---|---|---|
| Full address including postcode | | |
| Property type (detached/semi/terraced/flat/maisonette/other) | | |
| Year built or approximate age | | |
| Construction type (standard brick, timber frame, prefab, etc.) | | |
| Number of bedrooms | | |
| Number of bathrooms / shower rooms | | |
| Floor area (sq ft or sq m, if known) | | |
| Number of floors | | |
| Garden (yes/no, front/rear/both, approximate size) | | |

### 2. Price and Tenure
| Item | Status | Notes |
|---|---|---|
| Tenure: freehold / leasehold / commonhold | | |
| Guide / asking price expectation | | |
| Council tax band (England) | | |

### 3. Leasehold Details (complete if leasehold)
| Item | Status | Notes |
|---|---|---|
| Years remaining on lease | | |
| Ground rent — annual amount | | |
| Ground rent review clause (fixed / RPI / doubling / other) | | |
| Service charge — annual amount (last 3 years if available) | | |
| Major works planned or budget held? | | |
| Managing agent / freeholder name and contact | | |
| Management pack available or to be ordered? | | |
| Any arrears of ground rent or service charge? | | |
| Share of freehold held? | | |

### 4. EPC
| Item | Status | Notes |
|---|---|---|
| EPC rating (band A–G) | | |
| EPC certificate reference number | | |
| EPC expiry date (valid 10 years from issue) | | |
| EPC available as a document? | | |

### 5. Utilities and Services
| Item | Status | Notes |
|---|---|---|
| Mains gas (yes/no) | | |
| Electricity supplier | | |
| Water supply (mains / private / shared borehole) | | |
| Drainage (mains sewer / septic tank / cesspool) | | |
| Broadband type (FTTP / FTTC / ADSL / none) | | |
| Solar panels (owned / leased / none) | | |

### 6. Parking and Access
| Item | Status | Notes |
|---|---|---|
| Off-street parking (driveway / garage / allocated space) | | |
| On-street parking (permit zone / unrestricted) | | |
| Garage (integral / detached / none) | | |
| EV charging point installed? | | |
| Access road: adopted highway or private road? | | |
| Any access issues or shared maintenance arrangements? | | |

### 7. Restrictions and Rights
| Item | Status | Notes |
|---|---|---|
| Any known restrictive covenants? | | |
| Rights of way or footpaths across the property? | | |
| Shared access or shared drive? | | |
| Any boundary disputes (current or historical)? | | |
| Party wall agreements in place? | | |

### 8. Alterations and Permissions
| Item | Status | Notes |
|---|---|---|
| Any extensions or structural alterations? (with dates) | | |
| Building regulations approval obtained? (certificates available) | | |
| Planning permission obtained for any works? (ref numbers) | | |
| Listed building consent obtained for any works? | | |
| Any works carried out without required permissions? | | |
| FENSA / CERTASS cert for replaced windows/doors? | | |

### 9. Building Safety (leasehold / flats)
| Item | Status | Notes |
|---|---|---|
| Building height (storeys / metres)? | | |
| External wall cladding — type known? | | |
| EWS1 form in place (if required)? | | |
| Building safety certificate obtained? | | |
| Any building safety fund remediation planned or underway? | | |
| Leaseholder protection certificate issued? | | |

### 10. Flood, Subsidence and Environment
| Item | Status | Notes |
|---|---|---|
| Any history of flooding at the property? | | |
| Any subsidence, heave, or ground movement known? | | |
| Structural or underpinning works carried out? (with dates) | | |
| Japanese knotweed — present, treated, or historically treated? | | |
| Any contaminated land or former industrial use nearby (if known)? | | |

### 11. Local Charges and Designations
| Item | Status | Notes |
|---|---|---|
| Estate / maintenance charges (new builds / private estates)? | | |
| Any local authority notices, planning enforcement? | | |
| Conservation area? | | |
| Article 4 direction in effect? | | |
| Local land charges search — previously obtained? | | |

### 12. Disputes and Notices
| Item | Status | Notes |
|---|---|---|
| Any disputes with neighbours (current or resolved)? | | |
| Any legal proceedings relating to the property? | | |
| Any formal complaints from planning, building control, or other authority? | | |
| Shared services agreements (e.g., drains, roofspace)? | | |

### 13. Documentation to Gather
| Document | Available | Notes |
|---|---|---|
| Title register / official copy from HMLR | | |
| EPC certificate | | |
| Building regulations completion certificates | | |
| Planning approval letters | | |
| Structural warranties / NHBC Buildmark | | |
| Boiler service records | | |
| Electrical installation condition report (EICR) | | |
| Management pack (leasehold) | | |
| Party wall awards (if applicable) | | |

---

### Agent Notes
[Space for agent to add property-specific notes or follow-up items]

### Conveyancer / Professional Referral Notes
[Note any items that should be referred to the seller's conveyancer, surveyor, or other specialist
before listing. For example: unknown restrictive covenants, unpermitted works, building safety status,
short lease.]
```

### Step 4 — Append Standard Disclaimer

Always include at the foot of every checklist:
> This checklist was prepared by the instructed estate agent to assist with information gathering.
> It is not a substitute for legal advice, a building survey, or conveyancing. Technical and legal
> matters — including title, covenants, planning permissions, and building safety — should be
> referred to the seller's conveyancer or an appropriately qualified professional. This agent is
> not providing legal or financial advice.

## Red Lines

Do not:
- Omit the leasehold section without clear confirmation the property is freehold
- Present the checklist as a complete legal compliance requirement
- Advise the seller on how to answer specific legal or title questions
- Imply that completing the checklist means the listing is "ready to go" without professional review

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
