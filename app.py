from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from config import Config
from extensions import db, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # Import models so SQLAlchemy knows about them
    from models.user import User, Profile, ActionProgress

    # with app.app_context():
    #     print("=== CREATE_APP RUNNING ===")
    #     print("DB URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))
    #     print("Known tables:", list(db.metadata.tables.keys()))
    #     db.create_all()
    #     print("=== CREATE_ALL FINISHED ===")

    swagger_bp = get_swaggerui_blueprint(
        "/docs",
        "/static/openapi.yaml",
        config={"app_name": "FinPath API"},
    )
    app.register_blueprint(swagger_bp)

    from routes.auth import auth_bp
    from routes.onboarding import onboarding_bp
    from routes.snapshot import snapshot_bp
    from routes.actions import actions_bp
    from routes.ai import ai_bp
    from routes.meta import meta_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(onboarding_bp)
    app.register_blueprint(snapshot_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(meta_bp)
    app.register_blueprint(profile_bp)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "FinPath API v2.0"}), 200

    return app


if __name__ == "__main__":
    import os
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)