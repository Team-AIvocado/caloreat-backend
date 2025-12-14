variable "subnet_ids" {
    type = list(string)       # DB가 배치될 서브넷
}

variable "rds_sg_id" {
    type = string             # RDS Security Group
}

variable "db_password" {
    type      = string
    sensitive = true          # Terraform 출력 숨김
}

variable "monitoring_role_arn" {
    type        = string
    description = "IAM Role ARN for RDS Enhanced Monitoring"
}