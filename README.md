# Caloreat Backend API

**Caloreat** 프로젝트의 백엔드 서버 저장소입니다.  
음식 이미지를 분석하여 영양 정보를 제공하고, 사용자의 건강 상태를 관리하는 RESTful API를 제공합니다.

---

## 1. Quick Start

로컬 개발 환경 설정부터 서버 실행까지의 단계입니다.

### Prerequisites

- **Python 3.12+**, **Docker** (DB 실행용), **[uv](https://github.com/astral-sh/uv)** (필수)

### Installation

```bash
# 1. Clone & Setup
git clone https://github.com/Team-AIvocado/caloreat-backend.git
cd caloreat-backend

# 2. Install Dependencies
uv sync

# 3. Env Setup
cp .env.example .env
```

> **Note**: 필수 key 값은 **[팀 디스코드 중요-자료]** 채널을 참조하세요.

### Run (Local Recommended)

API 서버는 로컬에서, DB는 도커로 실행합니다.

```bash
# 1. Start DB & Migrate
docker-compose up -d db
uv run alembic upgrade head

# 2. Run API Server (Port: 8000)
uv run uvicorn main:app --port 8000 --reload
```

> **선택사항: AI Module (Port: 8001)**  
> 외부 Repo의 AI 서버가 필요하다면 실행하세요 (`.env`의 `AI_SERVICE_URL` 참조).
>
> ```bash
> uv run uvicorn main:app --port 8001 --reload
> ```

### Run (Full Docker)

```bash
docker-compose up --build
```

- **API Docs**: `http://localhost:8000/docs` 또는 `[서버주소]/docs`

---

## 2. Development

### Testing

비동기 테스트를 위해 반드시 `uv run`을 사용해야 합니다.

```bash
uv run pytest
```

### DB Migration

스키마 변경(`app/db/models`) 시 마이그레이션 파일을 생성하고 적용합니다.

```bash
# 1. Generate Revision (Message in English)
uv run alembic revision --autogenerate -m "describe_changes_in_english"

# 2. Apply to DB
uv run alembic upgrade head
```

---

## 3. Overview

이 프로젝트는 **FastAPI (Async)** 기반의 계층형 아키텍처(Layered Architecture)를 따릅니다.

### Key Features

- **식단 이미지 파이프라인**: 업로드 → 임시저장 → AI 감지 → S3 업로드 (TMP 파일 자동 관리)
- **영양소 분석**: 외부 AI 서비스 연동 (음식명/영양소 추출)
- **건강 관리**: 사용자 프로필 및 식단 로그 CRUD

### Architecture

1.  **Router**: 요청 파싱, 검증 (`routers/`)
2.  **Service**: 비즈니스 로직, 트랜잭션 (`services/`)
3.  **CRUD**: DB 접근 (`db/crud/`)
4.  **Model**: 데이터 정의 (`db/models/`, `db/schemas/`)

상세 원칙: `docs/backend_design_principles.md`

---

## 4. Tech Stack

| Category      | Technology                      | Note                          |
| :------------ | :------------------------------ | :---------------------------- |
| **Framework** | **FastAPI**                     | Python 3.12+                  |
| **Manager**   | **uv**                          | Fast Python Package Installer |
| **DB / ORM**  | **PostgreSQL** / **SQLAlchemy** | Async Session                 |
| **Infra**     | **AWS (ECS, S3)**               | Terraform Managed             |

---

## 5. Infrastructure & Docs

### Infrastructure

AWS 리소스는 `infra/`의 Terraform 코드로 관리됩니다.

> [!CAUTION] > **리소스 삭제 (비용 절약)**: 테스트 종료 후 반드시 리소스를 정리하세요.
>
> ```bash
> cd infra && terraform destroy
> ```

### API Contract

상세 명세는 노션, 실시간 테스트는 Swagger를 이용하세요.

- 📄 **[API 상세 명세서 (Notion)](https://www.notion.so/Caloreat-API-2be7c000046f80d3ae69c2c9d34d5b77?source=copy_link)**
- ⚡ **Swagger UI**: `http://localhost:8000/docs`

### Project Structure

```
.
├── .github/             # CI/CD
├── app/
│   ├── core/            # Config
│   ├── db/              # Models, CRUD
│   ├── routers/         # Endpoints
│   └── services/        # Logic
├── infra/               # Terraform
├── tests/               # Pytest
└── main.py              # Entrypoint
```
