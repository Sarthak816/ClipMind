import uuid
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), nullable=False, index=True)
    transcript_id = Column(String(36), nullable=False)
    version = Column(Integer, nullable=False, default=1)
    kind = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    model_name = Column(String(160), nullable=False)
    status = Column(String(20), nullable=False, default="ready")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KeyMoment(Base):
    __tablename__ = "key_moments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    video_id = Column(String(36), nullable=False, index=True)
    transcript_segment_id = Column(String(36), nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    title = Column(String(180), nullable=False)
    rationale = Column(Text, nullable=False)
    score = Column(Numeric(5, 4), nullable=False)
    rank = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(String(255), unique=True, nullable=False)


class VideoKeyword(Base):
    __tablename__ = "video_keywords"

    video_id = Column(String(36), primary_key=True)
    keyword_id = Column(String(36), primary_key=True)
    score = Column(Numeric(5, 4), nullable=True)
