from app.extensions import db
from sqlalchemy import CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
from decimal import Decimal


# Records PatientBill after full payment (=many)
class PaidBill(db.Model, SerializerMixin):
    __tablename__ = "paid_bills"

    __table_args__ = (
        CheckConstraint("patient_age >= 0", name="check_patient_age_positive"),
        CheckConstraint("amount >= 0", name="check_amount_positive"),
        CheckConstraint("paid_amount >= 0", name="check_paid_amount_positive"),
        CheckConstraint("status = 'paid'", name="check_status_paid"),
        CheckConstraint("paid_amount = amount", name="check_paid_bill_full_payment"),
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
    # [ ] Validate paid_amount == amount & status == "paid" in flask app
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
    # Transaction that fully paid the bill
    transaction_id = db.Column(
        db.Integer, db.ForeignKey("transactions.transaction_id"), nullable=False
    )
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable

    org = db.relationship(
        "Organization", back_populates="paid_bills", cascade="save-update, merge"
    )
    transaction = db.relationship(
        "Transaction", back_populates="paid_bills", cascade="save-update, merge"
    )

    serialize_rules = ("-org.bills",)