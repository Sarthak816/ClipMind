import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "",
    )
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MINUTES: int = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "1440"))
    JWT_REFRESH_TTL_DAYS: int = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "clipmind")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    MAX_UPLOAD_BYTES: int = 500 * 1024 * 1024
    
    # Cloudflare R2 Storage
    R2_ACCOUNT_ID: str = os.getenv("R2_ACCOUNT_ID", "")
    R2_ACCESS_KEY_ID: str = os.getenv("R2_ACCESS_KEY_ID", "")
    R2_SECRET_ACCESS_KEY: str = os.getenv("R2_SECRET_ACCESS_KEY", "")
    R2_BUCKET_NAME: str = os.getenv("R2_BUCKET_NAME", "clipmind-storage")

    class Config: MAX_DURATION_SECONDS: int = int(os.getenv("MAX_DURATION_SECONDS", "3600"))
    ALLOWED_VIDEO_MIME_TYPES: str = os.getenv(
        "ALLOWED_VIDEO_MIME_TYPES",
        "video/mp4,video/quicktime,video/webm,video/x-msvideo",
    )
    FFMPEG_PATH: str = os.getenv("FFMPEG_PATH", "ffmpeg")
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    WHISPER_DEVICE: str = os.getenv("WHISPER_DEVICE", "cpu")
    WHISPER_COMPUTE_TYPE: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
    SUMMARY_MODEL_NAME: str = os.getenv(
        "SUMMARY_MODEL_NAME", "facebook/bart-large-cnn"
    )
    SUMMARY_MAX_INPUT_TOKENS: int = int(
        os.getenv("SUMMARY_MAX_INPUT_TOKENS", "1024")
    )
    SUMMARY_TIMEOUT_SECONDS: int = int(os.getenv("SUMMARY_TIMEOUT_SECONDS", "120"))
    WORKER_POLL_SECONDS: int = int(os.getenv("WORKER_POLL_SECONDS", "2"))
    JOB_MAX_ATTEMPTS: int = int(os.getenv("JOB_MAX_ATTEMPTS", "2"))
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "clipmind.db")
        return f"sqlite:///{os.path.abspath(db_path)}"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


settings = Settings()
