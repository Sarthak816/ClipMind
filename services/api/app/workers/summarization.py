from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.job import ProcessingJob
from app.models.summary import Summary
from app.models.transcript import Transcript, TranscriptSegment
from app.models.video import Video

router = APIRouter(prefix="/worker", tags=["worker-summarize"])


@router.post("/summarize/{job_id}")
def summarize(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job or job.kind != "summarize":
        raise HTTPException(status_code=404, detail="Summarize job not found")
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
        job.error_message = "No transcript available for summarization"
        db.commit()
        return {"status": "failed", "error": "No transcript"}

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.attempt += 1
    db.commit()

    try:
        from transformers import pipeline

        text = transcript.body[:4096]
        summarizer = pipeline(
            "summarization",
            model=settings.SUMMARY_MODEL_NAME,
        )

        short_result = summarizer(
            text,
            max_length=150,
            min_length=30,
            do_sample=False,
        )
        short_content = short_result[0]["summary_text"]

        detailed_result = summarizer(
            text,
            max_length=512,
            min_length=100,
            do_sample=False,
        )
        detailed_content = detailed_result[0]["summary_text"]

        latest_version = (
            db.query(Summary)
            .filter(Summary.video_id == video.id)
            .order_by(Summary.version.desc())
            .first()
        )
        next_version = (latest_version.version + 1) if latest_version else 1

        short = Summary(
            video_id=video.id,
            transcript_id=transcript.id,
            version=next_version,
            kind="short",
            content=short_content,
            model_name=settings.SUMMARY_MODEL_NAME,
            status="ready",
        )
        detailed = Summary(
            video_id=video.id,
            transcript_id=transcript.id,
            version=next_version,
            kind="detailed",
            content=detailed_content,
            model_name=settings.SUMMARY_MODEL_NAME,
            status="ready",
        )
        db.add(short)
        db.add(detailed)
        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed"}

    except ImportError:
        job.status = "failed"
        job.error_code = "TRANSFORMERS_NOT_INSTALLED"
        job.error_message = "transformers is not installed"
        db.commit()
        return {"status": "failed", "error": "transformers not installed"}
    except Exception as e:
        job.status = "failed"
        job.error_code = "SUMMARY_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
