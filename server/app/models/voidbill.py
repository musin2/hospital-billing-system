from ..extensions import db
from enum import Enum
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
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

# Errenous bills that have been voided
class VoidBill(db.Model, SerializerMixin):
    __tablename__ = "void_bills"

    __table_args__ = (
        CheckConstraint("patient_age >= 0", name="check_patient_age_positive"),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint("paid_amount >= 0", name="check_paid_amount_positive"),
        CheckConstraint("status = 'void'", name="check_void_bill_status_paid"),
    )

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    voided_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    patient_number = db.Column(db.String(50), nullable=False)
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
    amount = db.Column(
        db.Numeric(15, 2), nullable=False, info={"check_constraint": "amount >= 0"}
    )
    status = db.Column(db.String(20), nullable=False)
    paid_amount = db.Column(
        db.Numeric(15, 2),
        default=Decimal("0.00"),
        nullable=False,
        info={"check_constraint": "paid_amount >= 0"},
    )
    # transaction_id should be nullable in the case where a bill is not fully paid
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable
    # [x] Set voided timestamp when bill status = void
    voided_at = db.Column(db.DateTime, default=func.now())

    org = db.relationship(
        "Organization", back_populates="voided_bills", cascade="save-update, merge"
    )
    user = db.relationship("User", back_populates="voids", cascade="save-update, merge")

    serialize_rules = ("-org.voided_bills",)