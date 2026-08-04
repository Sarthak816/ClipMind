# ClipMind AI — Security and Access

## Login method

Use email/password login over HTTPS with Argon2id password hashes. FastAPI issues a short-lived signed JWT access token (15 minutes) and a rotating refresh token stored in a `Secure`, `HttpOnly`, `SameSite=Lax` cookie; its hash is stored in `sessions`. The Next.js app never stores an access token in localStorage. Rate-limit login and upload-intent routes. OAuth is a future enhancement, not a Day 4 dependency.

An administrator assigns roles; public self-registration creates `learner` by default (or is disabled for the mentor demo and seeded accounts are used). Roles are server-enforced; hiding a UI button is never authorization.

## Role permissions

| Role | Can | Cannot |
|---|---|---|
| Content Creator | Manage own uploads; request/retry own processing; read/download own outputs; share view access; see own content analytics | Edit another owner’s video/transcript; change roles; see system/audit data; view unshared content |
| Learner | Read content explicitly shared to them; search transcript; click moments; bookmark and see own history | Upload/process, edit transcript, generate outputs, download private source videos, view another learner’s history |
| Educator | All creator actions for own lectures; create transcript versions; share learning material; view aggregate engagement for own shared lectures | Manage people/roles, platform data, or other educators’ private content |
| Administrator | Manage users/status/roles; list and moderate metadata/content when policy requires; inspect jobs/storage/system analytics and audit reports | Read/download a private video, transcript or summary merely out of curiosity; alter audit history; impersonate users |

## Row-level data rules

PostgreSQL RLS is enabled on user-owned tables. Every API request sets the authenticated `app.user_id` and `app.role` transaction-local setting; policies use it, while FastAPI additionally checks permissions.

- `users`: people update only their own profile, never `role` or `status`; administrators manage role/status.
- `videos`, `transcripts`, `summaries`, `key_moments`, `keywords`: owner can read/write; an entry in `video_access` grants learner read; administrator gets metadata/jobs only, with a separately logged moderation-read path.
- `video_access`: owner/educator-owner may create/revoke access for their own video; recipient may read only their own grant.
- `bookmarks` and `view_events`: only the related user can read/write their own records; educators get aggregate counts for their own shared video, not named learner histories.
- `processing_jobs`: owner reads their job; worker service role updates job/output; administrator reads operational fields and error codes.
- `audit_logs`: only server inserts, only administrator reads; no update/delete policy.

Object storage is private. Browser uploads/downloads use a narrow, short-lived signed URL after API authorization; object keys are unguessable and never accepted as permission proof.

## Plain-English failure handling

| Failure | What the user sees | Safe system behaviour | What the mentor/admin can do |
|---|---|---|---|
| File too large, unsupported or corrupt | “This file can’t be processed. Use MP4, MOV, WebM or AVI under the stated limit.” | Validate before worker; do not create an AI job; remove incomplete upload after expiry | Check configured limits and validation log |
| Network interrupted during upload | “Upload paused or failed. Your original video was not queued.” with Retry | Multipart upload can resume if supported; otherwise discard orphaned partial object after 24 hours | Inspect storage/orphan cleanup |
| Storage unavailable | “We can’t save this video right now. Please try again.” | No DB `ready` record until completion; log correlation ID | Check provider status/credentials; do not ask user to resend password or token |
| FFmpeg/media extraction fails | “We couldn’t read the audio from this video.” | Mark extraction job `failed`, retain source briefly for retry, never loop forever | Review sanitized stderr/error code; recommend re-exporting file |
| Whisper timeout/model failure | “Transcription took too long or stopped. You can retry.” | Timeout, record job state, retry at most twice with backoff; preserve prior successful transcript | Check worker capacity/model configuration |
| Empty/low-confidence transcript | “We found too little clear speech to summarize.” | Save available segments with warning; do not invent a summary or moments | Suggest clearer audio/language selection; owner may re-upload |
| Summary model fails or input is too long | “Transcript is ready; summary needs another try.” | Chunk text, cap tokens/time, mark only summary job failed; transcript stays usable | Retry with supported model/config; inspect model log without transcript content |
| Key-moment job fails | “Summary is ready; key moments are unavailable for now.” | Partial results remain available; no fake timeline | Retry its job separately |
| Unauthorized/expired share link | “You don’t have access to this video.” | Return 403/404 without confirming private resource existence; audit denied attempts | Owner grants access; admin investigates patterns |

## Before-launch checklist

- HTTPS in deployment; no development secrets, public buckets, debug traces or broad CORS.
- Validate MIME plus file signature, extension, size, duration and FFmpeg probe result; do not execute uploaded names/paths.
- Run media tools with fixed arguments, a non-privileged worker, resource/time limits and isolated temporary directories.
- Test expired/revoked sessions, IDOR attempts (changing a video ID), cross-role API calls, SQL injection, XSS in transcript/title/note, CSRF for cookie mutations, rate limits and password reset/login enumeration.
- Escape transcript and AI output in the UI; treat it as untrusted text. State that AI content may be incorrect and support human transcript correction.
- Retain source media only as required for the demo; provide owner deletion, delete derived objects, expire upload URLs and document backup/restore.
- Keep audit events for logins, role changes, sharing, deletion, admin reads and job actions; redact secrets and personal text from logs.

Security completion for Day 21 is a passed access-test matrix, not a claim that the prototype is enterprise certified.
