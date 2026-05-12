def classify_risk(text: str) -> dict:
    lowered = text.lower()

    high_keywords = [
        "outage",
        "data loss",
        "security",
        "breach",
        "payment failed",
        "checkout down",
        "unavailable",
    ]
    medium_keywords = [
        "latency",
        "degraded",
        "timeout",
        "error rate",
        "checkout",
        "database",
    ]

    if any(keyword in lowered for keyword in high_keywords):
        return {
            "risk_level": "high",
            "reasoning": "Matched keywords associated with outages, security issues, or failed critical flows.",
        }

    if any(keyword in lowered for keyword in medium_keywords):
        return {
            "risk_level": "medium",
            "reasoning": "Matched keywords associated with degraded service or important system components.",
        }

    return {
        "risk_level": "low",
        "reasoning": "No keywords matched the medium or high risk lists.",
    }
