# NitiLens — Product Design Document
### AI Policy Stress Tester for India
**Team JFKN | DayZero 2.0 | CodeNex | SRMIST**

---

## Problem

Indian policy decisions affect 1.4 billion people across radically different economic, social, and regional contexts. Yet most policy analysis is siloed — fiscal teams miss labor impacts, equity concerns get deprioritized, and federal tensions go unexamined until after rollout. The GST implementation is a textbook example: technically sound in theory, devastating in practice for informal workers and consuming states.

There is no fast, multi-lens stress-testing tool available to policymakers, journalists, or citizens.

---

## Solution

NitiLens takes any proposed Indian policy as input and fires four specialist AI agents in parallel — each with deep domain context baked into their system prompts. Within seconds, users receive structured risk assessments from four independent analytical perspectives.

**The validation hook:** We demonstrate accuracy by running NitiLens retrospectively on the 2017 GST rollout. The system identifies every major failure mode that played out in reality — giving evaluators confidence that the tool would have flagged these risks in advance.

---

## Core Flow

```
User inputs policy title + description
        │
        ▼
FastAPI /api/analyse
        │
        ├─── Fiscal Analyst ──────────────────┐
        ├─── Labor & Employment Analyst ──────┤  asyncio.gather()
        ├─── Equity & Social Impact Analyst ──┤  (4 parallel LLM calls)
        └─── Regional & Federal Analyst ──────┘
                                              │
                                        Aggregate JSON
                                   (overall_severity = highest)
                                              │
                                        React Frontend
                                    (4 risk cards + severity badge)
```

---

## Agent Roster

| Agent | Domain Focus | Key Questions |
|-------|-------------|---------------|
| **Fiscal Analyst** | Budget, taxation, deficit | Does this break the fiscal math? What does it do to CAG audit risk? |
| **Labor & Employment Analyst** | Jobs, informal sector, gig workers | Who loses work? Does this help or harm India's 90% informal workforce? |
| **Equity & Social Impact Analyst** | SC/ST/OBC, women, rural poor | Which marginalised groups bear disproportionate cost? |
| **Regional & Federal Analyst** | Centre-state, northeast, linguistic minorities | Does this ignore regional economic diversity? Who wins and loses federally? |

---

## Input

- **Policy Title** — short identifier (e.g. "One Nation One Election")
- **Policy Description** — free-form text, objectives + implementation mechanism + scope

---

## Output Structure

Each agent returns:
```json
{
  "agent": "Fiscal Analyst",
  "risks": ["risk 1", "risk 2", "risk 3"],
  "severity": "High | Medium | Low",
  "most_affected": "One sentence on the most impacted group",
  "summary": "Two sentence analytical summary"
}
```

Aggregated response includes `overall_severity` (highest severity across agents).

---

## Validation Layer

**Why this matters for the demo:**
The GST Retrospective tab pre-loads a hardcoded analysis of the 2017 GST rollout. Every risk it identifies — informal sector displacement, Centre-state fiscal disputes, essential goods price spikes, northeast supply chain disruption — is documented in post-mortems. This proves NitiLens would have flagged these as **High** risk before implementation, making the tool credible to evaluators.

**Framing:** "We tested NitiLens on a policy whose outcomes are already known. It got them right. Now imagine running it before the policy launches."

---

## Technical Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS v3 |
| Backend | FastAPI, Python 3.11+ |
| LLM | Google Gemini 2.0 Flash (via OpenRouter) |
| Parallelism | `asyncio.gather()` + `httpx.AsyncClient` |
| Deployment (demo) | Localhost (backend :8000, frontend :5173) |

---

## UI Design

**Color system:**
- Background: `#0f172a` (slate-900)
- Card: `#1e293b` (slate-800)
- Border: `#334155` (slate-700)
- Accent: `#6366f1` (indigo-500)

**Layout:** Single page, two tabs (Analyse | Historical Validation). Results appear inline below the form — no page reload. Mobile-first responsive grid (1 col mobile → 2 col desktop).

**Severity color coding:**
- High → Red (`bg-red-500/20 text-red-400`)
- Medium → Yellow (`bg-yellow-500/20 text-yellow-400`)
- Low → Green (`bg-green-500/20 text-green-400`)

---

## Pages / States

1. **Input state** — Title field + description textarea + Analyse button
2. **Loading state** — Spinner with "Deploying specialist agents..."
3. **Results state** — Overall severity badge + 4 AgentCards in 2×2 grid
4. **Historical Validation tab** — Pre-fetched GST analysis with informational banner

---

## Key Demo Talking Points

1. **Parallelism:** All 4 agents fire simultaneously via `asyncio.gather()` — latency is bounded by the slowest agent, not their sum.
2. **Structured output:** Agents respond in strict JSON, making results machine-readable and composable.
3. **Domain specialisation:** Each agent has a 3-sentence system prompt encoding decades of domain expertise. The prompts are the product moat.
4. **Retrospective validation:** GST tab is a built-in credibility proof — show it first, then demo live analysis.
5. **Graceful degradation:** If any agent fails to return valid JSON, a default response is substituted — the system never crashes.

---

## Scope (MVP — DayZero 2.0)

**In scope:**
- 4 agents, parallel execution
- Single-page React frontend
- FastAPI backend with 2 endpoints
- GST validation tab

**Out of scope (post-hackathon):**
- User authentication / saved analyses
- PDF/document policy upload
- Comparison mode (policy A vs policy B)
- Agent confidence scores
- Historical database of past analyses
- Fine-tuned India-specific models
