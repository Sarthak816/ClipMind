import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    moment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("key_moments.id", ondelete="SET NULL"),
        nullable=True,
    )
    note = Column(String(500), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "video_id", "moment_id", name="uq_bookmark_user_video_moment"
        ),
    )


class ViewEvent(Base):
    __tablename__ = "view_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    video_id = Column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    event_type = Column(
        Enum(
            "opened",
            "searched",
            "timestamp_clicked",
            "bookmarked",
            name="event_type",
        ),
        nullable=False,
    )
    occurred_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    action = Column(String(80), nullable=False)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    ip_hash = Column(String(128), nullable=True)
    metadata = Column(Text, nullable=True)
    occurred_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class VideoAccess(Base):
    __tablename__ = "video_access"

    video_id = Column(
        UUID(as_uuid=True),
        ForeignKey("videos.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    granted_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    permission = Column(
        Enum("view", name="access_permission"), nullable=False, default="view"
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
