#!/bin/bash
set -e

echo "Setting up AWS Infrastructure..."

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install it first."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI is not installed. Please install it first."
    exit 1
fi

cd infra

echo "Initializing Terraform..."
terraform init

echo "Planning Terraform changes..."
terraform plan -out=tfplan

echo "Applying Terraform changes..."
read -p "Do you want to apply these changes? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply "tfplan"
    echo "Infrastructure setup complete!"
    
    # Output important values
    echo "---------------------------------------------------"
    echo "ECR Repository URL: $(terraform output -raw ecr_repository_url)"
    echo "ALB DNS Name: $(terraform output -raw alb_dns_name)"
    echo "S3 Bucket Name: $(terraform output -raw s3_bucket_name)"
    echo "---------------------------------------------------"
    echo "Please update your GitHub Secrets with these values."
else
    echo "Setup cancelled."
fi
