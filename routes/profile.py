# routes/profile.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    profile = user.profile

    if not profile:
        return jsonify({
            "has_profile": False,
            "message": "No profile found"
        }), 200

    return jsonify({
        "has_profile": True,
        "profile": {
            "life_situations": profile.life_situations,
            "is_student": profile.is_student,
            "is_international": profile.is_international,
            "country_of_origin": profile.country_of_origin,
            "entry_route": profile.entry_route,
            "income_sources": profile.income_sources,
            "housing_type": profile.housing_type,
            "has_health_insurance": profile.has_health_insurance,
            "has_auto_insurance": profile.has_auto_insurance,
            "has_emergency_fund": profile.has_emergency_fund,
            "needs_renters_insurance": profile.needs_renters_insurance,
            "likely_gig_driver": profile.likely_gig_driver,
            "risk_score": profile.risk_score,
            "risk_level": profile.risk_level,
            "biggest_risk": profile.biggest_risk,
        }
    }), 200