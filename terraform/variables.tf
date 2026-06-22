variable "project_id" {
  type        = string
  description = "The GCP project ID where resources will be created."
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The GCP region for regional resources."
}

variable "location" {
  type        = string
  default     = "US"
  description = "The BigQuery dataset location."
}

variable "bigquery_dataset" {
  type        = string
  default     = "cal_energy_architecture_2026"
  description = "The BigQuery dataset ID to create."
}

variable "credentials_path" {
  type        = string
  default     = "~/.config/gcloud/application_default_credentials.json"
  description = "Path to the GCP service account credentials file used by Terraform."
}

variable "default_table_expiration_ms" {
  type        = number
  default     = 0
  description = "Default table expiration in milliseconds for tables created in the dataset. 0 means no expiration."
}

variable "environment" {
  type        = string
  default     = "dev"
  description = "Environment label for provisioned resources."
}
