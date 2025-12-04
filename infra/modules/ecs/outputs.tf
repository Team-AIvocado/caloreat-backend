# ECS 클러스터 이름 (필요 시 배포 자동화, 모니터링 등에서 사용)
output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

# ECS 클러스터 ARN (정책, 모니터링 등에서 ARN이 필요한 경우 사용)
output "cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

# ECS 서비스 이름
output "service_name" {
  value = aws_ecs_service.main.name
}

# ECS 서비스 ARN
output "service_arn" {
  value = aws_ecs_service.main.id
}

# Task Definition ARN (배포 자동화에서 가장 자주 씀)
output "task_definition_arn" {
  value = aws_ecs_task_definition.app.arn
}
