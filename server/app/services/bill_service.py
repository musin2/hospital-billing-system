from app.models.patientbill import PatientBill
from flask import make_response
from app.utils.serialization import serialize_bill

def get_all_bills():
    try:
        bills = PatientBill.query.all()

        if not bills:
            return make_response({"message": "Bills not found"}, 404)
        return make_response([serialize_bill(bill) for bill in bills], 200)

    except Exception as e:
        # Return error message with status code 500 if something goes wrong
        return make_response({"error": str(e)}, 500)

def create_new_bill():
    pass

def get_bill_by_id():
    pass

def edit_bill():
    pass

def void_bill():
    pass