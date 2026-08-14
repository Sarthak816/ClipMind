import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.video import Video
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/videos", tags=["videos"])

ALLOWED_MIMES = set(settings.ALLOWED_VIDEO_MIME_TYPES.split(","))


class UploadIntentRequest(BaseModel):
    fileName: str
    mimeType: str
    byteSize: int


@router.post("/upload-intent")
def upload_intent(
    body: UploadIntentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in ("creator", "educator", "administrator", "learner"):
        raise HTTPException(status_code=403, detail="Only creators and educators can upload")
    if body.mimeType not in ALLOWED_MIMES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {body.mimeType}")
    if body.byteSize > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 500 MB)")

    object_key = f"uploads/{user.id}/{uuid.uuid4()}/{body.fileName}"
    video = Video(
        owner_id=user.id,
        title=os.path.splitext(body.fileName)[0][:180],
        object_key=object_key,
        original_name=body.fileName,
        mime_type=body.mimeType,
        byte_size=body.byteSize,
        status="uploading",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return {
        "videoId": str(video.id),
        "objectKey": object_key,
        "status": "uploading",
    }


@router.post("/{video_id}/complete-upload")
def complete_upload(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    video.status = "queued"
    db.commit()
    return {"videoId": str(video.id), "status": video.status}


@router.get("")
def list_videos(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    videos = (
        db.query(Video)
        .filter(Video.owner_id == user.id, Video.deleted_at.is_(None))
        .order_by(Video.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "videos": [
            {
                "id": str(v.id),
                "title": v.title,
                "originalName": v.original_name,
                "status": v.status,
                "durationSeconds": v.duration_seconds,
                "mimeType": v.mime_type,
                "byteSize": v.byte_size,
                "createdAt": v.created_at.isoformat() if v.created_at else None,
            }
            for v in videos
        ]
    }


@router.get("/{video_id}")
def get_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "id": str(video.id),
        "title": video.title,
        "description": video.description,
        "originalName": video.original_name,
        "mimeType": video.mime_type,
        "byteSize": video.byte_size,
        "durationSeconds": video.duration_seconds,
        "status": video.status,
        "createdAt": video.created_at.isoformat() if video.created_at else None,
    }


@router.patch("/{video_id}")
def update_video(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if title is not None:
        video.title = title[:180]
    if description is not None:
        video.description = description
    db.commit()
    return {"message": "Updated"}


@router.delete("/{video_id}")
def delete_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    video.deleted_at = datetime.now(timezone.utc)
    video.status = "deleted"
    db.commit()
    return {"message": "Deletion scheduled"}


@router.post("/{video_id}/process")
def process_video(
    video_id: str,
    language: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.job import ProcessingJob

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    job = ProcessingJob(video_id=video.id, kind="extract_audio", status="queued")
    db.add(job)
    video.status = "processing"
    db.commit()
    return {"jobId": str(job.id), "status": "queued"}


@router.get("/{video_id}/status")
def video_status(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.job import ProcessingJob

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")

    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.video_id == video.id)
        .order_by(ProcessingJob.created_at.desc())
        .all()
    )
    return {
        "videoStatus": video.status,
        "jobs": [
            {
                "id": str(j.id),
                "kind": j.kind,
                "status": j.status,
                "progress": j.progress,
                "errorCode": j.error_code,
            }
            for j in jobs
        ],
    }
