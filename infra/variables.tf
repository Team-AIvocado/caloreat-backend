# 변수 정의

# DB 비밀번호 -> 코드에 하드코딩(프로그램 안의 값을 코드에 직접 박아 넣는 것) 방지
variable "db_password" {
    description = "Password for the RDS database"
    type        = string
    sensitive   = true     # Terraform 출력에 노출 방지
}
