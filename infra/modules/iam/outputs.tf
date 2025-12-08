output "execution_role_arn" {
  value = aws_iam_role.ecs_task_execution_role.arn
}

output "task_role_arn" {
  value = aws_iam_role.ecs_task_role.arn
}

output "s3_bucket_name" {
  value = aws_s3_bucket.storage.id   # 앱에서 환경변수로 사용하기 위해 출력
}
