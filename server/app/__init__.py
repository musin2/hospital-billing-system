from flask import Flask
from flask_restx import Api
from .config import Config
from .extensions import db,migrate,api
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
    api.init_app(app)
    
    # Register blueprints
    register_blueprints(app)

    return app