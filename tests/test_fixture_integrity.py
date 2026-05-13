"""Tests for scripts/check_fixture_integrity.py."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "check_fixture_integrity.py"
FIXTURES = ROOT / "fixtures"


def run_integrity_check(fixtures_dir: str | None = None) -> tuple[int, dict]:
    args = [sys.executable, str(SCRIPT)]
    if fixtures_dir:
        args += ["--fixtures-dir", fixtures_dir]
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)
    return result.returncode, data


# ---------------------------------------------------------------------------
# Fixtures pass integrity check
# ---------------------------------------------------------------------------

def test_all_fixtures_pass():
    rc, data = run_integrity_check(str(FIXTURES))
    assert rc == 0, f"Fixture integrity failed: {data}"
    assert data["status"] == "ok"
    assert data["total_errors"] == 0


def test_all_fixture_json_files_are_checked():
    _, data = run_integrity_check(str(FIXTURES))
    json_fixture_names = [f.name for f in FIXTURES.iterdir() if f.suffix == ".json"]
    checked_files = list(data["results"].keys())
    for name in json_fixture_names:
        assert name in checked_files, f"{name} was not checked"


def test_fixture_csv_is_checked():
    _, data = run_integrity_check(str(FIXTURES))
    assert "price_paid_sample.csv" in data["results"]


def test_files_checked_count():
    _, data = run_integrity_check(str(FIXTURES))
    # Should check at least 5 files (3 JSON listing fixtures + EPC + LLC + CSV)
    assert data["files_checked"] >= 5


# ---------------------------------------------------------------------------
# Secret detection — inject a fake secret and expect failure
# ---------------------------------------------------------------------------

def test_fake_api_key_detected(tmp_path):
    bad_fixture = tmp_path / "bad_listing.json"
    bad_fixture.write_text(json.dumps({
        "address": "1 Test Street",
        "api_key": "sk-AbCdEfGhIjKlMnOpQrStUvWxYz1234567890",
    }))

    cmd = [sys.executable, str(SCRIPT), "--fixtures-dir", str(tmp_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["status"] == "error"
    assert data["total_errors"] > 0


def test_pem_key_detected(tmp_path):
    bad_fixture = tmp_path / "with_key.json"
    bad_fixture.write_text(json.dumps({
        "note": "-----BEGIN RSA PRIVATE KEY-----",
    }))

    cmd = [sys.executable, str(SCRIPT), "--fixtures-dir", str(tmp_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)

    assert result.returncode == 1
    assert data["total_errors"] > 0


def test_empty_directory_returns_zero_errors(tmp_path):
    cmd = [sys.executable, str(SCRIPT), "--fixtures-dir", str(tmp_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    data = json.loads(result.stdout)
    assert result.returncode == 0
    assert data["files_checked"] == 0


def test_missing_directory_exits_3():
    cmd = [sys.executable, str(SCRIPT), "--fixtures-dir", "/nonexistent/dir"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    assert result.returncode == 3


# ---------------------------------------------------------------------------
# Output schema
# ---------------------------------------------------------------------------

def test_output_schema():
    _, data = run_integrity_check(str(FIXTURES))
    assert "status" in data
    assert "files_checked" in data
    assert "total_errors" in data
    assert "results" in data
    assert isinstance(data["results"], dict)
