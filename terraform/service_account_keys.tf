# This file handles exporting service account keys for dbt
# The private keys are stored in Terraform state and should be handled securely

output "dbt_service_account_keys" {
  description = "Service account keys as JSON strings. SENSITIVE: Do not share or commit these to version control."
  value = {
    for env in local.environments :
    env => google_service_account_key.dbt_env_keys[env].private_key_data
  }
  sensitive = true
}

# Helper locals to construct the key files for dbt profiles
locals {
  dbt_keys_json = {
    for env in local.environments :
    env => jsondecode(base64decode(google_service_account_key.dbt_env_keys[env].private_key_data))
  }
}

# Output individual key files (optional - for automated setup)
# Uncomment the resource below if you want Terraform to manage the keyfiles directly
# NOTE: This exposes keys in Terraform state - consider using Google Secret Manager instead

# resource "local_file" "dbt_keyfile" {
#   for_each = toset(local.environments)
#
#   filename        = "${path.module}/../.dbt/dbt-sa-key-${each.value}.json"
#   content         = base64decode(google_service_account_key.dbt_env_keys[each.value].private_key_data)
#   file_permission = "0600"
# }
