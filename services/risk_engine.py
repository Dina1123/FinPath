"""
Calculates a risk score (0-100) from the user's financial profile.
Higher score = more at risk.
"""


def calculate_risk(profile) -> dict:
    score = 0
    flags = []

    if not profile.has_auto_insurance:
        score += 25
        flags.append("No auto insurance")

    if not profile.has_health_insurance:
        score += 25
        flags.append("No health insurance")

    if not profile.has_emergency_fund:
        score += 20
        flags.append("No emergency fund")

    if not profile.has_renters_insurance:
        score += 10
        flags.append("No renters insurance")

    if profile.gig_driving and not profile.has_auto_insurance:
        score += 15  # extra penalty — gig driving without coverage is critical
        flags.append("Gig driving with no commercial coverage")

    if profile.income_stability == "variable":
        score += 5

    if profile.income_stability == "none":
        score += 10

    score = min(score, 100)

    if score >= 70:
        level = "critical"
    elif score >= 45:
        level = "high"
    elif score >= 20:
        level = "medium"
    else:
        level = "low"

    biggest_risk = flags[0] if flags else "You're in good shape!"

    return {
        "risk_score": score,
        "risk_level": level,
        "biggest_risk": biggest_risk,
        "flags": flags,
    }
