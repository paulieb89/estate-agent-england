#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.0"]
# ///
"""Validate a property listing JSON file for compliance risks.

Usage:
    uv run scripts/validate_listing.py fixtures/listing_valid.json
    uv run scripts/validate_listing.py --help

Exit codes:
    0 — no issues (risk_level: low)
    1 — warnings found (risk_level: medium)
    2 — high-risk issues found (risk_level: high)
    3 — script/input error
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Input model
# ---------------------------------------------------------------------------

class ListingInput(BaseModel):
    address: str | None = None
    full_address: str | None = None
    postcode: str | None = None
    price: int | None = None
    guide_price: str | None = None
    property_type: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    tenure: str | None = None
    lease_remaining_years: int | None = None
    ground_rent: str | None = None
    service_charge: str | None = None
    epc_rating: str | None = None
    epc_band: str | None = None
    council_tax_band: str | None = None
    description: str | None = None
    features: list[str] = Field(default_factory=list)
    parking: str | None = None
    utilities: dict | None = None
    source_evidence: list[str] = Field(default_factory=list)
    known_restrictions: list[str] = Field(default_factory=list)
    additional_notes: str | None = None


# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------

class ValidationReport(BaseModel):
    status: Literal["ok", "warning", "error"]
    summary: str
    risk_level: Literal["low", "medium", "high"]
    confirmed_facts: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    risky_phrases: list[str] = Field(default_factory=list)
    seller_questions: list[str] = Field(default_factory=list)
    human_review_required: bool


# ---------------------------------------------------------------------------
# Risky phrase patterns: (regex, label, risk_level)
# ---------------------------------------------------------------------------

RISKY_PATTERNS: list[tuple[str, str, str]] = [
    (r"\bguaranteed?\b", "Guarantee claim", "high"),
    (r"\bno\s+chain\s+guaranteed?\b", "Unverified no-chain guarantee", "high"),
    (r"\bguaranteed?\s+rental", "Guaranteed rental income claim", "high"),
    (r"\bbest\s+investment\b", "Superlative investment claim", "high"),
    (r"\bperfect\s+investment\b", "Superlative investment claim", "high"),
    (r"\binvestment\s+opportunit", "Investment recommendation (requires authorisation)", "high"),
    (r"\bcapital\s+growth", "Capital growth projection", "high"),
    (r"\bplanning\s+potential\b", "Unverified planning potential claim", "high"),
    (r"\bplanning\s+permission\s+potential\b", "Unverified planning permission potential", "high"),
    (r"\bdevelopment\s+opportunit", "Unverified development opportunity claim", "high"),
    (r"\bstructurally\s+sound\b", "Unverified structural condition claim", "high"),
    (r"\bno\s+damp\b", "Unverified structural/damp claim", "high"),
    (r"\bno\s+issues?\b", "Absolute 'no issues' claim", "high"),
    (r"\bnothing\s+to\s+do\b", "Absolute condition claim", "high"),
    (r"\bno\s+flood\s+risk\b", "Unverified flood risk claim", "high"),
    (r"\bflood.free\b", "Unverified flood-free claim", "high"),
    (r"\bno\s+japanese\s+knotweed\b", "Unverified knotweed claim", "high"),
    (r"\bknotweed.free\b", "Unverified knotweed-free claim", "high"),
    (r"\boutstanding\s+school", "Unverified school quality claim", "medium"),
    (r"\bexcellent\s+school", "Unverified school quality claim", "medium"),
    (r"\btop.rated\s+school", "Unverified school quality claim", "medium"),
    (r"\bofsted\s+outstanding", "Unverified Ofsted rating claim", "medium"),
    (r"\bimmaculate\b", "Superlative condition claim (unverified)", "medium"),
    (r"\bperfect\s+condition\b", "Absolute condition claim", "medium"),
    (r"\bmove.in\s+ready\b", "Unverified condition claim", "medium"),
    (r"\bwon.t\s+last\b", "Pressure-selling language", "medium"),
    (r"\brare\s+opportunit", "Pressure-selling language", "medium"),
    (r"\bprice\s+to\s+sell\b", "Motivation disclosure — may mislead", "medium"),
    (r"\brental\s+yield\s+of\s+\d", "Specific yield claim — requires sourcing", "medium"),
    (r"\bno\s+problem\b", "Absolute 'no problem' claim", "medium"),
]


# ---------------------------------------------------------------------------
# Material information fields required
# ---------------------------------------------------------------------------

ALWAYS_REQUIRED = [
    ("tenure", "Tenure (freehold/leasehold/commonhold) not specified"),
    (("epc_rating", "epc_band"), "EPC rating or band not specified"),
    ("council_tax_band", "Council tax band not specified"),
    ("bedrooms", "Number of bedrooms not specified"),
    ("property_type", "Property type not specified"),
]

LEASEHOLD_REQUIRED = [
    ("lease_remaining_years", "Lease length remaining (years) not specified — required for leasehold"),
    ("ground_rent", "Ground rent amount not specified — required for leasehold"),
    ("service_charge", "Service charge not specified — required for leasehold"),
]

LEASEHOLD_KEYWORDS = {"leasehold", "lease", "flat", "apartment", "maisonette"}


def _is_likely_leasehold(listing: ListingInput) -> bool:
    if listing.tenure and "leasehold" in listing.tenure.lower():
        return True
    if listing.tenure and "freehold" in listing.tenure.lower():
        return False
    prop_type = (listing.property_type or "").lower()
    return any(k in prop_type for k in {"flat", "apartment", "maisonette"})


def _field_present(listing: ListingInput, field: str | tuple[str, ...]) -> bool:
    if isinstance(field, tuple):
        return any(_field_present(listing, f) for f in field)
    val = getattr(listing, field, None)
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    return True


# ---------------------------------------------------------------------------
# Main validation logic
# ---------------------------------------------------------------------------

def validate(listing: ListingInput) -> ValidationReport:
    confirmed: list[str] = []
    missing: list[str] = []
    unsupported: list[str] = []
    risky: list[str] = []
    questions: list[str] = []
    max_risk = "low"

    def elevate(level: str) -> None:
        nonlocal max_risk
        order = {"low": 0, "medium": 1, "high": 2}
        if order[level] > order[max_risk]:
            max_risk = level

    # Confirmed facts
    if listing.tenure:
        confirmed.append(f"Tenure: {listing.tenure}")
    if listing.epc_rating or listing.epc_band:
        confirmed.append(f"EPC: {listing.epc_rating or listing.epc_band}")
    if listing.council_tax_band:
        confirmed.append(f"Council tax band: {listing.council_tax_band}")
    if listing.bedrooms is not None:
        confirmed.append(f"Bedrooms: {listing.bedrooms}")
    if listing.property_type:
        confirmed.append(f"Property type: {listing.property_type}")
    if listing.price:
        confirmed.append(f"Price: £{listing.price:,}")
    if listing.parking:
        confirmed.append(f"Parking: {listing.parking}")

    # Missing material information checks
    for field, label in ALWAYS_REQUIRED:
        if not _field_present(listing, field):
            missing.append(label)
            elevate("medium")
            q = label.replace(" not specified", "")
            questions.append(f"Please confirm: {q}")

    if _is_likely_leasehold(listing):
        for field, label in LEASEHOLD_REQUIRED:
            if not _field_present(listing, field):
                missing.append(label)
                elevate("medium")
                questions.append(f"Please confirm: {label.replace(' not specified — required for leasehold', '')}")

        if listing.lease_remaining_years is not None and listing.lease_remaining_years < 80:
            unsupported.append(
                f"Short lease: {listing.lease_remaining_years} years remaining — may impact mortgageability; "
                "buyer and lender should be informed"
            )
            elevate("high")
            questions.append(
                "Lease is under 80 years — has a lease extension been considered or initiated?"
            )

    # Risky phrase detection in description and features
    text_to_check = " ".join(
        filter(None, [
            listing.description or "",
            " ".join(listing.features),
            listing.additional_notes or "",
        ])
    ).lower()

    for pattern, label, risk in RISKY_PATTERNS:
        if re.search(pattern, text_to_check, re.IGNORECASE):
            risky.append(f"{label} — pattern: '{pattern}'")
            elevate(risk)

    # Unsupported claim detection based on high-risk phrase presence and absence of source evidence
    high_risk_patterns = [p for p, _, r in RISKY_PATTERNS if r == "high"]
    has_high_risk_phrase = any(
        re.search(p, text_to_check, re.IGNORECASE) for p in high_risk_patterns
    )
    if has_high_risk_phrase and not listing.source_evidence:
        unsupported.append(
            "One or more high-risk claims present but no source evidence provided in 'source_evidence' field"
        )
        elevate("high")

    # Generate summary
    issues = len(missing) + len(risky) + len(unsupported)
    if max_risk == "high":
        status = "error"
        summary = (
            f"High-risk issues found: {issues} item(s) require attention before listing. "
            "Human review required."
        )
    elif max_risk == "medium" or issues > 0:
        status = "warning"
        summary = (
            f"{issues} item(s) flagged for review. Verify missing information with seller "
            "before publication."
        )
    else:
        status = "ok"
        summary = "No significant issues identified from the supplied material. Human review still required."

    human_review_required = max_risk in ("high", "medium") or bool(unsupported)

    return ValidationReport(
        status=status,
        summary=summary,
        risk_level=max_risk,
        confirmed_facts=confirmed,
        missing_information=missing,
        unsupported_claims=unsupported,
        risky_phrases=risky,
        seller_questions=questions,
        human_review_required=human_review_required,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate a property listing JSON file for compliance risks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("listing_file", help="Path to a JSON file containing listing fields")
    parser.add_argument(
        "--pretty", action="store_true", default=False,
        help="Pretty-print the JSON output",
    )
    args = parser.parse_args()

    path = Path(args.listing_file)
    if not path.exists():
        print(
            json.dumps({"error": f"File not found: {path}", "status": "error"}),
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        print(
            json.dumps({"error": f"Invalid JSON: {exc}", "status": "error"}),
            file=sys.stderr,
        )
        sys.exit(3)

    try:
        listing = ListingInput.model_validate(raw)
    except Exception as exc:
        print(
            json.dumps({"error": f"Schema error: {exc}", "status": "error"}),
            file=sys.stderr,
        )
        sys.exit(3)

    report = validate(listing)
    indent = 2 if args.pretty else None
    print(json.dumps(report.model_dump(), indent=indent))

    exit_codes = {"low": 0, "medium": 1, "high": 2}
    sys.exit(exit_codes[report.risk_level])


if __name__ == "__main__":
    main()
