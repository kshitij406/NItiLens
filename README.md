# NitiLens — AI Policy Stress Tester for India

**Team JFKN | DayZero 2.0 | CodeNex SRMIST | AI & ML Track**

## What it does

NitiLens stress-tests Indian government policies through a streaming, multi-stage pipeline:

1. **4 specialist AI agents** stream findings sequentially (Fiscal, Labor, Equity, Regional)
2. **Persona validation** streams citizen-level checks in real time
   - `DEMO`: 30 personas (~2 min)
   - `FULL`: 50 personas (~5 min)
3. **Coordinator agent** synthesises the final intelligence briefing

Validated against MGNREGA retrospective data in the Historical Validation tab.

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# add OPENROUTER_API_KEY in .env
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/analyse/stream?title=&description=&mode=demo|full` | SSE stream: agent -> persona -> coordinator -> done |
| GET | `/api/validate` | Static retrospective validation payload |

### SSE event types

- `agent`: specialist result
- `persona`: persona validation result + `index` + `total`
- `coordinator`: synthesis object
- `done`: `overall_severity` and `policy_title`

## Architecture

```text
User submits title + description + mode
        |
        v
GET /api/analyse/stream (SSE)
        |
        +--> Fiscal agent      -> event: agent
        +--> Labor agent       -> event: agent
        +--> Equity agent      -> event: agent
        +--> Regional agent    -> event: agent
        +--> Persona batches   -> many events: persona
        +--> Coordinator       -> event: coordinator
        +--> Final marker      -> event: done
```

Frontend consumes stream with raw `fetch` + `ReadableStream` and progressively updates Stage 2/3 UI.

## Mode behavior

- `demo`: first 30 personas from the Indian persona catalog
- `full`: all 50 personas
- personas are processed in backend batches of 5 to limit rate spikes

## Deployment

| Service | Platform | Config |
|---|---|---|
| Backend | Render | `backend/render.yaml` |
| Frontend | Vercel | project settings / env |

Set `OPENROUTER_API_KEY` in backend environment.
Set `VITE_API_URL` on frontend if backend is not localhost.

## Documentation

- Product notes: `Product_DESIGN_DOC.md`
- Production design: `PRODUCTION_DESIGN_DOC.md`
