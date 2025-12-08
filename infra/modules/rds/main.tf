# DB Subnet Group (RDS는 두 개 이상의 서브넷 필요)
resource "aws_db_subnet_group" "default" {
    name       = "caloreat-db-subnet-group"
    subnet_ids = var.subnet_ids

    tags = {
        Name = "Caloreat DB subnet group"
    }
}

# PostgreSQL RDS 인스턴스 생성
resource "aws_db_instance" "default" {
  identifier           = "caloreat-db"
  allocated_storage    = 20                     # 스토리지 용량
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "16.6"                 # PostgreSQL 최신 버전
  instance_class       = "db.t3.micro"          # 프리티어/저비용 인스턴스
  db_name              = "caloreat"
  username             = "postgres"
  password             = var.db_password
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true                   # 삭제 시 스냅샷 생성 X
  publicly_accessible  = false                  # 인터넷에서 접속 금지

  vpc_security_group_ids = [var.rds_sg_id]      # ECS만 접속 가능
  db_subnet_group_name   = aws_db_subnet_group.default.name
}
