# 기본 VPC 사용 ( 새 VPC 만들지 않음 -> 설정 단순화)
data "aws_vpc" "default" {
    default = true
}

# 기본 VPC 내 서브넷 조회
data "aws_subnets" "default" {
    filter {
        name   = "vpc-id"
        values = [data.aws_vpc.default.id] 
    }
}

# ALB Security Group (외부 트래픽 -> ALB 허용)
resource "aws_security_group" "alb_sg" {
    name        = "caloreat-alb-sg"
    description = "Allow HTTP inbound traffic"
    vpc_id      = data.aws_vpc.default.id

    ingress {  # 들어오는 트래픽(Inbound)
        description = "HTTP from anywhere"
        from_port   = 80              # 80포트 허용
        to_port     = 80
        protocol    = "tcp"
        cidr_blocks = ["0.0.0.0/0"]   # 전세계에서 허용
    }

    # ALB -> 어디든 나갈 수 있게 허용
    egress {   # 나가는 트래픽(Outbound)
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
} 

# ECS Security Group (ALB -> ECS만 허용)
resource "aws_security_group" "ecs_sg" {
    name        = "caloreat-ecs-sg"
    description = "Allow traffic from ALB"
    vpc_id      = data.aws_vpc.default.id

    # ALB에서 오는 요청만 허용 (8000포트)
    ingress {
        description     = "HTTP from ALB"
        from_port       = 8000
        to_port         = 8000
        protocol        = "tcp"
        security_groups = [aws_security_group.alb_sg.id]
    }

    # ECS -> 외부 인터넷 등 outbound 모두 허용
    egress {
        from_port   = 0
        to_port     = 0
        protocol    = "-1"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

# RDS Security Group (ECS -> RDS만 허용)
resource "aws_security_group" "rds_sg" {
    name        = "caloreat-rds-sg"
    description = "Allow traffic from ECS"
    vpc_id      = data.aws_vpc.default.id

    ingress {
        description     = "PostgreSQL from ECS"
        from_port       = 5432                           # Postgres 포트
        to_port         = 5432
        protocol        = "tcp"
        security_groups = [aws_security_group.ecs_sg.id] # ECS만 허용
    }

    egress {
        from_port    = 0
        to_port      = 0
        protocol     = "-1"
        cidr_blocks  = ["0.0.0.0/0"]
    }
} 

# Application Load Balancer (외부 -> ECS로 라우팅)
resource "aws_lb" "main" {
    name               = "caloreat-alb"
    internal           = false              # 인터넷 향 ALB
    load_balancer_type = "application"
    security_groups    = [aws_security_group.alb_sg.id]
    subnets            = data.aws_subnets.default.ids
}

# ALB Target Group (ECS IP로 라우팅)
resource "aws_lb_target_group" "app" {
    name        = "caloreat-tg"
    port        = 8000
    protocol    = "HTTP"
    vpc_id      = data.aws_vpc.default.id
    target_type = "ip"                       # Fargate는 IP 모드

    health_check {
        path                = "/health"       # health 체크 경로
        healthy_threshold   = 2
        unhealthy_threshold = 10 
    }
}

# Listener (80포트 요청 -> Target Group으로 포워딩)
resource "aws_lb_listener" "front_end" {
    load_balancer_arn = aws_lb.main.arn
    port              = "80"
    protocol          = "HTTP"

    default_action {
        type             = "forward"
        target_group_arn = aws_lb_target_group.app.arn
    }
}

