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

**File format (standard PPD CSV):**
No header row in the standard annual/monthly download files. Columns:
1. Transaction unique identifier (GUID)
2. Price paid (£)
3. Date of transfer (YYYY-MM-DD)
4. Postcode
5. Property type: D=Detached, S=Semi-Detached, T=Terraced, F=Flat/Maisonette, O=Other
6. Old/New: Y=Newly built, N=Not newly built
7. Duration: F=Freehold, L=Leasehold, U=Unknown
8. PAON (Primary Addressable Object Name — typically house number or name)
9. SAON (Secondary Addressable Object Name — flat number, if applicable)
10. Street
11. Locality
12. Town/City
13. District
14. County
15. PPD category type: A=Standard price paid, B=Additional price paid
16. Record status (monthly files only): A=Addition, C=Change, D=Delete

**Data lag:** Typically 2–3 months from transaction completion to publication. Transactions registered
in December may not appear in the data until February or March.

**Data access:**
- Bulk downloads: hmlr/price-paid-data (gov.uk or data.gov.uk)
- Licence: Open Government Licence (OGL) — free to use, attribution required
- File sizes: Annual file ~4 GB; monthly update ~30–60 MB
- Plugin default: Use fixture `fixtures/price_paid_sample.csv` — do not download the full file during tests

**Script:** `scripts/summarise_price_paid.py` streams the file row-by-row. Do not load full HMLR files into memory.

---

## 2. EPC Data Service / Open Data Communities API

**What it covers:** Energy Performance Certificate (EPC) records for domestic properties in England
and Wales. Certificates are issued on sale, let, or new construction.

**What it does NOT cover:**
- Properties that have never been sold or rented since 2008 (no EPC required)
- Scotland (separate EPC register — Scottish EPC register)
- Properties exempt from EPC requirements (listed buildings, temporary buildings, places of worship,
  certain rural buildings)

**EPC certificate validity:** 10 years from issue date. An expired EPC is not valid for listing;
a new EPC must be commissioned.

**Key EPC data fields:**
- UPRN (Unique Property Reference Number)
- Property address and postcode
- Energy rating (band A–G) and score
- Potential rating and score
- Inspection date and lodgement date
- Certificate number (RRN — Recommendation Report Number)
- Property type, tenure, construction age
- Habitable rooms, floor area

**API access:**
- Open Data Communities API (opendatacommunities.org/docs/api)
- Authentication: email + API key (register free at epc.opendatacommunities.org)
- Endpoints: /api/v1/domestic/search, /api/v1/domestic/certificate/{certificate-number}
- Rate limits apply — check API documentation
- Plugin: `scripts/epc_lookup_stub.py` uses fixture mode by default; set env vars for live calls

---

## 3. HMLR Local Land Charges (LLC) API

**What it covers:** Local land charges registered against land and property in England. Since 2018,
local authorities have been migrating their LLC registers to the central HMLR LLC register.

**What it includes (examples):**
- Financial charges (local authority loans, improvement grants)
- Planning restrictions and conditions
- Listed building and conservation area designations
- Tree Preservation Orders
- Light obstruction notices
- Environmental health orders
- Road adoption status

**What it does NOT replace:**
- Full conveyancing searches (CON29 search covers matters not in the LLC register)
- Drainage and water searches
- Environmental searches
- Chancel repair search

**Important limitation:** The LLC register is not a substitute for a full conveyancing search pack.
The LLC search answers "what charges are registered against this property" — it does not answer all
the questions a buyer and their lender will need answered before exchange.

**API access:**
- HMLR integration service
- May require formal onboarding, client ID, and secret
- SOAP-based integration or REST depending on the service version
- Plugin: `scripts/local_land_charges_stub.py` uses fixture mode; live integration requires HMLR onboarding

---

## 4. User-Supplied Files

**Supported formats:**
- HMLR-compatible CSV (see PPD format above) for comparable price data
- JSON files matching the listing schema (see `fixtures/listing_valid.json`)
- EPC certificates or data exports in JSON

**User responsibility:** The user is responsible for ensuring any data file they supply is:
- Lawfully obtained
- Not derived from portal scraping without permission
- Not containing personal data that should not be shared

---

## 5. User-Supplied Context (CMA / ONS / Local Authority / Other)

The agent can work with:
- CMA (Comparable Market Analysis) data the agent provides directly
- ONS house price indices (published data — free to use)
- Local authority housing data (published OGL data)
- Any structured property data the user pastes or uploads

In all cases: label the source explicitly in the output, note the date of the data, and apply
appropriate staleness caveats.

---

## General Limitations

| Limitation | Detail |
|---|---|
| HMLR lag | 2–3 month lag from completion to publication; recent sales may not appear |
| EPC expiry | Certificates older than 10 years are invalid for listing purposes |
| LLC partial migration | Not all local authorities have migrated to the central register; search result may be incomplete |
| No asking prices in PPD | PPD contains only completed transactions; portal asking prices are not included |
| Large files | Full HMLR annual files are ~4 GB; stream with `summarise_price_paid.py`, do not load into memory |
| API credentials required for live | EPC and HMLR LLC APIs require registration; plugin defaults to fixture mode |
| OGL attribution | HMLR and EPC data are licensed under the Open Government Licence — attribution required in published output |
