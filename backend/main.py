import asyncio
import json
import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agents import (
    DEMO_PERSONAS,
    FULL_PERSONAS,
    MODEL,
    _default_agent,
    coordinator_agent,
    equity_agent,
    fiscal_agent,
    labor_agent,
    regional_agent,
    run_persona,
)

load_dotenv()
logger = logging.getLogger(__name__)

app = FastAPI(title="NitiLens API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/api/analyse/stream')
async def analyse_stream(title: str, description: str, mode: str = 'demo'):
    async def generate():
        agent_results = []
        persona_results = []

        # Run 4 agents sequentially, emit each as it completes
        for agent_fn in [fiscal_agent, labor_agent, equity_agent, regional_agent]:
            try:
                result = await agent_fn(title, description)
            except Exception:
                result = _default_agent(agent_fn.__name__)
            agent_results.append(result)
            logger.info(f"Agent complete: {result.get('agent')} | severity: {result.get('severity')}")
            yield f"data: {json.dumps({'type': 'agent', 'data': result})}\n\n"
            await asyncio.sleep(0.1)

        # Select personas based on mode
        personas = DEMO_PERSONAS if mode == "demo" else FULL_PERSONAS
        total = len(personas)

        # Extract top risks from agent results for persona validation
        all_risks = []
        for agent in agent_results:
            all_risks.extend(agent.get('risks', [])[:2])
        top_risks = all_risks[:8]  # Cap at 8 risks for persona prompts

        # Run personas in batches to avoid rate limits
        BATCH_SIZE = 2 if mode == "demo" else 3
        for batch_start in range(0, total, BATCH_SIZE):
            batch = personas[batch_start:batch_start + BATCH_SIZE]
            batch_results = await asyncio.gather(
                *[run_persona(p, title, top_risks) for p in batch],
                return_exceptions=True
            )
            for i, result in enumerate(batch_results):
                persona = batch[i]
                if isinstance(result, Exception):
                    result = {
                        "persona_id": persona["id"],
                        "name": persona["name"],
                        "state": persona["state"],
                        "occupation": persona["occupation"],
                        "caste_category": persona["caste_category"],
                        "validations": [],
                        "missed_risk": None,
                    }
                persona_results.append(result)
                yield f"data: {json.dumps({'type': 'persona', 'data': result, 'index': batch_start + i, 'total': total})}\n\n"
            await asyncio.sleep(1.0)  # Brief pause between batches to respect rate limits

        logger.info(f"Personas complete: {len(persona_results)} responses")

        # Run coordinator
        try:
            coordinator = await coordinator_agent(title, agent_results)
        except Exception:
            coordinator = {
                'verdict': 'Synthesis unavailable.',
                'key_risk': 'Unable to determine.',
                'blind_spot': 'Unable to determine.',
                'sharpest_disagreement': 'Unable to determine.',
                'confidence': 'Low'
            }

        # Compute overall severity
        severity_order = {'High': 3, 'Medium': 2, 'Low': 1}
        overall_severity = max(
            (r.get('severity', 'Low') for r in agent_results),
            key=lambda s: severity_order.get(s, 0),
            default='Medium'
        )

        logger.info(
            f"Coordinator complete | confidence: {coordinator.get('confidence')} | overall: {overall_severity}"
        )

        yield f"data: {json.dumps({'type': 'coordinator', 'data': coordinator})}\n\n"
        yield f"data: {json.dumps({'type': 'done', 'overall_severity': overall_severity, 'policy_title': title})}\n\n"

    return StreamingResponse(
        generate(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        }
    )


@app.get('/health')
async def health():
    return {"status": "ok", "model": MODEL}


@app.get('/api/validate')
async def validate():
    return {
        "policy_title": "MGNREGA - Mahatma Gandhi National Rural Employment Guarantee Act (2005)",
        "note": "Retrospective validation case. MGNREGA is one of India's most studied policy interventions with 20 years of outcome data from NSSO, World Bank, and peer-reviewed research.",
        "agents": [
            {
                "agent": "Fiscal Analyst",
                "risks": [
                    "Year-on-year budget overruns averaging 18% above allocation",
                    "Wage payment delays caused by fund release bottlenecks",
                    "Leakage and ghost beneficiary estimates ranged 20-30% in early years",
                ],
                "opportunities": [
                    "Automatic stabiliser effect during economic downturns",
                    "Counter-cyclical fiscal tool validated during 2008 global crisis",
                ],
                "severity": "Medium",
                "most_affected": "State finance ministries with poor administrative capacity, particularly Bihar, Jharkhand, and Odisha",
                "summary": "MGNREGA created significant fiscal pressure through persistent budget overruns and implementation leakage. However, its role as an automatic economic stabiliser during the 2008 financial crisis validated its counter-cyclical value, with World Bank studies confirming positive fiscal multiplier effects in rural districts.",
            },
            {
                "agent": "Labor & Employment Analyst",
                "risks": [
                    "Crowding out of agricultural labor in peak seasons",
                    "Wage rate distortions in local markets in some states",
                    "Implementation delays meant work was unavailable when most needed",
                ],
                "opportunities": [
                    "3.5 billion person-days of employment generated by 2023",
                    "Rural wage floor established and documented by NSSO data",
                    "Female labor force participation increased 12-18% in high-implementation districts",
                ],
                "severity": "Low",
                "most_affected": "Landless agricultural laborers and rural women - 270 million unique workers enrolled by 2020",
                "summary": "MGNREGA is among the most documented labor interventions in development economics. NSSO and ILO data confirm sustained rural wage floor effects and significant female workforce entry. Implementation quality varied enormously by state, with Kerala and Andhra Pradesh showing strongest outcomes.",
            },
            {
                "agent": "Equity & Social Impact Analyst",
                "risks": [
                    "SC/ST households faced caste-based exclusion in gram sabha meetings",
                    "Women faced safety issues at worksites in several states",
                    "Disabled and elderly excluded due to physical nature of work",
                ],
                "opportunities": [
                    "SC households reduced seasonal migration dependency significantly",
                    "Women gained independent income and banking access through Jan Dhan linkage",
                    "Asset creation disproportionately benefited poor landless households",
                ],
                "severity": "Low",
                "most_affected": "SC and ST landless households in BIMARU states - documented to have reduced extreme poverty by 14% in high-implementation blocks",
                "summary": "MGNREGA is one of the few Indian policies with documented positive equity outcomes at scale. Randomised control trials confirmed significant consumption gains for the poorest quintile. Caste-based exclusion in panchayat implementation was the primary equity failure.",
            },
            {
                "agent": "Regional & Federal Analyst",
                "risks": [
                    "States with weak administrative capacity could not absorb funds effectively",
                    "Centre-state wage rate disputes delayed implementation across 12 states in 2014-16",
                    "Northeast states faced logistical barriers to asset creation",
                ],
                "opportunities": [
                    "Panchayati raj institutions strengthened through mandatory gram sabha oversight",
                    "High-performing states used MGNREGA to build durable rural infrastructure",
                    "Federalism test case: state flexibility in implementation proved essential to success",
                ],
                "severity": "Low",
                "most_affected": "Weak-capacity states like Uttar Pradesh and Bihar where implementation gaps left the poorest beneficiaries underserved",
                "summary": "MGNREGA exposed deep interstate implementation capacity gaps that federal policy design had not anticipated. The contrast between Kerala and UP became a textbook case in Indian federalism studies. The social audit mechanism was the most significant institutional innovation.",
            },
        ],
        "coordinator": {
            "verdict": "MGNREGA is a net positive intervention with documented employment and wage floor effects at scale. Its primary failures were administrative rather than conceptual, concentrated in low-capacity states.",
            "key_risk": "Implementation quality variance across states meant the poorest districts - which needed the scheme most - received the weakest delivery.",
            "blind_spot": "All agents underweighted the long-term asset creation value. MGNREGA built roads, ponds, and watershed structures that compounded rural productivity gains beyond the direct wage effect.",
            "sharpest_disagreement": "Fiscal and Labor agents diverged on net value - Fiscal flagged persistent overruns while Labor confirmed the wage floor effect. Both are correct; they reflect different time horizons.",
            "confidence": "High",
        },
        "overall_severity": "Low",
    }
