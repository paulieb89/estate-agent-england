"""Tests for scripts/summarise_price_paid.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "summarise_price_paid.py"
FIXTURES = ROOT / "fixtures"
SAMPLE_CSV = str(FIXTURES / "price_paid_sample.csv")


def run_summarise(args: list[str]) -> tuple[int, dict]:
    cmd = [sys.executable, str(SCRIPT)] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)
    return result.returncode, data


# ---------------------------------------------------------------------------
# Basic functionality with fixture CSV
# ---------------------------------------------------------------------------

def test_summarise_returns_ok_status():
    rc, data = run_summarise(["--file", SAMPLE_CSV])
    assert rc == 0
    assert data["status"] == "ok"


def test_summarise_sample_size():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    # Fixture has 20 rows
    assert data["sample_size"] == 20


def test_summarise_has_median():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    assert data["median_price"] is not None
    assert isinstance(data["median_price"], int)
    assert data["median_price"] > 0


def test_summarise_has_quartiles():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    assert data["p25"] is not None
    assert data["p75"] is not None
    assert data["p25"] <= data["median_price"] <= data["p75"]


def test_summarise_date_range():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    assert data["date_range_from"] is not None
    assert data["date_range_to"] is not None
    assert data["date_range_from"] <= data["date_range_to"]


def test_summarise_recent_transactions():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    assert len(data["recent_transactions"]) > 0
    for tx in data["recent_transactions"]:
        assert "address" in tx
        assert "price" in tx
        assert "date" in tx


def test_summarise_has_caveat():
    _, data = run_summarise(["--file", SAMPLE_CSV])
    assert "caveat" in data
    assert len(data["caveat"]) > 20


# ---------------------------------------------------------------------------
# Filtering by outcode
# ---------------------------------------------------------------------------

def test_filter_by_outcode_sw9():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--outcode", "SW9"])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0
    assert data["sample_size"] < 20  # Should filter out SE24 rows


def test_filter_by_outcode_se24():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--outcode", "SE24"])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0


def test_filter_by_property_type_terraced():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--property-type", "T"])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0


def test_filter_by_property_type_flat():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--property-type", "F"])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0


def test_filter_by_freehold():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--duration", "F"])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0


def test_filter_by_date_range():
    _, data = run_summarise([
        "--file", SAMPLE_CSV,
        "--from-date", "2024-01-01",
        "--to-date", "2024-12-31",
    ])
    assert data["status"] == "ok"
    assert data["sample_size"] > 0
    # All transactions should be within the date range
    for tx in data["recent_transactions"]:
        assert tx["date"] >= "2024-01-01"
        assert tx["date"] <= "2024-12-31"


def test_no_matching_results_returns_no_results():
    _, data = run_summarise(["--file", SAMPLE_CSV, "--outcode", "W1A"])
    assert data["status"] == "no_results"
    assert data["sample_size"] == 0


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_missing_file_exits_nonzero():
    cmd = [sys.executable, str(SCRIPT), "--file", "/nonexistent/path/data.csv"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 3


def test_invalid_from_date_exits_3():
    cmd = [sys.executable, str(SCRIPT), "--file", SAMPLE_CSV, "--from-date", "not-a-date"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 3


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("extra_args", [
    [],
    ["--outcode", "SW9"],
    ["--property-type", "T"],
])
def test_output_schema_complete(extra_args):
    _, data = run_summarise(["--file", SAMPLE_CSV] + extra_args)
    required_keys = [
        "status", "sample_size", "median_price", "mean_price",
        "min_price", "max_price", "date_range_from", "date_range_to",
        "recent_transactions", "limitations", "caveat", "filters_applied",
    ]
    for key in required_keys:
        assert key in data, f"Missing key: {key}"
