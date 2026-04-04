from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User, Profile

snapshot_bp = Blueprint("snapshot", __name__)


@snapshot_bp.route("/snapshot", methods=["GET"])
@jwt_required()
def snapshot():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    profile = user.profile

    if not profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    coverage = {
        "auto_insurance":     {"covered": profile.has_auto_insurance,     "label": "Auto Insurance"},
        "health_insurance":   {"covered": profile.has_health_insurance,   "label": "Health Insurance"},
        "renters_insurance":  {"covered": profile.has_renters_insurance,  "label": "Renters Insurance"},
        "emergency_fund":     {"covered": profile.has_emergency_fund,     "label": "Emergency Fund"},
    }

    if profile.gig_driving:
        coverage["rideshare_coverage"] = {
            "covered": profile.has_auto_insurance,
            "label": "Rideshare Coverage",
        }

    return jsonify({
        "risk_score":   profile.risk_score,
        "risk_level":   profile.risk_level,
        "biggest_risk": profile.biggest_risk,
        "coverage":     coverage,
        "language":     user.language,
    }), 200
