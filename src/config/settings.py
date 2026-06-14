from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

GCP_PROJECT = os.getenv('GCP_PROJECT', 'your-gcp-project')
BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'cal_energy_architecture_2026')
DBT_PROFILE = os.getenv('DBT_PROFILE', 'california_energy_architecture_2026')
DBT_TARGET = os.getenv('DBT_TARGET', 'dev')
