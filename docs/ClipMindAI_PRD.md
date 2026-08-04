# ClipMind AI — Product Requirements Document

## Product statement

ClipMind AI turns a long uploaded video into a timestamped transcript, a short and detailed summary, and a small set of explainable key moments. Its promise is simple: read or search a long video instead of repeatedly scrubbing it.

The 25-day MVP is an educational, demo-ready web platform; it is not a production-scale media platform. It follows the roadmap in `ClipMindAI_25Day_Roadmap.md` and supports the required Week 2, 4, 6 and 8 evaluations.

## Problem and users

Long lectures, meetings and creator videos take too long to review. Existing viewers make people watch or scrub linearly, while useful decisions and teaching points are hidden in audio. ClipMind provides a reviewable text layer and links it back to the video timeline.

| Persona | Need | v1 outcome |
|---|---|---|
| Content Creator | Reuse and understand their own long videos quickly | Upload, generate outputs, download them, see basic per-video statistics |
| Learner | Find a topic or revisit an important point without replaying all video | View shared videos, summary, transcript search, timestamps, bookmarks and history |
| Educator | Turn a lecture into accurate learning material and share it with a class | Upload, edit transcript, generate summaries, share a private link, see engagement counts |
| Administrator | Keep the demo platform safe and observable | Manage accounts/roles/content, processing jobs, storage figures, activity and audit trail |

## Must-have requirements

1. Registration/login, profile and role-based access (Days 4–5).
2. Validated authenticated upload of MP4, MOV, WebM or AVI, ownership history and secure storage (Day 6).
3. Background media extraction with FFmpeg and visible step-by-step status (Day 7).
4. Whisper-based, timestamped transcript generation, storage, viewing and creator/educator editing (Days 8–10).
5. Short and detailed AI summaries from the transcript; error/retry state and saved output (Days 11–14).
6. Keywords, topic groups, transcript-signal key moments, timestamps and exportable highlight report (Days 15–18).
7. Per-video analytics, learner bookmarks/history, administrator activity/job dashboard (Days 19–20).
8. Dockerized, tested and deployed final demo with documentation (Days 21–25).

## Nice-to-have, only after core acceptance

- OAuth sign-in, email notifications and in-app notification centre.
- YouTube/Zoom/Google Drive imports; browser extension; public REST API.
- Speaker diarization, automatic thumbnail extraction, sentiment/NER, semantic/vector search.
- Slack/Notion exports, classroom roster management, advanced charts and real-time job updates.

## Primary user flow

1. A creator or educator signs in and uploads a supported video. The platform validates type, size and duration, then saves the original securely.
2. The video enters a background job. The UI truthfully reports `validating`, `extracting audio`, `transcribing`, `summarizing`, `finding key moments`, then `ready` or `needs attention`.
3. Whisper returns timestamped segments. The owner can read/search the transcript; an educator can correct it before generating learning material.
4. The summary service produces short and detailed summaries. The key-moment service ranks transcript segments and shows each moment as a clickable timestamp with its reason/keywords.
5. The owner may share a view-only link with intended learners. A learner opens the content, jumps by timestamp, searches text and saves bookmarks.
6. The owner sees basic results; the administrator can see platform-wide job and audit information without reading private content by default.

## MVP boundary

The MVP is complete when an authenticated creator can upload a short test video, receive a usable timestamped transcript, a short and detailed summary, three or more key moments, and download/export outputs; a learner can consume an explicitly shared video; each role is restricted correctly; and an administrator can diagnose a failed job. The Day 25 deployment must demonstrate this entire path.

## Not being built in v1

- Live streaming, video editing, automatic social-media clip rendering or billing.
- Guaranteed transcription accuracy, speaker labels, copyrighted-source ingestion, public search or anonymous sharing.
- Multi-tenant enterprise SSO, content moderation automation, data warehouse, Kubernetes, HA/load balancing, WAF, Prometheus/Grafana, or AWS-and-Azure dual deployment.
- MongoDB alongside PostgreSQL: one relational database keeps a solo build supportable.

## Success measures

| Metric | v1 target / evidence |
|---|---|
| Upload success rate | At least 90% for valid mentor test files |
| Processing completion | 80%+ of supported short test videos finish without manual intervention |
| Transcript quality | Manual review on 3 sample videos; document obvious errors rather than claiming an unsupported accuracy percentage |
| Summary relevance | Creator/educator rubric: 4/5 average on coverage, correctness and concision across 3 samples |
| Key-moment usefulness | Reviewer says at least 3 shown timestamps are meaningful in 3 samples; record result |
| App responsiveness | Normal pages load in under 2 seconds locally/demo deployment; processing is asynchronous |
| Access control | All role/access tests in the Day 21 matrix pass |

## Acceptance decisions

Only owners, approved shared viewers and administrators acting under an audited moderation need can access a video record. The first launch caps uploads at 500 MB and 60 minutes; limits are configurable. An AI result is always labelled AI-generated and a user can rerun a failed job, but not silently overwrite a completed output.
