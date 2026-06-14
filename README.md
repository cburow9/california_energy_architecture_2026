# California Energy Architecture 2026

This repository contains the preprocessing and dbt business logic for a public data science project focused on California's energy architecture in 2026. It is designed to source data from Google Cloud Platform and BigQuery, transform and cleanse it with dbt, and expose curated datasets for Looker Studio and analytics.

## Project scope

- Ingest public and seeded data from Google Cloud, local CSVs, and blogs.
- Clean, normalize, and standardize datasets in Python preprocessing code.
- Build dbt models for staging, transformation, and analytical marts.
- Provide reusable data assets for a separate LookML/dashboard repository.

## Repository structure

- `src/` — Python ingestion, transformation, and configuration code.
- `models/` — dbt models, staging logic, and mart tables.
- `seeds/` — example seed datasets for reference and initial lookup tables.
- `data/` — raw, external, and processed data storage paths.
- `docs/` — architecture notes, data dictionary, and project conventions.
- `notebooks/` — exploratory analysis and notebook examples.
- `.github/workflows/` — CI workflow for dbt and testing.

## Quick start

1. Create a Python virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install .
   ```
2. Copy the dbt profile example and update it:
   ```bash
   cp profiles.yml.example ~/.dbt/profiles.yml
   ```
3. Configure your GCP credentials and BigQuery dataset in `~/.dbt/profiles.yml`.
4. Run dbt dependencies and models:
   ```bash
   python -m dbt deps
   python -m dbt seed
   python -m dbt run
   python -m dbt test
   ```

## Notes

- LookML and dashboard code are intentionally stored in a separate repository.
- Secrets and service account keys should never be committed; use environment variables or secret managers.
