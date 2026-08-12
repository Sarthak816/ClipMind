import os
import subprocess
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.job import ProcessingJob
from app.models.video import Video
from app.models.transcript import Transcript, TranscriptSegment
from app.services.auth_deps import get_current_user, require_role

router = APIRouter(prefix="/worker", tags=["worker"])


@router.post("/extract-audio/{job_id}")
def extract_audio(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
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
        tmp_dir = f"/tmp/clipmind/{uuid.uuid4()}"
        os.makedirs(tmp_dir, exist_ok=True)
        input_path = os.path.join(tmp_dir, video.original_name)
        output_path = os.path.join(tmp_dir, "audio.wav")

        ffmpeg = settings.FFMPEG_PATH
        cmd = [
            ffmpeg, "-y", "-i", input_path,
            "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr[:500]}")

        probe_cmd = [ffmpeg, "-i", input_path, "-f", "null", "-"]
        probe = subprocess.run(
            [ffmpeg, "-i", input_path],
            capture_output=True, text=True, timeout=30,
        )
        for line in probe.stderr.split("\n"):
            if "Duration:" in line:
                dur = line.split("Duration:")[1].split(",")[0].strip()
                parts = dur.replace(",", ".").split(":")
                if len(parts) == 3:
                    secs = int(float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2]))
                    video.duration_seconds = secs
                    break

        job.status = "completed"
        job.progress = 100
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "completed", "audioPath": output_path}

    except Exception as e:
        job.status = "failed"
        job.error_code = "EXTRACTION_FAILED"
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)
        db.commit()
        return {"status": "failed", "error": str(e)[:200]}
