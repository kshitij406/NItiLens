import hashlib
import json
import os
from datetime import datetime, timezone

VALIDATION_LOG_DIR = "validation_log"


def seal_simulation(policy_title: str, policy_description: str, full_output: dict) -> dict:
    os.makedirs(VALIDATION_LOG_DIR, exist_ok=True)

    policy_hash = hashlib.md5(
        (policy_title + policy_description).encode()
    ).hexdigest()[:12]

    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "hash": policy_hash,
        "timestamp": timestamp,
        "policy_title": policy_title,
        "overall_severity": full_output.get("overall_severity"),
        "confidence": full_output.get("confidence", {}).get("score"),
        "agent_severities": {
            a.get("agent"): a.get("severity")
            for a in full_output.get("agents", [])
        },
        "coordinator_verdict": full_output.get("coordinator", {}).get("verdict"),
        "sealed": True,
        "validated_against_reality": False,
        "reality_check_notes": None,
    }

    filename = f"{VALIDATION_LOG_DIR}/{policy_hash}_{timestamp[:10]}.json"
    with open(filename, "w") as f:
        json.dump(record, f, indent=2)

    return {"hash": policy_hash, "timestamp": timestamp, "sealed": True}
