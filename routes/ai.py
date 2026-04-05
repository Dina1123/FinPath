from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from services.claude_service import get_ai_response

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/ai/ask", methods=["POST"])
@jwt_required()
def ask():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    if not user.profile:
        return jsonify({"error": "No profile found. Complete onboarding first."}), 404

    data = request.get_json() or {}
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not question:
        return jsonify({"error": "question is required"}), 400

    # Validate history shape — must be list of {role, content} dicts
    if not isinstance(history, list):
        history = []

    language = user.language
    answer = get_ai_response(user.profile, question, language, history=history)

    return jsonify({
        "question": question,
        "answer": answer,
        "language": language,
        "powered_by": "claude-api" if __import__("os").getenv("ANTHROPIC_API_KEY") else "local-mock",
    }), 200
