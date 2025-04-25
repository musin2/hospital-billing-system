from flask import Flask
from flask_restx import Api
from .config import Config
from .extensions import db,migrate
from app.routes import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app,db)
    # cors.init_app(app)

    # Register all models for flask migrate
    from app import models
    api = Api(
    app,
    title="Hospital Billing System API",
    description="API for managing the bills of patients and the organizations that represent them",
)
    
    # Register blueprints
    register_blueprints(app)

    return app