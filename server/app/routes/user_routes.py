from flask_restx import Resource
from app.utils.decorators import validate_record
from app.extensions import api
# Get, Patch, & Delete a specific user
class UserAPI(Resource):

    @validate_record
    def get(self, id, record, table="User"):
        pass

    # [ ] Fill AuditLog table before applying the changes
    # [ ] Check dynamic setting of attributes (is appropriate / secure ?)
    @validate_record
    def patch(self, id, record, table="User"):
        pass

    @validate_record
    def delete(self, id, record, table="User"):
        pass


api.add_resource(UserAPI, "/user/<int:id>")


# Create new user
class NewUser(Resource):
    def post(self):
        pass

api.add_resource(NewUser, "/user")
