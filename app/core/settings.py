from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from datetime import timedelta


class Settings(BaseSettings):

    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: str = Field("5432", alias="DB_PORT")  # postgresql port=5432
    db_name: str = Field(..., alias="DB_NAME")  # caloreat

    # JWT settings
    secret_key: str = Field(..., alias="SECRET_KEY")
    jwt_algo: str = Field("HS256", alias="JWT_ALGORITHM")
    access_token_expire_sec: int = Field(
        ..., alias="ACCESS_TOKEN_EXPIRE"
    )  # 15분 (900초)
    refresh_token_expire_sec: int = Field(
        ..., alias="REFRESH_TOKEN_EXPIRE"
    )  # 7일(604800)

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        populate_by_name=True,  # alias허용
        case_sensitive=True,  # 대소문자구분
    )

    # mysql기준 -> postgresql 변경예정
    @property
    def tmp_db(self) -> str:
        return f"{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.tmp_db}"  # postgreSQL변경필요

    # token expire
    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(seconds=self.access_token_expire_sec)

    @property
    def refresh_token_expire(self) -> timedelta:
        return timedelta(seconds=self.refresh_token_expire_sec)

    # AI Model URLs
    ai_detection_url: str = Field(..., alias="AI_DETECTION_URL")
    ai_analysis_url: str = Field(..., alias="AI_ANALYSIS_URL")

    # AWS S3 설정
    aws_access_key_id: str = Field(..., alias="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., alias="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("ap-northeast-2", alias="AWS_REGION")
    s3_bucket_name: str = Field(..., alias="S3_BUCKET_NAME")

    def inference_url(self, version: str, path: str) -> str:
        """
        version: "v1", "v2", "v3", "v4"
        path: "analyze", "analyze-url"
        """
        base = self.ai_detection_url.rstrip("/")
        return f"{base}/api/inference/{version}/{path}"

    # llm url은 일단 하드코딩
    # 추후 버전, 모델 변경시 수정 nutrition analysis url
    # def llm_url(self, version: str, path: str) -> str:
    #     base = self.ai_analysis_url.rstrip("/")
    #     return f"{base}/api/llm/{version}/{path}"


settings = Settings()
