# Docker 이미지 저장소(ECR) 생성
resource "aws_ecr_repository" "backend_repo" {
    name                 = "caloreat-backend"    # 리포지토리 이름
    image_tag_mutability = "MUTABLE"             # latest 태그 덮어쓰기 가능
    force_delete         = true                  # 삭제 시 이미지도 함께 제거 

    image_scanning_configuration {
        scan_on_push = true                      # 보안 취약점 자동 스캔
    }
}