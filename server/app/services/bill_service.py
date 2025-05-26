from flask import make_response, request
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from app.models.patientbill import PatientBill
from app.utils.serialization import serialize_bill
from app.utils.enums import BillStatus
from app.models.organization import Organization
from app.extensions import db
from app.utils.validation import validate_and_format_number


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
    try:
        data = request.get_json()  # Retreive form data

        # Data Validation
        required_fields = [
            "patient_number",
            "patient_id",
            "patient_name",
            "patient_gender",
            "patient_phone_number",
            "bill_date",
            "organization_id",
            "bill_type",
            "amount",
        ]
        # [x] additional validation in database ? with column data types
        for field in required_fields:
            if field not in data:
                return make_response({"error": f"Missing data: {field}"}, 400)

        patient_number = data["patient_number"]
        patient_id = data["patient_id"]
        patient_name = data["patient_name"]
        patient_gender = data["patient_gender"]
        patient_age = data["patient_age"]
        patient_birthdate = data["patient_birthdate"]

        # [ ] phone number format 0712356789 / +254712356789 from frontend
        # [x] Validate phone number
        try:
            patient_phone_number = validate_and_format_number(data["patient_phone_number"])
        except ValueError as e:
            return make_response({"error":str(e)},400)
        
        bill_date = data["bill_date"]
        organization_id = data["organization_id"]
        # [ ] Use Enum???
        bill_type = data["bill_type"]
        print(bill_type)
        print(patient_gender)
        amount = data["amount"]
        # created_at & updated_at are set to current time at database level (default / onupdate = func.now())

        # Validate if one of the two is present
        if patient_age is None and patient_birthdate is None:
            return make_response(
                {"error": "Patient's age or birthdate must be included"}, 400
            )

        # [x] Calculate age from birthdate / Calculate birthdate from age
        if patient_age is not None and patient_birthdate is None:
            current_year = datetime.now(timezone.utc).year
            birth_year = current_year - patient_age
            patient_birthdate = f"{birth_year}-1-1"
            print(f"Calculated birthdate: {patient_birthdate}")

        if patient_birthdate is not None and patient_age is None:
            current_date = datetime.now(timezone.utc).date()
            birthdate = datetime.strptime(patient_birthdate, "%Y-%m-%d")
            age_delta = relativedelta(current_date,birthdate)
            patient_age = age_delta.years
            print(f"Calculated age: {patient_age}")

        new_bill = PatientBill(
            patient_number=patient_number,
            patient_id=patient_id,
            patient_name=patient_name,
            patient_gender=patient_gender,
            patient_age=patient_age,
            patient_birthdate=patient_birthdate,
            patient_phone_number=patient_phone_number,
            bill_date=bill_date,
            organization_id=organization_id,
            bill_type=bill_type,
            amount=amount,
            status=BillStatus.unpaid.value,
        )
        # [ ] update outstanding_balance in 'Organization' table
        current_organization = Organization.query.filter_by(org_id = organization_id).first()
        if current_organization is None:
            return make_response({"error": "Organization not found"}, 404)
        current_organization.outstanding_balance += amount

        db.session.add(new_bill)
        db.session.commit()
        response_body = {"message": "Bill created successfully!"}
        return make_response(response_body, 200)

    except Exception as e:
        db.session.rollback()
        return make_response({"error": str(e)}, 500)


def get_bill_by_id(record):
    try:
        return make_response(serialize_bill(record),200)
    except Exception as e:
        return make_response({"error":str(e)},500)


def edit_bill():
    pass


def void_bill():
    pass
