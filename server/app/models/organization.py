from app.extensions import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from decimal import Decimal
from enum import Enum


class Organization(db.Model, SerializerMixin):
    __tablename__ = "organizations"

    org_id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(255), nullable=False)
    org_email = db.Column(db.String(255), nullable=False, unique=True)
    org_phone_number = db.Column(db.String(255), nullable=False, unique=True)
    org_type = db.Column(db.String(50), nullable=False)
    outstanding_balance = db.Column(
        db.Numeric(15, 2), default=Decimal("0.00"), nullable=False
    )
    # [ ] soft delete flag
    # deleted_at = db.Column(db.DateTime)  # Nullable

    bills = db.relationship(
        "PatientBill", back_populates="org", cascade="save-update, merge"
    )
    paid_bills = db.relationship(
        "PaidBill", back_populates="org", cascade="save-update, merge"
    )
    voided_bills = db.relationship(
        "VoidBill", back_populates="org", cascade="save-update, merge"
    )
    transactions = db.relationship(
        "Transaction", back_populates="org", cascade="save-update, merge"
    )

    serialize_rules = ("-bills.org", "-transactions.org", "-paid_bills.org")

    # Model Level Validation
    @validates("org_type")
    def validate_type(self, key, type):
        if type not in [t.value for t in OrganizationType]:
            raise ValueError(f"Invalid Organization Type: {type}")
        return type
