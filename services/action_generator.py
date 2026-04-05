"""
Generates a personalized top-3 action plan based on the user's financial profile.
Each action has a key, title, description, urgency, education card, and optional
State Farm product link. Supports English (en) and Spanish (es).
"""

ALL_ACTIONS = [
    {
        "key": "get_rideshare_coverage",
        "title": "Add rideshare coverage to your auto policy",
        "title_es": "Agrega cobertura de rideshare a tu póliza de auto",
        "description": (
            "Your personal auto insurance does NOT cover you while driving for Uber or DoorDash. "
            "A rideshare add-on fills that gap — it's usually $10–$20/month extra."
        ),
        "description_es": (
            "Tu seguro de auto personal NO te cubre mientras conduces para Uber o DoorDash. "
            "Un complemento de rideshare llena ese vacío — generalmente cuesta $10–$20/mes extra."
        ),
        "urgency": 1,
        "condition": lambda p: p.likely_gig_driver and not p.has_auto_insurance,
        "education_term": "rideshare coverage",
        "education_term_es": "cobertura de rideshare",
        "education_card": (
            "Rideshare coverage is an add-on to your regular auto policy that protects you "
            "while you're logged into a gig app but haven't accepted a ride yet. "
            "Without it, you have a coverage gap."
        ),
        "education_card_es": (
            "La cobertura de rideshare es un complemento a tu póliza de auto que te protege "
            "mientras estás conectado en una app pero aún no has aceptado un viaje. "
            "Sin ella, tienes una brecha en tu cobertura."
        ),
        "statefarm_product": "State Farm Rideshare Insurance",
        "resource_id": "rideshare_insurance",
    },
    {
        "key": "get_auto_insurance",
        "title": "Get auto insurance",
        "title_es": "Obtén seguro de auto",
        "description": (
            "Auto insurance is legally required in almost every state. "
            "Driving without it puts you at serious financial and legal risk."
        ),
        "description_es": (
            "El seguro de auto es legalmente requerido en casi todos los estados. "
            "Conducir sin él te pone en serio riesgo financiero y legal."
        ),
        "urgency": 2,
        "condition": lambda p: not p.has_auto_insurance,
        "education_term": "auto insurance",
        "education_term_es": "seguro de auto",
        "education_card": (
            "Auto insurance covers costs if you're in an accident — repairs, medical bills, "
            "and legal fees. Most states require at least liability coverage by law."
        ),
        "education_card_es": (
            "El seguro de auto cubre los costos si estás en un accidente — reparaciones, "
            "facturas médicas y honorarios legales. La mayoría de los estados requieren "
            "al menos cobertura de responsabilidad civil por ley."
        ),
        "statefarm_product": "State Farm Auto Insurance",
        "resource_id": "auto_insurance",
    },
    {
        "key": "get_health_insurance",
        "title": "Get health insurance",
        "title_es": "Obtén seguro médico",
        "description": (
            "Without health insurance, a single ER visit can cost $3,000+. "
            "You may qualify for a subsidized plan through healthcare.gov."
        ),
        "description_es": (
            "Sin seguro médico, una sola visita a urgencias puede costar $3,000 o más. "
            "Puedes calificar para un plan subsidiado a través de healthcare.gov."
        ),
        "urgency": 3,
        "condition": lambda p: not p.has_health_insurance,
        "education_term": "health insurance",
        "education_term_es": "seguro médico",
        "education_card": (
            "Health insurance pays for medical care — doctor visits, prescriptions, and hospital stays. "
            "If you're a gig worker or self-employed, check healthcare.gov for marketplace plans."
        ),
        "education_card_es": (
            "El seguro médico paga la atención médica — visitas al médico, medicamentos y "
            "hospitalizaciones. Si eres trabajador independiente, consulta healthcare.gov "
            "para planes del mercado."
        ),
        "statefarm_product": None,
        "resource_id": "health_insurance",
    },
    {
        "key": "build_emergency_fund",
        "title": "Start an emergency fund",
        "title_es": "Comienza un fondo de emergencia",
        "description": (
            "With variable income, an emergency fund is your financial safety net. "
            "Aim for $500 first — then build toward 3 months of expenses."
        ),
        "description_es": (
            "Con ingresos variables, un fondo de emergencia es tu red de seguridad financiera. "
            "Apunta a $500 primero — luego construye hacia 3 meses de gastos."
        ),
        "urgency": 4,
        "condition": lambda p: not p.has_emergency_fund,
        "education_term": "emergency fund",
        "education_term_es": "fondo de emergencia",
        "education_card": (
            "An emergency fund is money set aside for unexpected costs like car repairs or medical bills. "
            "Start small — even $25/week adds up fast."
        ),
        "education_card_es": (
            "Un fondo de emergencia es dinero reservado para gastos inesperados como "
            "reparaciones de auto o facturas médicas. Empieza pequeño — incluso $25 a la semana suma rápido."
        ),
        "statefarm_product": None,
        "resource_id": None,
    },
    {
        "key": "get_renters_insurance",
        "title": "Get renters insurance",
        "title_es": "Obtén seguro de arrendatario",
        "description": (
            "Renters insurance protects your belongings from theft, fire, and water damage. "
            "It typically costs $10–$20/month and is often required by landlords."
        ),
        "description_es": (
            "El seguro de arrendatario protege tus pertenencias de robo, incendio y daños por agua. "
            "Generalmente cuesta $10–$20/mes y a menudo es requerido por los arrendadores."
        ),
        "urgency": 5,
        "condition": lambda p: p.needs_renters_insurance,
        "education_term": "renters insurance",
        "education_term_es": "seguro de arrendatario",
        "education_card": (
            "Renters insurance covers your personal belongings if they're stolen or damaged, "
            "and protects you if someone is injured in your home. Your landlord's insurance "
            "does NOT cover your stuff."
        ),
        "education_card_es": (
            "El seguro de arrendatario cubre tus pertenencias personales si son robadas o dañadas, "
            "y te protege si alguien se lesiona en tu hogar. El seguro de tu arrendador "
            "NO cubre tus cosas."
        ),
        "statefarm_product": "State Farm Renters Insurance",
        "resource_id": "renters_insurance",
    },
]


def _serialize_action(a: dict, language: str) -> dict:
    es = language == "es"
    return {
        "key": a["key"],
        "title": a["title_es"] if es else a["title"],
        "description": a["description_es"] if es else a["description"],
        "education_term": a["education_term_es"] if es else a["education_term"],
        "education_card": a["education_card_es"] if es else a["education_card"],
        "statefarm_product": a["statefarm_product"],
        "resource_id": a["resource_id"],
    }


def generate_actions(profile, language: str = "en") -> list:
    """Return top 3 prioritized actions for the user's profile."""
    applicable = [a for a in ALL_ACTIONS if a["condition"](profile)]
    applicable.sort(key=lambda a: a["urgency"])
    return [_serialize_action(a, language) for a in applicable[:3]]


def serialize_action(a: dict, language: str = "en") -> dict:
    """Serialize a single action dict from ALL_ACTIONS with language support."""
    return _serialize_action(a, language)
