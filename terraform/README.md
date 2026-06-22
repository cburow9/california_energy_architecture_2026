# Terraform Configuration

This folder contains Terraform configuration for provisioning GCP resources used by the California Energy Architecture 2026 project.

## Included Resources

### BigQuery
- `california_energy_architecture` dataset with appropriate labels and retention settings
- Environment-specific dataset naming recommended (e.g., `cal_energy_architecture_2026_dev`)

### Service Accounts for dbt
This configuration creates **three service accounts** (one per environment) for secure dbt execution:
- `dbt-dev`: For local development and testing
- `dbt-staging`: For staging/pre-production runs
- `dbt-prod`: For production dbt runs

Each service account includes:
- BigQuery Editor role (read/write data and create/delete tables)
- BigQuery Job User role (submit and monitor BigQuery jobs)
- Logging Writer role (write execution logs)
- Dataset-level editor access

### Service Account Keys
- Service account keys are automatically generated and stored in Terraform state
- Keys are sensitive and should be managed securely
- Consider using Google Secret Manager for production environments

## Prerequisites

1. **Terraform** >= 1.5.0 installed
2. **gcloud CLI** authenticated with appropriate permissions:
   ```bash
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. Permissions to create:
   - Service accounts
   - IAM bindings
   - BigQuery datasets

## Setup Instructions

### 1. Initialize Terraform

```bash
cd terraform/
terraform init
```

### 2. Create terraform.tfvars (or use command-line variables)

```bash
# Create terraform.tfvars with your project details
cat > terraform.tfvars <<EOF
project_id = "your-gcp-project-id"
region     = "us-central1"
location   = "US"
environment = "dev"
bigquery_dataset = "cal_energy_architecture_2026"
EOF
```

Or use command-line variables:
```bash
terraform plan -var="project_id=YOUR_PROJECT_ID"
```

### 3. Plan and Apply

```bash
# Review what will be created
terraform plan

# Create the resources
terraform apply
```

### 4. Extract Service Account Keys

After successful `terraform apply`, extract the service account keys:

```bash
# Export keys from Terraform state to JSON files
mkdir -p ~/.dbt

# Extract dev key
terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json && chmod 600 ~/.dbt/dbt-sa-key-dev.json

# Extract staging key
terraform output -json | jq -r '.dbt_service_account_keys.value.staging' > ~/.dbt/dbt-sa-key-staging.json && chmod 600 ~/.dbt/dbt-sa-key-staging.json

# Extract prod key
terraform output -json | jq -r '.dbt_service_account_keys.value.prod' > ~/.dbt/dbt-sa-key-prod.json && chmod 600 ~/.dbt/dbt-sa-key-prod.json
```

### 5. Configure dbt Profiles

1. Copy the example profiles:
   ```bash
   cp profiles.yml.example ~/.dbt/profiles.yml
   ```

2. Update `~/.dbt/profiles.yml`:
   - Set your GCP project ID
   - Update dataset names to match your setup (e.g., `cal_energy_architecture_2026_dev`)
   - Verify keyfile paths match where you extracted the keys

3. Test the connection:
   ```bash
   dbt debug
   ```

## Security Best Practices

### For Development
- ✅ Service account keys are acceptable
- Use files with restricted permissions (0600)
- Keep keys in `~/.dbt/` directory (not in version control)

### For CI/CD (Cloud Build)
- ✅ Store service account keys securely in Cloud Build Secret Manager
- Reference secrets in `cloudbuild.yaml`:
  ```yaml
  - name: 'gcr.io/cloud-builders/gke-deploy'
    env:
      - 'CLOUDSDK_COMPUTE_ZONE=us-central1'
      - 'CLOUDSDK_CONTAINER_CLUSTER=my-cluster'
      - 'GOOGLE_APPLICATION_CREDENTIALS=/workspace/sa-key.json'
    secretEnv: ['SA_KEY']
    secretManager:
    - versionName: projects/$PROJECT_ID/secrets/dbt-sa-key-dev/versions/latest
      env: 'SA_KEY'
  ```

### For Production
- 🎯 **Recommended**: Use Workload Identity Federation instead of keys
- Alternative: Store keys in Google Secret Manager with access audit logs
- Rotate keys regularly (quarterly or more frequently)
- Monitor key usage in Cloud Audit Logs

## Outputs

After `terraform apply`, view outputs:

```bash
# View all service account details
terraform output dbt_service_accounts

# View key metadata (keys themselves are in state and marked sensitive)
terraform output dbt_service_account_keys_info

# View commands to export keys
terraform output dbt_keyfile_export_command
```

## Troubleshooting

### Keys not exported correctly
```bash
# Verify keys exist in state
terraform state list

# Check if jq is installed
which jq  # Install with: apt-get install jq (or brew install jq on macOS)

# Manual extraction
terraform show -json | jq '.values.outputs.dbt_service_account_keys.value.dev'
```

### dbt debug fails
```bash
# Check keyfile exists and is readable
ls -la ~/.dbt/dbt-sa-key-*.json

# Verify keyfile is valid JSON
jq . ~/.dbt/dbt-sa-key-dev.json

# Check dbt profiles.yml syntax
dbt parse
```

### Permission denied errors
- Verify service account has appropriate roles
- Check dataset IAM bindings: `terraform output dbt_service_accounts`
- Grant additional roles if needed

## State Management

### ⚠️ Important: Sensitive Data in State

Terraform state contains **private service account keys**. Protect it:

1. **Local Development**
   - Store state file locally (default)
   - Add `.terraform/` to `.gitignore`

2. **Team Collaboration**
   - Use Terraform Cloud/Enterprise
   - Or use GCS backend with encryption and access controls:
     ```bash
     # Uncomment in main.tf and configure:
     # terraform {
     #   backend "gcs" {
     #     bucket = "your-terraform-state-bucket"
     #     prefix = "california-energy"
     #   }
     # }
     ```

3. **CI/CD Pipelines**
   - Store Terraform state securely
   - Restrict access to state files
   - Use service account impersonation if possible

## Environment-Specific Datasets

For complete isolation, create separate BigQuery datasets per environment:

```bash
# Update dbt_project.yml for environment-specific datasets
# Or modify profiles.yml to point to different datasets

# Datasets should follow naming convention:
# - Development: cal_energy_architecture_2026_dev
# - Staging: cal_energy_architecture_2026_staging
# - Production: cal_energy_architecture_2026_prod
```

## Next Steps

1. ✅ Initialize Terraform and create service accounts
2. ✅ Extract and configure service account keys
3. ✅ Update dbt profiles.yml with correct paths and project ID
4. ✅ Test dbt connection: `dbt debug`
5. 📋 Create environment-specific BigQuery datasets (optional but recommended)
6. 🔒 For production: Implement Workload Identity Federation
7. 📊 Set up monitoring and alerts for service account key usage

## References

- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [dbt BigQuery setup](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup)
- [GCP Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [Workload Identity Federation](https://cloud.google.com/iam/docs/workload-identity-federation)
