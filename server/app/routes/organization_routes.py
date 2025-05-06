from flask_restx import Resource
from app.extensions import api
from app.utils.decorators import validate_record

# Get all organizations and create a new organization (corporate client)
class Organizations(Resource):
    def get(self):
        pass

    def post(self):
        pass


api.add_resource(Organizations, "/orgs")


# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# Get, Patch, & Delete a specific organization
class Organization(Resource):

    @validate_record
    def get(self, id, record, table="Organization"):
        pass

    # [ ] Non critical(financial) fields are editable by the admin
    # [ ] Fill AuditLog before applying the changes
    @validate_record
    def patch(self, id, record, table="Organization"):
        pass

    @validate_record
    def delete(self, id, record, table="Organization"):
        pass


api.add_resource(Organization, "/org/<int:id>")