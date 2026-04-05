"""
Calculates a risk score (0-100) from the user's financial profile.
Higher score = more at risk.
"""


def calculate_risk(profile) -> dict:
    score = 0
    flags = []

    # Core coverage gaps
    if not profile.has_auto_insurance:
        score += 25
        flags.append("No auto insurance")

    if (not profile.has_health_insurance):
        score += 25
        flags.append("No health insurance")

    if not profile.has_emergency_fund:
        score += 20
        flags.append("No emergency fund")

    # Housing-related risk
    # New model means: if this is True, they likely need renters coverage
    if (profile.needs_renters_insurance  & (profile.housing_type != "dorm" | profile.housing_type != "family")):
        score += 10
        flags.append("May need renters insurance")

    # Gig-worker / delivery risk
    if profile.likely_gig_driver:
        score += 10
        flags.append("Gig or delivery work may require extra coverage")

        if not profile.has_auto_insurance:
            score += 15
            flags.append("Gig driving with no auto insurance")

    # Student-related complexity
    if profile.is_student:
        score += 5
        flags.append("Student financial transition risk")

    # International-related complexity
    if profile.is_international:
        score += 10
        flags.append("International status may add tax and coverage complexity")

    # No-income / unstable-income signals from income_sources
    income_sources = profile.income_sources or []

    if "no_income" in income_sources:
        score += 10
        flags.append("No income currently")

    variable_income_sources = {
        "gig_delivery_work",
        "freelance_contract_work",
        "part_time_job",
    }
    if any(src in income_sources for src in variable_income_sources):
        score += 5
        flags.append("Variable income")

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