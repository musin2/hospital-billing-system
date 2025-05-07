from flask_restx import Resource,Namespace
from app.extensions import api
from app.utils.decorators import validate_record
from flask import Blueprint
from app.api_models.bill_models import patient_bill_model,create_patient_bill_model
from app.services.bill_service import get_all_bills

bill_bp = Blueprint("Bills",__name__)
bill_ns = Namespace("Bills", description="Bill Operations", path="/")

@bill_ns.route("/bills")
class Bills(Resource):
    # Get all Bills
    def get(self):
        """List all bills"""
        return get_all_bills()

    # Create a new bill
    def post(self):
        pass

# Patch, delete & get individual bill using id parameter
@bill_ns.route("/bill/<int:id>")
class Bill(Resource):
    # Get an individual bill
    @validate_record
    def get(self):
        pass

    # Edit a bill (non-financial data only - Admin access)
    @validate_record
    def patch(self):
        pass


# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# For duplicate / invalid bills,
# [ ] How to handle partially or full_paid void bills
class Void(Resource):
    pass