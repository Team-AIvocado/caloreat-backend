# 출력값 정의

output "ecr_repository_url" {
    value = module.ecr.repository_url
}

output "alb_dns_name" {
    value = module.vpc.alb_dns_name
    # 최종 서비스 URL
}

output "s3_bucket_name" {
    value = module.iam.s3_bucket_name
}

output "rds_endpoint" {
    value = module.rds.db_endpoint
}