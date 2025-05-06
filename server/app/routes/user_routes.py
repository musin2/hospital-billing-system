from flask import Blueprint
from flask_restx import Resource, Namespace
from app.utils.decorators import validate_record
from app.extensions import api
from app.services.user_service import get_user_by_id, create_new_user, update_user_data,delete_user,get_all_users
from app.api_models.user_models import user_model, create_user_model, patch_user_model

user_bp = Blueprint("user", __name__)
user_ns = Namespace("users", description="User operations", path="/")


# Get, Patch, & Delete a specific user
@user_ns.route("/user/<int:id>")
class UserAPI(Resource):
    # @user_ns.marshal_list_with(user_model)
    @validate_record("User")
    def get(self, id, record):
        """List User"""
        return get_user_by_id(record)

    # [ ] Fill AuditLog table before applying the changes
    # [ ] Check dynamic setting of attributes (is appropriate / secure ?)
    @validate_record("User")
    @user_ns.expect(patch_user_model,validate=True)
    def patch(self, id, record):
        """Edit user information"""
        return update_user_data(record)

    @validate_record("User")
    def delete(self, id, record):
        """Delete a User"""
        return delete_user(record)


# Create new user
@user_ns.route("/user")
class NewUser(Resource):
    @user_ns.expect(create_user_model, validate=True)
    def post(self):
        """Create New User"""
        return create_new_user()
    
    def get(self):
        """List all users"""
        return get_all_users()
