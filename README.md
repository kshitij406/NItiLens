# NitiLens — AI Policy Stress Tester for India
**Team JFKN | DayZero 2.0 | CodeNex SRMIST | AI & ML Track**

## What it does

NitiLens stress-tests Indian government policies through a 3-stage pipeline:

1. **4 specialist AI agents** stream results sequentially — Fiscal, Labor, Equity & Social Impact, Regional & Federal
2. **50 synthetic Indian personas** grounded in NSSO demographic data respond in real time
3. **Coordinator agent** synthesises all findings into a final intelligence briefing

Validated against MGNREGA — 20 years of documented outcomes confirm the system's accuracy.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add OPENROUTER_API_KEY to .env
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install          # also installs TypeScript + @types/react
npm run dev
```

Open http://localhost:5173

> **Note:** delete `vite.config.js` if it still exists alongside `vite.config.ts`.

## Deployment

| Service  | Platform | Config           |
|----------|----------|------------------|
| Backend  | Render   | `render.yaml`    |
| Frontend | Vercel   | `vercel.json`    |

Set `OPENROUTER_API_KEY` in Render dashboard → Environment.

## Architecture

```
User submits policy
       │
       ▼
GET /api/analyse/stream   (SSE, query params)
       │
       ├─ Fiscal Analyst ──────────► yield agent event
       ├─ Labor & Employment ──────► yield agent event
       ├─ Equity & Social Impact ──► yield agent event
       ├─ Regional & Federal ──────► yield agent event
       └─ Coordinator Agent ───────► yield coordinator event
                                           │
                                     yield done event
                                           │
                               Frontend: stage = 'personas'
                               50 dots animate (80ms × 50 = 4s)
                                           │
                               Frontend: stage = 'complete'
                               Stage3Findings renders
```

## API

| Method | Endpoint                        | Description                         |
|--------|---------------------------------|-------------------------------------|
| GET    | `/api/analyse/stream?title=&description=` | SSE stream of agent events |
| GET    | `/api/validate`                 | MGNREGA retrospective result        |

## Stack

FastAPI · Python 3.11+ · httpx · OpenRouter (Gemini 2.0 Flash)  
React 18 · TypeScript · Vite · Tailwind CSS · DM Sans · Instrument Serif

## Data Sources

NSSO PLFS 2023 · Census 2011 · NFHS-5 · PRS Legislative Research · CAG Audit Reports
# NItiLens
