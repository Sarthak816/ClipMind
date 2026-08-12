import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    transcript_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = Column(Integer, nullable=False, default=1)
    kind = Column(Enum("short", "detailed", name="summary_kind"), nullable=False)
    content = Column(Text, nullable=False)
    model_name = Column(String(160), nullable=False)
    status = Column(
        Enum("ready", "failed", name="summary_status"), nullable=False, default="ready"
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            "video_id",
            "transcript_id",
            "version",
            "kind",
            name="uq_summary_video_transcript_version_kind",
        ),
    )


class KeyMoment(Base):
    __tablename__ = "key_moments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    transcript_segment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcript_segments.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    title = Column(String(180), nullable=False)
    rationale = Column(Text, nullable=False)
    score = Column(Numeric(5, 4), nullable=False)
    rank = Column(SmallInteger, nullable=False)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("video_id", "rank", name="uq_moment_video_rank"),
    )


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String(255), unique=True, nullable=False)


class VideoKeyword(Base):
    __tablename__ = "video_keywords"

    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
    )
    keyword_id = Column(
        UUID(as_uuid=True),
        ForeignKey("keywords.id", ondelete="CASCADE"),
        primary_key=True,
    )
    score = Column(Numeric(5, 4), nullable=True)
