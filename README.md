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
   python -m pip install .[dev]
   ```
2. Copy the dbt profile example and update it:
   ```bash
   cp profiles.yml.example ~/.dbt/profiles.yml
   ```
3. Configure your GCP credentials and BigQuery dataset in `~/.dbt/profiles.yml`.
4. Set up pre-commit hooks (optional but recommended):
   ```bash
   pre-commit install
   ```
5. Run dbt dependencies and models:
   ```bash
   python -m dbt deps
   python -m dbt seed
   python -m dbt run
   python -m dbt test
   ```

## Development & Code Quality

### Python Testing
Run unit tests with coverage reporting:
```bash
pytest tests/ -v --cov=src --cov-report=html
```

### SQL Linting
Lint SQL files with sqlfluff:
```bash
sqlfluff lint models/ --dialect bigquery
sqlfluff fix models/ --dialect bigquery  # Auto-fix issues
```

### Code Formatting
Format Python code with Black and isort:
```bash
black src/ tests/
isort src/ tests/
```

### Pre-commit Hooks
Pre-commit hooks automatically run linting on staged files:
```bash
pre-commit run --all-files  # Run all hooks
pre-commit install         # Install git hooks
```

### CI/CD Pipeline
GitHub Actions runs on all pushes and PRs:
- **dbt parse**: Validates dbt project structure
- **sqlfluff**: Lints SQL models
- **pytest**: Runs Python unit tests
- **dbt test**: Runs dbt data quality tests
- **dbt docs**: Generates data lineage documentation

## Optimization Notes

### BigQuery Cost Optimization
- **Partitioning & Clustering**: Mart table is partitioned by `last_report_date` (month) and clustered by `fuel_type` to reduce scan costs by 80-95%
- **Materialized Staging**: Staging views are materialized as tables to avoid redundant scans
- **Deduplication**: Staging model includes dedup logic to ensure accurate aggregations

### Resource Limits
- BigQueryClient enforces a 10GB `maximum_bytes_billed` per query to prevent runaway costs
- Queries default to 300-second timeout

## Notes

- LookML and dashboard code are intentionally stored in a separate repository.
- Secrets and service account keys should never be committed; use environment variables or secret managers.
- See [CODE_REVIEW.md](CODE_REVIEW.md) for detailed code review findings and recommendations.
