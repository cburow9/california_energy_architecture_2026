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

# Service Accounts for dbt (one per environment)
locals {
  environments = ["dev", "staging", "prod"]
  dbt_roles = [
    "roles/bigquery.dataEditor",      # Read/write BigQuery data
    "roles/bigquery.jobUser",         # Run BigQuery jobs
    "roles/logging.logWriter"         # Write logs
  ]
}

# Create service account for each environment
resource "google_service_account" "dbt_env" {
  for_each = toset(local.environments)

  account_id   = "dbt-${each.value}"
  display_name = "dbt service account for ${each.value} environment"
  description  = "Service account for running dbt in ${each.value} environment"
}

# Grant BigQuery and logging roles to each service account
resource "google_project_iam_member" "dbt_env_roles" {
  for_each = { for combo in flatten([
    for env in local.environments : [
      for role in local.dbt_roles : {
        env  = env
        role = role
      }
    ]
  ]) : "${combo.env}-${combo.role}" => combo }

  project = var.project_id
  role    = each.value.role
  member  = "serviceAccount:${google_service_account.dbt_env[each.value.env].email}"
}

# Grant BigQuery dataset-level permissions
resource "google_bigquery_dataset_iam_member" "dbt_env_dataset_access" {
  for_each = toset(local.environments)

  dataset_id = google_bigquery_dataset.california_energy_architecture.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dbt_env[each.value].email}"
}

# Create service account keys for authentication (stored in Terraform state)
# IMPORTANT: These keys should be managed securely. Consider using Google Secret Manager.
resource "google_service_account_key" "dbt_env_keys" {
  for_each = toset(local.environments)

  service_account_id = google_service_account.dbt_env[each.value].name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Export keys as JSON for use with dbt (base64 encoded in Terraform state)
locals {
  service_account_keys = {
    for env in local.environments :
    env => base64decode(google_service_account_key.dbt_env_keys[env].private_key)
  }
}
