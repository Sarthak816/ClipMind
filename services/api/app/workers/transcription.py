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
        from faster_whisper import WhisperModel

        audio_path = f"/tmp/clipmind/{video.id}/audio.wav"
        model = WhisperModel(
            settings.WHISPER_MODEL,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
        segments_gen, info = model.transcribe(audio_path, beam_size=5)

        transcript = Transcript(
            video_id=video.id,
            version=1,
            language=info.language or "en",
            source="whisper",
            body="",
        )
        db.add(transcript)
        db.flush()

        full_text_parts = []
        for i, seg in enumerate(segments_gen, start=1):
            segment = TranscriptSegment(
                transcript_id=transcript.id,
                sequence=i,
                start_ms=int(seg.start * 1000),
                end_ms=int(seg.end * 1000),
                text=seg.text.strip(),
                confidence=round(seg.avg_logprob, 3) if seg.avg_logprob else None,
            )
            db.add(segment)
            full_text_parts.append(seg.text.strip())

        transcript.body = " ".join(full_text_parts)
        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed", "transcriptId": str(transcript.id)}

    except ImportError:
        job.status = "failed"
        job.error_code = "WHISPER_NOT_INSTALLED"
        job.error_message = "faster-whisper is not installed"
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": "faster-whisper not installed"}
    except Exception as e:
        job.status = "failed"
        job.error_code = "TRANSCRIPTION_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
