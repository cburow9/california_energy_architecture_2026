# dbt Service Account - Quick Reference

## Setup Summary

Your dbt service accounts are configured for three environments:
- **dev**: Development and testing
- **staging**: Pre-production
- **prod**: Production

Each account has permissions to:
- Create and modify BigQuery datasets and tables
- Run BigQuery jobs
- Write logs

## Quick Commands

### Extract Keys (one-time setup)
```bash
cd terraform/
mkdir -p ~/.dbt
terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json
terraform output -json | jq -r '.dbt_service_account_keys.value.staging' > ~/.dbt/dbt-sa-key-staging.json
terraform output -json | jq -r '.dbt_service_account_keys.value.prod' > ~/.dbt/dbt-sa-key-prod.json
chmod 600 ~/.dbt/dbt-sa-key-*.json
```

### Configure dbt
```bash
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml - update project ID and dataset names
dbt debug  # Verify connection
```

### View Service Account Information
```bash
cd terraform/
terraform output dbt_service_accounts
```

## Using dbt with Different Environments

### Development
```bash
dbt run --target dev
dbt test --target dev
dbt compile --target dev
```

### Staging
```bash
dbt run --target staging
dbt test --target staging
```

### Production (always use --select)
```bash
dbt run --target prod --select my_model
dbt test --target prod --select my_model
```

## Troubleshooting

### dbt debug fails
```bash
# Check if key file exists
ls ~/.dbt/dbt-sa-key-dev.json

# Verify it's valid JSON
jq . ~/.dbt/dbt-sa-key-dev.json

# Check profiles.yml is in correct location
cat ~/.dbt/profiles.yml

# Run debug with verbose output
dbt debug --verbose
```

### "Permission denied" errors
```bash
# Check service account has BigQuery roles
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:dbt-dev@*"

# View all service accounts
gcloud iam service-accounts list --filter="name:dbt"
```

### "Dataset not found" error
```bash
# List existing datasets
bq ls

# Create missing dataset
bq mk --dataset cal_energy_architecture_2026_dev

# Or create all three
for env in dev staging prod; do
  bq mk --dataset cal_energy_architecture_2026_${env}
done
```

### Re-extract keys
```bash
cd terraform/
rm ~/.dbt/dbt-sa-key-dev.json
terraform output -json | jq -r '.dbt_service_account_keys.value.dev' > ~/.dbt/dbt-sa-key-dev.json
chmod 600 ~/.dbt/dbt-sa-key-dev.json
```

## File Locations

| Item | Location | Notes |
|------|----------|-------|
| Service account keys | `~/.dbt/dbt-sa-key-*.json` | Never commit to git |
| dbt profiles | `~/.dbt/profiles.yml` | Never commit to git |
| Terraform config | `terraform/` | Safe to commit |
| Terraform state | `terraform/.terraform/` | Never commit to git |

## Environment Variables

Set environment variables for dbt targets:
```bash
export DBT_PROFILES_DIR=~/.dbt
export DBT_TARGET=dev
dbt run
```

Or in your shell config:
```bash
# Add to ~/.bashrc or ~/.zshrc
export DBT_PROFILES_DIR=~/.dbt
alias dbt-dev="dbt --target dev"
alias dbt-staging="dbt --target staging"
alias dbt-prod="dbt --target prod"
```

Then:
```bash
dbt-dev run   # Runs with dev target
dbt-staging run
dbt-prod run
```

## Security Reminders

⚠️ **Never commit these to git:**
- `~/.dbt/profiles.yml` (contains keyfile paths)
- `~/.dbt/dbt-sa-key-*.json` (contains credentials)
- `terraform/.terraform/` (contains state with keys)
- `terraform/terraform.tfvars` (may contain credentials)

✅ **Add to .gitignore:**
```bash
# dbt
profiles.yml
dbt_packages/
target/

# Terraform
.terraform/
terraform.tfstate*
terraform.tfvars

# Service accounts
dbt-sa-key-*.json
```

## Support

For more detailed information, see:
- [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md) - Full setup guide
- [terraform/README.md](../terraform/README.md) - Terraform details
- [profiles.yml.example](../profiles.yml.example) - dbt profile example
