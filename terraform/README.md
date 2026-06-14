# Terraform scaffold

This folder contains a minimal Terraform configuration for provisioning GCP resources used by the California Energy Architecture 2026 project.

## Included resources

- BigQuery dataset
- Service account for dbt execution
- IAM binding granting BigQuery editor access to the dbt service account

## Usage

1. Install Terraform.
2. Configure your GCP credentials and project.
3. Run:
   ```bash
   terraform init
   terraform plan -var="project_id=YOUR_PROJECT_ID" -var="credentials_path=/path/to/credentials.json"
   terraform apply -var="project_id=YOUR_PROJECT_ID" -var="credentials_path=/path/to/credentials.json"
   ```

## Notes

- Do not commit your credentials file to source control.
- Use a remote state backend if you want to share this configuration across teams.
