"""
AI response service.

Currently uses a local rule-based mock that generates realistic responses
based on the user's financial profile — no API key required.

To switch to the real Claude API, set ANTHROPIC_API_KEY in .env and
flip USE_REAL_API = True below (or set it via environment variable).
"""

import os


# ---------------------------------------------------------------------------
# Real Claude API (activated when ANTHROPIC_API_KEY is present)
# ---------------------------------------------------------------------------

def _build_system_prompt(profile, language: str) -> str:
    lang_instruction = (
        "Always respond in Spanish. Use simple, clear language."
        if language == "es"
        else "Always respond in English. Use simple, plain language."
    )
    coverage_summary = (
        f"- Life situations: {profile.life_situations}\n"
        f"- Is student: {profile.is_student}\n"
        f"- Is international: {profile.is_international}\n"
        f"- Country of origin: {profile.country_of_origin}\n"
        f"- Entry route: {profile.entry_route}\n"
        f"- Income sources: {profile.income_sources}\n"
        f"- Housing type: {profile.housing_type}\n"
        f"- Has auto insurance: {profile.has_auto_insurance}\n"
        f"- Has health insurance: {profile.has_health_insurance}\n"
        f"- Has emergency fund: {profile.has_emergency_fund}\n"
        f"- Needs renters insurance: {profile.needs_renters_insurance}\n"
        f"- Likely gig driver: {profile.likely_gig_driver}\n"
        f"- Risk score: {profile.risk_score}/100 ({profile.risk_level})\n"
        f"- Biggest risk: {profile.biggest_risk}"
    )
    return (
        "You are FinPath, a friendly financial wellness guide for underserved communities — "
        "recent immigrants, young adults, gig workers, and students. "
        "You give clear, non-judgmental, actionable guidance in plain language. "
        "Always frame your response as educational guidance, not professional financial advice. "
        "End every response with: 'This is educational guidance, not professional financial advice.'\n\n"
        f"{lang_instruction}\n\n"
        f"The user's financial profile (use this as context for all answers):\n{coverage_summary}"
    )


def _call_claude(profile, question: str, language: str, history: list) -> str:
    import anthropic

    # Build messages: prior history + new question
    messages = []
    for turn in history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": question})

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system=_build_system_prompt(profile, language),
        messages=messages,
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
                "aplicaciones como Uber o DoorDash. Necesitas una cobertura adicional para "
                "trabajo por aplicación o rideshare. Habla con tu aseguradora para revisar "
                "esa protección." + disclaimer
            )
        return (
            "Your personal auto insurance generally does NOT cover you while driving for gig apps "
            "like Uber or DoorDash. You may need rideshare or delivery-driver coverage. "
            "Based on your profile, this is an important gap to review with your insurer." + disclaimer
        )

    # Health insurance
    if any(w in q for w in ["health", "medical", "doctor", "hospital", "salud", "médico"]):
        if is_es:
            return (
                "Si no tienes seguro médico, una sola visita a urgencias puede ser muy costosa. "
                "Puedes revisar opciones en healthcare.gov o programas estatales, según tus ingresos "
                "y tu situación." + disclaimer
            )
        return (
            "Without health insurance, even one ER visit can be very expensive. "
            "You may want to check healthcare.gov or state programs based on your income and situation." + disclaimer
        )

    # Emergency fund
    if any(w in q for w in ["emergency", "savings", "save", "fund", "ahorros", "emergencia"]):
        if is_es:
            return (
                "Un fondo de emergencia es dinero reservado para gastos inesperados. "
                "Empieza con una meta pequeña, como $500, y luego sigue creciendo poco a poco." + disclaimer
            )
        return (
            "An emergency fund is money set aside for unexpected costs like car repairs, medical bills, "
            "or a sudden loss of income. Start small, such as a $500 goal, then build from there." + disclaimer
        )

    # Auto insurance
    if any(w in q for w in ["auto", "car", "vehicle", "carro", "auto seguro"]):
        if is_es:
            return (
                "El seguro de auto es obligatorio en casi todos los estados. "
                "Ayuda a cubrir daños, lesiones y responsabilidad legal en un accidente." + disclaimer
            )
        return (
            "Auto insurance is legally required in almost every state. "
            "It helps cover damage, injuries, and legal liability after an accident." + disclaimer
        )

    # Renters insurance
    if any(w in q for w in ["rent", "renter", "apartment", "belongings", "arrendatario", "inquilino"]):
        if is_es:
            return (
                "El seguro para inquilinos protege tus pertenencias en caso de robo, incendio "
                "o ciertos daños. El seguro del propietario normalmente NO cubre tus objetos personales." + disclaimer
            )
        return (
            "Renters insurance protects your belongings from theft, fire, and some types of damage. "
            "Your landlord's insurance usually does NOT cover your personal belongings." + disclaimer
        )

    # Student / scholarship / FAFSA
    if any(w in q for w in ["student", "scholarship", "fafsa", "college", "campus", "beca", "universidad"]):
        if is_es:
            return (
                "Como estudiante, puede haber temas importantes como FAFSA, impuestos sobre ciertas becas, "
                "y cobertura médica al depender de tus padres o de la escuela. "
                "Tu situación exacta depende de tus ingresos y tu estatus." + disclaimer
            )
        return (
            "As a student, important topics may include FAFSA, taxes on some scholarship income, "
            "and health coverage through parents, school, or the marketplace. "
            "Your exact situation depends on your income and status." + disclaimer
        )

    # International / immigrant
    if any(w in q for w in ["international", "visa", "itin", "immigrant", "f1", "student visa"]):
        if is_es:
            return (
                "Si eres estudiante internacional o nuevo en este país, puede haber reglas especiales "
                "sobre impuestos, ITIN o restricciones de trabajo según tu visa. "
                "Es importante revisar orientación específica para tu estatus." + disclaimer
            )
        return (
            "If you are an international student or new to this country, there may be special rules "
            "around taxes, ITINs, and work restrictions depending on your visa or immigration status. "
            "It is important to review guidance specific to your situation." + disclaimer
        )

    # Generic fallback based on profile
    gaps = []

    if not profile.has_auto_insurance:
        gaps.append("auto insurance" if not is_es else "seguro de auto")

    if not profile.has_health_insurance:
        gaps.append("health insurance" if not is_es else "seguro médico")

    if not profile.has_emergency_fund:
        gaps.append("an emergency fund" if not is_es else "un fondo de emergencia")

    if profile.needs_renters_insurance:
        gaps.append("renters insurance" if not is_es else "seguro para inquilinos")

    if gaps and not is_es:
        return (
            f"Based on your profile, your biggest financial gaps right now are: {', '.join(gaps)}. "
            f"Addressing these step by step will reduce your financial risk. "
            f"Check your action plan for the best next move." + disclaimer
        )

    if gaps and is_es:
        return (
            f"Según tu perfil, tus principales brechas financieras ahora son: {', '.join(gaps)}. "
            f"Resolverlas paso a paso reducirá tu riesgo financiero. "
            f"Revisa tu plan de acción para ver el mejor siguiente paso." + disclaimer
        )

    if is_es:
        return (
            "Estoy aquí para ayudarte con preguntas sobre seguros, ahorros, impuestos básicos "
            "y transición a la independencia financiera. ¿Qué te gustaría saber?" + disclaimer
        )

    return (
        "I'm here to help with questions about insurance, savings, basic tax topics, "
        "and financial independence. What would you like to know?" + disclaimer
    )


# ---------------------------------------------------------------------------
# AI-powered refresh (risk + actions re-evaluated by Claude)
# ---------------------------------------------------------------------------

def get_ai_refresh(profile, language: str = "en") -> dict | None:
    """
    Ask Claude to re-evaluate the user's risk and suggest personalized actions.
    Returns a dict with keys: biggest_risk, ai_insight, actions (list of dicts).
    Returns None if no API key is set (caller should fall back to rule-based).
    """
    if not os.getenv("ANTHROPIC_API_KEY"):
        return None

    import anthropic, json

    lang_instruction = (
        "Respond in Spanish." if language == "es" else "Respond in English."
    )

    profile_summary = (
        f"- Life situations: {profile.life_situations}\n"
        f"- Is student: {profile.is_student}\n"
        f"- Is international: {profile.is_international}\n"
        f"- Country of origin: {profile.country_of_origin}\n"
        f"- Entry route: {profile.entry_route}\n"
        f"- Income sources: {profile.income_sources}\n"
        f"- Housing type: {profile.housing_type}\n"
        f"- Has auto insurance: {profile.has_auto_insurance}\n"
        f"- Has health insurance: {profile.has_health_insurance}\n"
        f"- Has emergency fund: {profile.has_emergency_fund}\n"
        f"- Needs renters insurance: {profile.needs_renters_insurance}\n"
        f"- Likely gig driver: {profile.likely_gig_driver}\n"
        f"- Current risk score: {profile.risk_score}/100 ({profile.risk_level})\n"
        f"- Current biggest risk: {profile.biggest_risk}"
    )

    prompt = (
        f"User financial profile:\n{profile_summary}\n\n"
        f"{lang_instruction}\n\n"
        "Based on this profile, return a JSON object with exactly these keys:\n"
        "- biggest_risk: a short (under 15 words) plain-English description of their single biggest financial risk\n"
        "- ai_insight: a 2-3 sentence personalized financial insight for this user\n"
        "- actions: an array of exactly 3 objects, each with keys: key (snake_case), title (short), description (1-2 sentences), education_card (1 sentence plain explanation), statefarm_product (State Farm product name or null)\n\n"
        "Only return valid JSON. No markdown, no extra text."
    )

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        system=(
            "You are a financial wellness AI for underserved communities. "
            "Always respond with valid JSON only. No markdown fences. "
            "Frame all guidance as educational, not professional financial advice."
        ),
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        return json.loads(message.content[0].text)
    except (json.JSONDecodeError, IndexError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def get_ai_response(profile, question: str, language: str = "en", history: list = None) -> str:
    if os.getenv("ANTHROPIC_API_KEY"):
        return _call_claude(profile, question, language, history or [])
    return _mock_response(profile, question, language)