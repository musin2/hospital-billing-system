from flask_restx import fields
from app.extensions import api
from app.utils.enums import GenderOption,BillStatus,BillType

patient_bill_model = api.model("PatientBill", {
    "bill_id": fields.Integer(readonly=True),
    "patient_number": fields.String(required=True, description="Inpatient or Outpatient number"),
    "patient_id": fields.String(required=True, description="Personal ID/Passport"),
    "patient_name": fields.String(required=True),
    "patient_gender": fields.String(required=True, enum=[g.value for g in GenderOption]),
    "patient_age": fields.Integer(required=True, min=0),
    "patient_birthdate": fields.Date(required=False),
    "patient_phone_number": fields.String(required=True),
    "bill_date": fields.Date(required=True),
    "organization_id": fields.Integer(required=True),
    "bill_type": fields.String(required=True, enum=[t.value for t in BillType]),
    "amount": fields.Float(required=True, min=0.0),
    "status": fields.String(required=True, enum=[s.value for s in BillStatus]),
    "paid_amount": fields.Float(required=False, min=0.0),
    "created_at": fields.DateTime(readonly=True),
    "updated_at": fields.DateTime(readonly=True),
})

create_patient_bill_model = api.model("PatientBillCreate", {
    "patient_number": fields.String(required=True),
    "patient_id": fields.String(required=True),
    "patient_name": fields.String(required=True),
    "patient_gender": fields.String(required=True, enum=[g.value for g in GenderOption]),
    "patient_age": fields.Integer(required=False, min=0),
    "patient_birthdate": fields.Date(required=False),
    "patient_phone_number": fields.String(required=True),
    "bill_date": fields.Date(required=True),
    "organization_id": fields.Integer(required=True),
    "bill_type": fields.String(required=True, enum=[t.value for t in BillType]),
    "amount": fields.Float(required=True, min=0.0),
    "status": fields.String(required=True, enum=[s.value for s in BillStatus]),
    "paid_amount": fields.Float(min=0.0),
})
edit_patient_bill_model = api.model("PatientBillCreate", {
    "patient_number": fields.String(required=True),
    "patient_id": fields.String(required=True),
    "patient_name": fields.String(required=True),
    "patient_gender": fields.String(required=True, enum=[g.value for g in GenderOption]),
    "patient_age": fields.Integer(required=False, min=0),
    "patient_birthdate": fields.Date(required=False),
    "patient_phone_number": fields.String(required=True),
    "bill_date": fields.Date(required=True),
    "organization_id": fields.Integer(required=True),
    "bill_type": fields.String(required=True, enum=[t.value for t in BillType]),
})