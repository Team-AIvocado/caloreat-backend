# Caloreat Backend API

Caloreat 프로젝트의 백엔드 API 서버입니다. 음식 이미지를 분석하여 영양 정보를 제공하고, 사용자의 건강 상태를 관리합니다.

## Tech Stack

- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (Async)
- **Migration**: Alembic
- **Infrastructure**: AWS (ECS Fargate, ECR, RDS, ALB, S3)
- **IaC**: Terraform
- **CI/CD**: GitHub Actions

## 로컬 개발

### 1. Prerequisites
- Python 3.12+
- Docker & Docker Compose
- [uv](https://github.com/astral-sh/uv) (Python 패키지 매니저)

### 2. 실행 방법 (Docker)
가장 쉬운 방법은 Docker Compose를 사용하는 것입니다.

```bash
# 컨테이너 빌드 및 실행
docker-compose up --build
```
서버가 시작되면 [http://localhost:8000/docs](http://localhost:8000/docs) 에서 API 문서를 확인할 수 있습니다.

### 3. 실행 방법 (Local)
로컬 환경에서 직접 실행하려면 다음 단계를 따르세요.

```bash
# 의존성 설치
uv sync

# 서버 실행
uv run uvicorn main:app --port 8000 --reload

# 또는
uv run main.py
```

### 4. 테스트 실행
```bash
uv run pytest
```

## AWS 배포

이 프로젝트는 **Terraform**을 사용하여 AWS 인프라를 프로비저닝하고, **GitHub Actions**를 통해 자동 배포됩니다.

### 1. 인프라 구축
`infra/` 디렉토리의 Terraform 코드를 사용하여 AWS 리소스를 생성합니다.

**간편 설치 스크립트 사용:**
```bash
./setup_infra.sh
```
스크립트가 실행되면 DB 비밀번호를 입력하고, Terraform이 자동으로 리소스를 생성합니다.

**수동 실행:**
```bash
cd infra
terraform init
terraform apply
```
### 2. 리소스 삭제 (비용 절약)
테스트가 끝나면 반드시 리소스를 삭제해야 요금이 청구되지 않습니다.

```bash
cd infra
terraform destroy
# DB 비밀번호 입력 필요
```

### 3. CI/CD 파이프라인
- **CI (`ci.yml`)**: `dev` 또는 `main` 브랜치에 푸시되면 테스트(`pytest`)가 자동으로 실행됩니다.
- **CD (`deploy.yml`)**: `aws-test` 브랜치에 푸시되면 다음 과정이 진행됩니다.
    1.  Docker 이미지 빌드
    2.  AWS ECR로 이미지 푸시
    3.  AWS ECS 서비스 업데이트 (새 이미지 배포)
    4.  컨테이너 시작 시 `alembic upgrade head` 자동 실행 (DB 마이그레이션)



## Project Structure

```
.
├── .github/workflows/   # CI/CD 설정 (ci.yml, deploy.yml)
├── app/                 # 애플리케이션 코드 (Routers, Models, Schemas)
├── infra/               # Terraform 인프라 코드 (main.tf)
├── tests/               # Pytest 테스트 코드
├── alembic/             # DB 마이그레이션 스크립트
├── Dockerfile           # Docker 이미지 빌드 설정
├── entrypoint.sh        # 컨테이너 시작 스크립트 (Migration + App Start)
├── main.py              # FastAPI 진입점
└── setup_infra.sh       # 인프라 간편 설치 스크립트
```
