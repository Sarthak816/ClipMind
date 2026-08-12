from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.summary import Summary, KeyMoment
from app.models.transcript import Transcript
from app.models.video import Video
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/videos", tags=["summaries"])


def _check_access(video_id: str, user, db: Session) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    return video


@router.get("/{video_id}/summaries")
def get_summaries(
    video_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_access(video_id, user, db)
    summaries = (
        db.query(Summary)
        .filter(Summary.video_id == video_id, Summary.status == "ready")
        .order_by(Summary.version.desc())
        .all()
    )
    return {
        "summaries": [
            {
                "id": str(s.id),
                "kind": s.kind,
                "content": s.content,
                "modelName": s.model_name,
                "version": s.version,
                "createdAt": s.created_at.isoformat() if s.created_at else None,
            }
            for s in summaries
        ]
    }


@router.get("/{video_id}/key-moments")
def get_key_moments(
    video_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_access(video_id, user, db)
    moments = (
        db.query(KeyMoment)
        .filter(KeyMoment.video_id == video_id)
        .order_by(KeyMoment.rank)
        .all()
    )
    return {
        "moments": [
            {
                "id": str(m.id),
                "startMs": m.start_ms,
                "endMs": m.end_ms,
                "title": m.title,
                "rationale": m.rationale,
                "score": float(m.score),
                "rank": m.rank,
            }
            for m in moments
        ]
    }
