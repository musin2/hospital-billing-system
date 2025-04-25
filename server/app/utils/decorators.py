from app.models import Adjustment
from app.models import AuditLog
from app.models import Organization
from app.models import PaidBill
from app.models import PatientBill
from app.models import Transaction
from app.models import User
from app.models import VoidBill
from flask import make_response
from functools import wraps

# Function that validates the object passed from the validation decorator
def check_record(object):
    if object is None:
        return make_response({"error": "Record not found"}, 404)
    if not isinstance(
        object,
        (
            Organization,
            User,
            Transaction,
            AuditLog,
            PatientBill,
            Adjustment,
            PaidBill,
            VoidBill,
        ),
    ):
        return make_response({"error": "Invalid record type"}, 404)
    # Check if record is voided
    if hasattr(object, "voided_at") and object.voided_at is not None:
        return make_response({"error": "Record is  invalid (void)"}, 400)
    return None

# Decorator function for validation when looking up records with URL parameter
def validate_record(funct):
    @wraps(funct)
    def wrapper(*args, **kwargs):
        id = kwargs.get("id")
        table = kwargs.get("table")
        record = None

        if id is None or not isinstance(id, int) or id < 0:
            return make_response({"error": f"Invalid {table} ID"}, 400)

        if table == "Organization":
            record = Organization.query.filter_by(org_id=id).first()
        elif table == "User":
            record = User.query.filter_by(user_id=id).first()
        elif table == "Transaction":
            record = Transaction.query.filter_by(transaction_id=id).first()
        elif table == "AuditLog":
            record = AuditLog.query.filter_by(log_id=id).first()
        elif table == "PatientBill":
            record = PatientBill.query.filter_by(bill_id=id).first()
        elif table == "Adjustment":
            record = Adjustment.query.filter_by(adjustment_id=id).first()
        elif table == "PaidBill":
            record = PaidBill.query.filter_by(bill_id=id).first()
        elif table == "VoidBill":
            record = VoidBill.query.filter_by(bill_id=id).first()
        else:
            return make_response({"error": "Invalid Table"}, 400)
        error_response = check_record(record)

        if error_response:
            return error_response
        kwargs["record"] = record
        return funct(*args, **kwargs)

    return wrapper
