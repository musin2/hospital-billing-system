from flask_restx import fields

# api = Api(app, title="Hospital Billing System API", description="API for managing the bills of patients and the organizations that represent them")

def create_user_model(namespace):
    return namespace.model('User', {
        'user_id': fields.Integer(description='User ID'),
        'user_name': fields.String(required=True, description='Full name of the user'),
        'user_role': fields.String(required=True, description='Role of the user (e.g., Admin, Clerk)'),
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='Hashed password'),
    })