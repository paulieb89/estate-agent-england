"""Estate Agent Data MCP Server — FastMCP v3.

Exposes four tools:
  - validate_listing       — compliance check on a listing dict
  - summarise_price_paid   — HMLR PPD statistics from a CSV file
  - epc_lookup             — EPC certificate lookup (fixture by default)
  - local_land_charges_lookup_stub — LLC lookup (fixture only)

Defaults to fixture mode. Set ESTATE_AGENT_PLUGIN_MODE=live and supply
EPC_API_EMAIL + EPC_API_KEY for live EPC lookups.

Run:
    uv run python mcp/estate_agent_data_server.py
"""
from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

from fastmcp import Context, FastMCP

# Resolve plugin root — supports both direct execution and MCP server invocation
PLUGIN_ROOT = Path(
    os.environ.get("ESTATE_AGENT_PLUGIN_ROOT", Path(__file__).parent.parent)
)

# Ensure scripts are importable
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from epc_lookup_stub import fixture_lookup as epc_fixture  # noqa: E402
from epc_lookup_stub import live_lookup as epc_live  # noqa: E402
from local_land_charges_stub import fixture_lookup as llc_fixture  # noqa: E402
from summarise_price_paid import summarise  # noqa: E402
from validate_listing import ListingInput, validate  # noqa: E402

mcp = FastMCP(
    "estate-agent-data",
    instructions=(
        "Provides estate agency data tools for England residential property. "
        "All tools default to fixture mode. Supply ESTATE_AGENT_PLUGIN_MODE=live "
        "and API credentials for live EPC lookups. "
        "IMPORTANT: Outputs are not legal advice and do not constitute compliance sign-offs. "
        "Human review is required before using any output for property marketing or transactions."
    ),
)

_MODE = os.environ.get("ESTATE_AGENT_PLUGIN_MODE", "fixture")


# ---------------------------------------------------------------------------
# Tool: validate_listing
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Validate a property listing for compliance risks, missing material information, "
        "and risky claims. "
        "Input: a dict of listing fields (address, tenure, epc_rating, etc.). "
        "Output: structured JSON with status, risk_level (low/medium/high), confirmed_facts, "
        "missing_information, unsupported_claims, risky_phrases, seller_questions, "
        "and human_review_required flag. "
        "Does not make legal determinations. Human review always required."
    )
)
async def validate_listing(listing: dict, ctx: Context) -> dict:
    """Validate a property listing dict for compliance risks."""
    try:
        listing_obj = ListingInput.model_validate(listing)
        report = validate(listing_obj)
        return report.model_dump()
    except Exception as exc:
        return {
            "status": "error",
            "summary": f"Validation error: {exc}",
            "risk_level": "high",
            "confirmed_facts": [],
            "missing_information": [],
            "unsupported_claims": [],
            "risky_phrases": [],
            "seller_questions": [],
            "human_review_required": True,
        }


# ---------------------------------------------------------------------------
# Tool: summarise_price_paid
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Summarise HMLR Price Paid Data statistics from a CSV file. "
        "Input: file_path (str, required), optional filters: outcode (str, e.g. 'SW9'), "
        "property_type (D/S/T/F/O), duration (F/L/U), from_date (YYYY-MM-DD), "
        "to_date (YYYY-MM-DD), min_price (int), max_price (int). "
        "Output: sample_size, median_price, mean_price, min/max, p25/p75, date_range, "
        "recent_transactions (up to 10), limitations, caveat. "
        "Streams the file — safe for large HMLR datasets. "
        "Returns only completed/registered sold prices, not asking prices."
    )
)
async def summarise_price_paid(
    file_path: str,
    ctx: Context,
    outcode: str | None = None,
    property_type: str | None = None,
    duration: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
) -> dict:
    """Summarise HMLR Price Paid CSV data with optional filters."""
    path = Path(file_path)
    if not path.is_absolute():
        path = PLUGIN_ROOT / file_path

    if not path.exists():
        return {
            "status": "error",
            "message": f"File not found: {file_path}",
            "sample_size": 0,
        }

    from_date_obj = date.fromisoformat(from_date) if from_date else None
    to_date_obj = date.fromisoformat(to_date) if to_date else None

    try:
        report = summarise(
            file_path=path,
            outcode=outcode,
            property_type=property_type,
            duration=duration,
            from_date=from_date_obj,
            to_date=to_date_obj,
            min_price=min_price,
            max_price=max_price,
        )
        return report.model_dump()
    except Exception as exc:
        return {"status": "error", "message": f"Summariser error: {exc}", "sample_size": 0}


# ---------------------------------------------------------------------------
# Tool: epc_lookup
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Look up EPC (Energy Performance Certificate) records by postcode and optional address. "
        "Returns energy rating (band A–G), efficiency scores, lodgement date, certificate number, "
        "property type, floor area, and tenure from the EPC register. "
        "Defaults to fixture mode — set ESTATE_AGENT_PLUGIN_MODE=live with EPC_API_EMAIL and "
        "EPC_API_KEY environment variables for live lookups. "
        "Note: certificates are valid for 10 years from issue date. An expired EPC is not valid "
        "for listing. Does not cover Scotland (separate register)."
    )
)
async def epc_lookup(
    postcode: str,
    ctx: Context,
    address: str | None = None,
) -> dict:
    """Look up EPC records for a postcode."""
    result = epc_live(postcode, address) if _MODE == "live" else epc_fixture(postcode, address)
    return result.model_dump()


# ---------------------------------------------------------------------------
# Tool: local_land_charges_lookup_stub
# ---------------------------------------------------------------------------

@mcp.tool(
    description=(
        "Look up Local Land Charges (LLC) registered against a property, by postcode or UPRN. "
        "Returns charge types (e.g. planning restrictions, TPOs, financial charges, designations). "
        "FIXTURE MODE ONLY — live HMLR LLC integration requires formal HMLR onboarding and "
        "OAuth2 credentials. "
        "IMPORTANT: An LLC search does not replace a full conveyancing search. "
        "CON29 and other searches are needed for a complete picture. "
        "Not all local authorities have migrated to the central HMLR LLC register."
    )
)
async def local_land_charges_lookup_stub(
    ctx: Context,
    postcode: str | None = None,
    uprn: str | None = None,
) -> dict:
    """Look up LLC fixture data for a postcode or UPRN."""
    if not postcode and not uprn:
        return {
            "status": "error",
            "message": "Provide either postcode or uprn",
            "charges": [],
        }
    result = llc_fixture(postcode=postcode, uprn=uprn)
    return result.model_dump()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
