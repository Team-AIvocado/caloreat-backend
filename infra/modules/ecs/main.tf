# ECS 클러스터 생성
resource "aws_ecs_cluster" "main" {
  name = "caloreat-cluster"
}

# Fargate Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "caloreat-backend-task"
  network_mode             = "awsvpc"                      # Fargate 필수
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"                         # 0.25 vCPU
  memory                   = "512"                         # 0.5GB 메모리
  execution_role_arn       = var.execution_role_arn        # ECR pull 등
  task_role_arn            = var.task_role_arn             # 앱 IAM 권한

  # 컨테이너 설정(JSON)
  container_definitions = jsonencode([
    {
      name      = "caloreat-backend"
      image     = "${var.ecr_repository_url}:latest"       # 최신 이미지 pull
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]

      # CloudWatch 로그 설정
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/caloreat-backend"
          "awslogs-region"        = "ap-northeast-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }

      # 애플리케이션 환경 변수 (DB / S3 정보 전달)
      environment = [
        { name = "S3_BUCKET_NAME", value = var.s3_bucket_name },
        { name = "DB_HOST",        value = var.db_host },
        { name = "DB_PORT",        value = tostring(var.db_port) },
        { name = "DB_USER",        value = var.db_user },
        { name = "DB_PASSWORD",    value = var.db_password },
        { name = "DB_NAME",        value = var.db_name },
        { name = "SECRET_KEY",     value = "secret_caloreat" },
        { name = "ACCESS_TOKEN_EXPIRE",  value = "900" },
        { name = "REFRESH_TOKEN_EXPIRE", value = "604800" }
      ]
    }
  ])
}

# ECS Service (실제 실행되는 Fargate 컨테이너)
resource "aws_ecs_service" "main" {
  name            = "caloreat-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1                               # 컨테이너 1개로 운영
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids               # ECS가 실행될 서브넷
    security_groups  = [var.ecs_sg_id]              # ECS SG 적용
    assign_public_ip = true                         # ECR pull 위해 필요
  }

  # ALB 연결 설정
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = "caloreat-backend"
    container_port   = 8000
  }
}
