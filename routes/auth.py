from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from extensions import db
from models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    language = data.get("language", "en")

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        language=language,
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=user.id)
    return jsonify({"message": "User created", "token": token, "user_id": user.id}), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token,
                    "user_id": user.id,
                    "language": user.language,
                    "has_profile": user.profile is not None
                    }), 200
