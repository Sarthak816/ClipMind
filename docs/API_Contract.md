# ClipMind AI — API Contract

Base URL: `/api/v1`. FastAPI publishes the canonical OpenAPI document at `/openapi.json`; this document defines the Day 2 contract that the frontend will implement against.

## Shared conventions

- JSON uses `camelCase`; database uses `snake_case` internally.
- Protected requests use the HttpOnly session flow; the browser does not send long-lived tokens manually.
- Every error has `{ "code": "MACHINE_CODE", "message": "Safe user-facing explanation", "correlationId": "uuid" }`.
- List endpoints use `limit` (default 20, maximum 100) and opaque `cursor` pagination.
- A caller can only access a resource authorized by their role and ownership/share row.

## Authentication and profile

| Method/path | Request | Success |
|---|---|---|
| `POST /auth/register` | email, password, displayName | `201` user; default learner or seeded role policy |
| `POST /auth/login` | email, password | `200` user; sets refresh cookie |
| `POST /auth/refresh` | refresh cookie | `200` short access session |
| `POST /auth/logout` | refresh cookie | `204`; revokes session |
| `GET /me` | — | current user profile/role |
| `PATCH /me` | displayName | updated current profile |

## Video lifecycle

| Method/path | Role | Request | Success |
|---|---|---|---|
| `POST /videos/upload-intent` | creator, educator | fileName, mimeType, byteSize | `201` videoId, signedUploadUrl, requiredHeaders, expiresAt |
| `POST /videos/{id}/complete-upload` | owner | checksum optional | `202` video/job state after server verifies object |
| `GET /videos` | signed-in | cursor, limit, status | caller’s owned and explicitly shared video cards |
| `GET /videos/{id}` | authorized viewer | — | video metadata and allowed output links |
| `PATCH /videos/{id}` | owner | title, description | updated video |
| `DELETE /videos/{id}` | owner/admin moderation | — | `202` deletion scheduled |
| `POST /videos/{id}/process` | owner | language optional | `202` processing job |
| `GET /videos/{id}/status` | authorized viewer | — | overall state and safe job progress |
| `POST /videos/{id}/share` | owner | userEmail, expiresAt optional | `201` view grant |
| `DELETE /videos/{id}/share/{userId}` | owner | — | `204` |

Upload intent rejects disallowed MIME/signature/size before returning any storage URL. Direct browser upload goes only to the signed URL; it never passes video bytes through FastAPI.

## Generated content and activity

| Method/path | Role | Success response |
|---|---|---|
| `GET /videos/{id}/transcripts/current` | authorized viewer | transcript metadata, text and segments |
| `POST /videos/{id}/transcripts` | educator-owner | new human-edit transcript version |
| `GET /videos/{id}/search?q=` | authorized viewer | matched segment snippets and timestamps |
| `GET /videos/{id}/summaries` | authorized viewer | short/detailed latest summaries |
| `GET /videos/{id}/key-moments` | authorized viewer | ranked timestamp cards, rationale and keywords |
| `GET /videos/{id}/export?format=md` | owner/authorized viewer | content-disposition download, never source video |
| `POST /videos/{id}/bookmarks` | learner/authorized viewer | bookmark |
| `GET /me/history` | signed-in | caller’s video history/bookmarks |
| `POST /videos/{id}/events` | authorized viewer | `204`; accepts allowed event type only |

## Administrator routes

`GET /admin/users`, `PATCH /admin/users/{id}/role`, `PATCH /admin/users/{id}/status`, `GET /admin/jobs`, `GET /admin/audit-logs`, and `GET /admin/analytics`. All require `administrator`, write an audit event, and return metadata/job details rather than raw private media by default.

## Status and error mapping

`400` malformed request; `401` missing/expired session; `403` no access; `404` unavailable/not found without confirming private resource; `409` conflicting state; `413` too large; `415` unsupported media; `422` validation; `429` rate limit; `500` unexpected error; `503` temporarily unavailable. Processing failures are returned from the status endpoint as a safe `failed` job state, not as a browser crash.
