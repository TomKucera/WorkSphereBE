import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.DATABASE_URL: str | None = os.getenv("DATABASE_URL")
        self.JWT_SECRET_KEY: str = self._require_env("JWT_SECRET_KEY")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = self._get_positive_int(
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            60,
        )

    @staticmethod
    def _require_env(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    @staticmethod
    def _get_positive_int(name: str, default: int) -> int:
        raw_value = os.getenv(name)
        if raw_value is None:
            return default

        try:
            value = int(raw_value)
        except ValueError as exc:
            raise RuntimeError(f"Environment variable {name} must be an integer") from exc

        if value <= 0:
            raise RuntimeError(f"Environment variable {name} must be a positive integer")

        return value

settings = Settings()
