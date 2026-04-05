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

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    language = user.language
    answer = get_ai_response(user.profile, question, language)

    return jsonify({
        "question": question,
        "answer": answer,
        "language": language,
        "powered_by": "claude-api" if __import__("os").getenv("ANTHROPIC_API_KEY") else "local-mock",
    }), 200
