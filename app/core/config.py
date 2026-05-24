from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    max_retries: int = 3
    retry_delay: float = 2.0
    request_timeout: int = 30
    rate_limit_delay: float = 1.5
    max_pages: int = 20
    use_playwright_fallback: bool = True
    log_level: str = "INFO"
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    class Config:
        env_file = ".env"

settings = Settings()