from flask import Blueprint, jsonify

resources_bp = Blueprint("resources", __name__)

STATE_FARM_RESOURCES = [
    {
        "id": "renters_insurance",
        "category": "Renters Insurance",
        "provider": "State Farm",
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
        "learn_more_url": "https://www.statefarm.com/insurance/renters",
        "action_key": "get_renters_insurance",
    },
    {
        "id": "auto_insurance",
        "category": "Auto Insurance",
        "provider": "State Farm",
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
        "learn_more_url": "https://www.statefarm.com/insurance/auto",
        "action_key": "get_auto_insurance",
    },
    {
        "id": "rideshare_insurance",
        "category": "Rideshare / Gig Driver Coverage",
        "provider": "State Farm",
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
        "learn_more_url": "https://www.statefarm.com/insurance/auto/rideshare-insurance",
        "action_key": "get_rideshare_coverage",
    },
    {
        "id": "health_insurance",
        "category": "Health Insurance",
        "provider": "Healthcare.gov / State Marketplace",
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
        "learn_more_url": "https://www.healthcare.gov",
        "action_key": "get_health_insurance",
    },
]


@resources_bp.route("/resources", methods=["GET"])
def get_resources():
    """Public endpoint — no auth required. Returns all State Farm resource cards."""
    return jsonify({"resources": STATE_FARM_RESOURCES}), 200


@resources_bp.route("/resources/<string:resource_id>", methods=["GET"])
def get_resource(resource_id):
    """Returns a single resource card by ID."""
    resource = next((r for r in STATE_FARM_RESOURCES if r["id"] == resource_id), None)
    if not resource:
        return jsonify({"error": f"Resource '{resource_id}' not found"}), 404
    return jsonify(resource), 200
