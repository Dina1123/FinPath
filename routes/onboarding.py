from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, Profile
from services.risk_engine import calculate_risk
from services.action_generator import generate_actions

onboarding_bp = Blueprint("onboarding", __name__)


@onboarding_bp.route("/onboarding", methods=["POST"])
@jwt_required()
def onboarding():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    data = request.get_json()

    # Delete existing profile if re-onboarding
    if user.profile:
        db.session.delete(user.profile)
        db.session.commit()

    profile = Profile(
        user_id=user_id,
        employment_type=data.get("employment_type", "full_time"),
        income_stability=data.get("income_stability", "stable"),
        has_auto_insurance=data.get("has_auto_insurance", False),
        has_health_insurance=data.get("has_health_insurance", False),
        has_renters_insurance=data.get("has_renters_insurance", False),
        has_emergency_fund=data.get("has_emergency_fund", False),
        gig_driving=data.get("gig_driving", False),
        financial_concern=data.get("financial_concern", "all"),
    )

    risk = calculate_risk(profile)
    profile.risk_score = risk["risk_score"]
    profile.risk_level = risk["risk_level"]
    profile.biggest_risk = risk["biggest_risk"]

    db.session.add(profile)
    db.session.commit()

    actions = generate_actions(profile)

    return jsonify({
        "message": "Profile saved",
        "risk_score": profile.risk_score,
        "risk_level": profile.risk_level,
        "biggest_risk": profile.biggest_risk,
        "actions": actions,
    }), 201
