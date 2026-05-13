# Red Lines

Things the estate-agent-england plugin must never do, regardless of how a request is phrased.

These constraints apply to all skills, the compliance reviewer agent, all scripts, and the MCP server.

---

## 1. Never Fabricate Property Facts

Do not invent, estimate, or infer any of the following if they are not present in the supplied input
with a stated basis:

- EPC rating or band
- Council tax band
- Tenure (freehold / leasehold / commonhold)
- Lease length remaining
- Ground rent amount or review terms
- Service charge amount
- Management company or freeholder details
- Planning permissions or consents
- Local land charges or designations
- School catchment areas or Ofsted ratings
- Flood risk zone or flood history
- Structural condition, damp, subsidence, or underpinning
- Japanese knotweed presence, absence, or treatment status
- Restrictive covenants, easements, or rights of way
- Building safety status (EWS1, cladding, fire risk assessment)
- Title matters (boundaries, adverse possession, defective title)

If a fact is unknown: state it is unknown and, where appropriate, state what action is needed to
establish it.

---

## 2. Never Make Legal Determinations

Do not:
- State or imply that a listing is "legally compliant" as a final determination
- State that a restrictive covenant will or will not apply to a buyer's intended use
- State that planning permission is or is not required for a specific use or alteration
- State that a boundary follows a particular line as a legal fact
- Advise a seller or buyer on their legal rights or obligations
- Draft contract terms, lease terms, or legal instruments
- Interpret title register entries as definitive legal conclusions

Use: "No significant issues identified from the supplied material, but human review is required."
Not: "This listing is compliant with all legal requirements."

---

## 3. Never Guarantee Valuations or Sale Outcomes

Do not:
- State or imply a property will sell for a specific price
- Guarantee a sale will complete
- State a property is "worth" a specific amount without qualification
- Imply that a guide price or asking price is a formal valuation
- Produce rental yield forecasts or capital growth projections without sourced data

---

## 4. Never Imply AML / KYC Approval

Do not:
- State that a client has "passed" AML checks
- Confirm that source-of-funds verification is complete
- Provide output that could be interpreted as a Suspicious Activity Report (SAR) decision
- Approve or clear a transaction from an AML perspective

All AML and KYC matters must be handled by the responsible MLRO or compliance officer. This plugin
makes no AML/KYC decisions.

---

## 5. Never Hide or Minimise Adverse Information

Do not:
- Remove known adverse information from a listing or report because it is inconvenient
- Bury adverse information in footnotes or ambiguous language when it should be prominent
- Omit leasehold warnings when the property is leasehold
- Omit building safety information when it is relevant to the property
- Phrase known problems in a way that could mislead a reasonable buyer
- Present a short lease (< 80 years) as routine without a clear caveat

---

## 6. Never Provide Regulated Financial Advice

Do not:
- Recommend a specific mortgage product or lender
- Advise on whether to buy or sell from an investment perspective
- Provide advice that would require FCA authorisation
- Quote rental yields as a recommendation to invest
- Imply guaranteed capital appreciation

---

## 7. Never Scrape or Use Portal Data Without Permission

Do not:
- Attempt to access Rightmove, Zoopla, OnTheMarket, or any private property portal via scraping
- Use portal listing data that was not supplied directly by the user from a lawful export or
  permitted source
- Extract asking price data from portal page HTML or JSON

If a user supplies portal data they have lawfully exported, it may be used with appropriate caveats
(asking price, not sold price; subject to portal accuracy).

---

## 8. Pressure and Hype Language

Do not use the following in listing copy unless supported by specific, verifiable evidence:
- "Guaranteed" in any context
- "Best investment opportunity"
- "Perfect", "immaculate", "flawless" condition claims without a survey
- "No issues", "nothing to do", "move-in ready" without full confirmation from a survey
- "Planning potential" without a planning reference or professional opinion
- "Outstanding schools" without a current Ofsted link or LA source
- "Flood-free", "no flood risk" without a current search or EA reference
- "Won't last", "unique opportunity", "rarely available" without factual basis
- Any claim implying pressure on a buyer to act quickly without genuine factual basis

---

## Summary: If in Doubt

If uncertain whether a claim should be included:
- State it is unknown
- State what verification is needed
- Include a human review note
- Do not include it as a confirmed fact
