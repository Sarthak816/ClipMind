from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.video import Video
from app.models.transcript import Transcript
from app.models.summary import Summary
from app.models.job import ProcessingJob
from app.services.auth_deps import get_current_user, require_role

router = APIRouter()

@router.get("/overview")
def get_overview(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    total_videos = db.query(Video).filter(Video.owner_id == user.id, Video.deleted_at.is_(None)).count()
    total_processed = db.query(Video).filter(Video.owner_id == user.id, Video.deleted_at.is_(None), Video.status == 'ready').count()
    total_duration = db.query(func.sum(Video.duration_seconds)).filter(Video.owner_id == user.id, Video.deleted_at.is_(None)).scalar() or 0
    
    user_video_ids_subquery = db.query(Video.id).filter(Video.owner_id == user.id, Video.deleted_at.is_(None)).subquery()
    total_transcripts = db.query(Transcript).filter(Transcript.video_id.in_(user_video_ids_subquery)).count()
    total_summaries = db.query(Summary).filter(Summary.video_id.in_(user_video_ids_subquery)).count()
    
    recent_videos = db.query(Video).filter(Video.owner_id == user.id, Video.deleted_at.is_(None)).order_by(Video.created_at.desc()).limit(5).all()
    recent_videos_list = [
        {
            "id": str(v.id),
            "title": v.title,
            "status": v.status,
            "createdAt": v.created_at.isoformat() if v.created_at else None,
            "durationSeconds": v.duration_seconds
        } for v in recent_videos
    ]
    
    job_stats = db.query(ProcessingJob.status, func.count(ProcessingJob.id)).filter(ProcessingJob.video_id.in_(user_video_ids_subquery)).group_by(ProcessingJob.status).all()
    processing_stats = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
    for status, count in job_stats:
        st = status
        if st == 'processing':
            st = 'running'
        if st in processing_stats:
            processing_stats[st] += count
        else:
            processing_stats[st] = count
            
    return {
        "totalVideos": total_videos,
        "totalProcessed": total_processed,
        "totalDuration": total_duration,
        "totalTranscripts": total_transcripts,
        "totalSummaries": total_summaries,
        "recentVideos": recent_videos_list,
        "processingStats": processing_stats
    }


@router.get("/admin/overview")
def get_admin_overview(user: User = Depends(require_role('administrator')), db: Session = Depends(get_db)):
    total_users = db.query(User).count()
    total_videos = db.query(Video).filter(Video.deleted_at.is_(None)).count()
    total_processed = db.query(Video).filter(Video.deleted_at.is_(None), Video.status == 'ready').count()
    
    users_by_role_raw = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {role: count for role, count in users_by_role_raw}
    
    recent_activity = db.query(Video).filter(Video.deleted_at.is_(None)).order_by(Video.created_at.desc()).limit(10).all()
    recent_activity_list = [
        {
            "id": str(v.id),
            "title": v.title,
            "status": v.status,
            "createdAt": v.created_at.isoformat() if v.created_at else None,
            "durationSeconds": v.duration_seconds
        } for v in recent_activity
    ]
    
    job_stats_raw = db.query(ProcessingJob.status, func.count(ProcessingJob.id)).group_by(ProcessingJob.status).all()
    job_stats = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
    for status, count in job_stats_raw:
        st = status
        if st == 'processing':
            st = 'running'
        if st in job_stats:
            job_stats[st] += count
        else:
            job_stats[st] = count
            
    return {
        "totalUsers": total_users,
        "totalVideos": total_videos,
        "totalProcessed": total_processed,
        "usersByRole": users_by_role,
        "recentActivity": recent_activity_list,
        "jobStats": job_stats
    }
