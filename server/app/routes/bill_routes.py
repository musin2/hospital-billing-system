from flask_restx import Resource,Namespace
from app.extensions import api
from app.utils.decorators import validate_record
from flask import Blueprint
from app.api_models.bill_models import patient_bill_model,create_patient_bill_model,edit_patient_bill_model
from app.services.bill_service import get_all_bills,create_new_bill,get_bill_by_id,edit_bill

bill_bp = Blueprint("Bills",__name__)
bill_ns = Namespace("Bills", description="Bill Operations", path="/")

@bill_ns.route("/bills")
class Bills(Resource):
    # Get all Bills
    def get(self):
        """List all bills"""
        return get_all_bills()

    # Create a new bill
    @bill_ns.expect(create_patient_bill_model,validate=False)
    def post(self):
        """Create new Patient Bill"""
        return create_new_bill()

# Patch, delete & get individual bill using id parameter
@bill_ns.route("/bill/<int:id>")
class Bill(Resource):
    # @bill_ns.marshal_with(patient_bill_model)
    @validate_record("PatientBill")
    def get(self,id,record):
        """Get an individual bill"""
        return get_bill_by_id(record)

    # Edit a bill (non-financial data only - Admin access)
    @validate_record("PatientBill")
    @bill_ns.expect(edit_patient_bill_model,validation=False)
    def patch(self,id,record):
        """Edit Bill"""
        return edit_bill(record)


# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# For duplicate / invalid bills,
# [ ] How to handle partially or full_paid void bills
class Void(Resource):
    pass