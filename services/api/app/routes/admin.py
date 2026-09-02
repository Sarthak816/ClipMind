from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.job import ProcessingJob
from app.models.video import Video
from app.services.auth_deps import require_role

router = APIRouter()

@router.get("/users")
def get_admin_users(user: User = Depends(require_role('administrator')), db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "displayName": u.display_name,
            "role": u.role,
            "status": u.status,
            "createdAt": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]

@router.get("/jobs")
def get_admin_jobs(user: User = Depends(require_role('administrator')), db: Session = Depends(get_db)):
    results = db.query(ProcessingJob, Video).join(Video, ProcessingJob.video_id == Video.id).order_by(ProcessingJob.created_at.desc()).limit(100).all()
    return [
        {
            "id": str(job.id),
            "videoId": str(video.id),
            "videoTitle": video.title,
            "kind": job.kind,
            "status": job.status,
            "attempt": job.attempt,
            "progress": job.progress,
            "errorMessage": job.error_message,
            "startedAt": job.started_at.isoformat() if job.started_at else None,
            "finishedAt": job.finished_at.isoformat() if job.finished_at else None,
            "createdAt": job.created_at.isoformat() if job.created_at else None
        }
        for job, video in results
    ]
