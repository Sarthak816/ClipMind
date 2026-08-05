# ClipMind AI

ClipMind AI is an Infosys Springboard project that turns uploaded videos into timestamped transcripts, concise AI summaries, and explainable key moments.

## Project status

Current milestone: Day 2 — build-ready architecture, database schema, API contract and wireframes.

The planned MVP flow is:

`Upload video → extract audio → transcribe → summarize → identify key moments → review and export`

## Documentation

- [25-Day Roadmap](docs/ClipMindAI_25Day_Roadmap.md)
- [Product Requirements](docs/ClipMindAI_PRD.md)
- [Technical Architecture](docs/ClipMindAI_Technical_Architecture.md)
- [Security and Access](docs/ClipMindAI_Security_and_Access.md)
- [Frontend Specification](docs/ClipMindAI_Frontend_Specification.md)
- [Feature Tickets](docs/ClipMindAI_Feature_Tickets.md)
- [Database Schema](docs/Database_Schema.md)
- [API Contract](docs/API_Contract.md)
- [Wireframes](docs/Wireframes.md)

## Project structure

```text
clipmind/
  apps/web/           Next.js UI (TypeScript, Tailwind, App Router)
  services/api/       FastAPI backend (Python)
  docs/               Project documentation
  docker-compose.yml  Local development stack
```

## Planned stack

Next.js/React with TypeScript and Tailwind; FastAPI/Python; PostgreSQL; S3-compatible private storage; FFmpeg; faster-whisper; one Hugging Face summarization model; Docker Compose.

## Local development (Day 3+)

### Prerequisites

- Docker and Docker Compose v2
- Node.js 20+ (for local web development without Docker)
- Python 3.11+ (for local API development without Docker)

### Quick start with Docker Compose

```bash
# 1. Clone the repository
git clone https://github.com/Sarthak816/ClipMind.git
cd ClipMind

# 2. Copy environment files
cp .env.example .env

# 3. Start all services
docker compose up --build

# 4. Verify
#    Web:   http://localhost:3000
#    API:   http://localhost:8000/health
#    DB:    localhost:5432
```

### Running without Docker

**API:**

```bash
cd services/api
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Web:**

```bash
cd apps/web
npm install
npm run dev
```

## License

For academic project use. Add a chosen open-source license before making the repository publicly reusable.
