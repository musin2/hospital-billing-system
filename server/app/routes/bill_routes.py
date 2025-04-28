from flask_restx import Resource
from app.extensions import api
from app.utils.decorators import validate_record

# Get all bills & create a new bill
class Bills(Resource):
    # Get all bills
    def get(self):
        pass

    # Create a new bill
    def post(self):
        pass


api.add_resource(Bills, "/bills")


# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# Patch, delete & get individual bill using id parameter
class Bill(Resource):

    # [x] Updated at => func.now() - database level
    # [ ] void billl ->  Move Bill to VoidBill , fill adjustments / AuditLog table
    # [ ] Delete voided PatientBill ?
    # Organization.outstanding_balance - void Bill amount
    # Bill is void if the wrong patient or amount was recorded
    # Bill can only be voided by an admin (controlled visibility?)
    # ** Case of previous_balance & final_balance in 'Transactions' table???? (*adjustment?)
    # [ ] Non-financial data editing
    # [ ] Fill AuditLog table before applying the changes
    # [ ] Recalculate 'Organization' outsanding_balance when org_id is changed (subtract amount from previous, add amount to new org)
    # [ ] Bill org cannot be changed if bill_status = "paid" / "partially_paid"
    # Payment needs to be reversed then status changed to unpaid
    @validate_record
    def patch(self, id, record, table="PatientBill"):
        pass

    @validate_record
    def delete(self, id, record, table="PatientBill"):
        # [ ] Cannot Delete Bill??
        pass

    @validate_record
    def get(self, id, record, table="PatientBill"):
        pass


api.add_resource(Bill, "/bill/<int:id>")

# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# For duplicate / invalid bills,
# [ ] How to handle partially or full_paid void bills
class Void(Resource):
    pass