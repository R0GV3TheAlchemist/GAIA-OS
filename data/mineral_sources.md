# Mineral Data Sources — GAIA-OS C118

## Primary Sources

### 1. RRUFF / IMA Database (Primary)
- **URL:** `https://rruff.info/ima/RRUFF_Export.csv`
- **Format:** CSV
- **Contents:** ~6,000+ IMA-approved mineral species with formula, crystal system, space group, cell parameters
- **License:** Open access (RRUFF Project, University of Arizona)
- **Citation:** Lafuente B, Downs R T, Yang H, Stone N (2015) The power of databases: the RRUFF project. In: Armbruster T, Danisi R M, eds. Highlights in Mineralogy. Berlin, Germany, W. De Gruyter, pp 1-30

### 2. IMA CNMNC Master List (Authoritative)
- **URL:** `https://cnmnc.units.it/` → "IMA-CNMNC Master List"
- **Format:** PDF / Excel (updated monthly)
- **Current Count (May 2025):** 6,145 valid minerals
- **Note:** Wikipedia mirror available at `https://en.wikipedia.org/wiki/List_of_minerals_recognized_by_the_International_Mineralogical_Association`

### 3. Mindat.org API
- **URL:** `https://api.mindat.org/`
- **Format:** JSON (requires free API key)
- **Contents:** 6,152+ minerals with locality, photos, physical properties
- **API Docs:** `https://api.mindat.org/schema/redoc/`

### 4. Mineralogy Database (webmineral.com)
- **URL:** `http://webmineral.com/MySQL/search.php`
- **Format:** Web-scrape
- **Contents:** Dana classification, crystal symmetry, optical properties

## Data Pipeline

All sources are ingested through `core/mineral_ingestion.py` which:
1. Downloads the RRUFF_Export.csv as the primary source
2. Normalizes column names
3. Outputs `data/ima_minerals_full.csv` (the canonical GAIA mineral register)
4. Feeds `core/mineral_queue.py` for alchemical processing

## Alchemical Processing Status

See `data/alchemical_progress.json` — generated at runtime. Tracks which of the ~6,000+ minerals have been processed through all 4 alchemical stages.

## Crystal Count (as of C118 ingestion)

| Source | Count | Status |
|--------|-------|--------|
| C118 hand-curated | 28 | COMPLETE — seeded |
| IMA/RRUFF full database | ~6,000+ | PIPELINE READY |
| Target (all IMA valid species) | 6,145+ | IN PROGRESS |
