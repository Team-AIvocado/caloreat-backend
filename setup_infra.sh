#!/bin/bash
set -e

echo "AWS 인프라 설정 시작"

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform이 설치되어 있지 않습니다."
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "AWS CLI가 설치되어 있지 않습니다."
    exit 1
fi

cd infra

echo "Terraform 초기화 (terraform init)"
terraform init

# Prompt for DB Password
echo -n "데이터베이스 비밀번호 입력 (8자 이상): "
read -s DB_PASSWORD
echo

# Check password length
if [ ${#DB_PASSWORD} -lt 8 ]; then
    echo "패스워드가 8자 이상이어야 합니다."
    exit 1
fi

echo "Terraform 계획 생성 (terraform plan)"
terraform plan -var="db_password=$DB_PASSWORD" -out=tfplan

echo "Terraform 적용 (terraform apply)"
read -p "terraform plan을 적용 할까요? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    terraform apply "tfplan"
    echo "AWS 인프라 설정 완료!"
    
    # Output important values
    echo "---------------------------------------------------"
    echo "ECR Repository URL: $(terraform output -raw ecr_repository_url)"
    echo "ALB DNS Name: $(terraform output -raw alb_dns_name)"
    echo "S3 Bucket Name: $(terraform output -raw s3_bucket_name)"
    echo "---------------------------------------------------"
    echo "GitHub Secrets에 다음 값을 추가해주세요."
else
    echo "AWS 인프라 설정 취소"
fi
