from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    debug: bool = True
    port: int = 4321

    app_version: str = "1.0.0"
    app_title: str = "Vanna SQL Assistant"
    app_url: str = "http://localhost:4321"
    origin_url: str = "http://localhost:8000"

    model_name: str
    sqlite_path: Optional[str]
    chroma_folder: Optional[str]
    static_folder: str = "static"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
