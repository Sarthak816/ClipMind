from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.models.user import User
from app.models.video import Video
from app.models.activity import ViewEvent
from app.services.auth_deps import get_current_user

router = APIRouter()

class ViewEventCreate(BaseModel):
    videoId: str

@router.post("/view")
def record_view(body: ViewEventCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    view = ViewEvent(
        user_id=user.id,
        video_id=body.videoId,
        event_type='view'
    )
    db.add(view)
    db.commit()
    return {"message": "recorded"}

@router.get("")
def list_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Group by video_id to get the latest view per video
    subquery = db.query(
        ViewEvent.video_id,
        func.max(ViewEvent.occurred_at).label("last_viewed")
    ).filter(
        ViewEvent.user_id == user.id,
        ViewEvent.event_type == 'view'
    ).group_by(ViewEvent.video_id).subquery()
    
    results = db.query(Video, subquery.c.last_viewed).join(
        subquery, Video.id == subquery.c.video_id
    ).order_by(subquery.c.last_viewed.desc()).limit(50).all()
    
    history = []
    for video, last_viewed in results:
        history.append({
            "videoId": str(video.id),
            "title": video.title,
            "status": video.status,
            "durationSeconds": video.duration_seconds,
            "lastViewed": last_viewed.isoformat() if last_viewed else None
        })
    return history
