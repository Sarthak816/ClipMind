# ClipMind AI

<div align="center">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Neon-00E599?style=for-the-badge&logo=neon&logoColor=black" alt="Neon" />
  <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq AI" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind" />
</div>
<br/>

**ClipMind AI** is a premium, full-stack AI SaaS application that automatically extracts intelligence from video files and YouTube links. It leverages fast LPU inference (Groq) and Whisper transcription to generate deep analytical summaries, full search-indexed transcripts, and key-moment extraction from any video in seconds.

Designed with a high-end aesthetic, ClipMind features smooth Framer Motion animations, a pitch-black glassmorphic UI, and a true responsive design.

---

## Features

- **Universal Video Ingestion**: Drag-and-drop local `.mp4`/`.mov` files or paste a YouTube link.
- **Fast AI Pipelines**: Audio extraction via `ffmpeg`/`yt-dlp`, transcription via `faster-whisper`, and intelligent summarization powered by Groq's compound models.
- **Smart Transcripts**: Fully searchable, timestamped transcripts that allow you to jump to exact moments in the conversation.
- **Key Moments Detection**: Heuristic algorithms combined with AI analysis to automatically pinpoint the most important highlights of any video.
- **Analytics Dashboard**: Track watch history, process states, and bookmark critical video moments.
- **Premium UI/UX**: Built with Next.js 14, Tailwind CSS, Lucide Icons, and Framer Motion for a fluid user experience.

---

## System Architecture

ClipMind uses a highly scalable decoupled architecture, communicating via REST APIs and Background Task queues.

```mermaid
graph TD
    %% Frontend
    Client[Next.js Client] -->|Upload / Fetch| API[FastAPI Backend]
    
    %% API & Database
    API -->|Read / Write| DB[(Neon Serverless Postgres)]
    
    %% Background Workers
    API -.->|Spawns Background Task| Worker[Async Video Processor]
    
    %% Worker Steps
    Worker -->|1. Extract Audio| YTDLP[yt-dlp / ffmpeg]
    Worker -->|2. Transcribe| Whisper[Faster-Whisper]
    Worker -->|3. Summarize| Groq[Groq LPU API]
    
    %% Output
    Whisper -.-> DB
    Groq -.-> DB
```

---

## Tech Stack

### Frontend (Vercel)
- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + Framer Motion
- **Icons**: Lucide React
- **State Management**: React Context (Auth)

### Backend (Render / Docker)
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (Neon Serverless)
- **ORM**: SQLAlchemy + Alembic
- **AI Models**: `faster-whisper` (Local Transcription), `Groq` (Cloud LLM)
- **Video Processing**: `ffmpeg`, `yt-dlp`

---

## Getting Started (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/Sarthak816/ClipMind.git
cd ClipMind
```

### 2. Set up the Backend
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in `services/api` with your credentials:
```env
DATABASE_URL=postgresql://user:pass@ep-host.neon.tech/neondb?sslmode=require
GROQ_API_KEY=gsk_your_groq_api_key
CORS_ORIGINS=http://localhost:3000
```
Run the backend:
```bash
# Apply database migrations
alembic upgrade head
# Start the server
uvicorn app.main:app --reload --port 8001
```

### 3. Set up the Frontend
```bash
cd ../../apps/web
npm install
```
Create a `.env.local` file in `apps/web`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```
Run the frontend:
```bash
npm run dev
```

Visit `http://localhost:3000` in your browser.

---

## Deployment

ClipMind is fully Dockerized and optimized for cloud deployment.

- **Backend**: Can be instantly deployed to Render or Google Cloud Run using the included `Dockerfile`. (Note: Set `CORS_ORIGINS` to your production frontend URL).
- **Frontend**: One-click deployment to Vercel. (Note: Set `NEXT_PUBLIC_API_URL` to your production backend URL).

---

## License
This project is licensed under the MIT License.
