# RankUno GBP Intelligence Engine

Benchmarks a client school's Google Business Profile (GBP) against the true
local competitors in its territory and writes a four-sheet executive workbook
in the layout of `Childtime_GBP_MultiBrand_Audit_Verified_Live.xlsx`.

## Run

```powershell
python run_pilot_audit.py              # live website program sync + validation
python run_pilot_audit.py --offline    # use the dataset's program lists only
python run_pilot_audit.py --dataset data/childtime_pilot_dataset.json --output out.xlsx
python -m pytest tests -q              # 46 tests, no network
```

If the output workbook is open in Excel the engine writes a timestamped copy
next to it instead of failing.

## Data flow

```
data/*.json  --> core.dataset (pydantic validation)
             --> core.adapters.website_adapter (optional live program sync)
             --> core.gap_engine      one SchoolAnalysis per school
             --> core.reporter        4 sheets, layout from core.report_spec
             --> core.validator       re-derives every number from the .xlsx
```

Every cell on every sheet is computed once in `core/gap_engine.py` from the
same normalised data, so the Executive Summary, Service Comparison Matrix,
Category Gap Matrix and Raw Profile Details cannot disagree. The validator
proves it after each run (and will flag any hand-edited workbook that drifts).

## Rules (single source of truth)

| Rule | Where |
| :-- | :-- |
| Raw service label -> canonical program | `core/taxonomy.py` (`SERVICE_SYNONYMS`) |
| Program display / priority order | `core/taxonomy.py` (`CORE_PROGRAMS`) |
| Sister-brand filter (11 LCG brands + aliases/domains) | `config.py` |
| Gap threshold (default 50 %) and reputation floor (4.0) | `config.py` |
| Half-up percentage rounding (2 of 3 = 67 %) | `core/normalizer.py` |
| Service tiers: CRITICAL / INTERNAL / MARKET / DEFEND / USP / MONITOR | `core/gap_engine.py` |
| Category tiers: CRITICAL GAP / CONSIDER / COVERED | `core/gap_engine.py` |
| Sheet names, headers, palette | `core/report_spec.py` |

Service tier logic (`T` = threshold):

| Website | GBP chip | Competitor adoption | Tier |
| :-- | :-- | :-- | :-- |
| YES | NO | >= T | CRITICAL SYNC GAP |
| YES | NO | < T | INTERNAL SYNC GAP |
| NO | NO | >= T | MARKET GAP |
| any | YES | >= T | DEFEND |
| any | YES | 0 | DIFFERENTIATOR (USP) |
| otherwise | | | MONITOR |

Executive Summary columns derive from the matrix: *Internal gaps* = rows with
website YES / GBP NO; *External gaps* = rows with GBP NO and adoption >= T;
*Missing categories* = CRITICAL GAP category rows. Sister brands appear only
in Raw Profile Details (grey, `SISTER BRAND (FILTERED)`) and are excluded
from every denominator.

## Dataset

`data/childtime_pilot_dataset.json` holds the verified pilot data (two
Childtime schools, 11 true competitors, 2 sister brands). Add schools by
appending to `schools`; the schema is enforced by `core/models.py`.

## Secrets

Bright Data credentials live only in `.env` (see `config.py`). The Bright Data
adapter (`core/adapters/bright_data_adapter.py`) is a standalone extractor and
is not wired into the pilot run; GBP ratings, categories and service chips in
the pilot come from the verified dataset.

## Client data from the Google Business Profile API

`--client-source gbp-api` replaces the dataset's client categories, service
chips, rating, review count, address, website and Maps URL with the official
API values. Website programs still come from the school website. Competitors
are not available through this API (it only returns locations you manage).

One-time setup (agency Google account that is an owner/manager of the profiles):

1. Google Cloud project -> submit the *Application for Basic API Access* form
   (quota shows 0 QPM until approved, 300 QPM once approved).
2. Enable **My Business Business Information API**, **My Business Account
   Management API** and **Google My Business API (v4)**; create an OAuth
   *Desktop app* client and download it as `client_secret.json`.
3. `pip install google-auth-oauthlib` then `python scripts/gbp_auth.py login`
   (stores a refresh token in `.gbp_token.json`, git-ignored).
4. `python scripts/gbp_auth.py accounts` and
   `python scripts/gbp_auth.py locations --account <id>` to find each school's
   numeric `gbp_account_id` / `gbp_location_id`; put them in the dataset JSON.
5. `python run_pilot_audit.py --client-source gbp-api`.

Mapping (`core/adapters/gbp_api_adapter.py`): `categories.primaryCategory.displayName`
-> primary category; `categories.additionalCategories[].displayName` -> additional
categories; `serviceItems[]` -> service chips (structured items resolved through the
categories' `serviceTypes[]`, free-form items via `label.displayName`); v4
`reviews.averageRating` / `totalReviewCount` -> rating and review count.
