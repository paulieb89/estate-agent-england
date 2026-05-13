#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.0", "httpx>=0.25"]
# ///
"""EPC certificate lookup — fixture mode by default, live mode with credentials.

Usage:
    uv run scripts/epc_lookup_stub.py --postcode SW9 8NN
    uv run scripts/epc_lookup_stub.py --address "14 Railton Road" --postcode SE24 0JN
    uv run scripts/epc_lookup_stub.py --postcode SW9 8NN --live   # requires EPC_API_EMAIL + EPC_API_KEY
    uv run scripts/epc_lookup_stub.py --help

Exit codes:
    0 — certificate found (or fixture returned)
    1 — no certificate found
    2 — authentication error (live mode only)
    3 — script/network error

Environment variables (live mode only):
    EPC_API_EMAIL   — email registered at epc.opendatacommunities.org
    EPC_API_KEY     — API key from epc.opendatacommunities.org
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------

class EpcRecord(BaseModel):
    address: str
    postcode: str
    current_energy_rating: str | None = None
    potential_energy_rating: str | None = None
    current_energy_efficiency: int | None = None
    potential_energy_efficiency: int | None = None
    lodgement_date: str | None = None
    inspection_date: str | None = None
    certificate_number: str | None = None
    tenure: str | None = None
    property_type: str | None = None
    total_floor_area: float | None = None
    source: str = "fixture"


class EpcLookupResult(BaseModel):
    status: str
    postcode: str
    address_query: str | None
    records: list[EpcRecord] = Field(default_factory=list)
    message: str | None = None
    caveat: str = (
        "EPC data sourced from Open Data Communities / DLUHC EPC register. "
        "Certificates are valid for 10 years from issue date. "
        "An expired certificate is not valid for listing purposes. "
        "In fixture mode, data is illustrative only."
    )


# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture() -> list[dict]:
    fixture_path = FIXTURE_DIR / "epc_sample.json"
    if fixture_path.exists():
        data = json.loads(fixture_path.read_text())
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "rows" in data:
            return data["rows"]
    return []


def fixture_lookup(postcode: str, address: str | None) -> EpcLookupResult:
    rows = load_fixture()
    postcode_clean = postcode.replace(" ", "").upper()

    matched = []
    for row in rows:
        row_pc = row.get("postcode", "").replace(" ", "").upper()
        if row_pc == postcode_clean:
            if address:
                row_addr = row.get("address", "").lower()
                if address.split()[0].lower() not in row_addr:
                    continue
            matched.append(EpcRecord(
                address=row.get("address", "Unknown"),
                postcode=row.get("postcode", postcode),
                current_energy_rating=row.get("current-energy-rating"),
                potential_energy_rating=row.get("potential-energy-rating"),
                current_energy_efficiency=row.get("current-energy-efficiency"),
                potential_energy_efficiency=row.get("potential-energy-efficiency"),
                lodgement_date=row.get("lodgement-date"),
                inspection_date=row.get("inspection-date"),
                certificate_number=row.get("lmk-key"),
                tenure=row.get("tenure"),
                property_type=row.get("property-type"),
                total_floor_area=row.get("total-floor-area"),
                source="fixture",
            ))

    if matched:
        return EpcLookupResult(
            status="ok",
            postcode=postcode,
            address_query=address,
            records=matched,
        )
    return EpcLookupResult(
        status="not_found",
        postcode=postcode,
        address_query=address,
        message="No EPC records found in fixture for this postcode/address.",
    )


# ---------------------------------------------------------------------------
# Live lookup (requires credentials)
# ---------------------------------------------------------------------------

def live_lookup(postcode: str, address: str | None) -> EpcLookupResult:
    try:
        import httpx  # noqa: PLC0415
    except ImportError:
        return EpcLookupResult(
            status="error",
            postcode=postcode,
            address_query=address,
            message="httpx not installed. Run: pip install httpx",
        )

    email = os.environ.get("EPC_API_EMAIL", "")
    key = os.environ.get("EPC_API_KEY", "")
    if not email or not key:
        return EpcLookupResult(
            status="auth_error",
            postcode=postcode,
            address_query=address,
            message="EPC_API_EMAIL and EPC_API_KEY environment variables are required for live mode.",
        )

    params: dict = {"postcode": postcode, "size": 10}
    if address:
        params["address"] = address

    try:
        response = httpx.get(
            "https://epc.opendatacommunities.org/api/v1/domestic/search",
            params=params,
            auth=(email, key),
            headers={"Accept": "application/json"},
            timeout=10.0,
        )
    except httpx.RequestError as exc:
        return EpcLookupResult(
            status="error",
            postcode=postcode,
            address_query=address,
            message=f"Network error: {exc}",
        )

    if response.status_code == 401:
        return EpcLookupResult(
            status="auth_error",
            postcode=postcode,
            address_query=address,
            message="Authentication failed — check EPC_API_EMAIL and EPC_API_KEY.",
        )
    if response.status_code != 200:
        return EpcLookupResult(
            status="error",
            postcode=postcode,
            address_query=address,
            message=f"API returned HTTP {response.status_code}",
        )

    data = response.json()
    rows = data.get("rows", [])
    records = [
        EpcRecord(
            address=r.get("address", ""),
            postcode=r.get("postcode", postcode),
            current_energy_rating=r.get("current-energy-rating"),
            potential_energy_rating=r.get("potential-energy-rating"),
            current_energy_efficiency=r.get("current-energy-efficiency"),
            potential_energy_efficiency=r.get("potential-energy-efficiency"),
            lodgement_date=r.get("lodgement-date"),
            inspection_date=r.get("inspection-date"),
            certificate_number=r.get("lmk-key"),
            tenure=r.get("tenure"),
            property_type=r.get("property-type"),
            total_floor_area=r.get("total-floor-area"),
            source="live",
        )
        for r in rows
    ]

    status = "ok" if records else "not_found"
    return EpcLookupResult(
        status=status,
        postcode=postcode,
        address_query=address,
        records=records,
        message=None if records else "No EPC records found for this postcode/address.",
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Look up EPC certificates by postcode (fixture mode by default).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--postcode", required=True, help="UK postcode, e.g. SW9 8NN")
    parser.add_argument("--address", help="Optional address prefix to narrow results")
    parser.add_argument(
        "--live", action="store_true", default=False,
        help="Use live EPC API (requires EPC_API_EMAIL + EPC_API_KEY env vars)",
    )
    parser.add_argument(
        "--pretty", action="store_true", default=False,
        help="Pretty-print JSON output",
    )
    args = parser.parse_args()

    mode = os.environ.get("ESTATE_AGENT_PLUGIN_MODE", "fixture")
    use_live = args.live or mode == "live"

    if use_live:
        result = live_lookup(args.postcode, args.address)
    else:
        result = fixture_lookup(args.postcode, args.address)

    indent = 2 if args.pretty else None
    print(json.dumps(result.model_dump(), indent=indent))

    if result.status == "ok":
        sys.exit(0)
    elif result.status == "not_found":
        sys.exit(1)
    elif result.status == "auth_error":
        sys.exit(2)
    else:
        sys.exit(3)


if __name__ == "__main__":
    main()
