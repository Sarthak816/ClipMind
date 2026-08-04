# ClipMind AI — Frontend Specification

## Product character

The app borrows the supplied reference’s narrative pacing, stat-first marketing, soft dividers, gentle lift and warm plain-language voice without copying its portfolio layout. The product app is task-first: upload, truthful processing stages, answer-first summary, then transcript. One primary CTA is used consistently: **“Summarize a video”**. Copy says what is truly happening, never fabricates metrics or generic “Loading”.

The supplied local design notes specify warm-minimal/off-white and do not contain the dark hexadecimal, Inter Display, radius or shadow tokens described in the request. To make this buildable, the following accessible dark system is the explicit project standard; it preserves the brief’s warmth with a restrained coral accent.

## Tokens

```css
:root {
  --bg: #0B0D12; --surface: #121722; --surface-raised: #191F2C;
  --text: #F4F7FB; --text-muted: #AAB4C3; --border: #2A3445;
  --primary: #FF7A66; --primary-hover: #FF927F; --primary-active: #E86250;
  --focus: #7DD3FC; --success: #43D19E; --warning: #F7C35F; --danger: #FF6B6B;
  --radius-sm: 8px; --radius-md: 12px; --radius-lg: 20px; --radius-pill: 999px;
  --shadow-sm: 0 1px 2px rgb(0 0 0 / .28);
  --shadow-md: 0 12px 32px rgb(0 0 0 / .28);
  --shadow-focus: 0 0 0 3px rgb(125 211 252 / .45);
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 24px; --space-6: 32px; --space-8: 48px; --space-10: 64px;
}
```

Use `Inter Display, Inter, ui-sans-serif, system-ui, sans-serif`. Type scale: Display 64/68 px, 700 (desktop; 44/48 mobile); H1 40/44, 700; H2 28/34, 650; H3 20/28, 650; body 16/24, 400; small 14/20; caption 12/16. Use letter spacing -0.035em display, -0.02em headings, normal body. Text/background combinations meet WCAG 2.2 AA: normal text uses `--text` or `--text-muted` only where contrast is at least 4.5:1; never use accent alone for status meaning.

## Layout and surfaces

Marketing: section-per-scroll rhythm, max width 1200 px, 24 px mobile/48 px desktop gutters, three real/clearly labelled example stats, thin low-opacity curved SVG separators. Product: 240 px left navigation on desktop, collapsible at <1024 px, 16 px mobile padding, 12-column desktop grid, single column <640 px. Cards use `--surface`, 1 px `--border`, `--radius-lg`, `--shadow-sm`; hover translateY(-2px) only when `prefers-reduced-motion: no-preference`.

Dashboard cards: library, upload, recent jobs, learner bookmark. Summary screen: title/status and summary first, right/upper timeline second, transcript below with persistent search. Every timestamp is a semantic button that seeks the HTML video player and announces the new time. Processing has a labelled stepper, percentage only when known, elapsed time and retry/help action.

## Component contract and states

| Component | Base/default | Interaction and exceptional states |
|---|---|---|
| Primary button | coral fill, near-black text, 44 px min height, md radius | Hover lighter; active darker; keyboard `:focus-visible` focus shadow; disabled 45% opacity/no pointer; loading locks width and shows labelled spinner; error is shown adjacent, never by turning an unrelated action red |
| Secondary/ghost button | transparent surface, 1 px border, light text | Hover raised surface; active border; same focus/disabled/loading rules |
| Text/file input | raised surface, border, 44 px min height, persistent visible label | Hover border lightens; focus-visible cyan ring; active same; disabled subdued; loading progress state for upload; error danger border + icon + text explanation below, linked with `aria-describedby` |
| Card | surface, lg radius, padding 16–24 | Hover gentle lift when actionable; focus-visible ring when card is a link; active reset; disabled never clickable; skeleton uses non-flashing neutral shimmer; error card says recoverable next action |
| Modal | labelled dialog, surface-raised, lg radius, max 560 px | Focus trap, Escape/close button, restore opener focus; destructive action has confirmation text; disabled/loading action cannot double-submit; inline error announced with `role=alert` |
| Status chip | icon + text + colour: queued, processing, ready, failed | Never colour-only; `aria-live=polite` job updates; failure includes retry/reason |

Quality gates: keyboard navigation follows visual order; visible focus never removed; targets minimum 24×24 px (44×44 for primary controls); errors use understandable prose; headings/landmarks are semantic; modals and toast errors are announced; no animation is essential; test 320 px, 768 px, 1440 px and 200% zoom.

## Page specifications by roadmap day

Days 1–2: landing, auth wireframes and empty dashboard. Days 3–5: accessible auth/profile/app shell. Days 6–7: upload drop zone with validation and processing stepper. Days 8–10: transcript viewer/search/editor. Days 11–14: short/detailed summary panel and rerun state. Days 15–18: keyword chips, explainable timeline, export dialog. Days 19–20: analytics, bookmarks/history, restricted admin tables. Days 21–25: test/error/accessibility states, responsive polish, deployment/demo pages.

## Third-party/service integration contract

| Service | Purpose | Call/data in | Data out / UI rule |
|---|---|---|---|
| S3-compatible storage (MinIO locally; AWS S3 or Azure Blob in deployment) | Keep original video privately | Browser asks FastAPI for `upload-intent`; API returns short-lived signed PUT URL, content type/size constraints; browser uploads directly then calls completion | Object key and checksum only return to API. UI never gets bucket credentials or permanent public URL. Download uses a newly authorized signed URL. |
| FFmpeg (worker-local) | Probe video and extract normalized WAV audio | Worker reads private object into isolated temp path; fixed command receives only validated path | Duration/metadata and WAV; job progress `extracting audio`; no browser call. |
| Whisper / faster-whisper | Speech-to-text | Worker sends normalized audio, optional chosen language/model configuration | Timestamped segment text, start/end ms and confidence stored in PostgreSQL. UI polls status then reads API transcript endpoint. |
| Hugging Face Transformers, one BART or T5 model | Generate summary | Worker receives sanitized, length-capped transcript chunks and summary kind | Short/detailed summary text and model/version. The UI labels it AI-generated and exposes source transcript. |
| PostgreSQL full-text search | Find transcript passages | API receives user query, video ID and authorization | Matching safe text snippets/timestamps. It is not a third-party call and avoids a vector database in v1. |

All browser requests go to FastAPI over HTTPS with cookies/CSRF protection. The browser never calls Whisper, the model, FFmpeg or storage control plane with secrets. API errors have `{code, message, correlationId}`; display `message`, show correlation ID in support details, and never expose stack traces.
