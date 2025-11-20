from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    
    db_user: str = Field(..., alias="DB_USER")
    db_password: str = Field(..., alias="DB_PASSWORD")
    db_host: str = Field("localhost", alias="DB_HOST")
    db_port: str = Field("5432", alias="DB_PORT")  # postgresql port=5432
    db_name: str = Field(..., alias="DB_NAME") #caloreat

    # JWT settings 
    # secret_key: str = Field(..., alias="SECRET_KEY")
    # jwt_algo: str = Field("HS256", alias="JWT_ALGORITHM")
    # access_token_expire_sec: int = Field(900, alias="ACCESS_TOKEN_EXPIRE")
    # refresh_token_expire_sec: int = Field(604800, alias="REFRESH_TOKEN_EXPIRE")

    class Config:
        env_file=".env"
        extra = "allow"
        populate_by_name = True #alias허용
        case_sensitive = True   #대소문자구분

    #mysql기준 -> postgresql 변경예정
    @property
    def tmp_db(self) -> str:
        return f'{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
    
    @property
    def database_url(self) -> str:
        return f'postgresql+asyncpg://{self.tmp_db}'    # postgreSQL변경필요
    
    # ai_model url
    # @property
    # def ai_model_url(self)->str:
    #     pass
    
    
settings = Settings()