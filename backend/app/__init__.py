"""
Application factory for CareerLens AI backend.
"""

import os
import logging
from flask import Flask, jsonify

from .config import get_config
from .extensions import mongo, bcrypt, jwt, cors


def create_app(config_override: dict | None = None) -> Flask:
    app = Flask(__name__)

    # ------------------------------------------------------------------ #
    # Configuration                                                        #
    # ------------------------------------------------------------------ #
    cfg = get_config()
    app.config.from_object(cfg)
    if config_override:
        app.config.update(config_override)

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ------------------------------------------------------------------ #
    # Logging                                                              #
    # ------------------------------------------------------------------ #
    logging.basicConfig(
        level=logging.DEBUG if app.config["DEBUG"] else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ------------------------------------------------------------------ #
    # Extensions                                                           #
    # ------------------------------------------------------------------ #
    mongo.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    # ------------------------------------------------------------------ #
    # Blueprints                                                           #
    # ------------------------------------------------------------------ #
    from .blueprints.auth import auth_bp
    from .blueprints.resumes import resumes_bp
    from .blueprints.analysis import analysis_bp
    from .blueprints.recommendations import recommendations_bp
    from .blueprints.admin import admin_bp
    from .blueprints.health import health_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(resumes_bp, url_prefix="/api/resumes")
    app.register_blueprint(analysis_bp, url_prefix="/api/analysis")
    app.register_blueprint(recommendations_bp, url_prefix="/api/recommendations")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(health_bp, url_prefix="/api")

    # ------------------------------------------------------------------ #
    # Global error handlers                                               #
    # ------------------------------------------------------------------ #
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": "Bad request", "message": str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "Unauthorized", "message": "Authentication required"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "Forbidden", "message": "You do not have permission"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found", "message": str(e)}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": "File too large", "message": "Upload exceeds size limit"}), 413

    @app.errorhandler(500)
    def server_error(e):
        app.logger.exception("Unhandled exception")
        return jsonify({"error": "Internal server error", "message": "An unexpected error occurred"}), 500

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_data):
        return jsonify({"error": "Token expired", "message": "Please log in again"}), 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return jsonify({"error": "Invalid token", "message": reason}), 401

    @jwt.unauthorized_loader
    def missing_token(reason):
        return jsonify({"error": "Token missing", "message": reason}), 401

    return app
