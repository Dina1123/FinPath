from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    profile = user.profile
    language = user.language

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


@profile_bp.route("/profile", methods=["PATCH"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    allowed = {"name", "language"}
    updates = {k: v for k, v in data.items() if k in allowed}

    if not updates:
        return jsonify({"error": "No valid fields provided. Allowed: name, language"}), 400

    if "language" in updates and updates["language"] not in {"en", "es"}:
        return jsonify({"error": "language must be 'en' or 'es'"}), 400

    if "name" in updates:
        name = updates["name"].strip()
        if not name:
            return jsonify({"error": "name cannot be empty"}), 400
        user.name = name

    if "language" in updates:
        user.language = updates["language"]

    db.session.commit()

    return jsonify({
        "message": "Profile updated",
        "name": user.name,
        "language": user.language,
    }), 200