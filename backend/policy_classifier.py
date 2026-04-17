import json

import httpx

from agents import MODEL, OPENROUTER_URL, _headers, parse_response

CLASSIFIER_PROMPT = """Classify this Indian government policy for analysis purposes.
Return ONLY valid JSON, no markdown, no explanation.

{
  "domain": "fiscal|labor|social|federal|health|education|infrastructure|environment|other",
  "primary_affected": "rural_poor|urban_workers|farmers|youth|women|SC_ST|middle_class|all",
  "geography": "national|state_level|urban|rural|regional",
  "time_horizon": "immediate|short_term|long_term",
  "key_attributes": ["list", "of", "3", "most", "relevant", "demographic", "factors"]
}"""


async def classify_policy(title: str, description: str) -> dict:
    user_message = f"Policy Title: {title}\n\nPolicy Description: {description}\n\nClassify this policy."

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=_headers(),
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": CLASSIFIER_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 200,
            },
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        parsed = parse_response(content, "classifier")
        return {
            "domain": parsed.get("domain", "other"),
            "primary_affected": parsed.get("primary_affected", "all"),
            "geography": parsed.get("geography", "national"),
            "time_horizon": parsed.get("time_horizon", "short_term"),
            "key_attributes": parsed.get("key_attributes", ["income", "employment", "region"]),
        }
