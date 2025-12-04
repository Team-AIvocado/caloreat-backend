output "db_endpoint" {
  value = aws_db_instance.default.address
}

output "db_port" {
  value = aws_db_instance.default.port
}

output "db_username" {
  value = aws_db_instance.default.username
}

output "db_name" {
  value = aws_db_instance.default.db_name
}
