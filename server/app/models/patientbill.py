from app.extensions import db
from enum import Enum
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from decimal import Decimal

class BillType(Enum):
    medical = "Medical"
    surgical = "Surgical"

class GenderOption(Enum):
    male = "Male"
    female = "Female"
    other = "Not specified"

class BillStatus(Enum):
    paid = "paid"
    unpaid = "unpaid"
    partially_paid = "partially_paid"
    void = "void"  # Errored bill (move to voided bills table then create a new one)

# Bills Table (=many)
class PatientBill(db.Model, SerializerMixin):
    __tablename__ = "patient_bills"

    __table_args__ = (
        CheckConstraint("patient_age >= 0", name="check_patient_age_positive"),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint("paid_amount >= 0", name="check_paid_amount_positive"),
    )

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    patient_number = db.Column(db.String(50), nullable=False, unique=True, index=True)
    # Personal number (ID / Passport)
    patient_id = db.Column(db.String(15), nullable=False)
    patient_name = db.Column(db.String(255), nullable=False)
    patient_gender = db.Column(db.String(20), nullable=False)
    patient_age = db.Column(db.Integer, info={"check_constraint": "patient_age >= 0"})
    patient_birthdate = db.Column(db.Date)
    patient_phone_number = db.Column(db.String(50), nullable=False)
    bill_date = db.Column(db.Date, nullable=False)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    bill_type = db.Column(db.String(20), nullable=False)
    # amount can only be adjusted by Admin
    amount = db.Column(
        db.Numeric(15, 2), nullable=False, info={"check_constraint": "amount >= 0"}
    )
    # Status can not be edited
    status = db.Column(db.String(20), nullable=False)
    # paid_amount = amount in the case of complete payment; otherwise, it is partail payment
    paid_amount = db.Column(
        db.Numeric(15, 2),
        default=Decimal("0.00"),
        nullable=False,
        info={"check_constraint": "paid_amount >= 0"},
    )
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable

    org = db.relationship(
        "Organization", back_populates="bills", cascade="save-update, merge"
    )
    # [x] Model Level Validation

    serialize_rules = ("-org.bills",)

    @validates("patient_gender")
    def validate_patient_gender(self, key, gender):
        if gender not in [g.value for g in GenderOption]:
            raise ValueError(f"Invalid gender: {gender}")
        return gender

    @validates("bill_type")
    def validate_bill_type(self, key, type):
        if type not in [t.value for t in BillType]:
            raise ValueError(f"Invalid Bill Type: {type}")
        return type

    @validates("status")
    def validate_status(self, key, status):
        if status not in [s.value for s in BillStatus]:
            raise ValueError(f"Invalid Bill Status: {status}")
        return status
 