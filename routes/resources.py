from flask import Blueprint, request, jsonify

resources_bp = Blueprint("resources", __name__)

STATE_FARM_RESOURCES = [
    {
        "id": "renters_insurance",
        "action_key": "get_renters_insurance",
        "provider": "State Farm",
        "learn_more_url": "https://www.statefarm.com/insurance/renters",
        "en": {
            "category": "Renters Insurance",
            "title": "State Farm Renters Insurance",
            "description": (
                "Protects your personal belongings from theft, fire, and water damage. "
                "Also covers liability if someone is injured in your home. "
                "Your landlord's insurance does NOT cover your belongings."
            ),
            "typical_cost": "$10–$20/month",
            "why_it_matters": (
                "If your apartment floods or is broken into, renters insurance covers "
                "the cost of replacing your stuff — your landlord's policy won't."
            ),
            "who_needs_it": ["renters", "dorm residents"],
        },
        "es": {
            "category": "Seguro de Arrendatario",
            "title": "Seguro de Arrendatario de State Farm",
            "description": (
                "Protege tus pertenencias personales de robo, incendio y daños por agua. "
                "También cubre responsabilidad si alguien se lesiona en tu hogar. "
                "El seguro de tu arrendador NO cubre tus pertenencias."
            ),
            "typical_cost": "$10–$20/mes",
            "why_it_matters": (
                "Si tu apartamento se inunda o es robado, el seguro de arrendatario cubre "
                "el costo de reemplazar tus cosas — la póliza de tu arrendador no lo hará."
            ),
            "who_needs_it": ["arrendatarios", "residentes de dormitorios"],
        },
    },
    {
        "id": "auto_insurance",
        "action_key": "get_auto_insurance",
        "provider": "State Farm",
        "learn_more_url": "https://www.statefarm.com/insurance/auto",
        "en": {
            "category": "Auto Insurance",
            "title": "State Farm Auto Insurance",
            "description": (
                "Legally required in almost every state. Covers accident costs — "
                "vehicle repairs, medical bills, and legal liability. "
                "State Farm is the #1 auto insurer in the US."
            ),
            "typical_cost": "Varies by state, driving record, and vehicle",
            "why_it_matters": (
                "Driving without insurance can result in fines, license suspension, "
                "and full out-of-pocket liability if you cause an accident."
            ),
            "who_needs_it": ["anyone who drives"],
        },
        "es": {
            "category": "Seguro de Auto",
            "title": "Seguro de Auto de State Farm",
            "description": (
                "Legalmente requerido en casi todos los estados. Cubre costos de accidentes — "
                "reparaciones de vehículos, facturas médicas y responsabilidad legal. "
                "State Farm es el asegurador de auto #1 en EE.UU."
            ),
            "typical_cost": "Varía según el estado, historial de conducción y vehículo",
            "why_it_matters": (
                "Conducir sin seguro puede resultar en multas, suspensión de licencia "
                "y responsabilidad total de bolsillo si causas un accidente."
            ),
            "who_needs_it": ["cualquier persona que conduzca"],
        },
    },
    {
        "id": "rideshare_insurance",
        "action_key": "get_rideshare_coverage",
        "provider": "State Farm",
        "learn_more_url": "https://www.statefarm.com/insurance/auto/rideshare-insurance",
        "en": {
            "category": "Rideshare / Gig Driver Coverage",
            "title": "State Farm Rideshare Insurance",
            "description": (
                "An add-on to your personal auto policy that covers you while you're "
                "logged into a gig app (Uber, Lyft, DoorDash) but haven't accepted a ride yet. "
                "Personal auto insurance does NOT cover this gap."
            ),
            "typical_cost": "$10–$20/month extra on top of personal auto",
            "why_it_matters": (
                "Between when you log into the app and when you accept a trip, "
                "both your personal insurer and the app's insurance may deny a claim. "
                "This add-on closes that gap."
            ),
            "who_needs_it": ["gig drivers", "rideshare drivers", "delivery workers"],
        },
        "es": {
            "category": "Cobertura de Rideshare / Conductor de Plataforma",
            "title": "Seguro de Rideshare de State Farm",
            "description": (
                "Un complemento a tu póliza de auto personal que te cubre mientras estás "
                "conectado en una app (Uber, Lyft, DoorDash) pero aún no has aceptado un viaje. "
                "El seguro de auto personal NO cubre esta brecha."
            ),
            "typical_cost": "$10–$20/mes adicionales sobre el seguro de auto personal",
            "why_it_matters": (
                "Entre cuando te conectas a la app y cuando aceptas un viaje, "
                "tanto tu aseguradora personal como el seguro de la app pueden negar un reclamo. "
                "Este complemento cierra esa brecha."
            ),
            "who_needs_it": ["conductores de rideshare", "conductores de entrega"],
        },
    },
    {
        "id": "health_insurance",
        "action_key": "get_health_insurance",
        "provider": "Healthcare.gov / State Marketplace",
        "learn_more_url": "https://www.healthcare.gov",
        "en": {
            "category": "Health Insurance",
            "title": "Health Insurance Marketplace Plans",
            "description": (
                "If you don't have employer-sponsored health insurance, you can shop for "
                "plans on healthcare.gov. Many gig workers, students, and immigrants "
                "qualify for subsidized plans based on income."
            ),
            "typical_cost": "Varies — subsidies available based on income",
            "why_it_matters": (
                "A single ER visit without insurance can cost $3,000 or more. "
                "Health insurance protects you from catastrophic medical bills."
            ),
            "who_needs_it": ["gig workers", "self-employed", "students", "recent graduates"],
        },
        "es": {
            "category": "Seguro Médico",
            "title": "Planes de Seguro Médico del Mercado",
            "description": (
                "Si no tienes seguro médico del empleador, puedes buscar planes en healthcare.gov. "
                "Muchos trabajadores independientes, estudiantes e inmigrantes "
                "califican para planes subsidiados según sus ingresos."
            ),
            "typical_cost": "Varía — subsidios disponibles según ingresos",
            "why_it_matters": (
                "Una sola visita a urgencias sin seguro puede costar $3,000 o más. "
                "El seguro médico te protege de facturas médicas catastróficas."
            ),
            "who_needs_it": ["trabajadores independientes", "estudiantes", "recién graduados"],
        },
    },
]


def _serialize_resource(r: dict, language: str) -> dict:
    lang = "es" if language == "es" else "en"
    return {
        "id": r["id"],
        "action_key": r["action_key"],
        "provider": r["provider"],
        "learn_more_url": r["learn_more_url"],
        **r[lang],
    }


@resources_bp.route("/resources", methods=["GET"])
def get_resources():
    """Public endpoint. Pass ?lang=es for Spanish."""
    language = request.args.get("lang", "en")
    resources = [_serialize_resource(r, language) for r in STATE_FARM_RESOURCES]
    return jsonify({"resources": resources}), 200


@resources_bp.route("/resources/<string:resource_id>", methods=["GET"])
def get_resource(resource_id):
    """Pass ?lang=es for Spanish."""
    language = request.args.get("lang", "en")
    resource = next((r for r in STATE_FARM_RESOURCES if r["id"] == resource_id), None)
    if not resource:
        return jsonify({"error": f"Resource '{resource_id}' not found"}), 404
    return jsonify(_serialize_resource(resource, language)), 200
