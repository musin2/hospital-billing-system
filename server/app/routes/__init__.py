from flask import Flask
from app.routes.user_routes import user_ns,user_bp
from app.routes.bill_routes import bill_ns, bill_bp
from app.extensions import api

# [ ] Generate requirements.txt ?

def register_blueprints(app:Flask):
    app.register_blueprint(user_bp)
    api.add_namespace(user_ns,path="")

    app.register_blueprint(bill_bp)
    api.add_namespace(bill_ns)