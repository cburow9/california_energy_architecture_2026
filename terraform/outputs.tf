output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID created by Terraform."
  value       = google_bigquery_dataset.california_energy_architecture.dataset_id
}

output "dbt_service_account_email" {
  description = "The email address of the created dbt service account."
  value       = google_service_account.dbt_runner.email
}
