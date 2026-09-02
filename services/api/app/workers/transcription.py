import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.job import ProcessingJob
from app.models.transcript import Transcript, TranscriptSegment
from app.models.video import Video
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/worker", tags=["worker-transcribe"])


@router.post("/transcribe/{job_id}")
def transcribe(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job or job.kind != "transcribe":
        raise HTTPException(status_code=404, detail="Transcribe job not found")
    if job.status != "queued":
        raise HTTPException(status_code=409, detail="Job not in queued state")

    video = db.query(Video).filter(Video.id == job.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.attempt += 1
    db.commit()

    try:
        from groq import Groq
        import json

        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")

        client = Groq(api_key=settings.GROQ_API_KEY)
        audio_path = f"/tmp/clipmind/{video.id}/audio.wav"
        
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
            )
            
        # The transcription object has a text attribute and a segments attribute
        transcript = Transcript(
            video_id=video.id,
            version=1,
            language=transcription.language if hasattr(transcription, 'language') else "en",
            source="groq-whisper",
            body=transcription.text,
        )
        db.add(transcript)
        db.flush()

        segments = getattr(transcription, 'segments', [])
        for i, seg in enumerate(segments, start=1):
            # Groq returns dicts for segments in verbose_json in some SDK versions, or objects in others
            if isinstance(seg, dict):
                start = seg.get("start", 0)
                end = seg.get("end", 0)
                text = seg.get("text", "").strip()
                confidence = None
            else:
                start = getattr(seg, "start", 0)
                end = getattr(seg, "end", 0)
                text = getattr(seg, "text", "").strip()
                confidence = getattr(seg, "avg_logprob", None)
                if confidence is not None:
                    confidence = round(confidence, 3)

            segment = TranscriptSegment(
                transcript_id=transcript.id,
                sequence=i,
                start_ms=int(start * 1000),
                end_ms=int(end * 1000),
                text=text,
                confidence=confidence,
            )
            db.add(segment)

        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed", "transcriptId": str(transcript.id)}

    except Exception as e:
        job.status = "failed"
        job.error_code = "TRANSCRIPTION_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
