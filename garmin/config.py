from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GARMIN_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    email: str | None = None
    password: str | None = None
    tokenstore: Path = Path.home() / ".garmin" / "tokens"
    db_path: Path = Path.home() / ".garmin" / "garmin.db"
    training_lookback_days: int = 30
    request_delay: float = 0.3
    login_retries: int = 1

    @property
    def db_url(self) -> str:
        return f"sqlite:///{self.db_path}"
