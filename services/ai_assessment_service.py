# services/ai_assessment_service.py
import json
import os
from typing import Any

from anthropic import Anthropic

VALID_RISK_LEVELS = {"low", "medium", "high", "critical"}
VALID_ACTION_KEYS = {
    "get_rideshare_coverage",
    "get_auto_insurance",
    "get_health_insurance",
    "build_emergency_fund",
    "get_renters_insurance",
    "file_student_taxes",
    "review_scholarship_taxability",
    "check_fafsa_deadline",
    "review_itin_or_ssn_filing",
    "review_visa_tax_rules",
    "review_marketplace_health_options",
}

SYSTEM_PROMPT = """
You are FinPath, a financial wellness assessment engine.

Your task is to analyze one user's financial profile and produce:
1. A risk score from 0 to 100
2. A risk level: low, medium, high, or critical
3. The single biggest financial risk
4. A short list of risk flags
5. Exactly 3 prioritized actions

Rules:
- Respond with JSON only.
- No markdown.
- No prose outside JSON.
- Be practical, non-judgmental, and aligned to the user's actual profile.
- Consider student, international, gig-work, housing, health, auto, and emergency-fund context.
- Favor the next best step, not a giant plan.
- Actions must be educational guidance, not professional financial advice.
- Keep action descriptions short and clear.
- If renter's insurance seems relevant because of housing, include it.
- If student/international/scholarship context matters, reflect it in flags or actions.
- If no car is implied, do not over-prioritize auto issues unless the profile indicates driving/gig delivery.
- Return exactly 3 actions.
- Use the user's preferred language for titles/descriptions if language is "es", otherwise use English.

JSON shape:
{
  "risk_score": 0,
  "risk_level": "low|medium|high|critical",
  "biggest_risk": "string",
  "flags": ["string", "string"],
  "actions": [
    {
      "key": "string",
      "title": "string",
      "description": "string",
      "education_term": "string",
      "education_card": "string",
      "statefarm_product": "string|null"
    }
  ]
}
"""


def _profile_payload(profile, language: str) -> dict[str, Any]:
    return {
        "language": language,
        "life_situations": profile.life_situations or [],
        "is_student": bool(profile.is_student),
        "is_international": bool(profile.is_international),
        "country_of_origin": profile.country_of_origin,
        "entry_route": profile.entry_route,
        "income_sources": profile.income_sources or [],
        "housing_type": profile.housing_type,
        "has_health_insurance": bool(profile.has_health_insurance),
        "has_auto_insurance": bool(profile.has_auto_insurance),
        "has_emergency_fund": bool(profile.has_emergency_fund),
        "needs_renters_insurance": bool(profile.needs_renters_insurance),
        "likely_gig_driver": bool(profile.likely_gig_driver),
    }


def _validate_result(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("Claude response is not an object")

    risk_score = int(data.get("risk_score", 0))
    risk_score = max(0, min(100, risk_score))

    risk_level = data.get("risk_level")
    if risk_level not in VALID_RISK_LEVELS:
        raise ValueError("Invalid risk_level")

    biggest_risk = str(data.get("biggest_risk", "")).strip()
    if not biggest_risk:
        raise ValueError("Missing biggest_risk")

    flags = data.get("flags", [])
    if not isinstance(flags, list):
        raise ValueError("flags must be a list")
    flags = [str(x) for x in flags][:6]

    actions = data.get("actions", [])
    if not isinstance(actions, list) or len(actions) != 3:
        raise ValueError("actions must contain exactly 3 items")

    cleaned_actions = []
    for action in actions:
        if not isinstance(action, dict):
            raise ValueError("Invalid action item")

        key = str(action.get("key", "")).strip()
        if not key:
            raise ValueError("Action missing key")

        # Keep known keys if possible, but do not hard-fail the hackathon flow.
        if key not in VALID_ACTION_KEYS:
            key = f"custom_{key.lower().replace(' ', '_')}"

        cleaned_actions.append({
            "key": key,
            "title": str(action.get("title", "")).strip() or "Recommended action",
            "description": str(action.get("description", "")).strip() or "Take the next practical step.",
            "education_term": str(action.get("education_term", "")).strip() or "financial guidance",
            "education_card": str(action.get("education_card", "")).strip() or "This step can help reduce your financial risk.",
            "statefarm_product": action.get("statefarm_product"),
        })

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "biggest_risk": biggest_risk,
        "flags": flags,
        "actions": cleaned_actions,
    }


def generate_ai_assessment(profile, language: str = "en") -> dict[str, Any]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = Anthropic(api_key=api_key)

    payload = _profile_payload(profile, language)

    user_prompt = (
        "Assess this user profile and return JSON only.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1400,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": user_prompt,
            }
        ],
    )

    text = "".join(
        block.text for block in message.content
        if getattr(block, "type", None) == "text"
    ).strip()

    result = json.loads(text)
    return _validate_result(result)