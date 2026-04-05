"""
Generates a personalized top-3 action plan based on the user's financial profile.
Each action has a key, title, description, urgency, education card, and optional
State Farm product link.
"""

ALL_ACTIONS = [
    {
        "key": "get_rideshare_coverage",
        "title": "Add rideshare coverage to your auto policy",
        "description": (
            "Your personal auto insurance does NOT cover you while driving for Uber or DoorDash. "
            "A rideshare add-on fills that gap — it's usually $10–$20/month extra."
        ),
        "urgency": 1,
        "condition": lambda p: p.likely_gig_driver and not p.has_auto_insurance,
        "education_term": "rideshare coverage",
        "education_card": (
            "Rideshare coverage is an add-on to your regular auto policy that protects you "
            "while you're logged into a gig app but haven't accepted a ride yet. "
            "Without it, you have a coverage gap."
        ),
        "statefarm_product": "State Farm Rideshare Insurance",
        "resource_id": "rideshare_insurance",
    },
    {
        "key": "get_auto_insurance",
        "title": "Get auto insurance",
        "description": (
            "Auto insurance is legally required in almost every state. "
            "Driving without it puts you at serious financial and legal risk."
        ),
        "urgency": 2,
        "condition": lambda p: not p.has_auto_insurance,
        "education_term": "auto insurance",
        "education_card": (
            "Auto insurance covers costs if you're in an accident — repairs, medical bills, "
            "and legal fees. Most states require at least liability coverage by law."
        ),
        "statefarm_product": "State Farm Auto Insurance",
        "resource_id": "auto_insurance",
    },
    {
        "key": "get_health_insurance",
        "title": "Get health insurance",
        "description": (
            "Without health insurance, a single ER visit can cost $3,000+. "
            "You may qualify for a subsidized plan through healthcare.gov."
        ),
        "urgency": 3,
        "condition": lambda p: not p.has_health_insurance,
        "education_term": "health insurance",
        "education_card": (
            "Health insurance pays for medical care — doctor visits, prescriptions, and hospital stays. "
            "If you're a gig worker or self-employed, check healthcare.gov for marketplace plans."
        ),
        "statefarm_product": None,
        "resource_id": "health_insurance",
    },
    {
        "key": "build_emergency_fund",
        "title": "Start an emergency fund",
        "description": (
            "With variable income, an emergency fund is your financial safety net. "
            "Aim for $500 first — then build toward 3 months of expenses."
        ),
        "urgency": 4,
        "condition": lambda p: not p.has_emergency_fund,
        "education_term": "emergency fund",
        "education_card": (
            "An emergency fund is money set aside for unexpected costs like car repairs or medical bills. "
            "Start small — even $25/week adds up fast."
        ),
        "statefarm_product": None,
        "resource_id": None,
    },
    {
        "key": "get_renters_insurance",
        "title": "Get renters insurance",
        "description": (
            "Renters insurance protects your belongings from theft, fire, and water damage. "
            "It typically costs $10–$20/month and is often required by landlords."
        ),
        "urgency": 5,
        "condition": lambda p: p.needs_renters_insurance,
        "education_term": "renters insurance",
        "education_card": (
            "Renters insurance covers your personal belongings if they're stolen or damaged, "
            "and protects you if someone is injured in your home. Your landlord's insurance "
            "does NOT cover your stuff."
        ),
        "statefarm_product": "State Farm Renters Insurance",
        "resource_id": "renters_insurance",
    },
]


def generate_actions(profile) -> list:
    """Return top 3 prioritized actions for the user's profile."""
    applicable = [a for a in ALL_ACTIONS if a["condition"](profile)]
    applicable.sort(key=lambda a: a["urgency"])
    top3 = applicable[:3]

    return [
        {
            "key": a["key"],
            "title": a["title"],
            "description": a["description"],
            "education_term": a["education_term"],
            "education_card": a["education_card"],
            "statefarm_product": a["statefarm_product"],
            "resource_id": a["resource_id"],
        }
        for a in top3
    ]
