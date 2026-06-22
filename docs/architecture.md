# Architecture Overview

This repository implements the data preparation and transformation layer for California's 2026 energy architecture analysis.

## Data flow

1. Raw public data is ingested from Google Cloud Platform and BigQuery public datasets.
2. Local seed files and external CSVs provide reference and enrichment tables.
3. Python preprocessing standardizes raw records prior to dbt ingestion.
4. dbt builds staging models, cleansed transformation layers, and analytical marts.
5. Curated datasets are published to BigQuery for consumption by Looker Studio or other analytics tools.

## Components

- `src/` — Python ingestion and preprocessing modules.
- `models/` — dbt SQL models.
- `seeds/` — seed lookup data and reference tables.
- `data/` — local data storage paths for raw, external, and processed files.
- `.github/workflows/` — CI workflow for verifying dbt and Python build steps.
