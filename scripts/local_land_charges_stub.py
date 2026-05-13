#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.0"]
# ///
"""Local Land Charges (LLC) lookup — fixture mode only.

Live HMLR LLC integration requires formal onboarding with HM Land Registry and
client credentials. This stub returns fixture data and documents the integration
requirements for a production implementation.

Usage:
    uv run scripts/local_land_charges_stub.py --postcode "SW9 8NN"
    uv run scripts/local_land_charges_stub.py --uprn 100021888417
    uv run scripts/local_land_charges_stub.py --help

Exit codes:
    0 — result returned (may be empty charges list)
    1 — no results found in fixture
    3 — script/input error

Live integration notes:
    HMLR LLC API requires:
    - Formal onboarding at hmlr.gov.uk
    - Client ID and client secret (not a simple API key)
    - OAuth 2.0 token exchange
    - In some regions: SOAP client configuration
    - Not all local authorities have migrated to the central register yet
    - Do not substitute LLC results for a full conveyancing search pack (CON29)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------

class LandCharge(BaseModel):
    charge_type: str
    registration_date: str | None = None
    description: str | None = None
    originating_authority: str | None = None
    geometry: str | None = None


class LlcResult(BaseModel):
    status: str
    postcode: str | None
    uprn: str | None
    charges: list[LandCharge] = Field(default_factory=list)
    charge_count: int = 0
    source: str = "fixture"
    message: str | None = None
    caveat: str = (
        "This result is from fixture data and is illustrative only. "
        "A Local Land Charges search does not replace a full conveyancing search. "
        "CON29 searches and other conveyancing searches are required for a full picture. "
        "Not all local authorities have migrated to the central HMLR LLC register. "
        "Live LLC integration requires formal HMLR onboarding."
    )


# ---------------------------------------------------------------------------
# Fixture lookup
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


def fixture_lookup(postcode: str | None, uprn: str | None) -> LlcResult:
    fixture_path = FIXTURE_DIR / "local_land_charges_sample.json"
    if not fixture_path.exists():
        return LlcResult(
            status="not_found",
            postcode=postcode,
            uprn=uprn,
            message="Fixture file local_land_charges_sample.json not found.",
        )

    data = json.loads(fixture_path.read_text())

    # Try to match by postcode or UPRN
    entries: list[dict] = []
    if isinstance(data, list):
        entries = data
    elif isinstance(data, dict) and "results" in data:
        entries = data["results"]

    matched: list[dict] = []
    for entry in entries:
        if postcode and postcode.replace(" ", "").upper() == entry.get("postcode", "").replace(" ", "").upper():
            matched = entry.get("charges", [])
            break
        if uprn and str(uprn) == str(entry.get("uprn", "")):
            matched = entry.get("charges", [])
            break

    if not entries and isinstance(data, dict) and "charges" in data:
        matched = data["charges"]

    charges = [
        LandCharge(
            charge_type=c.get("charge_type", "Unknown"),
            registration_date=c.get("registration_date"),
            description=c.get("description"),
            originating_authority=c.get("originating_authority"),
        )
        for c in matched
    ]

    return LlcResult(
        status="ok" if charges else "no_charges",
        postcode=postcode,
        uprn=uprn,
        charges=charges,
        charge_count=len(charges),
        message=None if charges else "No local land charges found in fixture for this location.",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local Land Charges lookup — fixture mode only (live requires HMLR onboarding).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--postcode", help="UK postcode, e.g. SW9 8NN")
    group.add_argument("--uprn", help="Unique Property Reference Number (UPRN)")
    parser.add_argument(
        "--pretty", action="store_true", default=False,
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    result = fixture_lookup(
        postcode=args.postcode,
        uprn=args.uprn,
    )

    indent = 2 if args.pretty else None
    print(json.dumps(result.model_dump(), indent=indent))
    sys.exit(0 if result.status in ("ok", "no_charges") else 1)


if __name__ == "__main__":
    main()
