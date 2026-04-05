from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Profile
from services.risk_engine import calculate_risk
from services.action_generator import generate_actions
from constants.onboarding import (
    LIFE_SITUATIONS,
    INCOME_SOURCES,
    ENTRY_ROUTES,
    HOUSING_TYPES,
)
from services.ai_assessment_service import generate_ai_assessment

onboarding_bp = Blueprint("onboarding", __name__)

VALID_LIFE_SITUATIONS = {item["value"] for item in LIFE_SITUATIONS}
VALID_INCOME_SOURCES = {item["value"] for item in INCOME_SOURCES}
VALID_ENTRY_ROUTES = {item["value"] for item in ENTRY_ROUTES}
VALID_HOUSING_TYPES = {item["value"] for item in HOUSING_TYPES}


@onboarding_bp.route("/onboarding", methods=["POST"])
@jwt_required()
def onboarding():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    life_situations = data.get("life_situations", [])
    income_sources = data.get("income_sources", [])
    entry_route = data.get("entry_route")
    housing_type = data.get("housing_type")
    country_of_origin = data.get("country_of_origin")
    is_international = data.get("is_international", False)

    if not isinstance(life_situations, list):
        return jsonify({"error": "life_situations must be a list"}), 400

    if not isinstance(income_sources, list):
        return jsonify({"error": "income_sources must be a list"}), 400

    invalid_life_situations = [x for x in life_situations if x not in VALID_LIFE_SITUATIONS]
    if invalid_life_situations:
        return jsonify({
            "error": "Invalid life_situations values",
            "invalid_values": invalid_life_situations
        }), 400

    invalid_income_sources = [x for x in income_sources if x not in VALID_INCOME_SOURCES]
    if invalid_income_sources:
        return jsonify({
            "error": "Invalid income_sources values",
            "invalid_values": invalid_income_sources
        }), 400

    if entry_route is not None and entry_route not in VALID_ENTRY_ROUTES:
        return jsonify({
            "error": "Invalid entry_route",
            "invalid_value": entry_route
        }), 400

    if housing_type is not None and housing_type not in VALID_HOUSING_TYPES:
        return jsonify({
            "error": "Invalid housing_type",
            "invalid_value": housing_type
        }), 400

    derived_is_student = (
        "full_time_student" in life_situations or
        "student_working" in life_situations
    )

    if entry_route and "new_to_country" not in life_situations:
        return jsonify({
            "error": "entry_route can only be provided when life_situations includes 'new_to_country'"
        }), 400

    if is_international and not country_of_origin:
        return jsonify({
            "error": "country_of_origin is required when is_international is true"
        }), 400

    profile_already_exists = user.profile is not None
    profile = user.profile or Profile(user_id=user_id)

    profile.life_situations = life_situations
    profile.is_student = derived_is_student
    profile.is_international = is_international
    profile.country_of_origin = country_of_origin
    profile.entry_route = entry_route
    profile.income_sources = income_sources
    profile.housing_type = housing_type
    profile.has_health_insurance = data.get("has_health_insurance", False)
    profile.has_auto_insurance = data.get("has_auto_insurance", False)
    profile.has_emergency_fund = data.get("has_emergency_fund", False)

    profile.needs_renters_insurance = profile.housing_type in {"rent", "dorm"}
    profile.likely_gig_driver = "gig_delivery_work" in profile.income_sources

    risk = calculate_risk(profile)
    profile.risk_score = risk["risk_score"]
    profile.risk_level = risk["risk_level"]
    profile.biggest_risk = risk["biggest_risk"]

    if not profile_already_exists:
        db.session.add(profile)

    try:
        assessment = generate_ai_assessment(profile, user.language)
        profile.risk_score = assessment["risk_score"]
        profile.risk_level = assessment["risk_level"]
        profile.biggest_risk = assessment["biggest_risk"]
        actions = assessment["actions"]
    except Exception as e:
        print("AI assessment failed, using fallback:", e)
        risk = calculate_risk(profile)
        profile.risk_score = risk["risk_score"]
        profile.risk_level = risk["risk_level"]
        profile.biggest_risk = risk["biggest_risk"]
        actions = generate_actions(profile)

    db.session.commit()

    # actions = generate_actions(profile)

    return jsonify({
        "message": "Profile saved",
        "has_profile": True,
        "risk_score": profile.risk_score,
        "risk_level": profile.risk_level,
        "biggest_risk": profile.biggest_risk,
        "actions": actions,
    }), 200 if profile_already_exists else 201

        # except Exception as e:
        #     db.session.rollback()
        #     return jsonify({
        #         "error": "Failed to save profile",
        #         "details": str(e)
        #     }), 500