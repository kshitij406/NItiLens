import json
import os
import re
import asyncio

import httpx
from dotenv import load_dotenv

load_dotenv()

BACKBOARD_BASE = "https://app.backboard.io/api"
BACKBOARD_API_KEY = os.getenv("BACKBOARD_API_KEY", "")
MODEL = "backboard"

AGENT_USER_TEMPLATE = (
    "Policy classification: {classification}\n\n"
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
    "Respond ONLY with valid JSON."
)

LABOR_SYSTEM = (
    "You are a labor economist specialising in India's workforce. "
    "Analyse the given policy for job creation or loss, wage effects, impact on the informal sector "
    "which employs 90% of Indian workers, migrant labor, and gig economy workers. "
    "Respond ONLY with valid JSON."
)

EQUITY_SYSTEM = (
    "You are a social equity researcher specialising in India. "
    "Analyse the given policy for effects on Scheduled Castes, Scheduled Tribes, OBCs, women, "
    "and low-income rural households. Identify which groups bear disproportionate costs or benefits. "
    "Respond ONLY with valid JSON."
)

REGIONAL_SYSTEM = (
    "You are a federalism and regional policy analyst for India. "
    "Analyse the given policy for state-level variance, Centre-state fiscal tensions, "
    "impact on northeastern states, linguistic minorities, and whether the policy ignores "
    "regional economic diversity. Respond ONLY with valid JSON."
)

COORDINATOR_SYSTEM = (
    "You are the lead policy intelligence coordinator for NitiLens. "
    "You have received independent risk assessments from 4 specialist agents. "
    "Synthesise their findings into a final intelligence briefing. "
    "Be direct, specific, and highlight where agents disagree. "
    "Respond ONLY with valid JSON."
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

DEMO_PERSONAS = INDIAN_PERSONAS[:15]
FULL_PERSONAS = INDIAN_PERSONAS

PERSONA_SYSTEM_PROMPT = """You are validating policy risk assessments from the perspective of a specific Indian citizen. Domain experts identified risks for an Indian government policy. Your job: determine which risks ACTUALLY AFFECT someone matching your demographic profile.

Be honest and specific. Most policies affect most people at 0 or 1. Only use severity 3 if this risk would genuinely destabilize your life.

Respond ONLY with valid JSON, no markdown, no explanation."""

BATCH_PERSONA_SYSTEM_PROMPT = (
    "You validate policy risks for multiple Indian citizens at once. "
    "For each citizen, assess which specialist-identified risks actually apply given their specific profile. "
    "Be realistic: most risks affect most people at 0 (none) or 1 (minor). "
    "Use 3 (severe) only if a risk would genuinely destabilise that person's life. "
    "Respond ONLY with a valid JSON array, no markdown."
)


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


_assistant_cache: dict[str, str] = {}


def _bb_headers() -> dict:
    return {"X-API-Key": BACKBOARD_API_KEY}


async def _ensure_assistant(system_prompt: str, name: str) -> str:
    if system_prompt in _assistant_cache:
        return _assistant_cache[system_prompt]
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BACKBOARD_BASE}/assistants",
            headers=_bb_headers(),
            json={"name": name, "system_prompt": system_prompt},
        )
        r.raise_for_status()
        aid = r.json()["assistant_id"]
    _assistant_cache[system_prompt] = aid
    return aid


async def _post_backboard(
    system_prompt: str,
    user_message: str,
    name: str = "NitiLens Agent",
    timeout: float = 45.0,
    retries: int = 2,
) -> str:
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            assistant_id = await _ensure_assistant(system_prompt, name)
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(
                    f"{BACKBOARD_BASE}/assistants/{assistant_id}/threads",
                    headers=_bb_headers(),
                    json={},
                )
                r.raise_for_status()
                thread_id = r.json()["thread_id"]

                r = await client.post(
                    f"{BACKBOARD_BASE}/threads/{thread_id}/messages",
                    headers=_bb_headers(),
                    data={"content": user_message, "stream": "false"},
                )
                r.raise_for_status()
                return r.json().get("content", "")
        except Exception as exc:
            last_exc = exc
            if attempt < retries:
                await asyncio.sleep(0.8 * (attempt + 1))
            continue
    raise last_exc or RuntimeError("Backboard request failed")


async def _run_agent(
    agent_name: str,
    system: str,
    title: str,
    description: str,
    classification: dict | None = None,
) -> dict:
    if classification is None:
        classification = {
            "domain": "other",
            "primary_affected": "all",
            "geography": "national",
            "time_horizon": "short_term",
            "key_attributes": ["income", "employment", "region"],
        }
    user_msg = AGENT_USER_TEMPLATE.format(
        title=title,
        description=description,
        agent_name=agent_name,
        classification=json.dumps(classification),
    )
    try:
        content = await _post_backboard(system, user_msg, name=f"NitiLens-{agent_name}", timeout=45.0)
        return parse_response(content, agent_name)
    except Exception:
        return _default_agent(agent_name)


async def fiscal_agent(title: str, description: str, classification: dict | None = None) -> dict:
    return await _run_agent("Fiscal Analyst", FISCAL_SYSTEM, title, description, classification)


async def labor_agent(title: str, description: str, classification: dict | None = None) -> dict:
    return await _run_agent("Labor & Employment Analyst", LABOR_SYSTEM, title, description, classification)


async def equity_agent(title: str, description: str, classification: dict | None = None) -> dict:
    return await _run_agent("Equity & Social Impact Analyst", EQUITY_SYSTEM, title, description, classification)


async def regional_agent(title: str, description: str, classification: dict | None = None) -> dict:
    return await _run_agent("Regional & Federal Analyst", REGIONAL_SYSTEM, title, description, classification)


async def coordinator_agent(title: str, all_results: list) -> dict:
    user_msg = COORDINATOR_USER_TEMPLATE.format(
        title=title, reports=json.dumps(all_results, indent=2)
    )
    try:
        content = await _post_backboard(COORDINATOR_SYSTEM, user_msg, name="NitiLens-Coordinator", timeout=45.0)
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
        content = await _post_backboard(PERSONA_SYSTEM_PROMPT, user_message, name="NitiLens-Persona", timeout=30.0)
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


def _persona_fallback(p: dict) -> dict:
    return {
        "persona_id": p["id"],
        "name": p["name"],
        "state": p["state"],
        "occupation": p["occupation"],
        "caste_category": p["caste_category"],
        "validations": [],
        "missed_risk": None,
    }


async def run_persona_batch(personas: list[dict], policy_title: str, specialist_risks: list[str]) -> list[dict]:
    risks_text = "\n".join(f"{i + 1}. {r}" for i, r in enumerate(specialist_risks))
    personas_text = "\n".join(
        f"[{i + 1}, id={p['id']}] {p['name']}: {p['age_bracket']} {p['gender']}, "
        f"{p['occupation']}, {p['caste_category']}, {p['income_bracket']} income, "
        f"{p['residence']} {p['state']}, {p['employment_type']}, {p['family_size']}"
        for i, p in enumerate(personas)
    )
    user_msg = (
        f"Policy: {policy_title}\n\n"
        f"Risks:\n{risks_text}\n\n"
        f"Citizens:\n{personas_text}\n\n"
        f"Return a JSON array with one object per citizen in order:\n"
        f'[{{"persona_id": <id>, "name": "<name>", "state": "<state>", "occupation": "<occ>", '
        f'"caste_category": "<caste>", "validations": [{{"risk_index": 1, "applies": true, '
        f'"severity_for_me": 2, "reason": "one sentence"}}], "missed_risk": null}}]\n'
        f"severity_for_me: 0=none, 1=minor, 2=significant, 3=severe"
    )

    fallbacks = [_persona_fallback(p) for p in personas]

    try:
        content = await _post_backboard(
            BATCH_PERSONA_SYSTEM_PROMPT, user_msg, name="NitiLens-PersonaBatch", timeout=60.0
        )
        cleaned = re.sub(r"```(?:json)?\s*", "", content or "").strip()
        start = cleaned.find("[")
        end = cleaned.rfind("]")
        if start == -1 or end == -1:
            return fallbacks
        parsed = json.loads(cleaned[start : end + 1])

        returned_ids: set[int] = set()
        results: list[dict] = []
        for item in parsed:
            pid = item.get("persona_id")
            source = next((p for p in personas if p["id"] == pid), None)
            if not source:
                continue
            returned_ids.add(pid)
            results.append({
                "persona_id": pid,
                "name": item.get("name", source["name"]),
                "state": item.get("state", source["state"]),
                "occupation": item.get("occupation", source["occupation"]),
                "caste_category": item.get("caste_category", source["caste_category"]),
                "validations": item.get("validations", []),
                "missed_risk": item.get("missed_risk"),
            })

        for p in personas:
            if p["id"] not in returned_ids:
                results.append(_persona_fallback(p))

        return results
    except Exception:
        return fallbacks
