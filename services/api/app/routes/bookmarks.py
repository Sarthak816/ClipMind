from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.video import Video
from app.models.activity import Bookmark
from app.services.auth_deps import get_current_user

router = APIRouter()

class BookmarkCreate(BaseModel):
    videoId: str
    momentId: str | None = None
    note: str | None = None


@router.post("")
def create_bookmark(body: BookmarkCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check for duplicate
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == user.id,
        Bookmark.video_id == body.videoId,
        Bookmark.moment_id == body.momentId
    ).first()
    
    if existing:
        return {
            "id": str(existing.id),
            "userId": existing.user_id,
            "videoId": existing.video_id,
            "momentId": existing.moment_id,
            "note": existing.note,
            "createdAt": existing.created_at.isoformat() if existing.created_at else None
        }
        
    bookmark = Bookmark(
        user_id=user.id,
        video_id=body.videoId,
        moment_id=body.momentId,
        note=body.note
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    
    return {
        "id": str(bookmark.id),
        "userId": bookmark.user_id,
        "videoId": bookmark.video_id,
        "momentId": bookmark.moment_id,
        "note": bookmark.note,
        "createdAt": bookmark.created_at.isoformat() if bookmark.created_at else None
    }


@router.get("")
def list_bookmarks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(Bookmark, Video).join(Video, Bookmark.video_id == Video.id).filter(
        Bookmark.user_id == user.id
    ).order_by(Bookmark.created_at.desc()).all()
    
    bookmarks = []
    for bookmark, video in results:
        bookmarks.append({
            "id": str(bookmark.id),
            "videoId": str(video.id),
            "videoTitle": video.title,
            "videoStatus": video.status,
            "momentId": bookmark.moment_id,
            "note": bookmark.note,
            "createdAt": bookmark.created_at.isoformat() if bookmark.created_at else None
        })
    return bookmarks


@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    bookmark = db.query(Bookmark).filter(Bookmark.id == bookmark_id, Bookmark.user_id == user.id).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
        
    db.delete(bookmark)
    db.commit()
    return {"message": "Bookmark deleted"}
