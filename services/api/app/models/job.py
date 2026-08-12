import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    kind = Column(
        Enum(
            "extract_audio",
            "transcribe",
            "summarize",
            "key_moments",
            name="job_kind",
        ),
        nullable=False,
    )
    status = Column(
        Enum(
            "queued",
            "running",
            "completed",
            "failed",
            "cancelled",
            name="job_status",
        ),
        nullable=False,
        default="queued",
    )
    attempt = Column(SmallInteger, default=0)
    progress = Column(SmallInteger, default=0)
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
