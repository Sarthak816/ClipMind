from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.job import ProcessingJob
from app.models.summary import KeyMoment
from app.models.transcript import Transcript, TranscriptSegment
from app.models.video import Video

router = APIRouter(prefix="/worker", tags=["worker-moments"])


@router.post("/key-moments/{job_id}")
def generate_key_moments(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job or job.kind != "key_moments":
        raise HTTPException(status_code=404, detail="Key moments job not found")
    if job.status != "queued":
        raise HTTPException(status_code=409, detail="Job not in queued state")

    video = db.query(Video).filter(Video.id == job.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    transcript = (
        db.query(Transcript)
        .filter(Transcript.video_id == video.id, Transcript.is_current == True)
        .first()
    )
    if not transcript:
        job.status = "failed"
        job.error_code = "NO_TRANSCRIPT"
        job.error_message = "No transcript available"
        db.commit()
        return {"status": "failed", "error": "No transcript"}

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.attempt += 1
    db.commit()

    try:
        segments = (
            db.query(TranscriptSegment)
            .filter(TranscriptSegment.transcript_id == transcript.id)
            .order_by(TranscriptSegment.sequence)
            .all()
        )

        scored = []
        for seg in segments:
            words = seg.text.split()
            word_count = len(words)
            avg_word_len = sum(len(w) for w in words) / max(word_count, 1)
            question_bonus = 2.0 if "?" in seg.text else 0
            keyword_bonus = sum(
                0.5
                for kw in [
                    "important", "decision", "action", "key", "summary",
                    "conclusion", "next", "deadline", "plan", "result",
                ]
                if kw in seg.text.lower()
            )
            score = min(
                1.0,
                (word_count * 0.02 + avg_word_len * 0.05 + question_bonus + keyword_bonus) / 5.0,
            )
            scored.append((seg, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:5]

        for rank, (seg, score) in enumerate(top, start=1):
            moment = KeyMoment(
                video_id=video.id,
                transcript_segment_id=seg.id,
                start_ms=seg.start_ms,
                end_ms=seg.end_ms,
                title=seg.text[:180],
                rationale=f"Score based on length, vocabulary richness, and keyword signals (score: {score:.2f})",
                score=score,
                rank=rank,
            )
            db.add(moment)

        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed", "momentsGenerated": len(top)}

    except Exception as e:
        job.status = "failed"
        job.error_code = "MOMENTS_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
