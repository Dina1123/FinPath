"""
AI response service.

Currently uses a local rule-based mock that generates realistic responses
based on the user's financial profile — no API key required.

To switch to the real Claude API, set ANTHROPIC_API_KEY in .env and
flip USE_REAL_API = True below (or set it via environment variable).
"""

import os

USE_REAL_API = bool(os.getenv("ANTHROPIC_API_KEY"))


# ---------------------------------------------------------------------------
# Real Claude API (activated when ANTHROPIC_API_KEY is present)
# ---------------------------------------------------------------------------

def _call_claude(profile, question: str, language: str) -> str:
    import anthropic

    lang_instruction = (
        "Respond in Spanish. Use simple, clear language." if language == "es"
        else "Respond in English. Use simple, plain language."
    )

    coverage_summary = (
        f"- Employment: {profile.employment_type}\n"
        f"- Income stability: {profile.income_stability}\n"
        f"- Has auto insurance: {profile.has_auto_insurance}\n"
        f"- Has health insurance: {profile.has_health_insurance}\n"
        f"- Has renters insurance: {profile.has_renters_insurance}\n"
        f"- Has emergency fund: {profile.has_emergency_fund}\n"
        f"- Does gig driving: {profile.gig_driving}\n"
        f"- Risk score: {profile.risk_score}/100 ({profile.risk_level})\n"
        f"- Biggest risk: {profile.biggest_risk}"
    )

    system_prompt = (
        "You are FinPath, a friendly financial wellness guide for underserved communities — "
        "recent immigrants, young adults, and gig workers. "
        "You give clear, non-judgmental, actionable guidance in plain language. "
        "Always frame your response as educational guidance, not professional financial advice. "
        "End every response with: 'This is educational guidance, not professional financial advice.'"
    )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": (
                    f"My financial profile:\n{coverage_summary}\n\n"
                    f"{lang_instruction}\n\n"
                    f"My question: {question}"
                ),
            }
        ],
    )
    return message.content[0].text


# ---------------------------------------------------------------------------
# Local mock (used when no API key is set)
# ---------------------------------------------------------------------------

DISCLAIMER_EN = "\n\n*This is educational guidance, not professional financial advice.*"
DISCLAIMER_ES = "\n\n*Esto es orientación educativa, no asesoramiento financiero profesional.*"


def _mock_response(profile, question: str, language: str) -> str:
    q = question.lower()
    is_es = language == "es"
    disclaimer = DISCLAIMER_ES if is_es else DISCLAIMER_EN

    # Gig driving / rideshare coverage
    if any(w in q for w in ["gig", "uber", "lyft", "doordash", "rideshare", "driving"]):
        if is_es:
            return (
                "Tu seguro de auto personal generalmente NO te cubre cuando conduces para "
                "aplicaciones como Uber o DoorDash. Necesitas un seguro adicional para conductores "
                "de plataformas digitales. Habla con tu aseguradora para agregar esta cobertura — "
                "suele costar entre $10 y $20 al mes." + disclaimer
            )
        return (
            f"Your personal auto insurance generally does NOT cover you while driving for gig apps "
            f"like Uber or DoorDash. You need a rideshare add-on to your policy. "
            f"This typically costs $10–$20/month extra and closes a serious coverage gap. "
            f"Based on your profile, this is your most urgent action right now." + disclaimer
        )

    # Health insurance
    if any(w in q for w in ["health", "medical", "doctor", "hospital", "salud", "médico"]):
        if is_es:
            return (
                "Si no tienes seguro médico, una visita a urgencias puede costar más de $3,000. "
                "Como trabajador independiente, puedes buscar planes en healthcare.gov — "
                "muchos tienen subsidios según tus ingresos." + disclaimer
            )
        return (
            "Without health insurance, a single ER visit can cost $3,000 or more. "
            "As a gig or contract worker, check healthcare.gov for marketplace plans — "
            "you may qualify for subsidized coverage based on your income." + disclaimer
        )

    # Emergency fund
    if any(w in q for w in ["emergency", "savings", "save", "fund", "ahorros", "emergencia"]):
        if is_es:
            return (
                "Un fondo de emergencia es dinero reservado para gastos inesperados. "
                "Empieza con una meta de $500. Con ingresos variables, intenta ahorrar "
                "al menos el 10% de cada pago que recibas." + disclaimer
            )
        return (
            "An emergency fund is money set aside for unexpected costs — car repairs, medical bills, job loss. "
            "Start with a $500 goal, then build toward 3 months of expenses. "
            "With variable income, try to save at least 10% of every payment you receive." + disclaimer
        )

    # Auto insurance
    if any(w in q for w in ["auto", "car", "vehicle", "carro", "auto seguro"]):
        if is_es:
            return (
                "El seguro de auto es obligatorio en casi todos los estados. "
                "Cubre los costos de un accidente — reparaciones, facturas médicas y honorarios legales. "
                "Sin él, podrías enfrentar multas y responsabilidad financiera total." + disclaimer
            )
        return (
            "Auto insurance is legally required in almost every state. "
            "It covers accident costs — repairs, medical bills, and legal fees. "
            "Driving without it exposes you to fines and full financial liability." + disclaimer
        )

    # Renters insurance
    if any(w in q for w in ["rent", "renter", "apartment", "belongings", "arrendatario", "inquilino"]):
        if is_es:
            return (
                "El seguro para inquilinos protege tus pertenencias en caso de robo, incendio "
                "o daños por agua. Suele costar entre $10 y $20 al mes. "
                "El seguro de tu arrendador NO cubre tus objetos personales." + disclaimer
            )
        return (
            "Renters insurance protects your belongings from theft, fire, and water damage. "
            "It usually costs $10–$20/month. Your landlord's insurance does NOT cover your personal belongings." + disclaimer
        )

    # Generic fallback based on profile
    gaps = []
    if not profile.has_auto_insurance:
        gaps.append("auto insurance" if not is_es else "seguro de auto")
    if not profile.has_health_insurance:
        gaps.append("health insurance" if not is_es else "seguro médico")
    if not profile.has_emergency_fund:
        gaps.append("an emergency fund" if not is_es else "un fondo de emergencia")

    if gaps and not is_es:
        return (
            f"Based on your profile, your biggest financial gaps right now are: {', '.join(gaps)}. "
            f"Addressing these in order will significantly reduce your financial risk. "
            f"Tap any action step in your plan for more details." + disclaimer
        )
    if gaps and is_es:
        return (
            f"Según tu perfil, tus mayores brechas financieras son: {', '.join(gaps)}. "
            f"Resolverlas en orden reducirá significativamente tu riesgo financiero." + disclaimer
        )

    if is_es:
        return (
            "Estoy aquí para ayudarte con preguntas sobre seguros, ahorros e independencia financiera. "
            "¿Qué te gustaría saber?" + disclaimer
        )
    return (
        "I'm here to help with questions about insurance, savings, and financial independence. "
        "What would you like to know?" + disclaimer
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_ai_response(profile, question: str, language: str = "en") -> str:
    if USE_REAL_API:
        return _call_claude(profile, question, language)
    return _mock_response(profile, question, language)
