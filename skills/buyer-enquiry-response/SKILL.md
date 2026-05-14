---
name: Buyer Enquiry Response
description: >
  This skill should be used when the user asks to "draft a buyer response", "respond to a buyer
  enquiry", "write a reply to a buyer question", "answer a buyer's question about the property",
  "help me respond to a viewer enquiry", "draft an email to a buyer", or "buyer wants to know X —
  what should I say". Drafts buyer-facing replies using only confirmed facts from the listing or
  seller-provided information, with explicit caveats for unknowns and a firm refusal to answer
  open factual questions as settled.
version: 0.1.1
---

# Buyer Enquiry Response

Draft buyer-facing responses to property enquiries using only confirmed facts and explicit caveats.
Refuse to answer unknown or unverified matters as if they are settled, and refer technical or legal
questions to the appropriate professional.

## Input Requirements

Expect:
- The buyer's question or enquiry (verbatim or paraphrased)
- The listing details or property fact sheet
- Any seller-provided information relevant to the question

If the question cannot be answered from confirmed facts in the supplied information, produce a
response that acknowledges the gap and states what will be done to obtain the answer.

## Response Process

### Step 1 — Load Reference Material

Read `$PLUGIN_ROOT/references/red-lines.md` to know what claims must never be made in buyer
communications, regardless of how the question is framed.

### Step 2 — Classify the Enquiry

Determine whether the buyer's question concerns:

| Category | Handling |
|---|---|
| Confirmed fact in listing | Answer directly, cite source |
| Item not in listing but obtainable from seller | Acknowledge gap, promise to seek information |
| Legal or title matter (covenants, title, easements) | Refer to conveyancer |
| Survey or structural matter | Refer to surveyor or specialist |
| Planning or building regulations matter | Refer to planning authority or building control |
| Financial or investment matter | Refer to independent financial adviser or mortgage adviser |
| Flood/environmental matter | Refer to conveyancing search or Environment Agency |

### Step 3 — Draft the Response

**Do:**
- Answer clearly and directly when the fact is confirmed
- State source or basis for any factual claim ("The EPC, which rates the property band D, is
  available on request")
- Acknowledge when information is not available and state the next step
- Use UK English, professional but approachable tone

**Do not:**
- Answer questions about structural condition, flood risk, school catchment grades, planning consent,
  knotweed status, or title matters as confirmed facts unless the listing explicitly states them with a
  verified source
- Use hedge language that still implies certainty ("we believe there are no issues")
- Fabricate or estimate answers to factual questions
- Give legal or financial advice ("you should buy this", "it's a sound investment")
- Apply pressure-selling tactics in buyer communications

### Step 4 — Structure the Output

```
## Draft Reply to Buyer

**Re:** [Property address]
**Query:** [Summary of buyer's question]

---

[Response text]

---

**Drafting Notes**
- Based on: [sources used]
- Items marked unknown: [list]
- Referrals included: [yes/no — which professional type]
- Items to verify with seller before sending: [list, or "None"]
```

### Step 5 — Caveats

Append to the drafting notes (not to the buyer-facing reply unless relevant):
> This draft is based on confirmed information only. Before sending, verify that all stated facts
> remain accurate. Do not send buyer responses containing unverified claims. This skill does not
> provide legal or financial advice.

## Red Lines

Do not:
- Answer unknowns as if they are known to avoid an awkward buyer interaction
- State that there are "no issues" with the property without full knowledge of the position
- Offer an opinion on value, investment quality, or rental yield
- Confirm planning consent, structural condition, flood risk, or school catchment without a stated,
  verified source

Consult `$PLUGIN_ROOT/references/red-lines.md` for the complete list.
