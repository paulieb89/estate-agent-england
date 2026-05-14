# Data Sources Reference

Supported data sources for the estate-agent-england plugin, with limitations and access notes.

---

## 1. HMLR Price Paid Data (PPD)

**What it covers:** Residential property transactions in England and Wales that are:
- Standard residential sales (Category A — the main dataset)
- Additional price paid data, e.g., repossessions and buy-to-lets (Category B — separate dataset)
- New builds and transfers of existing residential properties
- Lodged with HM Land Registry after the transaction completes

**What it does NOT cover:**
- Properties that have not yet completed or not yet been registered
- Properties under offer (STC — Sold Subject to Contract)
- Properties where the sale was not at arm's length (gifts, inheritances, transfers to connected parties)
- Transactions below £40,000 (threshold as of last update)
- Commercial, mixed-use, or agricultural property (different datasets)
- Scotland, Northern Ireland (separate land registries)

**Data lag:** Typically 2–3 months from transaction completion to publication. Transactions registered
in December may not appear in the data until February or March.

**Access via property-shared MCP tools (preferred):**
- `property_comps(postcode, property_type, months, enrich_epc)` — live stats + EPC-enriched
  transactions with price/sqm; defaults to sector-level search
- `ppd_transactions(postcode, property_type)` — raw recent transactions list
- No CSV download or credentials needed

**Access via bulk CSV (fallback for offline/batch analysis):**
- Bulk downloads: hmlr/price-paid-data (gov.uk or data.gov.uk)
- Licence: Open Government Licence (OGL) — free to use, attribution required
- File sizes: Annual file ~4 GB; monthly update ~30–60 MB
- `scripts/summarise_price_paid.py` streams the file row-by-row — do not load full files into memory
- Plugin fixture: `fixtures/price_paid_sample.csv`

**CSV file format (standard PPD, no header row):**
1. Transaction unique identifier (GUID)
2. Price paid (£)
3. Date of transfer (YYYY-MM-DD)
4. Postcode
5. Property type: D=Detached, S=Semi-Detached, T=Terraced, F=Flat/Maisonette, O=Other
6. Old/New: Y=Newly built, N=Not newly built
7. Duration: F=Freehold, L=Leasehold, U=Unknown
8. PAON, SAON, Street, Locality, Town/City, District, County
9. PPD category type: A=Standard, B=Additional
10. Record status (monthly files only): A=Addition, C=Change, D=Delete

---

## 2. EPC Data

**What it covers:** Energy Performance Certificate records for domestic properties in England and
Wales. Certificates are issued on sale, let, or new construction.

**What it does NOT cover:**
- Properties that have never been sold or rented since 2008 (no EPC required)
- Scotland (separate EPC register)
- Properties exempt from EPC requirements (listed buildings, temporary buildings, places of worship)

**EPC certificate validity:** 10 years from issue date. An expired EPC is not valid for listing;
a new EPC must be commissioned before the property can be marketed.

**Key EPC data fields:**
- UPRN, address and postcode
- Energy rating (band A–G) and score; potential rating and score
- Inspection date and lodgement date
- Certificate number (RRN — Recommendation Report Number)
- Property type, tenure, construction age
- Habitable rooms, floor area (m²)

**Access via property-shared MCP tool (preferred):**
- `property_epc(postcode, address)` — returns matched certificate for the specific property, or
  postcode-level summary (rating distribution, type breakdown, floor-area range) if no address given
- No credentials needed

**Access via scripts (offline dev reference only):**
- `scripts/epc_lookup_stub.py` — fixture mode by default; set `EPC_API_EMAIL` + `EPC_API_KEY`
  environment variables for live calls against the Open Data Communities API

---

## 3. Rightmove Listings

**What it covers:** Current sale and rental listings on Rightmove for England and Wales.

**What it does NOT cover:**
- Sold/exchanged/completed listings (use HMLR PPD for sold prices)
- Off-market properties
- Portal-exclusive or pre-launch listings

**Access via property-shared MCP tools:**
- `rightmove_search(postcode, listing_type, property_type, radius, min_bedrooms)` — current
  listings by postcode; listing_type: "sale" or "rent"
- `rightmove_listing(listing_id)` — full detail for one listing
- **Note:** Asking prices are not sold prices. Never blend Rightmove prices with HMLR PPD figures
  without explicit labelling.

---

## 4. Rental and Yield Data

**Access via property-shared MCP tools:**
- `rental_analysis(postcode, purchase_price)` — achievable rent estimate; auto-escalates on thin
  markets (fewer than 5 active listings)
- `property_yield(postcode, property_type)` — gross yield: combines HMLR median sale price with
  Rightmove median monthly rent
- **Note:** Gross yield only. Net yield depends on void periods, management fees, maintenance,
  and finance costs — not computed by these tools. Do not present gross yield as net yield.

---

## 5. HMLR Local Land Charges (LLC)

**What it covers:** Local land charges registered against land and property in England.

**Examples of registered charges:**
- Financial charges, planning restrictions, listed building designations
- Tree Preservation Orders, conservation area designations
- Environmental health orders, road adoption status

**Important limitation:** An LLC search is not a substitute for a full conveyancing search pack.
CON29 and other searches cover matters not held in the LLC register.

**API access:** Requires formal HMLR onboarding, client ID, and secret. Not all local authorities
have migrated to the central register.
- `scripts/local_land_charges_stub.py` — fixture mode only; kept for offline reference and dev
- No live LLC tool is available in this plugin

---

## 6. User-Supplied Files and Context

**Supported formats:**
- HMLR-compatible CSV for comparable price data (see PPD format above)
- JSON files matching the listing schema (see `fixtures/listing_valid.json`)
- CMA data, ONS house price indices, or local authority housing data

**User responsibility:** The user is responsible for ensuring any data file they supply is
lawfully obtained, not derived from portal scraping without permission, and not containing
personal data that should not be shared.

---

## General Limitations

| Limitation | Detail |
|---|---|
| HMLR lag | 2–3 month lag from completion to publication; recent sales may not appear |
| EPC expiry | Certificates older than 10 years are invalid for listing purposes |
| LLC partial migration | Not all local authorities have migrated to the central register |
| No asking prices in PPD | PPD contains only completed transactions; portal asking prices not included |
| Gross yield only | `property_yield` returns gross yield; net yield requires further calculation |
| Large CSV files | Full HMLR annual files ~4 GB; stream with `summarise_price_paid.py` |
| OGL attribution | HMLR and EPC data are licensed under the Open Government Licence — attribution required |
