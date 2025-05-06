from app.extensions import api
from flask_restx import fields

user_model = api.model('User', {
    'user_id': fields.Integer(readOnly=True, description='Unique user ID'),
    'user_name': fields.String(required=True, description='Full name of the user'),
    'user_role': fields.String(required=True, description='Role of the user'),
    'email': fields.String(required=True, description='User email address'),
})

create_user_model = api.model('UserCreate', {
    'user_name': fields.String(required=True, description='Full name of the user'),
    'user_role': fields.String(required=True, description='Role of the user'),
    'email': fields.String(required=True, description='User email address'),
    'password': fields.String(required=True, description='User password'),
})

patch_user_model = api.model("UserPatch", {
    "user_name": fields.String(required=False, description='Full name of the user'),
    "user_role": fields.String(required=False, description='Role of the user'),
    "email": fields.String(required=False, description='User email address'),
    "password": fields.String(required=False, description='User password'),
})
