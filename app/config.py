from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DB_URL: str
    MONGODB_DATABASE: str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    CLIENT_ORIGIN: str
    class Config:
        env_file = './.env'

settings = Settings()