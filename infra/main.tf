terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2" # Seoul Region
}

# Data sources
data "aws_caller_identity" "current" {}
data "aws_vpc" "default" {
  default = true
}
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# --- Variables ---
variable "db_password" {
  description = "Password for the RDS database"
  type        = string
  sensitive   = true
}

# --- ECR Repository ---
resource "aws_ecr_repository" "backend_repo" {
  name                 = "caloreat-backend"
  image_tag_mutability = "MUTABLE"
  force_delete         = true

  image_scanning_configuration {
    scan_on_push = true
  }
}

# --- S3 Bucket ---
resource "aws_s3_bucket" "storage" {
  bucket_prefix = "caloreat-storage-"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "storage_access" {
  bucket = aws_s3_bucket.storage.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- ECS Cluster ---
resource "aws_ecs_cluster" "main" {
  name = "caloreat-cluster"
}

# --- IAM Roles ---
# ECS Task Execution Role (allows ECS to pull images and write logs)
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "caloreat-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Allow creating log groups (required for awslogs-create-group)
resource "aws_iam_role_policy" "ecs_task_execution_role_logs_policy" {
  name = "caloreat-ecs-task-execution-role-logs-policy"
  role = aws_iam_role.ecs_task_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup"
        ]
        Resource = "*"
      }
    ]
  })
}

# ECS Task Role (allows the app to access S3, DB, etc.)
resource "aws_iam_role" "ecs_task_role" {
  name = "caloreat-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# Allow Task Role to access S3
resource "aws_iam_policy" "s3_access_policy" {
  name        = "caloreat-s3-access-policy"
  description = "Allow access to the storage bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = [
          aws_s3_bucket.storage.arn,
          "${aws_s3_bucket.storage.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_role_s3_policy" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.s3_access_policy.arn
}

# --- Security Groups ---
resource "aws_security_group" "alb_sg" {
  name        = "caloreat-alb-sg"
  description = "Allow HTTP inbound traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ecs_sg" {
  name        = "caloreat-ecs-sg"
  description = "Allow traffic from ALB"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "HTTP from ALB"
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "caloreat-rds-sg"
  description = "Allow traffic from ECS"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL from ECS"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# --- Load Balancer (ALB) ---
resource "aws_lb" "main" {
  name               = "caloreat-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "app" {
  name        = "caloreat-tg"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 10
  }
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# --- RDS Instance ---
resource "aws_db_subnet_group" "default" {
  name       = "caloreat-db-subnet-group"
  subnet_ids = data.aws_subnets.default.ids

  tags = {
    Name = "Caloreat DB subnet group"
  }
}

resource "aws_db_instance" "default" {
  identifier           = "caloreat-db"
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "16.6" # Check available versions
  instance_class       = "db.t3.micro"
  db_name              = "caloreat"
  username             = "postgres"
  password             = var.db_password
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true
  publicly_accessible  = false # Security best practice
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
}

# --- ECS Task Definition ---
resource "aws_ecs_task_definition" "app" {
  family                   = "caloreat-backend-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "caloreat-backend"
      image     = "${aws_ecr_repository.backend_repo.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/caloreat-backend"
          "awslogs-region"        = "ap-northeast-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
      environment = [
        { name = "S3_BUCKET_NAME", value = aws_s3_bucket.storage.id },
        { name = "DB_HOST", value = aws_db_instance.default.address },
        { name = "DB_PORT", value = tostring(aws_db_instance.default.port) },
        { name = "DB_USER", value = aws_db_instance.default.username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "DB_NAME", value = aws_db_instance.default.db_name },
        { name = "SECRET_KEY", value = "secret_caloreat" }, # 개발용 키 - 실제 서비스에선 바꾸기
        { name = "ACCESS_TOKEN_EXPIRE", value = "900" },
        { name = "REFRESH_TOKEN_EXPIRE", value = "604800" }
      ]
    }
  ])
}

# --- ECS Service ---
resource "aws_ecs_service" "main" {
  name            = "caloreat-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true # Required for Fargate to pull images if in public subnet
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "caloreat-backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.front_end]
}

# --- Outputs ---
output "ecr_repository_url" {
  value = aws_ecr_repository.backend_repo.repository_url
}

output "alb_dns_name" {
  value = aws_lb.main.dns_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.storage.id
}

output "rds_endpoint" {
  value = aws_db_instance.default.address
}
