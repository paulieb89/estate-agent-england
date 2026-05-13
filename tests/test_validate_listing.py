"""Tests for scripts/validate_listing.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "validate_listing.py"
FIXTURES = ROOT / "fixtures"


def run_validate(fixture_name: str, extra_args: list[str] | None = None) -> tuple[int, dict]:
    cmd = [sys.executable, str(SCRIPT), str(FIXTURES / fixture_name)] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)
    return result.returncode, data


# ---------------------------------------------------------------------------
# Valid listing — should pass with low risk
# ---------------------------------------------------------------------------

def test_valid_listing_returns_low_risk():
    rc, data = run_validate("listing_valid.json")
    assert rc == 0
    assert data["risk_level"] == "low"
    assert data["status"] == "ok"


def test_valid_listing_has_confirmed_facts():
    _, data = run_validate("listing_valid.json")
    confirmed = " ".join(data["confirmed_facts"]).lower()
    assert "freehold" in confirmed
    assert "epc" in confirmed or "d" in confirmed


def test_valid_listing_no_missing_material_info():
    _, data = run_validate("listing_valid.json")
    assert len(data["missing_information"]) == 0


def test_valid_listing_output_is_valid_schema():
    _, data = run_validate("listing_valid.json")
    required_keys = [
        "status", "summary", "risk_level", "confirmed_facts",
        "missing_information", "unsupported_claims", "risky_phrases",
        "seller_questions", "human_review_required",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Missing material info fixture — must flag tenure, EPC, council tax
# ---------------------------------------------------------------------------

def test_missing_tenure_flagged():
    _, data = run_validate("listing_missing_material_info.json")
    missing_text = " ".join(data["missing_information"]).lower()
    assert "tenure" in missing_text


def test_missing_epc_flagged():
    _, data = run_validate("listing_missing_material_info.json")
    missing_text = " ".join(data["missing_information"]).lower()
    assert "epc" in missing_text


def test_missing_council_tax_flagged():
    _, data = run_validate("listing_missing_material_info.json")
    missing_text = " ".join(data["missing_information"]).lower()
    assert "council tax" in missing_text


def test_missing_material_info_returns_medium_or_higher():
    rc, data = run_validate("listing_missing_material_info.json")
    assert data["risk_level"] in ("medium", "high")
    assert rc in (1, 2)


def test_flat_without_tenure_generates_leasehold_questions():
    _, data = run_validate("listing_missing_material_info.json")
    # Flat without tenure should trigger leasehold missing-info checks
    missing_text = " ".join(data["missing_information"]).lower()
    # Should mention at least one leasehold-related field
    leasehold_terms = ["lease", "ground rent", "service charge"]
    assert any(t in missing_text for t in leasehold_terms)


# ---------------------------------------------------------------------------
# Risky claims fixture — must detect forbidden phrases
# ---------------------------------------------------------------------------

def test_risky_phrases_detected():
    _, data = run_validate("listing_risky_claims.json")
    assert len(data["risky_phrases"]) > 0


def test_planning_potential_flagged():
    _, data = run_validate("listing_risky_claims.json")
    phrases_text = " ".join(data["risky_phrases"]).lower()
    assert "planning" in phrases_text


def test_flood_free_claim_flagged():
    _, data = run_validate("listing_risky_claims.json")
    phrases_text = " ".join(data["risky_phrases"]).lower()
    assert "flood" in phrases_text


def test_guarantee_claim_flagged():
    _, data = run_validate("listing_risky_claims.json")
    phrases_text = " ".join(data["risky_phrases"]).lower()
    assert "guarantee" in phrases_text


def test_risky_claims_returns_high_risk():
    rc, data = run_validate("listing_risky_claims.json")
    assert data["risk_level"] == "high"
    assert rc == 2


def test_risky_claims_sets_human_review_required():
    _, data = run_validate("listing_risky_claims.json")
    assert data["human_review_required"] is True


# ---------------------------------------------------------------------------
# Output is always JSON-parseable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fixture", [
    "listing_valid.json",
    "listing_missing_material_info.json",
    "listing_risky_claims.json",
])
def test_output_is_json_parseable(fixture):
    _, data = run_validate(fixture)
    assert isinstance(data, dict)
    assert "status" in data
    assert "risk_level" in data


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_missing_file_exits_3():
    cmd = [sys.executable, str(SCRIPT), str(FIXTURES / "nonexistent.json")]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 3


def test_invalid_json_exits_3(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json {{{")
    cmd = [sys.executable, str(SCRIPT), str(bad_file)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 3
