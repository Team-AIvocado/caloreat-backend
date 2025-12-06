output "subnet_ids" {
    value = data.aws_subnets.default.ids
}

output "ecs_sg_id" {
    value = aws_security_group.ecs_sg.id
}

output "rds_sg_id" {
    value = aws_security_group.rds_sg.id
}

output "target_group_arn" {
    value = aws_lb_target_group.app.arn
}

output "alb_dns_name" {
    value = aws_lb.main.dns_name   # 최종 서비스 주소
}