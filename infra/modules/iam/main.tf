# S3 Bucket (애플리케이션에서 사용할 스토리지)
resource "aws_s3_bucket" "storage" {
  bucket_prefix = "caloreat-storage-"   # 고유 버킷 이름(prefix)
  force_destroy = true                  # 삭제 시 안의 파일도 함께 삭제 (개발용)
}

# 퍼블릭 접근 차단 (실수로 공개되지 않도록 보안 설정)
resource "aws_s3_bucket_public_access_block" "storage_access" {
  bucket = aws_s3_bucket.storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ECS Task Execution Role
# 컨테이너 실행을 위해 ECS가 AWS API(ECR pull, 로그 등)를 호출할 때 사용하는 역할
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "caloreat-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"             # ECS가 이 역할을 assume 할 수 있도록 설정
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com" # ECS Task가 사용하는 서비스 principal
        }
      }
    ]
  })
}

# AWS에서 제공하는 표준 정책 — ECR pull, CloudWatch 로그 권한 포함
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
    role       = aws_iam_role.ecs_task_execution_role.name
    policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"   
}

# 로그 그룹 생성 권한 추가 (awslogs-create-group=true 옵션 때문에 필요)
resource "aws_iam_role_policy" "ecs_task_execution_role_logs_policy" {
  name = "caloreat-ecs-task-execution-role-logs-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["logs:CreateLogGroup"]  # CloudWatch Log group 생성
        Resource = "*"
      }
    ]
  })
}

# ECS Task Role
# 컨테이너 안의 애플리케이션이 AWS 리소스 접근 시 사용하는 역할
# 예 : S3 Put/Get, DynamoDB, SQS 등
resource "aws_iam_role" "ecs_task_role" {
  name = "caloreat-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"  # ECS 태스크가 역할을 획득함
        }
      }
    ]
  })
}

# S3 접근 정책 (특정 버킷만 접근 가능)
resource "aws_iam_policy" "s3_access_policy" {
  name        = "caloreat-s3-access-policy"
  description = "Allow access to the storage bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.storage.arn,         # 버킷 자체
          "${aws_s3_bucket.storage.arn}/*"   # 버킷 내부 파일들
        ]
      }
    ]
  })
}

# 위에서 만든 S3 정책을 Task Role에 연결
resource "aws_iam_role_policy_attachment" "ecs_task_role_s3_policy" {
    role       = aws_iam_role.ecs_task_role.name
    policy_arn = aws_iam_policy.s3_access_policy.arn 
}

# RDS Monitoring Role
resource "aws_iam_role" "rds_monitoring_role" {
  name = "caloreat-rds-monitoring-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring_role_policy" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudFront Invalidation Policy (Frontend Deploy 용)
resource "aws_iam_policy" "cloudfront_invalidation" {
  name        = "caloreat-cloudfront-invalidation"
  description = "Allow CloudFront invalidation for deployment"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "cloudfront:CreateInvalidation"
        Resource = "*"
      }
    ]
  })
}

# Attach to existing caloreat-s3 user
resource "aws_iam_user_policy_attachment" "frontend_deploy_attach" {
  user       = "caloreat-s3"
  policy_arn = aws_iam_policy.cloudfront_invalidation.arn
}