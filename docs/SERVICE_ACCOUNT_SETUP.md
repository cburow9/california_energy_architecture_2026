# Service Account Setup Guide for dbt

This guide walks you through setting up Google Cloud Platform (GCP) service accounts for running dbt in the California Energy Architecture 2026 project.

## Overview

You'll set up **three service accounts** for different environments:
- **dbt-dev**: Local development and testing
- **dbt-staging**: Staging/pre-production environment
- **dbt-prod**: Production environment

Each account has the minimum required permissions to:
- Read/write BigQuery datasets and tables
- Submit and monitor BigQuery jobs
- Write execution logs

## Quick Start (5 minutes)

```bash
# 1. Navigate to Terraform
cd terraform/

# 2. Initialize Terraform
terraform init

# 3. Create your variables file
cat > terraform.tfvars <<EOF
project_id = "your-gcp-project-id"
region     = "us-central1"
location   = "US"
EOF

# 4. Apply the configuration
terraform apply

# 5. Extract service account keys
mkdir -p ~/.dbt
terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json
terraform output -json | jq -r '.dbt_service_account_keys.value.staging' > ~/.dbt/dbt-sa-key-staging.json
terraform output -json | jq -r '.dbt_service_account_keys.value.prod' > ~/.dbt/dbt-sa-key-prod.json

# 6. Secure the keys
chmod 600 ~/.dbt/dbt-sa-key-*.json

# 7. Configure dbt
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml with your project ID and dataset names

# 8. Test the connection
dbt debug
```

## Detailed Setup

### Prerequisites

- ✅ GCP project created and configured
- ✅ `gcloud` CLI installed and authenticated:
  ```bash
  gcloud auth application-default login
  gcloud config set project YOUR_PROJECT_ID
  ```
- ✅ Terraform installed (>= 1.5.0):
  ```bash
  terraform -v
  ```
- ✅ `jq` installed for JSON parsing:
  ```bash
  # macOS
  brew install jq
  
  # Ubuntu/Debian
  sudo apt-get install jq
  ```

### Step 1: Prepare Terraform Configuration

1. **Navigate to the Terraform directory:**
   ```bash
   cd terraform/
   ```

2. **Create `terraform.tfvars` with your GCP settings:**
   ```bash
   cat > terraform.tfvars <<'EOF'
   project_id              = "your-gcp-project-id"
   region                  = "us-central1"
   location                = "US"
   bigquery_dataset        = "cal_energy_architecture_2026"
   environment             = "dev"
   default_table_expiration_ms = 0
   EOF
   ```

   Or use environment variables:
   ```bash
   export TF_VAR_project_id="your-gcp-project-id"
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init
   ```

### Step 2: Create Service Accounts and Keys

1. **Review what will be created:**
   ```bash
   terraform plan
   ```

2. **Apply the Terraform configuration:**
   ```bash
   terraform apply
   ```

   This creates:
   - 3 service accounts (dbt-dev, dbt-staging, dbt-prod)
   - 3 service account keys (for authentication)
   - IAM role bindings for each service account

3. **Verify the service accounts were created:**
   ```bash
   # View service account details
   terraform output dbt_service_accounts
   
   # Example output:
   # {
   #   "dev": {
   #     "account_id" = "dbt-dev"
   #     "email" = "dbt-dev@your-project.iam.gserviceaccount.com"
   #     "unique_id" = "12345..."
   #   },
   #   ...
   # }
   ```

### Step 3: Extract Service Account Keys

Extract the service account keys from Terraform state to JSON files:

```bash
# Create the .dbt directory
mkdir -p ~/.dbt

# Extract development key
echo "Extracting development key..."
terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json

# Extract staging key
echo "Extracting staging key..."
terraform output -json | jq -r '.dbt_service_account_keys.value.staging' > ~/.dbt/dbt-sa-key-staging.json

# Extract production key
echo "Extracting production key..."
terraform output -json | jq -r '.dbt_service_account_keys.value.prod' > ~/.dbt/dbt-sa-key-prod.json

# Verify keys were extracted
ls -la ~/.dbt/dbt-sa-key-*.json
```

### Step 4: Secure the Keys

```bash
# Set restrictive permissions (readable only by you)
chmod 600 ~/.dbt/dbt-sa-key-*.json

# Verify permissions
ls -la ~/.dbt/dbt-sa-key-*.json
# Should show: -rw------- (600)

# Never commit these files to version control!
# Verify they're in .gitignore
grep "dbt-sa-key" ../.gitignore
```

### Step 5: Configure dbt Profiles

1. **Copy the example profiles file:**
   ```bash
   cp ../profiles.yml.example ~/.dbt/profiles.yml
   ```

2. **Edit `~/.dbt/profiles.yml`:**
   ```bash
   nano ~/.dbt/profiles.yml
   # or
   code ~/.dbt/profiles.yml
   ```

3. **Update the following placeholders:**
   - `your-gcp-project`: Your GCP project ID
   - `cal_energy_architecture_2026_dev`: Your dev dataset name
   - `cal_energy_architecture_2026_staging`: Your staging dataset name
   - `cal_energy_architecture_2026_prod`: Your prod dataset name

   Example:
   ```yaml
   california_energy_architecture_2026:
     target: dev
     outputs:
       dev:
         type: bigquery
         method: service-account
         project: my-gcp-project-12345
         dataset: cal_energy_architecture_2026_dev
         keyfile: ~/.dbt/dbt-sa-key-dev.json
         # ... other settings
   ```

### Step 6: Test the Connection

1. **Test dbt can connect to BigQuery:**
   ```bash
   dbt debug
   ```

   Success output:
   ```
   Environment:
     installed version: 1.x.x
     ...
   
   Credentials:
     BigQuery connection: OK
   ```

2. **If debug fails**, check:
   ```bash
   # Verify keyfile exists and is readable
   cat ~/.dbt/dbt-sa-key-dev.json | jq . > /dev/null && echo "Key is valid JSON"
   
   # Check dbt profiles.yml syntax
   dbt parse
   
   # Verify service account has BigQuery permissions
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.members:dbt-dev@*"
   ```

## Creating Environment-Specific BigQuery Datasets

For complete environment isolation, create separate datasets:

```bash
# Using gcloud
for env in dev staging prod; do
  bq mk --dataset \
    --description="California energy data - $env environment" \
    --location=US \
    cal_energy_architecture_2026_${env}
done

# Or manually in the GCP Console
# BigQuery > Create Dataset > Name: cal_energy_architecture_2026_dev (repeat for staging, prod)
```

Verify datasets were created:
```bash
bq ls --transfer_config --transfer_location=us
```

## Using Service Accounts for Different Environments

### Local Development

```bash
# Use the dev account (default)
dbt run

# Or explicitly specify target
dbt run --target dev
dbt test --target dev
```

### Staging Runs

```bash
# Use the staging service account
dbt run --target staging
dbt test --target staging
```

### Production Runs

```bash
# Use the production service account
dbt run --target prod
dbt test --target prod --select specific_model  # Always use --select in prod
```

## CI/CD Integration (Cloud Build)

### Option 1: Store Keys in Cloud Build Secret Manager

```bash
# Create a secret for each environment
gcloud secrets create dbt-sa-key-dev --replication-policy="automatic"
gcloud secrets create dbt-sa-key-staging --replication-policy="automatic"
gcloud secrets create dbt-sa-key-prod --replication-policy="automatic"

# Add the secret data
gcloud secrets versions add dbt-sa-key-dev --data-file=~/.dbt/dbt-sa-key-dev.json
gcloud secrets versions add dbt-sa-key-staging --data-file=~/.dbt/dbt-sa-key-staging.json
gcloud secrets versions add dbt-sa-key-prod --data-file=~/.dbt/dbt-sa-key-prod.json
```

### Option 2: Update cloudbuild.yaml

```yaml
steps:
  - name: python:3.11-slim
    id: "Run dbt"
    env:
      - 'DBT_TARGET=dev'
    secretEnv: ['DBT_SA_KEY']
    entrypoint: bash
    args:
      - -c
      - |
        mkdir -p ~/.dbt
        echo "$$DBT_SA_KEY" > ~/.dbt/dbt-sa-key-dev.json
        chmod 600 ~/.dbt/dbt-sa-key-dev.json
        cp ../profiles.yml.example ~/.dbt/profiles.yml
        dbt deps
        dbt run --target $DBT_TARGET

secrets:
  - name: DBT_SA_KEY
    versionName: projects/$PROJECT_ID/secrets/dbt-sa-key-dev/versions/latest
```

## Security Best Practices

### ✅ Development Environment
- Service account keys stored locally in `~/.dbt/`
- Keys have restricted file permissions (600)
- Not committed to version control

### ✅ Staging Environment
- Keys stored in Cloud Build Secret Manager
- Access logged and auditable
- Rotated quarterly

### 🎯 Production Environment (Recommended)
- **Use Workload Identity Federation** instead of keys
- If keys required: Store in Secret Manager with strict access controls
- Implement key rotation policy (quarterly or more frequently)
- Monitor key usage in Cloud Audit Logs

## Troubleshooting

### Issue: "Permission denied" when running dbt

**Solution**: Verify service account has correct roles
```bash
# Check current roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:dbt-dev@*"

# Grant missing role (if needed)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:dbt-dev@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"
```

### Issue: "Authentication failed" when running dbt debug

**Solution**: Verify keyfile is valid
```bash
# Check if file exists and is readable
ls -la ~/.dbt/dbt-sa-key-dev.json

# Verify it's valid JSON
jq . ~/.dbt/dbt-sa-key-dev.json | head -20

# Check profiles.yml has correct path
grep -A5 "keyfile:" ~/.dbt/profiles.yml
```

### Issue: "Dataset not found" error

**Solution**: Create the BigQuery datasets
```bash
# List existing datasets
bq ls

# Create missing datasets
bq mk --dataset \
  --description="California energy data - dev" \
  --location=US \
  cal_energy_architecture_2026_dev
```

### Issue: Terraform shows sensitive keys as "sensitive"

This is normal! Terraform protects sensitive data. To view keys:
```bash
# View keys in state file (use with caution!)
terraform state show 'google_service_account_key.dbt_env_keys["dev"]'

# Or export programmatically
terraform output -json | jq '.dbt_service_account_keys.value.dev' | jq . > key.json
```

## Managing Multiple Machines

If you work on multiple machines:

1. **Extract keys on each machine:**
   ```bash
   # On each machine with access to Terraform state
   cd terraform/
   mkdir -p ~/.dbt
   terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json
   chmod 600 ~/.dbt/dbt-sa-key-dev.json
   ```

2. **Or use Secret Manager:**
   ```bash
   # Retrieve key from Cloud Secret Manager
   gcloud secrets versions access latest --secret="dbt-sa-key-dev" > ~/.dbt/dbt-sa-key-dev.json
   chmod 600 ~/.dbt/dbt-sa-key-dev.json
   ```

## Next Steps

1. ✅ Complete the setup using the steps above
2. ✅ Run `dbt debug` to verify connection
3. 📋 Create environment-specific datasets
4. 🔄 Test dbt in each environment (dev, staging, prod)
5. 📊 Set up CI/CD pipeline with Cloud Build
6. 🔒 For production: Implement Workload Identity Federation
7. 📝 Document your environment-specific dbt_projects.yml configurations

## References

- [dbt BigQuery setup guide](https://docs.getdbt.com/docs/core/connect-data-platform/bigquery-setup)
- [GCP Service Accounts documentation](https://cloud.google.com/iam/docs/service-accounts)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Cloud Build Secret Manager integration](https://cloud.google.com/build/docs/securing-builds/use-secrets)
- [Workload Identity Federation setup](https://cloud.google.com/iam/docs/workload-identity-federation-with-applications)
