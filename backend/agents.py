import json
import os
import re
import asyncio

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-3.1-flash-lite-preview")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
AGENT_MAX_TOKENS = 650
COORDINATOR_MAX_TOKENS = 750
PERSONA_MAX_TOKENS = 520

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

INDIAN_PERSONAS = [
    {"id": 1, "name": "Ramesh Kumar", "age_bracket": "35-49", "state": "Uttar Pradesh", "district": "Lucknow", "income_bracket": "low", "occupation": "small farmer", "caste_category": "OBC", "gender": "male", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 2, "name": "Priya Sharma", "age_bracket": "25-34", "state": "Delhi", "district": "East Delhi", "income_bracket": "medium", "occupation": "government school teacher", "caste_category": "general", "gender": "female", "residence": "urban", "employment_type": "salaried", "family_size": "small_family"},
    {"id": 3, "name": "Mohammed Irfan", "age_bracket": "18-24", "state": "Uttar Pradesh", "district": "Moradabad", "income_bracket": "very_low", "occupation": "factory worker", "caste_category": "OBC", "gender": "male", "residence": "semi_urban", "employment_type": "informal", "family_size": "large_family"},
    {"id": 4, "name": "Sunita Devi", "age_bracket": "50-64", "state": "Bihar", "district": "Muzaffarpur", "income_bracket": "very_low", "occupation": "MGNREGA worker", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "informal", "family_size": "large_family"},
    {"id": 5, "name": "Harpreet Singh", "age_bracket": "35-49", "state": "Punjab", "district": "Ludhiana", "income_bracket": "medium", "occupation": "wheat farmer", "caste_category": "general", "gender": "male", "residence": "rural", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 6, "name": "Kavita Rani", "age_bracket": "25-34", "state": "Haryana", "district": "Rohtak", "income_bracket": "low", "occupation": "Anganwadi worker", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "government_scheme", "family_size": "small_family"},
    {"id": 7, "name": "Vikram Chauhan", "age_bracket": "18-24", "state": "Rajasthan", "district": "Jaipur", "income_bracket": "medium", "occupation": "gig delivery worker", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "gig", "family_size": "single"},
    {"id": 8, "name": "Meena Gurjar", "age_bracket": "35-49", "state": "Rajasthan", "district": "Alwar", "income_bracket": "very_low", "occupation": "stone quarry worker", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "informal", "family_size": "large_family"},
    {"id": 9, "name": "Deepak Tiwari", "age_bracket": "50-64", "state": "Madhya Pradesh", "district": "Bhopal", "income_bracket": "medium", "occupation": "retired government clerk", "caste_category": "general", "gender": "male", "residence": "urban", "employment_type": "retired", "family_size": "small_family"},
    {"id": 10, "name": "Lakshmi Venkatesh", "age_bracket": "35-49", "state": "Tamil Nadu", "district": "Chennai", "income_bracket": "high", "occupation": "IT professional", "caste_category": "general", "gender": "female", "residence": "urban", "employment_type": "salaried", "family_size": "small_family"},
    {"id": 11, "name": "Rajan Pillai", "age_bracket": "50-64", "state": "Kerala", "district": "Thiruvananthapuram", "income_bracket": "medium", "occupation": "nurse", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "salaried", "family_size": "small_family"},
    {"id": 12, "name": "Ammaji Reddy", "age_bracket": "35-49", "state": "Andhra Pradesh", "district": "Kurnool", "income_bracket": "low", "occupation": "ASHA worker", "caste_category": "OBC", "gender": "female", "residence": "rural", "employment_type": "government_scheme", "family_size": "large_family"},
    {"id": 13, "name": "Suresh Babu", "age_bracket": "25-34", "state": "Telangana", "district": "Hyderabad", "income_bracket": "high", "occupation": "software engineer", "caste_category": "SC", "gender": "male", "residence": "urban", "employment_type": "salaried", "family_size": "single"},
    {"id": 14, "name": "Fatima Begum", "age_bracket": "25-34", "state": "Karnataka", "district": "Bengaluru", "income_bracket": "low", "occupation": "garment factory worker", "caste_category": "OBC", "gender": "female", "residence": "urban", "employment_type": "informal", "family_size": "small_family"},
    {"id": 15, "name": "Krishnamurthy", "age_bracket": "65+", "state": "Tamil Nadu", "district": "Madurai", "income_bracket": "very_low", "occupation": "retired farmer", "caste_category": "SC", "gender": "male", "residence": "rural", "employment_type": "retired", "family_size": "couple"},
    {"id": 16, "name": "Bapi Das", "age_bracket": "25-34", "state": "West Bengal", "district": "Kolkata", "income_bracket": "low", "occupation": "jute mill worker", "caste_category": "SC", "gender": "male", "residence": "urban", "employment_type": "informal", "family_size": "small_family"},
    {"id": 17, "name": "Mamta Oraon", "age_bracket": "35-49", "state": "Jharkhand", "district": "Ranchi", "income_bracket": "very_low", "occupation": "tribal farmer", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 18, "name": "Prakash Mahato", "age_bracket": "18-24", "state": "Odisha", "district": "Bhubaneswar", "income_bracket": "low", "occupation": "migrant construction worker", "caste_category": "OBC", "gender": "male", "residence": "semi_urban", "employment_type": "informal", "family_size": "single"},
    {"id": 19, "name": "Anjali Biswas", "age_bracket": "25-34", "state": "West Bengal", "district": "Murshidabad", "income_bracket": "very_low", "occupation": "domestic worker", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "informal", "family_size": "small_family"},
    {"id": 20, "name": "Ratan Tudu", "age_bracket": "50-64", "state": "Jharkhand", "district": "Dumka", "income_bracket": "very_low", "occupation": "forest rights holder", "caste_category": "ST", "gender": "male", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 21, "name": "Rajesh Patel", "age_bracket": "35-49", "state": "Gujarat", "district": "Surat", "income_bracket": "medium", "occupation": "textile MSME owner", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 22, "name": "Savita Jadhav", "age_bracket": "25-34", "state": "Maharashtra", "district": "Mumbai", "income_bracket": "low", "occupation": "street vendor", "caste_category": "OBC", "gender": "female", "residence": "urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 23, "name": "Arjun Desai", "age_bracket": "25-34", "state": "Maharashtra", "district": "Pune", "income_bracket": "high", "occupation": "startup founder", "caste_category": "general", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "single"},
    {"id": 24, "name": "Manisha Bhil", "age_bracket": "35-49", "state": "Rajasthan", "district": "Udaipur", "income_bracket": "very_low", "occupation": "tribal artisan", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 25, "name": "Dinesh Ambani", "age_bracket": "50-64", "state": "Gujarat", "district": "Ahmedabad", "income_bracket": "high", "occupation": "diamond trader", "caste_category": "general", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 26, "name": "Lalthansangi", "age_bracket": "25-34", "state": "Mizoram", "district": "Aizawl", "income_bracket": "low", "occupation": "government school teacher", "caste_category": "ST", "gender": "female", "residence": "urban", "employment_type": "salaried", "family_size": "small_family"},
    {"id": 27, "name": "Biren Sharma", "age_bracket": "35-49", "state": "Manipur", "district": "Imphal", "income_bracket": "medium", "occupation": "small business owner", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 28, "name": "Gita Boro", "age_bracket": "18-24", "state": "Assam", "district": "Sonitpur", "income_bracket": "very_low", "occupation": "tea garden worker", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "informal", "family_size": "large_family"},
    {"id": 29, "name": "Temjen Jamir", "age_bracket": "35-49", "state": "Nagaland", "district": "Kohima", "income_bracket": "medium", "occupation": "tribal council member", "caste_category": "ST", "gender": "male", "residence": "semi_urban", "employment_type": "government", "family_size": "large_family"},
    {"id": 30, "name": "Phajolly Syiem", "age_bracket": "25-34", "state": "Meghalaya", "district": "Shillong", "income_bracket": "low", "occupation": "handloom weaver", "caste_category": "ST", "gender": "female", "residence": "urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 31, "name": "Santosh Yadav", "age_bracket": "18-24", "state": "Bihar", "district": "Patna", "income_bracket": "low", "occupation": "college student", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "student", "family_size": "single"},
    {"id": 32, "name": "Kamla Bai", "age_bracket": "65+", "state": "Madhya Pradesh", "district": "Gwalior", "income_bracket": "very_low", "occupation": "widow pensioner", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "retired", "family_size": "single"},
    {"id": 33, "name": "Arun Nair", "age_bracket": "35-49", "state": "Kerala", "district": "Kochi", "income_bracket": "high", "occupation": "Gulf returnee entrepreneur", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 34, "name": "Devika Menon", "age_bracket": "25-34", "state": "Kerala", "district": "Kozhikode", "income_bracket": "medium", "occupation": "nurse working abroad", "caste_category": "general", "gender": "female", "residence": "urban", "employment_type": "salaried", "family_size": "couple"},
    {"id": 35, "name": "Iqbal Hussain", "age_bracket": "50-64", "state": "Uttar Pradesh", "district": "Varanasi", "income_bracket": "low", "occupation": "handloom weaver", "caste_category": "OBC", "gender": "male", "residence": "urban", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 36, "name": "Shanti Murmu", "age_bracket": "35-49", "state": "West Bengal", "district": "Purulia", "income_bracket": "very_low", "occupation": "Santali tribal farmer", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 37, "name": "Gopal Krishnan", "age_bracket": "50-64", "state": "Tamil Nadu", "district": "Thanjavur", "income_bracket": "low", "occupation": "temple priest", "caste_category": "general", "gender": "male", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 38, "name": "Nirmala Devi", "age_bracket": "25-34", "state": "Himachal Pradesh", "district": "Shimla", "income_bracket": "medium", "occupation": "apple orchard worker", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "seasonal", "family_size": "small_family"},
    {"id": 39, "name": "Jitendra Kashyap", "age_bracket": "18-24", "state": "Chhattisgarh", "district": "Raipur", "income_bracket": "low", "occupation": "coal mine contract worker", "caste_category": "OBC", "gender": "male", "residence": "semi_urban", "employment_type": "informal", "family_size": "single"},
    {"id": 40, "name": "Padma Venkat", "age_bracket": "35-49", "state": "Andhra Pradesh", "district": "Visakhapatnam", "income_bracket": "medium", "occupation": "fisherwoman cooperative member", "caste_category": "OBC", "gender": "female", "residence": "coastal", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 41, "name": "Bhupinder Gill", "age_bracket": "50-64", "state": "Punjab", "district": "Amritsar", "income_bracket": "medium", "occupation": "retired army soldier", "caste_category": "general", "gender": "male", "residence": "semi_urban", "employment_type": "retired", "family_size": "large_family"},
    {"id": 42, "name": "Zainab Sheikh", "age_bracket": "25-34", "state": "Maharashtra", "district": "Aurangabad", "income_bracket": "low", "occupation": "textile worker", "caste_category": "OBC", "gender": "female", "residence": "urban", "employment_type": "informal", "family_size": "small_family"},
    {"id": 43, "name": "Manoj Thakur", "age_bracket": "35-49", "state": "Uttarakhand", "district": "Dehradun", "income_bracket": "medium", "occupation": "hill farmer turned hotelier", "caste_category": "general", "gender": "male", "residence": "semi_urban", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 44, "name": "Rosy Tigga", "age_bracket": "18-24", "state": "Jharkhand", "district": "Jamshedpur", "income_bracket": "low", "occupation": "first-generation college student", "caste_category": "ST", "gender": "female", "residence": "urban", "employment_type": "student", "family_size": "large_family"},
    {"id": 45, "name": "Chandran Pillai", "age_bracket": "65+", "state": "Kerala", "district": "Palakkad", "income_bracket": "medium", "occupation": "retired bank manager", "caste_category": "OBC", "gender": "male", "residence": "rural", "employment_type": "retired", "family_size": "couple"},
    {"id": 46, "name": "Pushpa Kumari", "age_bracket": "35-49", "state": "Bihar", "district": "Gaya", "income_bracket": "very_low", "occupation": "bonded labor freed by government scheme", "caste_category": "SC", "gender": "female", "residence": "rural", "employment_type": "informal", "family_size": "large_family"},
    {"id": 47, "name": "Naresh Solanki", "age_bracket": "25-34", "state": "Gujarat", "district": "Kutch", "income_bracket": "low", "occupation": "salt pan worker", "caste_category": "SC", "gender": "male", "residence": "rural", "employment_type": "seasonal", "family_size": "small_family"},
    {"id": 48, "name": "Dhanmaya Rai", "age_bracket": "35-49", "state": "Sikkim", "district": "Gangtok", "income_bracket": "medium", "occupation": "organic cardamom farmer", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "self_employed", "family_size": "small_family"},
    {"id": 49, "name": "Akbar Ali", "age_bracket": "50-64", "state": "West Bengal", "district": "Malda", "income_bracket": "low", "occupation": "mango orchard farmer", "caste_category": "general", "gender": "male", "residence": "rural", "employment_type": "self_employed", "family_size": "large_family"},
    {"id": 50, "name": "Savitri Nayak", "age_bracket": "25-34", "state": "Odisha", "district": "Koraput", "income_bracket": "very_low", "occupation": "tribal rights activist", "caste_category": "ST", "gender": "female", "residence": "rural", "employment_type": "NGO", "family_size": "single"},
]

DEMO_PERSONAS = INDIAN_PERSONAS[:30]
FULL_PERSONAS = INDIAN_PERSONAS

PERSONA_SYSTEM_PROMPT = """You are validating policy risk assessments from the perspective of a specific Indian citizen. Domain experts identified risks for an Indian government policy. Your job: determine which risks ACTUALLY AFFECT someone matching your demographic profile.

Be honest and specific. Most policies affect most people at 0 or 1. Only use severity 3 if this risk would genuinely destabilize your life.

Respond ONLY with valid JSON, no markdown, no explanation."""


def parse_response(content: str, agent_name: str) -> dict:
    if not content:
        return _default_agent(agent_name)

    content = re.sub(r"```(?:json)?\s*", "", content)
    content = content.strip()

    start = content.find("{")
    end = content.rfind("}")
    if start == -1 or end == -1:
        return _default_agent(agent_name)
    content = content[start : end + 1]

    try:
        parsed = json.loads(content)
        raw_risks = parsed.get("risks", [])
        if raw_risks and isinstance(raw_risks[0], dict):
            parsed["risks"] = [r.get("risk", str(r)) for r in raw_risks]
            parsed["mechanisms"] = [r.get("mechanism", "") for r in raw_risks]
        else:
            parsed["mechanisms"] = []

        parsed.setdefault("agent", agent_name)
        parsed.setdefault("risks", ["No risks identified"])
        parsed.setdefault("opportunities", [])
        parsed.setdefault("severity", "Medium")
        parsed.setdefault("most_affected", "Unable to determine")
        parsed.setdefault("summary", "")
        return parsed
    except Exception:
        return _default_agent(agent_name)


def _default_agent(agent_name: str) -> dict:
    return {
        "agent": agent_name,
        "risks": ["Agent response could not be parsed. Please retry."],
        "mechanisms": [],
        "opportunities": [],
        "severity": "Medium",
        "most_affected": "Unable to determine",
        "summary": "Parsing failed. Please retry.",
    }


def _default_coordinator() -> dict:
    return {
        "verdict": "Synthesis unavailable.",
        "key_risk": "Unable to determine.",
        "blind_spot": "Unable to determine.",
        "sharpest_disagreement": "Unable to determine.",
        "confidence": "Low",
    }


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://nitilens.vercel.app",
        "Content-Type": "application/json",
    }


async def _post_openrouter(payload: dict, timeout: float, retries: int = 2) -> httpx.Response:
    last_exc = None
    for attempt in range(retries + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(OPENROUTER_URL, json=payload, headers=_headers())

            if response.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                await asyncio.sleep(0.8 * (attempt + 1))
                continue

            return response
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                await asyncio.sleep(0.8 * (attempt + 1))
                continue
            raise

    if last_exc:
        raise last_exc
    raise RuntimeError("OpenRouter request failed")


async def _run_agent(agent_name: str, system: str, title: str, description: str) -> dict:
    user_msg = AGENT_USER_TEMPLATE.format(
        title=title, description=description, agent_name=agent_name
    )
    payload = {
        "model": MODEL,
        "max_tokens": AGENT_MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
    }

    try:
        response = await _post_openrouter(payload, timeout=45.0)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return parse_response(content, agent_name)
    except Exception:
        return _default_agent(agent_name)


async def fiscal_agent(title: str, description: str) -> dict:
    return await _run_agent("Fiscal Analyst", FISCAL_SYSTEM, title, description)


async def labor_agent(title: str, description: str) -> dict:
    return await _run_agent("Labor & Employment Analyst", LABOR_SYSTEM, title, description)


async def equity_agent(title: str, description: str) -> dict:
    return await _run_agent("Equity & Social Impact Analyst", EQUITY_SYSTEM, title, description)


async def regional_agent(title: str, description: str) -> dict:
    return await _run_agent("Regional & Federal Analyst", REGIONAL_SYSTEM, title, description)


async def coordinator_agent(title: str, all_results: list) -> dict:
    user_msg = COORDINATOR_USER_TEMPLATE.format(
        title=title, reports=json.dumps(all_results, indent=2)
    )
    payload = {
        "model": MODEL,
        "max_tokens": COORDINATOR_MAX_TOKENS,
        "messages": [
            {"role": "system", "content": COORDINATOR_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
    }

    try:
        response = await _post_openrouter(payload, timeout=45.0)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1:
            return _default_coordinator()
        parsed = json.loads(content[start : end + 1])
        parsed.setdefault("verdict", "Synthesis unavailable.")
        parsed.setdefault("key_risk", "Unable to determine.")
        parsed.setdefault("blind_spot", "Unable to determine.")
        parsed.setdefault("sharpest_disagreement", "Unable to determine.")
        parsed.setdefault("confidence", "Low")
        return parsed
    except Exception:
        return _default_coordinator()


async def run_persona(persona: dict, policy_title: str, specialist_risks: list[str]) -> dict:
    risks_text = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(specialist_risks))

    user_message = f"""You are: {persona['name']}, {persona['age_bracket']} year old {persona['gender']} from {persona['district']}, {persona['state']}.
Occupation: {persona['occupation']}
Caste category: {persona['caste_category']}
Income bracket: {persona['income_bracket']}
Residence: {persona['residence']}
Employment: {persona['employment_type']}
Family: {persona['family_size']}

Policy being analysed: {policy_title}

Specialist-identified risks:
{risks_text}

For each risk, assess whether it affects someone with your exact profile. Return ONLY this JSON:
{{
  "persona_id": {persona['id']},
  "name": "{persona['name']}",
  "state": "{persona['state']}",
  "occupation": "{persona['occupation']}",
  "caste_category": "{persona['caste_category']}",
  "validations": [
    {{
      "risk_index": 1,
      "applies": true,
      "severity_for_me": 2,
      "reason": "one sentence why this does or does not apply to my specific situation"
    }}
  ],
  "missed_risk": null
}}
severity_for_me: 0=does not apply, 1=minor inconvenience, 2=significant impact, 3=severe hardship
missed_risk: a risk the specialists missed that specifically affects my demographic, or null"""

    fallback = {
        "persona_id": persona["id"],
        "name": persona["name"],
        "state": persona["state"],
        "occupation": persona["occupation"],
        "caste_category": persona["caste_category"],
        "validations": [],
        "missed_risk": None,
    }

    try:
        response = await _post_openrouter(
            {
                "model": MODEL,
                "max_tokens": PERSONA_MAX_TOKENS,
                "messages": [
                    {"role": "system", "content": PERSONA_SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        cleaned = re.sub(r"```(?:json)?\s*", "", content or "").strip()
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1:
            return fallback
        parsed = json.loads(cleaned[start : end + 1])

        return {
            "persona_id": parsed.get("persona_id", persona["id"]),
            "name": parsed.get("name", persona["name"]),
            "state": parsed.get("state", persona["state"]),
            "occupation": parsed.get("occupation", persona["occupation"]),
            "caste_category": parsed.get("caste_category", persona["caste_category"]),
            "validations": parsed.get("validations", []),
            "missed_risk": parsed.get("missed_risk", None),
        }
    except Exception:
        return fallback
