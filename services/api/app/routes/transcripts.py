from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.transcript import Transcript, TranscriptSegment
from app.models.video import Video
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/videos", tags=["transcripts"])


def _check_access(video_id: str, user, db: Session) -> Video:
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    return video


@router.get("/{video_id}/transcripts/current")
def get_current_transcript(
    video_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_access(video_id, user, db)
    transcript = (
        db.query(Transcript)
        .filter(Transcript.video_id == video_id, Transcript.is_current == True)
        .first()
    )
    if not transcript:
        raise HTTPException(status_code=404, detail="No transcript available")
    segments = (
        db.query(TranscriptSegment)
        .filter(TranscriptSegment.transcript_id == transcript.id)
        .order_by(TranscriptSegment.sequence)
        .all()
    )
    return {
        "id": str(transcript.id),
        "version": transcript.version,
        "language": transcript.language,
        "source": transcript.source,
        "body": transcript.body,
        "segments": [
            {
                "id": str(s.id),
                "sequence": s.sequence,
                "startMs": s.start_ms,
                "endMs": s.end_ms,
                "text": s.text,
                "confidence": float(s.confidence) if s.confidence else None,
            }
            for s in segments
        ],
    }


@router.get("/{video_id}/search")
def search_transcript(
    video_id: str,
    q: str = Query(..., min_length=1),
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _check_access(video_id, user, db)
    transcript = (
        db.query(Transcript)
        .filter(Transcript.video_id == video_id, Transcript.is_current == True)
        .first()
    )
    if not transcript:
        raise HTTPException(status_code=404, detail="No transcript available")
    segments = (
        db.query(TranscriptSegment)
        .filter(
            TranscriptSegment.transcript_id == transcript.id,
            TranscriptSegment.text.ilike(f"%{q}%"),
        )
        .order_by(TranscriptSegment.sequence)
        .limit(50)
        .all()
    )
    return {
        "query": q,
        "results": [
            {
                "sequence": s.sequence,
                "startMs": s.start_ms,
                "endMs": s.end_ms,
                "text": s.text,
            }
            for s in segments
        ],
    }
