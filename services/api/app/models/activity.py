import uuid
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    video_id = Column(String(36), nullable=False, index=True)
    moment_id = Column(String(36), nullable=True)
    note = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ViewEvent(Base):
    __tablename__ = "view_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    video_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(30), nullable=False)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_id = Column(String(36), nullable=True)
    action = Column(String(80), nullable=False)
    entity_type = Column(String(40), nullable=False)
    entity_id = Column(String(36), nullable=True)
    ip_hash = Column(String(128), nullable=True)
    metadata_ = Column("metadata", Text, nullable=True)
    occurred_at = Column(DateTime(timezone=True), server_default=func.now())


class VideoAccess(Base):
    __tablename__ = "video_access"

    video_id = Column(String(36), primary_key=True)
    user_id = Column(String(36), primary_key=True)
    granted_by = Column(String(36), nullable=False)
    permission = Column(String(20), nullable=False, default="view")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
