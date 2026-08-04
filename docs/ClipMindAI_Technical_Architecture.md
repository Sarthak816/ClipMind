# ClipMind AI — Technical Architecture

## Recommendation and scope decision

Use **Next.js (React, TypeScript, Tailwind)** for the app, **FastAPI (Python)** for an API and worker-facing services, **PostgreSQL** for all application data, **S3-compatible object storage** for video files, **FFmpeg** for audio/metadata extraction, **faster-whisper** for local transcription, and **Hugging Face Transformers using one summarization model** (BART *or* T5, not both) for summaries. Docker Compose runs web, API, worker, PostgreSQL and local MinIO in development.

This trims the supplied stack deliberately. A solo 25-day build should not add MongoDB, TensorFlow and PyTorch, both BART and T5, OpenCV scene detection, Kubernetes, API gateway/service discovery, data lake or AWS+Azure. Whisper/faster-whisper and Transformers already depend on PyTorch; OpenCV is deferred because transcript-based moments satisfy the required milestone with less model risk. Azure Blob Storage may replace S3 in deployment, but v1 chooses exactly one storage provider.

## Logical flow

`Next.js browser → FastAPI → PostgreSQL / object storage` for ordinary requests. Upload is issued a short-lived object-storage URL. A queued `processing_job` is picked up by the Python worker: FFmpeg creates mono WAV audio, Whisper creates timestamped segments, the summary model processes chunks, then key-moment scoring ranks segments. The worker persists outputs and status. The browser polls one status endpoint until ready.

## Repository structure

```text
clipmind/
  apps/web/                         # Next.js UI
    app/(auth)/ app/(dashboard)/ api/ components/ lib/ styles/
  services/api/
    app/main.py api/routes/ core/ db/ models/ schemas/ services/ workers/
    alembic/ tests/
  packages/contracts/               # OpenAPI-derived TypeScript types/shared enums
  infra/docker/ docker-compose.yml  # local Postgres, MinIO, API, worker, web
  docs/                             # the project documentation
  .env.example README.md
```

Days 1–7 only require shells, auth, upload and FFmpeg. `workers/transcription.py` arrives Day 8, `summarization.py` Days 11–13, `key_moments.py` Days 15–17, and analytics routes Days 19–20. Keep background jobs in PostgreSQL and one worker for MVP; Redis/Celery is an optional post-MVP replacement if polling is insufficient.

## Database schema

| Table | Important fields | Relationship / plain-English purpose |
|---|---|---|
| `users` | id, email (unique), password_hash, display_name, role, status, created_at | One person has one v1 role: creator, learner, educator or administrator. |
| `sessions` | id, user_id, refresh_token_hash, expires_at, revoked_at | A user can have several logged-in devices; store only refresh-token hashes. |
| `videos` | id, owner_id, title, description, object_key, original_name, mime_type, byte_size, duration_seconds, status, shared_at, created_at | One owner uploads many videos. Object key is not a public URL. |
| `video_access` | video_id, user_id, granted_by, permission, expires_at | Explicit private sharing. `permission` is `view`; owners retain control. |
| `processing_jobs` | id, video_id, kind, status, attempt, progress, error_code, started_at, finished_at | Each video has many immutable processing attempts: extract, transcript, summary, moments. |
| `transcripts` | id, video_id, version, language, source, body, created_by, is_current | A video can have versions; edits create a version rather than destroy model output. |
| `transcript_segments` | id, transcript_id, sequence, start_ms, end_ms, text, confidence | A transcript has ordered timestamped segments, enabling seek/search and moments. |
| `summaries` | id, video_id, transcript_id, version, kind, content, model_name, status, created_at | A video can keep short and detailed summary versions tied to a transcript version. |
| `key_moments` | id, video_id, transcript_segment_id, start_ms, end_ms, title, rationale, score, rank | A moment points to a transcript segment; its rationale makes its AI ranking reviewable. |
| `keywords` / `video_keywords` | keyword id/text; video_id, keyword_id, score | Many videos can use the same keyword; joining supports content insights. |
| `bookmarks` | id, user_id, video_id, moment_id nullable, note, created_at | Learners save a video or one of its moments. |
| `view_events` | id, user_id, video_id, event_type, occurred_at | Minimal engagement counts: opened, searched, timestamp_clicked, bookmarked. No behavioural profiling. |
| `audit_logs` | id, actor_id nullable, action, entity_type, entity_id, ip_hash, metadata, occurred_at | Append-only record of security/admin actions. |

Foreign keys use UUIDs. Delete policy is restrictive for users with content; removing a video deletes/transitions its dependent derived data and asynchronously deletes its object. Index `videos(owner_id, created_at)`, `processing_jobs(video_id, status)`, `transcript_segments(transcript_id, sequence)`, access mappings, and search text (PostgreSQL full-text index).

## API surface

`POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`; `GET/PATCH /me`; `POST /videos/upload-intent`, `POST /videos/{id}/complete-upload`, `GET /videos`, `GET /videos/{id}`, `POST /videos/{id}/process`, `GET /videos/{id}/status`; transcript, summary, moment and export read routes; `POST /videos/{id}/share`, bookmark/history routes; and `/admin/users`, `/admin/jobs`, `/admin/audit-logs` routes. The FastAPI OpenAPI document is the single contract consumed by Next.js.

## Environment and configuration

| Variable | Notes |
|---|---|
| `APP_ENV`, `APP_URL`, `API_URL`, `CORS_ORIGINS` | Environment identity and exact allowed browser origin(s) |
| `DATABASE_URL` | PostgreSQL connection; TLS required outside local Docker |
| `JWT_SECRET`, `JWT_ACCESS_TTL_MINUTES`, `JWT_REFRESH_TTL_DAYS` | Long random secret in secret manager, short access token, rotated refresh session |
| `S3_ENDPOINT`, `S3_BUCKET`, `S3_REGION`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` | MinIO locally; S3/Azure adapter in deployment; private bucket only |
| `MAX_UPLOAD_BYTES`, `MAX_DURATION_SECONDS`, `ALLOWED_VIDEO_MIME_TYPES` | Default 500 MB, 3600 seconds, narrow allow-list |
| `WHISPER_MODEL`, `WHISPER_DEVICE`, `WHISPER_COMPUTE_TYPE` | `base`/CPU for demo reliability; never assume a GPU |
| `SUMMARY_MODEL_NAME`, `SUMMARY_MAX_INPUT_TOKENS`, `SUMMARY_TIMEOUT_SECONDS` | Select one tested BART or T5 model and chunk deterministically |
| `FFMPEG_PATH`, `WORKER_POLL_SECONDS`, `JOB_MAX_ATTEMPTS` | Validate executable at startup, defaults 2 seconds and 2 attempts |
| `LOG_LEVEL`, `SENTRY_DSN` optional | Structured logs; never log raw transcripts, tokens or signed URLs |

Use `.env.example` with empty secrets; no actual credentials in Git. Cloud deployment on Day 23 provisions managed PostgreSQL and private object storage, configures HTTPS and runs one web/API process plus one worker.
