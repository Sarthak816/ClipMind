import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://clipmind:changeme@localhost:5432/clipmind",
    )
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MINUTES: int = int(os.getenv("JWT_ACCESS_TTL_MINUTES", "15"))
    JWT_REFRESH_TTL_DAYS: int = int(os.getenv("JWT_REFRESH_TTL_DAYS", "7"))
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "")
    S3_BUCKET: str = os.getenv("S3_BUCKET", "clipmind")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "")
    S3_REGION: str = os.getenv("S3_REGION", "us-east-1")
    MAX_UPLOAD_BYTES: int = int(os.getenv("MAX_UPLOAD_BYTES", str(500 * 1024 * 1024)))
    MAX_DURATION_SECONDS: int = int(os.getenv("MAX_DURATION_SECONDS", "3600"))
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


settings = Settings()
