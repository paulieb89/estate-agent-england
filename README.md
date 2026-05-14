# estate-agent-england

A Claude Code plugin for UK residential estate agents operating in England. Provides compliance-aware
property listing review, listing drafting, comparable evidence summaries, and seller onboarding
checklists. Evidence-bound. Never legal advice.

---

## What this plugin does

- **Reviews draft listings** for missing material information, risky claims, misleading language, and
  regulatory red flags (DMCCA, Estate Agents Act 1979, TPO Code)
- **Drafts professional listing copy** from seller notes, separating confirmed facts from assumptions
- **Summarises HMLR Price Paid comparable evidence** from CSV files, with statistics and limitations
- **Generates seller onboarding checklists** tailored to freehold/leasehold and property type
- **Drafts buyer enquiry responses** using only confirmed facts
- **Compliance review agent** provides a second-opinion check on all outputs before finalising

## What this plugin does NOT do

- Provide legal advice or make legal determinations
- Guarantee a listing is compliant
- Make AML/KYC decisions
- Scrape Rightmove, Zoopla, or any private portal
- Provide regulated financial advice or investment recommendations
- Fabricate EPC ratings, tenure, lease length, structural condition, or any property fact
- Replace a conveyancer, surveyor, or solicitor

---

## Installation

### Local testing (development)

```bash
claude --plugin-dir ./estate-agent-england
```

### Marketplace install (when published)

```
/plugin install estate-agent-england
```

---

## Skills

All skills are namespaced as `/estate-agent-england:<skill-name>`.

| Skill | Usage |
|---|---|
| `property-listing-review` | Review a draft listing for compliance and material information |
| `property-listing-draft` | Draft a listing from seller notes |
| `market-comparable-summary` | Summarise HMLR Price Paid comparable evidence |
| `seller-onboarding-checklist` | Generate a seller information request checklist |
| `buyer-enquiry-response` | Draft a buyer-facing reply to a property enquiry |

Skills trigger automatically when the context matches — or invoke them explicitly:

```
/estate-agent-england:property-listing-review
/estate-agent-england:seller-onboarding-checklist
```

### Example invocations

```
# Review a listing
"Review this listing draft for compliance: [paste listing copy]"

# Review a listing JSON file
uv run scripts/validate_listing.py fixtures/listing_valid.json --pretty

# Draft a listing
"Draft a property listing from these seller notes: [paste notes]"

# Summarise comparables — postcode workflow (live MCP data)
"Summarise sold comparables for 3-bed terraced houses in SW9 8NN"

# Summarise comparables — CSV fallback (offline / user-supplied file)
uv run scripts/summarise_price_paid.py --file fixtures/price_paid_sample.csv --outcode SW9 --property-type T --pretty

# Generate seller checklist
"Create a seller onboarding checklist for [address], [property type], [tenure]"

# Draft buyer reply
"Draft a reply to a buyer asking about the flood risk at [address]"
```

---

## Agent

The `uk-property-compliance-reviewer` agent is automatically invoked by skills before finalising
compliance-sensitive outputs. It can also be invoked manually:

```
/agents → uk-property-compliance-reviewer
```

---

## Runtime

The plugin uses the hosted **property-shared** MCP server by default — no credentials required:

```json
// .mcp.json
{ "mcpServers": { "property-shared": { "type": "http", "url": "https://property-shared.fly.dev/mcp" } } }
```

The hosted server provides:
- HMLR Price Paid comparable data (`property_comps`, `ppd_transactions`)
- EPC register lookups (`property_epc`)
- Rightmove listing data (`rightmove_search`, `rightmove_listing`)
- Rental and yield analysis (`rental_analysis`, `property_yield`)

Local validation scripts remain available for offline work and CSV fallback.
The local FastMCP server was removed in v0.1.1 — the `mcp/` directory no longer exists.

---

## Data source limitations

| Source | Limitation |
|---|---|
| HMLR Price Paid Data | 2–3 month lag; completed transactions only; no STC/asking prices |
| EPC data | 10-year certificate validity; no EPC for buildings never sold/let since 2008 |
| HMLR Local Land Charges | Not all LAs migrated yet; not a substitute for full conveyancing search |

Full details in `references/data-sources.md`.

---

## Compliance disclaimer

This plugin is a tool to assist estate agents. It is not legal advice, a regulatory compliance
audit, or a substitute for professional review. All plugin outputs must be reviewed by the
responsible agent (and where legal, structural, or financial matters arise, by a qualified
professional) before use in marketing or transactions.

Material information requirements in England are evolving. The NTS Part A/B/C guidance has been
withdrawn following DMCCA 2024. MHCLG is consulting on replacement statutory guidance. The
`references/england-estate-agent-compliance.md` reference file should be updated as the law evolves.

---

## Development

### Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) for dependency management

### Setup

```bash
cd estate-agent-england
uv sync --extra dev --no-install-project
```

### Run tests

```bash
uv run pytest
```

### Lint

```bash
uv run ruff check .
```

### Run a script

```bash
uv run scripts/validate_listing.py fixtures/listing_valid.json --pretty
uv run scripts/summarise_price_paid.py --file fixtures/price_paid_sample.csv --outcode SW9 --pretty
uv run scripts/check_fixture_integrity.py
uv run scripts/epc_lookup_stub.py --postcode SE24 0JN --pretty
uv run scripts/local_land_charges_stub.py --postcode SW9 8NN --pretty
```

---

## Repository structure

```
estate-agent-england/
  .claude-plugin/
    plugin.json              # Plugin manifest
    marketplace.json         # Marketplace catalog entry
  skills/
    property-listing-review/SKILL.md
    property-listing-draft/SKILL.md
    market-comparable-summary/SKILL.md
    seller-onboarding-checklist/SKILL.md
    buyer-enquiry-response/SKILL.md
  agents/
    uk-property-compliance-reviewer.md
  references/
    england-estate-agent-compliance.md
    material-information-checklist.md
    data-sources.md
    output-templates.md
    red-lines.md
    property-shared-tools.json
  scripts/
    validate_listing.py
    summarise_price_paid.py
    check_fixture_integrity.py
    epc_lookup_stub.py
    local_land_charges_stub.py
  tests/
    test_validate_listing.py
    test_summarise_price_paid.py
    test_fixture_integrity.py
    test_format_integrity.py
  fixtures/
    listing_valid.json
    listing_missing_material_info.json
    listing_risky_claims.json
    price_paid_sample.csv
    epc_sample.json
    local_land_charges_sample.json
  evals/
    listing_review_cases.jsonl
    comparable_summary_cases.jsonl
    seller_checklist_cases.jsonl
  README.md
  pyproject.toml
  .mcp.json
  .gitignore
  .env.example
```

---

## Known limitations (v0.1)

- Scotland-specific estate agency workflow not included (separate legal regime)
- Wales-specific variants not included (HMLR/EPC data covers England and Wales but compliance differs)
- Lettings compliance not implemented as a full workflow
- Conveyancing automation is out of scope
- Client money handling is out of scope
- Automated AML/KYC decisions are explicitly excluded
- Material information guidance is in transition (post-NTS withdrawal); keep references updated

## Next recommended improvements

1. Add `references/leasehold-detail.md` with detailed ground rent reform guidance
2. Add `scripts/epc_batch_lookup.py` for multi-property EPC pulls
3. Integrate HMLR PPD streaming with live API once available
4. Add `scripts/generate_seller_checklist.py` for structured JSON output
5. Expand evals with more leasehold flat scenarios and building safety cases
6. Add a `lettings-compliance` skill for letting agent workflow
