output "bigquery_dataset_id" {
  description = "The BigQuery dataset ID created by Terraform."
  value       = google_bigquery_dataset.california_energy_architecture.dataset_id
}

output "dbt_service_accounts" {
  description = "Email addresses for dbt service accounts by environment"
  value = {
    for env in local.environments :
    env => {
      email          = google_service_account.dbt_env[env].email
      account_id     = google_service_account.dbt_env[env].account_id
      unique_id      = google_service_account.dbt_env[env].unique_id
    }
  }
}

output "dbt_service_account_keys_info" {
  description = "Service account key metadata (do not log the actual private keys - see terraform state)"
  value = {
    for env in local.environments :
    env => {
      key_id         = google_service_account_key.dbt_env_keys[env].id
      valid_after    = google_service_account_key.dbt_env_keys[env].valid_after
      valid_before   = google_service_account_key.dbt_env_keys[env].valid_before
    }
  }
  sensitive = true
}

output "dbt_keyfile_export_command" {
  description = "Commands to export service account keys from Terraform state to JSON files"
  value = {
    for env in local.environments :
    env => "terraform output -json | jq -r '.dbt_service_account_keys.value.${env}' > ~/.dbt/dbt-sa-key-${env}.json && chmod 600 ~/.dbt/dbt-sa-key-${env}.json"
  }
}
