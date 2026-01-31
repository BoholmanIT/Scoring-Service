from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    app_host: str = "0.0.0.0"
    app_port: int = 8002
    
    class Config:
        env_file = ".env"

settings = Settings()