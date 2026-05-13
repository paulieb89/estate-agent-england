#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Validate fixture files and check for accidentally committed secrets.

Usage:
    uv run scripts/check_fixture_integrity.py
    uv run scripts/check_fixture_integrity.py --fixtures-dir fixtures/
    uv run scripts/check_fixture_integrity.py --help

Exit codes:
    0 — all checks passed
    1 — one or more checks failed
    3 — script error
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Secret / credential detection patterns
# ---------------------------------------------------------------------------

SECRET_PATTERNS: list[tuple[str, str]] = [
    # Env-file / YAML style: api_key=value or api_key: value
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}", "Possible API key"),
    # JSON style: "api_key": "value"
    (r'(?i)"(?:api[_-]?key|apikey)"\s*:\s*"[A-Za-z0-9_\-]{16,}"', "Possible API key in JSON"),
    (r"(?i)password\s*[=:]\s*['\"]?[^\s'\"]{8,}", "Possible password"),
    (r'(?i)"password"\s*:\s*"[^\s"]{8,}"', "Possible password in JSON"),
    (r"(?i)secret\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{16,}", "Possible secret"),
    (r'(?i)"(?:secret|client[_-]?secret)"\s*:\s*"[A-Za-z0-9_\-]{16,}"', "Possible secret in JSON"),
    (r"(?i)token\s*[=:]\s*['\"]?[A-Za-z0-9_\-]{20,}", "Possible token"),
    (r'(?i)"token"\s*:\s*"[A-Za-z0-9_\-]{20,}"', "Possible token in JSON"),
    (r"(?i)private[_-]?key\s*[=:]\s*['\"]?[A-Za-z0-9+/]{20,}", "Possible private key"),
    (r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----", "PEM private key block"),
    # Real-looking email addresses (not example.com or placeholder domains)
    (
        r"[A-Za-z0-9._%+\-]+@(?!example\.com|test\.com|placeholder\.com|yourdomain\.com)[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        "Possible real email address",
    ),
]

# Fixture-specific safe values that are intentionally realistic-looking
SAFE_EMAIL_PATTERNS: list[str] = [
    r"estate-agent-england@example",
    r"@example\.com",
    r"@test\.com",
]


def looks_like_secret(text: str) -> list[tuple[str, str]]:
    """Return list of (pattern_label, matched_text) for suspicious content."""
    findings = []
    for pattern, label in SECRET_PATTERNS:
        for match in re.finditer(pattern, text):
            matched = match.group(0)
            # Skip safe patterns
            if any(re.search(safe, matched, re.IGNORECASE) for safe in SAFE_EMAIL_PATTERNS):
                continue
            findings.append((label, matched[:80]))
    return findings


# ---------------------------------------------------------------------------
# File validators
# ---------------------------------------------------------------------------

def check_json_file(path: Path) -> list[str]:
    errors = []
    try:
        content = path.read_text()
    except OSError as exc:
        return [f"Cannot read: {exc}"]

    if not content.strip():
        return ["File is empty"]

    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON: {exc}")
        return errors

    secrets = looks_like_secret(content)
    for label, snippet in secrets:
        errors.append(f"Possible secret ({label}): {snippet!r}")

    return errors


def check_csv_file(path: Path) -> list[str]:
    errors = []
    try:
        content = path.read_text()
    except OSError as exc:
        return [f"Cannot read: {exc}"]

    if not content.strip():
        return ["File is empty"]

    try:
        rows = list(csv.reader(content.splitlines()))
        if len(rows) < 2:
            errors.append("CSV has fewer than 2 rows (expected at least one data row)")
    except Exception as exc:
        errors.append(f"CSV parse error: {exc}")
        return errors

    secrets = looks_like_secret(content)
    for label, snippet in secrets:
        errors.append(f"Possible secret ({label}): {snippet!r}")

    return errors


VALIDATORS = {
    ".json": check_json_file,
    ".csv": check_csv_file,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate fixture files and check for accidentally committed secrets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--fixtures-dir",
        default="fixtures",
        help="Directory containing fixture files (default: fixtures/)",
    )
    args = parser.parse_args()

    fixtures_dir = Path(args.fixtures_dir)
    if not fixtures_dir.exists():
        print(
            json.dumps({"error": f"Fixtures directory not found: {fixtures_dir}", "status": "error"}),
            file=sys.stderr,
        )
        sys.exit(3)

    results: dict[str, list[str]] = {}
    total_errors = 0

    for path in sorted(fixtures_dir.iterdir()):
        if path.is_dir():
            continue
        suffix = path.suffix.lower()
        if suffix not in VALIDATORS:
            continue

        validator = VALIDATORS[suffix]
        errors = validator(path)
        results[path.name] = errors
        total_errors += len(errors)

    report = {
        "status": "ok" if total_errors == 0 else "error",
        "files_checked": len(results),
        "total_errors": total_errors,
        "results": results,
    }

    print(json.dumps(report, indent=2))
    sys.exit(0 if total_errors == 0 else 1)


if __name__ == "__main__":
    main()
