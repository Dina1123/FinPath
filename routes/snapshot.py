from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User
from services.risk_engine import calculate_risk
from services.action_generator import generate_actions
from services.claude_service import get_ai_refresh

snapshot_bp = Blueprint("snapshot", __name__)


@snapshot_bp.route("/snapshot", methods=["GET"])
@jwt_required()
def snapshot():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    coverage = {
        "auto_insurance": {
            "covered": profile.has_auto_insurance,
            "label": "Auto Insurance",
        },
        "health_insurance": {
            "covered": profile.has_health_insurance,
            "label": "Health Insurance",
        },
        "renters_insurance": {
            "covered": False,  # hackathon-safe until you collect this explicitly
            "needed": (profile.needs_renters_insurance  & (profile.housing_type != "dorm" | profile.housing_type != "dorm")),
            "label": "Renters Insurance",
        },
        "emergency_fund": {
            "covered": profile.has_emergency_fund,
            "label": "Emergency Fund",
        },
    }

    if profile.likely_gig_driver:
        coverage["rideshare_coverage"] = {
            "covered": profile.has_auto_insurance,
            "label": "Rideshare Coverage",
        }

    return jsonify({
        "risk_score": profile.risk_score,
        "risk_level": profile.risk_level,
        "biggest_risk": profile.biggest_risk,
        "coverage": coverage,
        "language": user.language,
    }), 200


@snapshot_bp.route("/snapshot/refresh", methods=["POST"])
@jwt_required()
def refresh_snapshot():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    # Always recalculate rule-based risk score (reliable baseline)
    risk = calculate_risk(profile)
    profile.risk_score = risk["risk_score"]
    profile.risk_level = risk["risk_level"]
    profile.biggest_risk = risk["biggest_risk"]

    # Try AI-enhanced actions and insight, fall back to rule-based
    ai_result = get_ai_refresh(profile, language=user.language)
    powered_by = "local"

    if ai_result and "actions" in ai_result:
        actions = ai_result["actions"]
        ai_insight = ai_result.get("ai_insight")
        # Use AI's biggest_risk description if provided
        if ai_result.get("biggest_risk"):
            profile.biggest_risk = ai_result["biggest_risk"]
        powered_by = "claude-api"
    else:
        actions = generate_actions(profile, language=user.language)
        ai_insight = None

    db.session.commit()

    return jsonify({
        "risk_score": profile.risk_score,
        "risk_level": profile.risk_level,
        "biggest_risk": profile.biggest_risk,
        "ai_insight": ai_insight,
        "actions": actions,
        "powered_by": powered_by,
    }), 200