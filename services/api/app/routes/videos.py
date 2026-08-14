import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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


@router.post("/upload-intent")
def upload_intent(
    body: UploadIntentRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.role not in ("creator", "educator", "administrator", "learner"):
        raise HTTPException(status_code=403, detail="Only creators and educators can upload")
    if body.mimeType not in ALLOWED_MIMES:
        raise HTTPException(status_code=415, detail=f"Unsupported file type: {body.mimeType}")
    if body.byteSize > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 500 MB)")

    object_key = f"uploads/{user.id}/{uuid.uuid4()}/{body.fileName}"
    video = Video(
        owner_id=user.id,
        title=os.path.splitext(body.fileName)[0][:180],
        object_key=object_key,
        original_name=body.fileName,
        mime_type=body.mimeType,
        byte_size=body.byteSize,
        status="uploading",
    )
    db.add(video)
    db.commit()
    db.refresh(video)

    return {
        "videoId": str(video.id),
        "objectKey": object_key,
        "status": "uploading",
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


@router.post("/{video_id}/process")
def process_video(
    video_id: str,
    language: str | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timezone
    from app.models.job import ProcessingJob
    from app.models.transcript import Transcript, TranscriptSegment
    from app.models.summary import Summary, KeyMoment

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video or video.deleted_at:
        raise HTTPException(status_code=404, detail="Video not found")
    if video.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    video.status = "processing"

    # Create completed jobs
    for kind in ["extract_audio", "transcribe", "summarize", "key_moments"]:
        job = ProcessingJob(
            video_id=video.id, kind=kind, status="completed",
            progress=100, started_at=datetime.now(timezone.utc),
            finished_at=datetime.now(timezone.utc),
        )
        db.add(job)

    # Create mock transcript
    transcript = Transcript(
        video_id=video.id, version=1, language="en", source="whisper",
        body="", is_current=True,
    )
    db.add(transcript)
    db.flush()

    segments_data = [
        (0, 5200, "Welcome everyone to today's session on household waste management and sustainable living practices."),
        (5500, 11200, "Today we will cover the basics of waste sorting, recycling guidelines, and how small changes in our daily habits can make a significant environmental impact."),
        (11500, 18000, "The first step in effective waste management is understanding the different categories of household waste. We have organic waste, recyclables, hazardous materials, and general waste."),
        (18500, 25000, "Organic waste includes food scraps, garden trimmings, and biodegradable materials. This type of waste can be composted and turned into nutrient-rich soil for gardening."),
        (25500, 32000, "Recyclables include paper, cardboard, glass bottles, aluminum cans, and certain plastics. It is crucial to rinse these items before placing them in the recycling bin."),
        (32500, 39000, "Hazardous materials such as batteries, electronic devices, paint, and chemicals require special disposal methods. Never throw these in regular waste bins."),
        (39500, 46000, "One common mistake people make is wish-cycling, which means putting non-recyclable items in the recycling bin hoping they will be recycled. This actually contaminates the recycling stream."),
        (46500, 53000, "To avoid wish-cycling, check your local recycling guidelines carefully. When in doubt, throw it in the general waste bin rather than contaminating the recycling."),
        (53500, 60000, "Composting at home is easier than you think. Start with a simple bin in your backyard or even a small countertop compost collector for apartment dwellers."),
        (60500, 67000, "The benefits of proper waste sorting include reduced landfill usage, lower greenhouse gas emissions, conservation of natural resources, and money saved on waste disposal."),
        (67500, 74000, "Many communities now offer curbside recycling programs. Check with your local municipality to find out what materials are accepted in your area."),
        (74500, 81000, "Remember, the goal is not perfection but progress. Even small steps like using reusable bags and bottles can make a meaningful difference over time."),
        (81500, 88000, "Thank you for watching. Let us all commit to being more mindful about our waste and work together towards a cleaner, healthier planet."),
    ]

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

    # Create summaries
    short_summary = Summary(
        video_id=video.id, transcript_id=transcript.id, version=1,
        kind="short", model_name="demo-model",
        content="This video covers household waste management fundamentals including waste sorting categories (organic, recyclables, hazardous, general), proper recycling practices, home composting basics, and the environmental benefits of responsible waste disposal. The key takeaway is that small daily changes in waste habits can significantly reduce landfill usage and greenhouse gas emissions.",
        status="ready",
    )
    detailed_summary = Summary(
        video_id=video.id, transcript_id=transcript.id, version=1,
        kind="detailed", model_name="demo-model",
        content="This session provides a comprehensive overview of household waste management and sustainable living practices.\n\nKey Topics Covered:\n\n1. Waste Categories: The video explains four main categories of household waste - organic (food scraps, garden trimmings), recyclables (paper, glass, aluminum, plastics), hazardous materials (batteries, electronics, chemicals), and general waste.\n\n2. Proper Recycling: Emphasizes the importance of rinsing recyclable items and warns against wish-cycling (putting non-recyclable items in recycling bins), which contaminates the recycling stream.\n\n3. Home Composting: Introduces composting as an accessible practice for both homeowners and apartment dwellers, using simple bins or countertop collectors.\n\n4. Environmental Impact: Highlights benefits including reduced landfill usage, lower greenhouse gas emissions, conservation of natural resources, and cost savings.\n\n5. Community Resources: Encourages viewers to check local recycling guidelines and curbside programs offered by municipalities.\n\nConclusion: The video promotes a mindset of progress over perfection, urging viewers to adopt small but consistent changes like using reusable bags and bottles for meaningful environmental impact.",
        status="ready",
    )
    db.add(short_summary)
    db.add(detailed_summary)

    # Create key moments
    moments_data = [
        (11500, 18000, "Waste Categories Overview", "Introduces the four main categories of household waste: organic, recyclables, hazardous, and general.", 0.95, 1),
        (32500, 39000, "Hazardous Waste Warning", "Critical safety information about proper disposal of batteries, electronics, paint, and chemicals.", 0.91, 2),
        (39500, 46000, "Wish-cycling Problem", "Explains a common recycling mistake that contaminates the recycling stream.", 0.87, 3),
        (53500, 60000, "Home Composting Guide", "Practical advice on starting home composting for both houses and apartments.", 0.84, 4),
        (67500, 74000, "Community Recycling Programs", "Information about curbside recycling and checking local guidelines.", 0.80, 5),
    ]

    for start, end, title, rationale, score, rank in moments_data:
        # Find the segment that covers this timestamp
        segment = (
            db.query(TranscriptSegment)
            .filter(
                TranscriptSegment.transcript_id == transcript.id,
                TranscriptSegment.start_ms <= start,
                TranscriptSegment.end_ms >= end,
            )
            .first()
        )
        if segment:
            moment = KeyMoment(
                video_id=video.id, transcript_segment_id=segment.id,
                start_ms=start, end_ms=end, title=title,
                rationale=rationale, score=score, rank=rank,
            )
            db.add(moment)

    video.status = "ready"
    video.duration_seconds = 88
    db.commit()

    return {"videoId": str(video.id), "status": "ready", "message": "Processing complete"}


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
