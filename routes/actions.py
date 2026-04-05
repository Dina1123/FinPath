from datetime import datetime
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models.user import User, ActionProgress
from services.action_generator import generate_actions, ALL_ACTIONS, serialize_action
from services.risk_engine import calculate_risk

actions_bp = Blueprint("actions", __name__)


@actions_bp.route("/actions", methods=["GET"])
@jwt_required()
def get_actions():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    actions = generate_actions(user.profile, language=user.language)

    completed_keys = {
        ap.action_key for ap in user.action_progress if ap.completed
    }

    for action in actions:
        action["completed"] = action["key"] in completed_keys

    return jsonify({"actions": actions}), 200


@actions_bp.route("/actions/completed", methods=["GET"])
@jwt_required()
def get_completed_actions():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    completed_keys = {
        ap.action_key for ap in user.action_progress if ap.completed
    }

    action_map = {a["key"]: a for a in ALL_ACTIONS}
    actions = [
        {**serialize_action(action_map[key], language=user.language), "completed": True}
        for key in completed_keys
        if key in action_map
    ]

    return jsonify({"actions": actions, "total": len(actions)}), 200


@actions_bp.route("/actions/<string:action_key>", methods=["PATCH"])
@jwt_required()
def complete_action(action_key):
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    profile = user.profile

    progress = ActionProgress.query.filter_by(
        user_id=user_id,
        action_key=action_key
    ).first()

    if not progress:
        progress = ActionProgress(user_id=user_id, action_key=action_key)
        db.session.add(progress)

    progress.completed = True
    progress.completed_at = datetime.utcnow()

    # Update profile fields where the action directly changes known state
    if action_key in {"get_auto_insurance", "get_rideshare_coverage"}:
        profile.has_auto_insurance = True

    elif action_key == "get_health_insurance":
        profile.has_health_insurance = True

    elif action_key == "build_emergency_fund":
        profile.has_emergency_fund = True

    # Hackathon note:
    # We do NOT update renters coverage here because the current Profile model
    # does not store `has_renters_insurance`; it only stores whether renters
    # insurance is relevant via `needs_renters_insurance`.

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