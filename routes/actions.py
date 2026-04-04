from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, ActionProgress
from services.action_generator import generate_actions
from services.risk_engine import calculate_risk

actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/actions", methods=["GET"])
@jwt_required()
def get_actions():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    actions = generate_actions(user.profile)

    # Annotate each action with completion status
    completed_keys = {
        ap.action_key for ap in user.action_progress if ap.completed
    }
    for action in actions:
        action["completed"] = action["key"] in completed_keys

    return jsonify({"actions": actions}), 200


@actions_bp.route("/actions/<string:action_key>", methods=["PATCH"])
@jwt_required()
def complete_action(action_key):
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    # Mark action complete (upsert)
    progress = ActionProgress.query.filter_by(
        user_id=user_id, action_key=action_key
    ).first()

    if not progress:
        progress = ActionProgress(user_id=user_id, action_key=action_key)
        db.session.add(progress)

    progress.completed = True
    progress.completed_at = datetime.utcnow()

    # Update profile coverage field if applicable
    profile = user.profile
    if action_key == "get_auto_insurance" or action_key == "get_rideshare_coverage":
        profile.has_auto_insurance = True
    elif action_key == "get_health_insurance":
        profile.has_health_insurance = True
    elif action_key == "get_renters_insurance":
        profile.has_renters_insurance = True
    elif action_key == "build_emergency_fund":
        profile.has_emergency_fund = True

    # Recalculate risk after update
    risk = calculate_risk(profile)
    profile.risk_score = risk["risk_score"]
    profile.risk_level = risk["risk_level"]
    profile.biggest_risk = risk["biggest_risk"]

    db.session.commit()

    return jsonify({
        "message": f"Action '{action_key}' marked complete",
        "new_risk_score": profile.risk_score,
        "new_risk_level": profile.risk_level,
    }), 200
