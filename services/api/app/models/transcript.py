import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    version = Column(Integer, nullable=False, default=1)
    language = Column(String(12), nullable=False, default="en")
    source = Column(
        Enum("whisper", "human_edit", name="transcript_source"),
        nullable=False,
        default="whisper",
    )
    body = Column(Text, nullable=False, default="")
    created_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    is_current = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("video_id", "version", name="uq_transcript_video_version"),
    )


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        nullable=False,
    )
    sequence = Column(Integer, nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    confidence = Column(Numeric(4, 3), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "transcript_id", "sequence", name="uq_segment_transcript_sequence"
        ),
    )
