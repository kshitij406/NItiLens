# NitiLens — AI Policy Stress Tester for India
**Team JFKN | DayZero 2.0 | CodeNex SRMIST | AI & ML Track**

🔗 Live: https://niti-lens.vercel.app
📦 Backend: https://nitilens.onrender.com

## What it does
NitiLens stress-tests Indian government policies through a 4-stage AI pipeline:

1. **Policy Classifier** — Categorises the policy by domain, geography, and affected demographics before analysis begins
2. **4 Specialist Agents** — Fiscal Analyst, Labor Economist, Equity Researcher, Regional Analyst run sequentially, each independently assessing risk through their domain lens
3. **30/50 Synthetic Indian Personas** — Real LLM calls grounded in Indian demographic data (NSSO, Census 2011). Each persona reads specialist risks and responds from their own position. Demo mode: 30 personas. Full mode: 50 personas.
4. **Coordinator Synthesis** — A final agent synthesises all findings into an intelligence briefing with verdict, key risk, blind spot, and sharpest agent disagreement

Every analysis is sealed with a hash and timestamp for future real-world validation.

## Validated against MGNREGA
We pre-ran NitiLens on MGNREGA (2005) — one of India's most studied policies with 20 years of outcome data from NSSO and World Bank. The system correctly identified rural wage floor effects, fiscal overrun patterns, and state capacity gaps. Available on the Historical Validation tab.

## Tech Stack
- **Backend**: FastAPI, Python, httpx, OpenRouter API
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **AI**: Multi-agent LLM pipeline via OpenRouter
- **Deployment**: Render (backend) + Vercel (frontend)

## Data Sources
NSSO PLFS 2023 · Census 2011 · NFHS-5 · PRS Legislative Research · CAG Audit Reports

## Setup

### Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add OPENROUTER_API_KEY to .env
uvicorn main:app --reload --port 8000

### Frontend
cd frontend
npm install
npm run dev

## Team JFKN
- Kshitij Jha (Team Leader)
- Nithul Krishna
- Faiz Mohammed Salim
- Johann Peter Maju

## Architecture Reference
Inspired by Civica (Hack Canada 2026) by Shlok Ippala et al. NitiLens is an independent India-specific implementation with different data sources, validation approach, streaming architecture, and demographic persona system.
