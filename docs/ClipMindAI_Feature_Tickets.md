# ClipMind AI — Feature Ticket List

Each ticket is intentionally small enough for one mentor-demoable day and aligns exactly to `ClipMindAI_25Day_Roadmap.md`. “Prompt” blocks are ready to use with an AI coding assistant after substituting current repository conventions.

| Day | Ticket / priority | Description and acceptance criteria | Dependencies |
|---|---|---|---|
| 1 | CM-01 Scope & journeys — must-have | Document personas, MVP/out-of-scope and flows. Accepted when mentor can trace four roles through a flow. | None |
| 2 | CM-02 Architecture & wireframes — must-have | Add schema, API outline and low-fi screens. Accepted when upload-to-output design is approved. | CM-01 |
| 3 | CM-03 Application foundation — must-have | Create Next.js/FastAPI/Compose/health route. Accepted when one command starts all services. | CM-02 |
| 4 | CM-04 Authentication — must-have | Register/login/refresh/logout with secure hashes/cookies. Accepted when invalid login is safely rejected. | CM-03 |
| 5 | CM-05 Roles/profile — must-have | Add four roles, protected navigation and profile. Accepted when server rejects unauthorized role route. | CM-04 |
| 6 | CM-06 Video upload — must-have | Signed upload, validation and owned library. Accepted when valid file appears and invalid file is explained. | CM-05 |
| 7 | CM-07 Media extraction job — must-have | FFmpeg probe/audio job and status view. Accepted when a sample shows extraction state/result. | CM-06 |
| 8 | CM-08 Whisper transcription — must-have | Worker makes timestamped transcript. Accepted when short sample segments persist. | CM-07 |
| 9 | CM-09 Transcript viewing/search — must-have | Secure viewer, timestamp seek, full-text search, download. Accepted when learner sees only shared transcript. | CM-08 |
| 10 | CM-10 Transcript editing — should-have | Educator edits and versions transcript. Accepted when original remains recoverable. | CM-09 |
| 11 | CM-11 Summary preprocessing — must-have | Deterministic chunking and short-summary trial. Accepted when long transcript does not exceed model input. | CM-08 |
| 12 | CM-12 Summary UI — must-have | Detailed/short panels, action items and failures. Accepted when user can distinguish model failure from transcript failure. | CM-11 |
| 13 | CM-13 Summary persistence/rerun — must-have | Versioned output and limited retry. Accepted when rerun does not silently erase prior result. | CM-12 |
| 14 | CM-14 M2 end-to-end — must-have | Test full processing journey and record quality rubric. Accepted when demo video completes. | CM-06–13 |
| 15 | CM-15 Keywords/topics — must-have | Extract/rank keywords and simple topic grouping. Accepted when results link to transcript terms. | CM-08 |
| 16 | CM-16 Importance scoring — must-have | Score transcript segments with documented signals. Accepted when rationale is persisted. | CM-15 |
| 17 | CM-17 Key-moment timeline — must-have | Render ranked timestamps and seek. Accepted when three moments work on sample. | CM-16 |
| 18 | CM-18 Highlight export — should-have | Export summary/moments as Markdown/TXT. Accepted when export respects access control. | CM-17 |
| 19 | CM-19 Content analytics — must-have | Per-video counts, bookmarks and history. Accepted when educator sees aggregate only. | CM-09 |
| 20 | CM-20 Admin operations — must-have | Jobs/activity tables and moderation metadata. Accepted when audit event is recorded. | CM-05, CM-07 |
| 21 | CM-21 Test/access matrix — must-have | Automated critical API/role tests. Accepted when all documented cases pass. | All core tickets |
| 22 | CM-22 Resilience/a11y pass — must-have | Limits, retries, responsive and WCAG checks. Accepted when stated quality gates pass. | CM-21 |
| 23 | CM-23 Deployment — must-have | Production Docker/config/HTTPS-ready release. Accepted when deployed health and demo flow work. | CM-22 |
| 24 | CM-24 Demo pack — should-have | Seed data, guide, slides and recovery script. Accepted when mentor can follow it. | CM-23 |
| 25 | CM-25 Final showcase — must-have | Final deployed walkthrough and metrics evidence. Accepted when rubric is presented. | CM-24 |

## Reusable implementation prompt

Use this prompt once for each ticket above, replacing the brackets:

```text
Implement [CM-XX: ticket name] in the ClipMind repository.
Scope: [copy the ticket description and acceptance criteria].
Roadmap constraint: this is Day [N]; do not add later-day features.
Respect `docs/ClipMindAI_Technical_Architecture.md`, `docs/ClipMindAI_Security_and_Access.md` and `docs/ClipMindAI_Frontend_Specification.md`. Reuse existing patterns, make no unrelated edits, and do not add new infrastructure unless the ticket requires it.
Implement server-side authorization and validation, accessible UI states (default, hover, focus-visible, active, disabled, loading, error), and focused tests. Run the relevant checks. Return changed files, acceptance evidence, and any blocker.
```

## Ticket-specific prompt additions

- CM-04/05: “Use Argon2id hashes, rotating HttpOnly refresh cookies, short JWT access tokens, and server-side role checks.”
- CM-06/07: “Accept only the configured MIME/signature/size/duration; use signed private storage URLs and never expose keys.”
- CM-08–13: “Run AI work in the worker, persist job/error state, impose timeout/retry limits, and preserve usable partial outputs.”
- CM-15–18: “Keep key-moment scoring explainable by showing the linked transcript segment and rationale.”
- CM-19/20: “Do not expose named learner histories to educators or raw private media to administrators.”
- CM-21/22: “Add regression tests for IDOR, expired session, role bypass, upload failure, AI timeout and keyboard/error accessibility.”

## Consistency cross-check

This ticket list does not schedule summaries before transcripts, moments before transcripts/keywords, analytics before views exist, or deployment before test/resilience work. It uses PostgreSQL-only storage metadata, one worker and one summary model, exactly as the architecture specifies. It preserves the PRD MVP and security permissions; deferred integrations never appear as a must-have ticket.
