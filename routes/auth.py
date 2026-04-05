from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
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

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
    "message": "User created",
    "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "language": user.language,
        "has_profile": False,
    }), 201


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user_id": user.id,
        "language": user.language,
        "has_profile": user.profile is not None,
    }), 200


@auth_bp.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return jsonify({
        "access_token": access_token
    }), 200

@auth_bp.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    profile = user.profile

    return jsonify({
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "language": user.language,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
        "has_profile": profile is not None,
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
        } if profile else None
    }), 200
