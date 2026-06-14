#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${DBT_PROFILES_DIR:-}" ]]; then
  export DBT_PROFILES_DIR=$(pwd)
fi

python -m dbt deps
python -m dbt seed
python -m dbt run
python -m dbt test
