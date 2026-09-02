import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.models.video import Video
from app.services.auth_deps import get_current_user

router = APIRouter(prefix="/videos", tags=["videos"])

ALLOWED_MIMES = set(settings.ALLOWED_VIDEO_MIME_TYPES.split(","))


class UploadIntentRequest(BaseModel):
    fileName: str
    mimeType: str
    byteSize: int


class YouTubeImportRequest(BaseModel):
    url: str
    title: str | None = None


@router.post("/youtube", status_code=201)
def import_youtube_video(
    body: YouTubeImportRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    url = body.url.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    # Gracefully handle duplicate URLs
    existing = db.query(Video).filter(Video.object_key == url, Video.deleted_at.is_(None)).first()
    if existing:
        return {
            "videoId": str(existing.id),
            "title": existing.title,
            "status": existing.status,
            "message": "Video already imported"
        }

    video_title = body.title.strip() if body.title else "YouTube Video"
    video = Video(
        owner_id=user.id,
        title=video_title[:180],
        object_key=url,
        original_name="youtube",
        mime_type="video/youtube",
        byte_size=0,
        status="queued",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return {
        "videoId": str(video.id),
        "title": video.title,
        "status": video.status,
    }


@router.post("/upload")
async def upload_video_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in ("creator", "educator", "administrator", "learner"):
        raise HTTPException(status_code=403, detail="Only creators and educators can upload")
    
    file_bytes = await file.read()
    byte_size = len(file_bytes)
    if byte_size > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 500 MB)")

    import tempfile
    
    object_key = f"uploads/{user.id}/{uuid.uuid4()}/{file.filename}"
    abs_path = os.path.join(tempfile.gettempdir(), "clipmind", object_key)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "wb") as f:
        f.write(file_bytes)

    video = Video(
        owner_id=user.id,
        title=os.path.splitext(file.filename)[0][:180],
        object_key=abs_path,
        original_name=file.filename,
        mime_type=file.content_type,
        byte_size=byte_size,
        status="queued",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return {
        "videoId": str(video.id),
        "objectKey": object_key,
        "status": "queued",
    }


@router.post("/{video_id}/complete-upload")
def complete_upload(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    video.status = "queued"
    db.commit()
    return {"videoId": str(video.id), "status": video.status}


@router.get("")
def list_videos(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    videos = (
        db.query(Video)
        .filter(Video.owner_id == user.id, Video.deleted_at.is_(None))
        .order_by(Video.created_at.desc())
        .limit(100)
        .all()
    )
    return {
        "videos": [
            {
                "id": str(v.id),
                "title": v.title,
                "originalName": v.original_name,
                "status": v.status,
                "durationSeconds": v.duration_seconds,
                "mimeType": v.mime_type,
                "byteSize": v.byte_size,
                "createdAt": v.created_at.isoformat() if v.created_at else None,
            }
            for v in videos
        ]
    }


@router.get("/{video_id}")
def get_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    return {
        "id": str(video.id),
        "title": video.title,
        "description": video.description,
        "originalName": video.original_name,
        "mimeType": video.mime_type,
        "byteSize": video.byte_size,
        "durationSeconds": video.duration_seconds,
        "status": video.status,
        "createdAt": video.created_at.isoformat() if video.created_at else None,
    }


@router.patch("/{video_id}")
def update_video(
    video_id: str,
    title: str | None = None,
    description: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if title is not None:
        video.title = title[:180]
    if description is not None:
        video.description = description
    db.commit()
    return {"message": "Updated"}


@router.delete("/{video_id}")
def delete_video(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")
    video.deleted_at = datetime.now(timezone.utc)
    video.status = "deleted"
    db.commit()
    return {"message": "Deletion scheduled"}


def run_mock_pipeline(video_id: str, db: Session):
    from datetime import datetime, timezone
    from app.models.job import ProcessingJob
    from app.models.video import Video
    from app.models.transcript import Transcript, TranscriptSegment
    from app.models.summary import Summary, KeyMoment

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return

    # Update jobs to complete
    for kind in ["extract_audio", "transcribe", "summarize", "key_moments"]:
        job = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video.id,
            ProcessingJob.kind == kind
        ).first()
        if not job:
            job = ProcessingJob(video_id=video.id, kind=kind)
            db.add(job)
        job.status = "completed"
        job.progress = 100
        job.started_at = datetime.now(timezone.utc)
        job.finished_at = datetime.now(timezone.utc)
    
    # Check if transcript already exists
    transcript = db.query(Transcript).filter(Transcript.video_id == video.id, Transcript.is_current == True).first()
    if not transcript:
        transcript = Transcript(
            video_id=video.id, version=1, language="en", source="whisper",
            body="", is_current=True,
        )
        db.add(transcript)
        db.flush()

    # Generate Dynamic Mock Data based on Video Title
    title = video.title or "YouTube Video"
    title_lower = title.lower()

    if any(k in title_lower for k in ["astley", "music", "song", "video", "official", "remastered", "feat", "artist", "album", "pop"]):
        # Music Theme
        segments_data = [
            (0, 8000, f"Welcome to this special broadcast highlighting the artistic history and production of '{title}'."),
            (8500, 18000, "In this segment, we explore the creative song-writing process, the instruments, and the vocal delivery that made this release stand out."),
            (18500, 30000, "The track's signature rhythmic beat and synth hook immediately captured global charts, leading to massive global success."),
            (30500, 45000, "Beyond the music itself, the music video features iconic choreography, retro style, and stage presence characteristic of its era."),
            (45500, 60000, "In later years, the song achieved an unexpected second life online, evolving into one of the most famous internet memes of all time."),
            (60500, 75000, "This viral digital phenomenon introduced the song and the artist to a completely new generation of listeners around the world."),
            (75500, 88000, f"Thank you for watching this breakdown of '{title}'. Let us know your thoughts in the comments section below.")
        ]
        short_content = f"This video covers the history, musical production, and cultural legacy of the release '{title}'. It highlights the track's distinctive synth-pop style, its visual choreography, and its eventual digital renaissance as a massive internet meme."
        detailed_content = f"A comprehensive review of the iconic release '{title}'.\n\nKey areas discussed:\n\n1. Production & Vocal Style: Highlights the arrangement, synth hooks, and deep vocal delivery of the artist.\n2. Visual & Performance: Analyzes the unique dance choreography, visual direction, and styling shown in the video.\n3. Internet Culture Legacy: Explores how the track transitioned from a classic 80s hit into a global digital meme, creating a unique online phenomenon that keeps it relevant today.\n4. Modern Audience: Examines the song's ability to span multiple generations and bridge traditional pop success with modern social media culture."
        moments_data = [
            (0, 8000, "Introduction", "Setting the stage and introducing the release.", 0.90, 1),
            (18500, 30000, "Musical Hook Analysis", "A breakdown of the signature melody and instrumentals.", 0.88, 2),
            (30500, 45000, "Visual Choreography", "Exploring the dance styles and aesthetic direction.", 0.82, 3),
            (45500, 60000, "Internet & Meme Legacy", "How the track became a global phenomenon online.", 0.95, 4),
            (75500, 88000, "Closing Thoughts", "Summary of the track's multigenerational impact.", 0.78, 5)
        ]
    elif any(k in title_lower for k in ["python", "react", "code", "tutorial", "learn", "course", "how to", "programming", "software", "development", "js", "html"]):
        # Software/Tutorial Theme
        segments_data = [
            (0, 8000, f"Hello everyone and welcome back to the channel. Today we are diving into this tutorial on '{title}'."),
            (8500, 18000, "We will start by setting up our local development environment, installing the required packages, and initializing our project folder."),
            (18500, 30000, "The core concept we need to understand is how data flows through the application. We will configure basic state, event handlers, and data bindings."),
            (30500, 45000, "Next, we will look at how to modularize our code into clean, reusable components, adhering to industry best practices."),
            (45500, 60000, "A common trap beginners fall into is improper state synchronization. We will walk through how to debug and optimize these lifecycle hooks."),
            (60500, 75000, "Towards the end, we will cover writing basic test cases to verify our logic and ensure our code remains maintainable and bug-free."),
            (75500, 88000, f"That wraps up our session on '{title}'. Make sure to like, subscribe, and download the source files in the description.")
        ]
        short_content = f"This tutorial provides a step-by-step walkthrough of '{title}', covering environment setup, core architecture patterns, component design, state management, debugging, and unit testing."
        detailed_content = f"A structured tutorial on '{title}' designed for developers.\n\nKey Concepts Covered:\n\n1. Environment Setup: Installing tools, initializing folders, and configuring the dev server.\n2. Core Architecture: Understanding components, modular design, and unidirectional data flow.\n3. State & Event Handling: Binding user actions to state modifications and avoiding desync bugs.\n4. Debugging & Optimization: Profiling render loops and writing clean, maintainable logic.\n5. Testing & Verification: Using testing frameworks to run assertions and protect against regressions."
        moments_data = [
            (0, 8000, "Course Ingestion & Setup", "Overview of course goals and setup.", 0.92, 1),
            (18500, 30000, "State & Data Flow", "Detailed explanation of data structures and data binding.", 0.94, 2),
            (30500, 45000, "Component Design Patterns", "Guidelines on writing clean, modular components.", 0.87, 3),
            (45500, 60000, "Debugging State Sync", "Troubleshooting common render and state bugs.", 0.89, 4),
            (60500, 75000, "Testing Frameworks", "How to write and run unit tests for your code.", 0.80, 5)
        ]
    else:
        # Default Theme (General/Educational/Business)
        segments_data = [
            (0, 8000, f"Hello and welcome to this presentation. Today we are discussing key insights regarding '{title}'."),
            (8500, 18000, "First, we should establish the baseline context, including the historical trends and market conditions that led to this point."),
            (18500, 30000, "Next, we'll examine the primary data. This includes user behavior metrics, structural variables, and our core operational statistics."),
            (30500, 45000, "A key challenge we face is managing resource constraints and maintaining stable performance under concurrent workloads."),
            (45500, 60000, "To address this, we developed a series of strategic workflows designed to optimize efficiency, automate pipelines, and reduce manual overhead."),
            (60500, 75000, "The direct outcomes of these changes include faster cycle times, lower cost of operations, and a highly scalable architecture."),
            (75500, 88000, f"Thank you for attending. Let's open up the floor to any comments or questions you might have about '{title}'.")
        ]
        short_content = f"This presentation outlines the core concepts, challenges, and strategic solutions related to '{title}'. It highlights target operational metrics, automated workflows, and the benefits of a scalable system."
        detailed_content = f"An analytical review of '{title}' outlining key findings and strategic directions.\n\nSummary Points:\n\n1. Contextual Background: Market analysis and baseline definitions.\n2. Core Analytics: Examining user metrics and system data.\n3. Operational Challenges: Managing scaling bottlenecks and resource limitations.\n4. Strategic Implementations: Introducing automated pipelines and software-driven solutions.\n5. Project Outcomes: Significant improvements in efficiency, scalability, and delivery speed."
        moments_data = [
            (0, 8000, "Welcome & Context", "Setting the background and objectives.", 0.89, 1),
            (18500, 30000, "Analytical Insights", "Reviewing data structures and baseline metrics.", 0.91, 2),
            (30500, 45000, "Core Bottlenecks", "Identifying scaling challenges and performance locks.", 0.85, 3),
            (45500, 60000, "System Automation", "Explaining how the pipeline resolves manual bottlenecks.", 0.93, 4),
            (60500, 75000, "Outcome Evaluation", "Review of key efficiency and cost-saving results.", 0.81, 5)
        ]

    # Add segments if they don't exist
    existing_segs = db.query(TranscriptSegment).filter(TranscriptSegment.transcript_id == transcript.id).first()
    if not existing_segs:
        full_text_parts = []
        for i, (start, end, text) in enumerate(segments_data, start=1):
            seg = TranscriptSegment(
                transcript_id=transcript.id, sequence=i,
                start_ms=start, end_ms=end, text=text, confidence=0.92,
            )
            db.add(seg)
            full_text_parts.append(text)
        transcript.body = " ".join(full_text_parts)
        db.flush()

    # Add summaries if they don't exist
    existing_sums = db.query(Summary).filter(Summary.video_id == video.id).first()
    if not existing_sums:
        short_summary = Summary(
            video_id=video.id, transcript_id=transcript.id, version=1,
            kind="short", model_name="demo-model",
            content=short_content,
            status="ready",
        )
        detailed_summary = Summary(
            video_id=video.id, transcript_id=transcript.id, version=1,
            kind="detailed", model_name="demo-model",
            content=detailed_content,
            status="ready",
        )
        db.add(short_summary)
        db.add(detailed_summary)

    # Add key moments if they don't exist
    existing_moments = db.query(KeyMoment).filter(KeyMoment.video_id == video.id).first()
    if not existing_moments:
        for start, end, m_title, rationale, score, rank in moments_data:
            segment = db.query(TranscriptSegment).filter(
                TranscriptSegment.transcript_id == transcript.id,
                TranscriptSegment.start_ms <= start,
                TranscriptSegment.end_ms >= end
            ).first()
            # If segment is not found, map to first segment to avoid foreign key/joining issues
            segment_id = segment.id if segment else None
            if not segment_id:
                first_seg = db.query(TranscriptSegment).filter(TranscriptSegment.transcript_id == transcript.id).first()
                if first_seg:
                    segment_id = first_seg.id
            
            if segment_id:
                moment = KeyMoment(
                    video_id=video.id, transcript_segment_id=segment_id,
                    start_ms=start, end_ms=end, title=m_title,
                    rationale=rationale, score=score, rank=rank
                )
                db.add(moment)

    video.status = "ready"
    if not video.duration_seconds:
        video.duration_seconds = 88
    db.commit()


def run_pipeline_task(video_id: str):
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        from app.models.video import Video
        from app.models.job import ProcessingJob
        
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return

        # 1. Run extract_audio
        job_ext = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.kind == "extract_audio"
        ).first()
        if job_ext:
            from app.workers.extraction import extract_audio
            res = extract_audio(job_ext.id, db)
            if res.get("status") == "failed":
                raise RuntimeError(f"Audio extraction failed: {res.get('error')}")

        # 2. Run transcribe
        job_tra = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.kind == "transcribe"
        ).first()
        if job_tra:
            from app.workers.transcription import transcribe
            res = transcribe(job_tra.id, db)
            if res.get("status") == "failed":
                raise RuntimeError(f"Transcription failed: {res.get('error')}")

        # 3. Run summarize
        job_sum = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.kind == "summarize"
        ).first()
        if job_sum:
            from app.workers.summarization import summarize
            res = summarize(job_sum.id, db)
            if res.get("status") == "failed":
                raise RuntimeError(f"Summarization failed: {res.get('error')}")

        # 4. Run key_moments
        job_mom = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video_id,
            ProcessingJob.kind == "key_moments"
        ).first()
        if job_mom:
            from app.workers.key_moments import generate_key_moments
            res = generate_key_moments(job_mom.id, db)
            if res.get("status") == "failed":
                raise RuntimeError(f"Key moments failed: {res.get('error')}")

        # Complete video
        video.status = "ready"
        db.commit()

    except Exception as e:
        print(f"Error in pipeline: {e}")
        try:
            from app.models.video import Video
            video = db.query(Video).filter(Video.id == video_id).first()
            if video:
                video.status = "failed"
                db.commit()
        except:
            pass
    finally:
        db.close()


@router.post("/{video_id}/process")
def process_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    language: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.job import ProcessingJob

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    video.status = "processing"
    
    # Initialize/reset jobs
    for kind in ["extract_audio", "transcribe", "summarize", "key_moments"]:
        job = db.query(ProcessingJob).filter(
            ProcessingJob.video_id == video.id,
            ProcessingJob.kind == kind
        ).first()
        if not job:
            job = ProcessingJob(video_id=video.id, kind=kind)
            db.add(job)
        job.status = "queued"
        job.progress = 0
        job.error_code = None
        job.error_message = None
        
    db.commit()

    # Add background orchestrator
    background_tasks.add_task(run_pipeline_task, video.id)

    return {"videoId": str(video.id), "status": "processing", "message": "Processing started"}



@router.get("/{video_id}/status")
def video_status(
    video_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.job import ProcessingJob

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id and user.role != "administrator":
        raise HTTPException(status_code=403, detail="Access denied")

    jobs = (
        db.query(ProcessingJob)
        .filter(ProcessingJob.video_id == video.id)
        .order_by(ProcessingJob.created_at.desc())
        .all()
    )
    return {
        "videoStatus": video.status,
        "jobs": [
            {
                "id": str(j.id),
                "kind": j.kind,
                "status": j.status,
                "progress": j.progress,
                "errorCode": j.error_code,
            }
            for j in jobs
        ],
    }
