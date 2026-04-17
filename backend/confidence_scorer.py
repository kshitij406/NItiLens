def calculate_confidence(agent_results: list, persona_results: list) -> dict:
    score = 10
    reasons = []
    caveats = []

    # Check specialist signal
    total_risks = sum(len(a.get('risks', [])) for a in agent_results)
    if total_risks < 4:
        score -= 1
        reasons.append("Low specialist risk signal")

    # Check severity agreement
    severities = [a.get('severity', 'Medium') for a in agent_results]
    high_count = severities.count('High')
    low_count = severities.count('Low')
    medium_count = severities.count('Medium')

    if high_count == 4:
        reasons.append("All agents agree: High severity")
    elif low_count == 4:
        reasons.append("All agents agree: Low severity")
        score += 1
    elif high_count >= 2 and low_count >= 2:
        score -= 2
        reasons.append("Agents strongly disagree on severity")
        caveats.append("High disagreement between agents — treat findings as hypotheses")
    elif high_count >= 3 or low_count >= 3:
        reasons.append("Strong agent consensus on severity")
    else:
        score -= 1
        reasons.append("Mixed severity signals across agents")

    # Check persona confirmation
    if persona_results:
        total_validations = sum(len(p.get('validations', [])) for p in persona_results)
        confirmed = sum(
            1 for p in persona_results
            for v in p.get('validations', [])
            if v.get('applies') and v.get('severity_for_me', 0) >= 2
        )
        confirmation_rate = confirmed / total_validations if total_validations > 0 else 0

        if confirmation_rate < 0.2:
            score -= 1
            caveats.append("Low persona confirmation rate — specialists may be overstating risk")
        elif confirmation_rate > 0.5:
            reasons.append(f"Strong persona confirmation: {int(confirmation_rate*100)}% of validations flagged significant impact")

        empty_responses = len([p for p in persona_results if not p.get('validations')])
        if empty_responses > 5:
            score -= 1
            caveats.append(f"{empty_responses} persona responses were empty")
    else:
        score -= 2
        caveats.append("No persona validation data available")

    score = max(1, min(10, score))

    if score >= 8:
        label = "High"
    elif score >= 5:
        label = "Medium"
    else:
        label = "Low"

    return {
        "score": score,
        "out_of": 10,
        "label": label,
        "reasons": reasons,
        "caveats": caveats,
        "caveat_text": "This is a hypothesis generation tool. Findings should be validated against real policy data before informing decisions."
    }
