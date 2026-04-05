# routes/meta.py
from flask import Blueprint, jsonify
from constants.onboarding import (
    LIFE_SITUATIONS,
    INCOME_SOURCES,
    ENTRY_ROUTES,
    HOUSING_TYPES,
)

meta_bp = Blueprint("meta", __name__)

@meta_bp.route("/meta/onboarding-options", methods=["GET"])
def get_onboarding_options():
    return jsonify({
        "life_situations": LIFE_SITUATIONS,
        "income_sources": INCOME_SOURCES,
        "entry_routes": ENTRY_ROUTES,
        "housing_types": HOUSING_TYPES,
    }), 200