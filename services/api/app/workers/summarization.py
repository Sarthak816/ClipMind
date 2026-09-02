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
        from groq import Groq

        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment.")

        client = Groq(api_key=settings.GROQ_API_KEY)
        text = transcript.body[:25000] # Groq models have large context windows (8k-128k)

        # Generate short summary
        completion_short = client.chat.completions.create(
            model="groq/compound-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes concise summaries."},
                {"role": "user", "content": f"Write a 2-sentence summary of this transcript:\n\n{text}"}
            ],
            max_tokens=150,
        )
        short_content = completion_short.choices[0].message.content.strip()

        # Generate detailed summary
        completion_detailed = client.chat.completions.create(
            model="groq/compound-mini",
            messages=[
                {"role": "system", "content": "You are an expert analyst. Write a detailed, structured summary with bullet points."},
                {"role": "user", "content": f"Write a detailed summary of this transcript with key takeaways:\n\n{text}"}
            ],
            max_tokens=1000,
        )
        detailed_content = completion_detailed.choices[0].message.content.strip()

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
            model_name="groq-llama-3.1",
            status="ready",
        )
        detailed = Summary(
            video_id=video.id,
            transcript_id=transcript.id,
            version=next_version,
            kind="detailed",
            content=detailed_content,
            model_name="groq-llama-3.1",
            status="ready",
        )
        db.add(short)
        db.add(detailed)
        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed"}

    except Exception as e:
        job.status = "failed"
        job.error_code = "SUMMARY_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
