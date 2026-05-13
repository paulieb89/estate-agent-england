#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = ["pydantic>=2.0"]
# ///
"""Summarise HMLR Price Paid Data from a CSV/TXT file.

Streams rows — safe for large files. Does not load the full file into memory.

Usage:
    uv run scripts/summarise_price_paid.py --file fixtures/price_paid_sample.csv
    uv run scripts/summarise_price_paid.py --file data.csv --outcode SW9 --property-type T
    uv run scripts/summarise_price_paid.py --help

Exit codes:
    0 — summary produced
    1 — no matching records found
    3 — file/input error

HMLR Price Paid Data column order (no header row in standard files):
  0: transaction_id, 1: price, 2: date, 3: postcode, 4: property_type (D/S/T/F/O),
  5: old_new (Y/N), 6: duration (F/L/U), 7: paon, 8: saon, 9: street,
  10: locality, 11: town, 12: district, 13: county, 14: ppd_category, 15: record_status
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path
from statistics import mean, median, quantiles
from typing import Literal

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Output model
# ---------------------------------------------------------------------------

class ComparableSample(BaseModel):
    address: str
    date: str
    price: int
    property_type: str
    duration: str


class SummaryReport(BaseModel):
    status: Literal["ok", "no_results", "error"]
    filters_applied: dict = Field(default_factory=dict)
    sample_size: int
    median_price: int | None
    mean_price: int | None
    min_price: int | None
    max_price: int | None
    p25: int | None
    p75: int | None
    date_range_from: str | None
    date_range_to: str | None
    recent_transactions: list[ComparableSample] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    caveat: str = (
        "HMLR Price Paid Data records completed and lodged transactions only. "
        "Data lag is typically 2–3 months. Does not include unsold or STC properties. "
        "Licensed under the Open Government Licence (OGL). "
        "This summary is not a formal valuation."
    )


# ---------------------------------------------------------------------------
# Column indices for the standard HMLR PPD format
# ---------------------------------------------------------------------------

COL_TRANSACTION = 0
COL_PRICE = 1
COL_DATE = 2
COL_POSTCODE = 3
COL_PROPERTY_TYPE = 4
COL_OLD_NEW = 5
COL_DURATION = 6
COL_PAON = 7
COL_SAON = 8
COL_STREET = 9
COL_LOCALITY = 10
COL_TOWN = 11
COL_DISTRICT = 12
COL_COUNTY = 13
COL_PPD_CATEGORY = 14

PROPERTY_TYPE_LABELS = {
    "D": "Detached", "S": "Semi-Detached", "T": "Terraced",
    "F": "Flat/Maisonette", "O": "Other",
}
DURATION_LABELS = {"F": "Freehold", "L": "Leasehold", "U": "Unknown"}


# ---------------------------------------------------------------------------
# Streaming summariser
# ---------------------------------------------------------------------------

def summarise(
    file_path: Path,
    outcode: str | None = None,
    postcode_prefix: str | None = None,
    property_type: str | None = None,
    duration: str | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    max_samples: int = 10,
) -> SummaryReport:
    prices: list[int] = []
    dates: list[date] = []
    samples: list[ComparableSample] = []
    skipped_header = False

    filters: dict = {}
    if outcode:
        filters["outcode"] = outcode
    if postcode_prefix:
        filters["postcode_prefix"] = postcode_prefix
    if property_type:
        filters["property_type"] = property_type
    if duration:
        filters["duration"] = duration
    if from_date:
        filters["from_date"] = from_date.isoformat()
    if to_date:
        filters["to_date"] = to_date.isoformat()
    if min_price:
        filters["min_price"] = min_price
    if max_price:
        filters["max_price"] = max_price

    with file_path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        for row in reader:
            if not row:
                continue

            # Detect and skip header row (HMLR standard files have no header,
            # but user files may include one)
            if not skipped_header and not row[COL_PRICE].strip().lstrip("{\"'").isdigit():
                skipped_header = True
                continue

            if len(row) < 8:
                continue

            # Parse price
            try:
                price = int(row[COL_PRICE].strip().strip('"'))
            except ValueError:
                continue

            # Parse date
            try:
                tx_date = datetime.strptime(
                    row[COL_DATE].strip().strip('"')[:10], "%Y-%m-%d"
                ).date()
            except ValueError:
                continue

            postcode = row[COL_POSTCODE].strip().strip('"').upper()
            ptype = row[COL_PROPERTY_TYPE].strip().strip('"').upper()
            dur = row[COL_DURATION].strip().strip('"').upper()

            # Derive outcode from postcode (e.g. "SW9 8NN" -> "SW9")
            pc_parts = postcode.split()
            row_outcode = pc_parts[0] if pc_parts else ""

            # Apply filters
            if outcode and row_outcode.upper() != outcode.upper():
                continue
            if postcode_prefix and not postcode.upper().startswith(postcode_prefix.upper()):
                continue
            if property_type and ptype != property_type.upper():
                continue
            if duration and dur != duration.upper():
                continue
            if from_date and tx_date < from_date:
                continue
            if to_date and tx_date > to_date:
                continue
            if min_price and price < min_price:
                continue
            if max_price and price > max_price:
                continue

            prices.append(price)
            dates.append(tx_date)

            if len(samples) < max_samples:
                paon = row[COL_PAON].strip().strip('"')
                saon = row[COL_SAON].strip().strip('"')
                street = row[COL_STREET].strip().strip('"')
                town = row[COL_TOWN].strip().strip('"')
                addr_parts = [p for p in [saon, paon, street, town] if p]
                samples.append(
                    ComparableSample(
                        address=", ".join(addr_parts),
                        date=tx_date.isoformat(),
                        price=price,
                        property_type=PROPERTY_TYPE_LABELS.get(ptype, ptype),
                        duration=DURATION_LABELS.get(dur, dur),
                    )
                )

    # Replace sample list with the N most recent by date
    all_samples_with_dates = sorted(
        zip(dates[-len(samples):], samples, strict=False), key=lambda x: x[0], reverse=True
    )
    recent_samples = [s for _, s in all_samples_with_dates[:max_samples]]

    n = len(prices)
    if n == 0:
        return SummaryReport(
            status="no_results",
            filters_applied=filters,
            sample_size=0,
            median_price=None,
            mean_price=None,
            min_price=None,
            max_price=None,
            p25=None,
            p75=None,
            date_range_from=None,
            date_range_to=None,
            recent_transactions=[],
            limitations=["No records matched the supplied filters."],
        )

    sorted_prices = sorted(prices)
    p25_val, p75_val = None, None
    if n >= 2:
        qs = quantiles(sorted_prices, n=4)
        p25_val = int(qs[0])
        p75_val = int(qs[2])

    limitations: list[str] = []
    if n < 5:
        limitations.append(
            f"Small sample: only {n} matching transaction(s). Results may not be representative."
        )
    if dates:
        oldest = min(dates)
        newest = max(dates)
        months_old = (date.today() - oldest).days / 30
        if months_old > 18:
            limitations.append(
                f"Sample includes transactions up to {int(months_old)} months old. "
                "Data older than 18 months should be treated as indicative only."
            )
        # Warn about HMLR lag
        days_since_newest = (date.today() - newest).days
        if days_since_newest < 90:
            limitations.append(
                "Most recent transaction in sample is within 90 days. HMLR data typically lags "
                "completion by 2–3 months; very recent sales may not yet appear."
            )

    return SummaryReport(
        status="ok",
        filters_applied=filters,
        sample_size=n,
        median_price=int(median(prices)),
        mean_price=int(mean(prices)),
        min_price=min(prices),
        max_price=max(prices),
        p25=p25_val,
        p75=p75_val,
        date_range_from=min(dates).isoformat() if dates else None,
        date_range_to=max(dates).isoformat() if dates else None,
        recent_transactions=recent_samples,
        limitations=limitations,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarise HMLR Price Paid Data from a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--file", required=True, help="Path to HMLR PPD CSV/TXT file")
    parser.add_argument("--outcode", help="Filter by postcode outcode, e.g. SW9")
    parser.add_argument("--postcode-prefix", help="Filter by postcode prefix, e.g. SW9 8")
    parser.add_argument(
        "--property-type", choices=["D", "S", "T", "F", "O"],
        help="Filter by property type: D=Detached, S=Semi, T=Terraced, F=Flat, O=Other",
    )
    parser.add_argument(
        "--duration", choices=["F", "L", "U"],
        help="Filter by tenure: F=Freehold, L=Leasehold, U=Unknown",
    )
    parser.add_argument("--from-date", help="Include transactions from this date (YYYY-MM-DD)")
    parser.add_argument("--to-date", help="Include transactions up to this date (YYYY-MM-DD)")
    parser.add_argument("--min-price", type=int, help="Minimum price filter")
    parser.add_argument("--max-price", type=int, help="Maximum price filter")
    parser.add_argument(
        "--pretty", action="store_true", default=False,
        help="Pretty-print the JSON output",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(
            json.dumps({"error": f"File not found: {path}", "status": "error"}),
            file=sys.stderr,
        )
        sys.exit(3)

    from_date = None
    if args.from_date:
        try:
            from_date = date.fromisoformat(args.from_date)
        except ValueError:
            print(
                json.dumps({"error": "Invalid --from-date, use YYYY-MM-DD", "status": "error"}),
                file=sys.stderr,
            )
            sys.exit(3)

    to_date = None
    if args.to_date:
        try:
            to_date = date.fromisoformat(args.to_date)
        except ValueError:
            print(
                json.dumps({"error": "Invalid --to-date, use YYYY-MM-DD", "status": "error"}),
                file=sys.stderr,
            )
            sys.exit(3)

    report = summarise(
        file_path=path,
        outcode=args.outcode,
        postcode_prefix=args.postcode_prefix,
        property_type=args.property_type,
        duration=args.duration,
        from_date=from_date,
        to_date=to_date,
        min_price=args.min_price,
        max_price=args.max_price,
    )

    indent = 2 if args.pretty else None
    print(json.dumps(report.model_dump(), indent=indent))
    sys.exit(0 if report.status == "ok" else 1)


if __name__ == "__main__":
    main()
