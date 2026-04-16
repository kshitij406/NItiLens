import re
import json
import httpx

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.0-flash-exp:free"

AGENT_USER_TEMPLATE = (
    "Policy Title: {title}\n\n"
    "Policy Description: {description}\n\n"
    "Return ONLY this JSON:\n"
    "{{\n"
    '  "agent": "{agent_name}",\n'
    '  "risks": ["risk 1", "risk 2", "risk 3"],\n'
    '  "opportunities": ["opportunity 1", "opportunity 2"],\n'
    '  "severity": "High",\n'
    '  "most_affected": "one sentence",\n'
    '  "summary": "two sentences"\n'
    "}}"
)

COORDINATOR_USER_TEMPLATE = (
    "Policy Title: {title}\n\n"
    "Specialist Agent Reports:\n{reports}\n\n"
    "Return ONLY this JSON:\n"
    "{{\n"
    '  "verdict": "2 sentence overall verdict",\n'
    '  "key_risk": "the single most critical risk across all agents",\n'
    '  "blind_spot": "what all agents may have missed or underweighted",\n'
    '  "sharpest_disagreement": "where agents diverged most and why it matters",\n'
    '  "confidence": "High"\n'
    "}}"
)

AGENT_DEFAULTS = {
    "risks": ["Agent response could not be parsed. Please retry."],
    "opportunities": [],
    "severity": "Medium",
    "most_affected": "Unable to determine",
    "summary": "Parsing failed. Please retry.",
}

COORDINATOR_DEFAULTS = {
    "verdict": "Coordinator synthesis unavailable.",
    "key_risk": "Unable to determine.",
    "blind_spot": "Unable to determine.",
    "sharpest_disagreement": "Unable to determine.",
    "confidence": "Low",
}

FISCAL_SYSTEM = (
    "You are a senior fiscal policy analyst specialising in Indian government finance. "
    "Analyse the given policy for fiscal impact, tax revenue implications, government expenditure, "
    "deficit risks, and debt sustainability. Focus on Union Budget alignment and CAG audit concerns. "
    "Respond ONLY with a valid JSON object, no markdown, no explanation, no preamble. "
    "Your response must start with { and end with }. No markdown. No code fences. No explanation before or after the JSON."
)

LABOR_SYSTEM = (
    "You are a labor economist specialising in India's workforce. "
    "Analyse the given policy for job creation or loss, wage effects, impact on the informal sector "
    "which employs 90% of Indian workers, migrant labor, and gig economy workers. "
    "Respond ONLY with a valid JSON object, no markdown, no explanation, no preamble. "
    "Your response must start with { and end with }. No markdown. No code fences. No explanation before or after the JSON."
)

EQUITY_SYSTEM = (
    "You are a social equity researcher specialising in India. "
    "Analyse the given policy for effects on Scheduled Castes, Scheduled Tribes, OBCs, women, "
    "and low-income rural households. Identify which groups bear disproportionate costs or benefits. "
    "Respond ONLY with a valid JSON object, no markdown, no explanation, no preamble. "
    "Your response must start with { and end with }. No markdown. No code fences. No explanation before or after the JSON."
)

REGIONAL_SYSTEM = (
    "You are a federalism and regional policy analyst for India. "
    "Analyse the given policy for state-level variance, Centre-state fiscal tensions, "
    "impact on northeastern states, linguistic minorities, and whether the policy ignores "
    "regional economic diversity. "
    "Respond ONLY with a valid JSON object, no markdown, no explanation, no preamble. "
    "Your response must start with { and end with }. No markdown. No code fences. No explanation before or after the JSON."
)

COORDINATOR_SYSTEM = (
    "You are the lead policy intelligence coordinator for NitiLens. "
    "You have received independent risk assessments from 4 specialist agents. "
    "Synthesise their findings into a final intelligence briefing. "
    "Be direct, specific, and highlight where agents disagree. "
    "Respond ONLY with a valid JSON object, no markdown, no explanation, no preamble. "
    "Your response must start with { and end with }. No markdown. No code fences. No explanation before or after the JSON."
)

AGENTS = [
    {"name": "Fiscal Analyst", "system": FISCAL_SYSTEM},
    {"name": "Labor & Employment Analyst", "system": LABOR_SYSTEM},
    {"name": "Equity & Social Impact Analyst", "system": EQUITY_SYSTEM},
    {"name": "Regional & Federal Analyst", "system": REGIONAL_SYSTEM},
]


def parse_response(content: str, agent_name: str, default_keys: dict) -> dict:
    content = content.strip()
    # Remove all markdown code fences
    content = re.sub(r'```json', '', content)
    content = re.sub(r'```', '', content)
    content = content.strip()
    # Extract just the JSON object if there is surrounding text
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        content = match.group()
    try:
        return json.loads(content)
    except Exception:
        return {"agent": agent_name, **default_keys}


def _headers(api_key: str) -> dict:
    return {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://nitilens.vercel.app",
        "Content-Type": "application/json",
    }


async def run_agent(
    client: httpx.AsyncClient,
    api_key: str,
    agent_name: str,
    system: str,
    title: str,
    description: str,
) -> dict:
    user_msg = AGENT_USER_TEMPLATE.format(
        title=title, description=description, agent_name=agent_name
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    }
    try:
        resp = await client.post(
            OPENROUTER_URL, json=payload, headers=_headers(api_key), timeout=45.0
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        result = parse_response(content, agent_name, AGENT_DEFAULTS.copy())
        result.setdefault("agent", agent_name)
        result.setdefault("risks", [])
        result.setdefault("opportunities", [])
        result.setdefault("severity", "Medium")
        result.setdefault("most_affected", "Unable to determine")
        result.setdefault("summary", "")
        return result
    except Exception:
        return {"agent": agent_name, **AGENT_DEFAULTS}


async def run_coordinator(
    client: httpx.AsyncClient,
    api_key: str,
    title: str,
    all_results: list,
) -> dict:
    user_msg = COORDINATOR_USER_TEMPLATE.format(
        title=title, reports=json.dumps(all_results, indent=2)
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": COORDINATOR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    }
    try:
        resp = await client.post(
            OPENROUTER_URL, json=payload, headers=_headers(api_key), timeout=45.0
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return parse_response(content, "Coordinator", COORDINATOR_DEFAULTS.copy())
    except Exception:
        return {"agent": "Coordinator", **COORDINATOR_DEFAULTS}


def compute_overall_severity(agents: list) -> str:
    severities = {a.get("severity") for a in agents}
    if "High" in severities:
        return "High"
    if "Medium" in severities:
        return "Medium"
    return "Low"
