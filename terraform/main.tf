terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file(var.credentials_path)
}

resource "google_bigquery_dataset" "california_energy_architecture" {
  dataset_id                  = var.bigquery_dataset
  friendly_name               = "California Energy Architecture 2026"
  description                 = "BigQuery dataset for California energy architecture analytics."
  location                    = var.location
  default_table_expiration_ms = var.default_table_expiration_ms
  labels = {
    environment = var.environment
    project     = "california_energy_architecture_2026"
  }
}

resource "google_service_account" "dbt_runner" {
  account_id   = "dbt-runner"
  display_name = "dbt runner service account"
}

resource "google_project_iam_member" "dbt_bigquery_access" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.dbt_runner.email}"
}
