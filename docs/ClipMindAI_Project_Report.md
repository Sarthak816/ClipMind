# ClipMind AI — Project Report

## Infosys Springboard Project

**Student:** [Your Name]
**Mentor:** [Mentor Name]
**Duration:** 25-Day MVP Development
**Report Covers:** Milestone 1 (Days 1–7) & Milestone 2 (Days 8–14)

---

## 1. Project Overview

ClipMind AI is an AI-powered video intelligence platform that transforms long videos into timestamped transcripts, concise AI summaries, and explainable key moments. The platform enables content creators, learners, educators, and administrators to review video content efficiently without watching entire videos.

### Core Value Proposition

Turn a 40-minute video into a 2-minute read.

### Primary User Flow

```
Upload Video → Extract Audio (FFmpeg) → Transcribe (Whisper) → Summarize (AI) → Identify Key Moments → Review & Export
```

---

## 2. Problem Statement

Long lectures, meetings, and creator videos take too long to review. Existing video viewers force users to watch or scrub linearly, while useful decisions and teaching points are hidden in audio. ClipMind provides a reviewable text layer and links it back to the video timeline.

### Target Users

| Persona | Need | ClipMind Outcome |
|---|---|---|
| Content Creator | Reuse and understand own videos quickly | Upload, generate outputs, download, see statistics |
| Learner | Find topics without replaying all video | View shared videos, search transcript, timestamps, bookmarks |
| Educator | Turn lectures into learning material | Upload, edit transcript, generate summaries, share with class |
| Administrator | Keep platform safe and observable | Manage users/roles, inspect jobs, audit trail |

---

## 3. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, React, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11, SQLAlchemy ORM |
| Database | PostgreSQL 16 |
| AI - Transcription | faster-whisper (OpenAI Whisper implementation) |
| AI - Summarization | BART-large-CNN (Hugging Face Transformers) |
| Media Processing | FFmpeg (audio extraction and metadata) |
| Authentication | Argon2id password hashing, JWT tokens |
| Infrastructure | Docker Compose, Alembic migrations |
| Version Control | Git, GitHub |

### Architecture Diagram

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Browser    │────▶│  FastAPI     │────▶│  PostgreSQL  │
│  (Next.js)   │     │   (Python)   │     │   Database   │
└─────────────┘     └──────┬───────┘     └──────────────┘
                           │
                    ┌──────▼───────┐
                    │   Workers    │
                    │ FFmpeg       │
                    │ Whisper      │
                    │ BART         │
                    └──────────────┘
```

---

## 4. Database Design

### Entity Relationship Summary

The database contains 12 tables with the following relationships:

- **users** → has many **sessions**, **videos**, **bookmarks**, **view_events**
- **videos** → has many **processing_jobs**, **transcripts**, **summaries**, **key_moments**, **video_access**
- **transcripts** → has many **transcript_segments**, sources **summaries**
- **transcript_segments** → explains **key_moments**

### Key Tables

| Table | Purpose | Key Fields |
|---|---|---|
| users | User accounts and roles | id, email, password_hash, role, status |
| sessions | Active login sessions | id, user_id, refresh_token_hash, expires_at |
| videos | Uploaded video metadata | id, owner_id, title, object_key, status |
| processing_jobs | Background job tracking | id, video_id, kind, status, progress |
| transcripts | Full transcript text | id, video_id, version, language, source |
| transcript_segments | Timestamped text chunks | id, transcript_id, sequence, start_ms, end_ms, text |
| summaries | AI-generated summaries | id, video_id, kind (short/detailed), content |
| key_moments | Ranked important moments | id, video_id, start_ms, end_ms, title, rationale, score |
| video_access | Explicit sharing grants | video_id, user_id, permission |
| bookmarks | User saved moments | user_id, video_id, moment_id |
| view_events | Usage analytics | user_id, video_id, event_type |
| audit_logs | Security audit trail | actor_id, action, entity_type |

### Design Decisions

- UUIDs for all primary keys (non-guessable)
- TIMESTAMPTZ for all timestamps (UTC)
- Soft delete for videos (deleted_at timestamp)
- Versioned transcripts (educator edits create new versions)
- Enum types for status fields (database-level constraint)

---

## 5. API Design

### Authentication Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/register | Create new account (default: learner role) |
| POST | /auth/login | Authenticate and receive JWT tokens |
| POST | /auth/refresh | Rotate refresh token, get new access token |
| POST | /auth/logout | Revoke session, clear cookies |
| GET | /auth/me | Get current user profile |

### Video Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | /videos/upload-intent | Get signed upload URL, create video record |
| POST | /videos/{id}/complete-upload | Mark upload finished, queue processing |
| GET | /videos | List user's videos |
| GET | /videos/{id} | Get video metadata |
| PATCH | /videos/{id} | Update title/description |
| DELETE | /videos/{id} | Soft-delete video |
| POST | /videos/{id}/process | Start processing pipeline |
| GET | /videos/{id}/status | Get job status and progress |

### Content Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | /videos/{id}/transcripts/current | Get current transcript with segments |
| GET | /videos/{id}/search?q= | Full-text search transcript |
| GET | /videos/{id}/summaries | Get short and detailed summaries |
| GET | /videos/{id}/key-moments | Get ranked key moments |

### Worker Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | /worker/extract-audio/{job_id} | FFmpeg audio extraction |
| POST | /worker/transcribe/{job_id} | Whisper transcription |
| POST | /worker/summarize/{job_id} | BART summarization |
| POST | /worker/key-moments/{job_id} | Key moment scoring |

---

## 6. Security Implementation

### Authentication Flow

1. User registers with email/password
2. Password hashed with Argon2id (memory-hard,抗 GPU attacks)
3. Server creates JWT access token (15-minute expiry)
4. Server creates refresh token, stores hash in sessions table
5. Refresh token set as HttpOnly, Secure, SameSite=Lax cookie
6. Browser never stores tokens in localStorage
7. Access token sent via Authorization header on API calls

### Role-Based Access Control

| Role | Permissions |
|---|---|
| Content Creator | Manage own uploads, request processing, read/download outputs |
| Learner | Read explicitly shared content, search transcript, bookmark |
| Educator | All creator actions + edit transcript versions + share |
| Administrator | Manage users/roles, inspect jobs, audit logs |

### Security Measures

- Server-side role enforcement (never just hidden UI)
- CSRF protection via SameSite cookies
- No secrets or credentials in git repository
- .env.example files with safe placeholders only
- Input validation on all endpoints
- SQL injection prevention via SQLAlchemy ORM

---

## 7. Frontend Implementation

### Design System

Dark accessible UI with the following design tokens:

| Token | Value | Usage |
|---|---|---|
| Background | #0B0D12 | Page background |
| Surface | #121722 | Card backgrounds |
| Surface Raised | #191F2C | Hover states |
| Text | #F4F7FB | Primary text |
| Text Muted | #AAB4C3 | Secondary text |
| Border | #2A3445 | Dividers |
| Primary (Coral) | #FF7A66 | CTAs, accents |
| Focus | #7DD3FC | Focus rings |
| Success | #43D19E | Positive states |
| Warning | #F7C35F | Caution states |
| Danger | #FF6B6B | Error states |

### Pages Built

| Page | Route | Description |
|---|---|---|
| Landing | / | Marketing page with hero, stats, how-it-works |
| Login | /login | Email/password authentication form |
| Register | /register | Account creation form |
| Dashboard | /dashboard | Main app shell with sidebar navigation |
| Video Library | /dashboard/videos | List of user's videos with status |
| Upload | /dashboard/upload | Drag-and-drop file upload with validation |
| Video Detail | /dashboard/videos/[id] | Transcript viewer, summary, key moments |
| Profile | /dashboard/profile | User profile and role display |
| Bookmarks | /dashboard/bookmarks | Saved moments (empty state) |
| History | /dashboard/history | Viewing history (empty state) |
| Admin Users | /dashboard/admin/users | User management (stub) |
| Admin Jobs | /dashboard/admin/jobs | Job dashboard (stub) |

### Accessibility

- WCAG 2.2 AA color contrast ratios
- Keyboard navigation follows visual order
- Visible focus indicators on all interactive elements
- Semantic HTML with ARIA labels
- Error messages linked to inputs via aria-describedby
- Minimum touch target size 44x44px for primary controls

---

## 8. Infrastructure

### Docker Compose Services

| Service | Image | Port | Purpose |
|---|---|---|---|
| db | postgres:16-alpine | 5432 | PostgreSQL database |
| api | Custom (Python 3.11) | 8000 | FastAPI backend |
| web | Custom (Node 20) | 3000 | Next.js frontend |

### Local Development

```bash
# Start all services
docker compose up --build

# Or run locally
cd services/api && uvicorn app.main:app --reload
cd apps/web && npm run dev -- --turbo
```

### Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| DATABASE_URL | PostgreSQL connection string | postgresql://clipmind:changeme@localhost:5432/clipmind |
| JWT_SECRET | Token signing secret | dev-secret-change-in-production |
| CORS_ORIGINS | Allowed browser origins | http://localhost:3000 |
| NEXT_PUBLIC_API_URL | API base URL for frontend | http://localhost:8000 |

---

## 9. Milestone Completion Summary

### Milestone 1: Project Initialization & Core Setup (Days 1–7)

| Day | Deliverable | Status |
|---|---|---|
| 1 | Problem definition, personas, user journeys, repository setup | Complete |
| 2 | System architecture, database schema, API contract, wireframes | Complete |
| 3 | Next.js + FastAPI shells, Docker Compose, health endpoint | Complete |
| 4 | PostgreSQL models, Alembic migrations, authentication system | Complete |
| 5 | Role-aware app shell, profile settings, password change | Complete |
| 6 | Video upload with validation, video library | Complete |
| 7 | FFmpeg audio extraction worker, job status tracking | Complete |

### Milestone 2: Transcript Generation & AI Summarization (Days 8–14)

| Day | Deliverable | Status |
|---|---|---|
| 8 | Whisper transcription worker with timestamped segments | Complete |
| 9 | Transcript viewer, pagination, full-text search | Complete |
| 10 | Transcript versioning support (educator edits) | Complete |
| 11 | Text chunking for model input, short summary prototype | Complete |
| 12 | Detailed summary panel, error/retry states | Complete |
| 13 | Summary persistence, versioning, rerun controls | Complete |
| 14 | Key moment scoring from transcript signals | Complete |

---

## 10. Project File Structure

```
clipmind/
├── apps/
│   └── web/                          # Next.js frontend
│       ├── src/
│       │   ├── app/
│       │   │   ├── (auth)/           # Login, Register pages
│       │   │   ├── (dashboard)/      # Dashboard, Videos, Upload, Profile
│       │   │   ├── layout.tsx        # Root layout with AuthProvider
│       │   │   ├── page.tsx          # Landing page
│       │   │   └── globals.css       # ClipMind design tokens
│       │   ├── components/           # Logo, shared components
│       │   └── lib/
│       │       ├── api.ts            # API client
│       │       └── auth-context.tsx  # Authentication state
│       ├── Dockerfile
│       ├── package.json
│       ├── tailwind.config.ts
│       └── tsconfig.json
│
├── services/
│   └── api/                          # FastAPI backend
│       ├── app/
│       │   ├── core/
│       │   │   ├── config.py         # Environment settings
│       │   │   └── security.py       # JWT, password hashing
│       │   ├── db/
│       │   │   └── session.py        # Database connection
│       │   ├── models/               # 7 SQLAlchemy model files
│       │   ├── routes/               # 5 route files (auth, videos, me, transcripts, summaries)
│       │   ├── schemas/              # Pydantic request/response schemas
│       │   ├── services/             # Auth dependencies
│       │   └── workers/              # 4 worker files (extraction, transcription, summarization, key_moments)
│       ├── alembic/                  # Database migrations
│       ├── Dockerfile
│       ├── requirements.txt
│       └── alembic.ini
│
├── docs/                             # 9 documentation files
│   ├── ClipMindAI_25Day_Roadmap.md
│   ├── ClipMindAI_PRD.md
│   ├── ClipMindAI_Technical_Architecture.md
│   ├── ClipMindAI_Security_and_Access.md
│   ├── ClipMindAI_Frontend_Specification.md
│   ├── ClipMindAI_Feature_Tickets.md
│   ├── Database_Schema.md
│   ├── API_Contract.md
│   └── Wireframes.md
│
├── docker-compose.yml                # Local development stack
├── start.ps1                         # One-click startup script
├── stop.ps1                          # Stop all servers
├── .env.example                      # Environment template
├── .gitignore
└── README.md
```

---

## 11. Git Commit History

| Commit | Hash | Description |
|---|---|---|
| Day 1-2 | 071fabe | Documentation foundation and implementation design |
| Day 3 | d142b33 | Application foundation (Next.js, FastAPI, Docker) |
| Day 4-14 | 6ef5399 | Auth, upload, transcripts, summaries, key moments |
| Scripts | 8da48a3 | Local dev startup scripts |

---

## 12. What's Next (Milestones 3 & 4)

### Milestone 3: Key Moments & Analytics (Days 15–20)

- Keyword extraction and topic grouping
- Explainable importance scoring from transcript signals
- Timestamped key moments timeline viewer
- Highlight report/export (Markdown and TXT)
- Per-video content analytics
- Learner bookmarks and history
- Administrator job/activity dashboard

### Milestone 4: Testing & Deployment (Days 21–25)

- Unit and integration tests
- Role/access test matrix
- Performance optimization
- Responsive UI and accessibility audit
- Docker production build
- Cloud deployment
- Seed data and demo preparation
- Final walkthrough and metrics report

---

## 13. Conclusion

Milestones 1 and 2 are complete with a working end-to-end flow:

1. User registers/logs in with secure authentication
2. User uploads a video file with validation
3. FFmpeg extracts audio from the video
4. Whisper generates timestamped transcript
5. BART produces short and detailed summaries
6. Key moments are scored and ranked with explainable rationale
7. User can view, search, and navigate transcript by timestamp
8. All protected by role-based access control

The platform is ready for Milestone 3 enhancements (keywords, topics, timeline, export, analytics) and Milestone 4 hardening (testing, deployment, documentation).

---

*Report generated for Infosys Springboard evaluation.*
