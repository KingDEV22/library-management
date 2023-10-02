from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    DB_URL: str
    MONGODB_DATABASE: str
    USER_COLLECTION:str
    BOOK_COLLECTION:str
    ISSUE_COLLECTION:str
    REFRESH_TOKEN_EXPIRES_IN: int
    ACCESS_TOKEN_EXPIRES_IN: int
    CLIENT_ORIGIN: str
    class Config:
        env_file = './.env'

settings = Settings()