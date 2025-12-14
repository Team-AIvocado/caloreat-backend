# 전체 리소스들을 불러오고 관리하는 중심 파일

# VPC / Subnet / SecurityGroup / ALB 등 네트워크 관련 리소스 모듈
module "vpc" {
  source = "./modules/vpc"
}

# IAM 역할 / 정책 + S3버킷
module "iam" {
  source = "./modules/iam"
}

# ECR 리포지토리
module "ecr" {
  source = "./modules/ecr"
}

# RDS(PostgreSQL) DB 생성 모듈
module "rds" {
  source      = "./modules/rds"

  subnet_ids  = module.vpc.subnet_ids   # DB가 배치될 서브넷 목록
  rds_sg_id   = module.vpc.rds_sg_id    # RDS에 적용할 Security Group
  db_password = var.db_password         # DB 비밀번호 입력
  monitoring_role_arn = module.iam.rds_monitoring_role_arn
}

# ECS Cluster + Task Definition + Service
module "ecs" {
  source = "./modules/ecs"

  subnet_ids       = module.vpc.subnet_ids       # ECS가 실행될 서브넷
  ecs_sg_id        = module.vpc.ecs_sg_id        # ECS에 적용할 SG
  target_group_arn = module.vpc.target_group_arn # ALB Target Group 연결

  execution_role_arn = module.iam.execution_role_arn # ECR pull, 로그 등에 필요한 실행 역할
  task_role_arn      = module.iam.task_role_arn      # 컨테이너 내부 앱 권한
  s3_bucket_name     = module.iam.s3_bucket_name     # 앱에서 사용할 S3 버킷

  ecr_repository_url = module.ecr.repository_url     # 도커 이미지 위치

  # RDS 연결 정보
  db_host     = module.rds.db_endpoint
  db_port     = module.rds.db_port
  db_user     = module.rds.db_username
  db_name     = module.rds.db_name
  db_password = var.db_password
}

# 예산 알림 (월 $50 초과 예상 시 이메일 전송)
resource "aws_budgets_budget" "monthly_cost" {
  name              = "monthly-budget-50"
  budget_type       = "COST"
  limit_amount      = "50"
  limit_unit        = "USD"
  time_period_start = "2025-12-01_00:00"
  time_unit         = "MONTHLY"

  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 100
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["wlsdnr710@naver.com"] # 이메일 입력
  }
}