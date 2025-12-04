variable "subnet_ids" { type = list(string) }      # ECS 실행 서브넷
variable "ecs_sg_id"  { type = string }            # ECS Security Group
variable "target_group_arn" { type = string }      # ALB Target Group 연결

variable "execution_role_arn" { type = string }        # ECR pull / 로그용 IAM Role
variable "task_role_arn"      { type = string }        # 앱에서 사용할 IAM Role
variable "s3_bucket_name"     { type = string }        # 앱에서 사용할 S3 버킷

variable "ecr_repository_url" { type = string }        # backend 이미지 경로

variable "db_host" { type = string }
variable "db_port" { type = number }
variable "db_user" { type = string }
variable "db_name" { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}
