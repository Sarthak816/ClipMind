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


def get_ffmpeg_path():
    # 1. Check default settings
    ffmpeg = settings.FFMPEG_PATH
    try:
        subprocess.run([ffmpeg, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ffmpeg
    except FileNotFoundError:
        pass

    # 2. Check "ffmpeg"
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "ffmpeg"
    except FileNotFoundError:
        pass

    # 3. Search winget path
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\LENOVO")
    winget_packages_dir = os.path.join(user_profile, "AppData", "Local", "Microsoft", "WinGet", "Packages")
    if os.path.exists(winget_packages_dir):
        for root, dirs, files in os.walk(winget_packages_dir):
            if "ffmpeg.exe" in files:
                ffmpeg_path = os.path.join(root, "ffmpeg.exe")
                try:
                    subprocess.run([ffmpeg_path, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return ffmpeg_path
                except:
                    pass

    # 4. Check other common paths
    common_paths = [
        "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\ffmpeg\\bin\\ffmpeg.exe",
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p

    return "ffmpeg"


@router.post("/extract-audio/{job_id}")
def extract_audio(
    job_id: str,
    db: Session = Depends(get_db),
):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "queued" and job.status != "running":
        pass

    video = db.query(Video).filter(Video.id == job.video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    job.attempt += 1
    db.commit()

    ffmpeg_bin = get_ffmpeg_path()

    try:
        tmp_dir = f"/tmp/clipmind/{video.id}"
        os.makedirs(tmp_dir, exist_ok=True)
        output_path = os.path.join(tmp_dir, "audio.wav")

        if video.mime_type == "video/youtube":
            youtube_url = video.object_key
            
            # Use yt-dlp to download and convert to wav
            import sys
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "-x",
                "--audio-format", "wav",
                "--ffmpeg-location", ffmpeg_bin,
                "--js-runtimes", "node",
                "--cookies-from-browser", "chrome",
                "--cookies-from-browser", "edge",
                "-o", os.path.join(tmp_dir, "audio.%(ext)s"),
                youtube_url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                raise RuntimeError(f"yt-dlp failed: {result.stderr[:500]}")

            # Verify and rename if needed
            if not os.path.exists(output_path):
                for f in os.listdir(tmp_dir):
                    if f.startswith("audio.") and f.endswith(".wav"):
                        if os.path.join(tmp_dir, f) != output_path:
                            os.rename(os.path.join(tmp_dir, f), output_path)
                            break

            # Try to fetch title and duration
            meta_cmd = [
                sys.executable, "-m", "yt_dlp",
                "--ffmpeg-location", ffmpeg_bin,
                "--print", "%(title)s",
                "--print", "%(duration)s",
                youtube_url
            ]
            meta_res = subprocess.run(meta_cmd, capture_output=True, text=True, timeout=30)
            if meta_res.returncode == 0:
                meta_lines = meta_res.stdout.strip().split("\n")
                if len(meta_lines) >= 2:
                    video.title = meta_lines[0][:180]
                    try:
                        video.duration_seconds = int(float(meta_lines[1]))
                    except:
                        pass
        else:
            # Local uploaded video file
            input_path = video.object_key
            if not os.path.isabs(input_path):
                input_path = os.path.join("/tmp/clipmind", video.object_key)
            
            if not os.path.exists(input_path):
                # Fallback: if local file is missing, we create a fake WAV to let pipeline run
                # but let's see if we should throw error
                raise FileNotFoundError(f"Source video file not found at: {input_path}")

            cmd = [
                ffmpeg_bin, "-y", "-i", input_path,
                "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
                output_path,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg failed: {result.stderr[:500]}")

            # Get duration
            probe = subprocess.run(
                [ffmpeg_bin, "-i", input_path],
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
