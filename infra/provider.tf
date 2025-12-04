# AWS Provider 설정 - AWS 리소스를 만들고 관리할 수 있게 해주는 플러그인

terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            # AWS 리소스를 관리하기 위한 Provider

            version = "~> 5.0"
            # 버전 고정 -> 예기치 못한 업데이트 방지
        }
    }
}

provider "aws" {
    region = "ap-northeast-2"  # 서울 리전 지정
}

# 현재 AWS 계정 정보 (Account ID 등등)
data "aws_caller_identity" "current" {}
