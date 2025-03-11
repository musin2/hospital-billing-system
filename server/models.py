from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()


# [x] MODELS
class UserRole(Enum):
    admin = "admin"
    employee = "employee"


class BillType(Enum):
    medical = "Medical"
    surgical = "Surgical"


class OrganizationType(Enum):
    insurance = "Insurance Company"
    corporation = "Company / Corporation"


class GenderOption(Enum):
    male = "Male"
    female = "Female"
    other = "Not specified"


class BillStatus(Enum):
    paid = "paid"
    unpaid = "unpaid"
    partially_paid = "partially_paid"


print(OrganizationType.corporation.name)
print(BillStatus.unpaid.name)


# Users table
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Enum(UserRole), nullable=False)
    # user_role = db.Column(db.Enum(UserRole), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    logs = db.relationship(
        "AuditLog", back_populates="user", cascade="save-update, merge"
    )
    adjustments = db.relationship(
        "Adjustment", back_populates="user", cascade="save-update, merge"
    )

    serialize_rules = (
        "-logs.user",
        "-logs",
        "-adjustments",
    )  # Exclude user.logs & user.adjustments


class AuditLog(db.Model, SerializerMixin):
    __tablename__ = "auditlogs"

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    # Action that was taken on the record
    action = db.Column(db.String(255), nullable=False)
    # Model name
    table_name = db.Column(db.String(255), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.String(255), nullable=False)
    new_value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship("User", back_populates="logs", cascade="save-update, merge")

    serialize_rules = ("-user.logs",)


# Bills Table (=many)
class PatientBill(db.Model, SerializerMixin):
    __tablename__ = "patient_bills"

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    patient_number = db.Column(db.String(255), nullable=False, unique=True)
    # Personal number (ID / Passport)
    patient_id = db.Column(db.Integer, nullable=False)
    patient_name = db.Column(db.String(255), nullable=False)
    patient_gender = db.Column(db.Enum(GenderOption), nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    patient_phone_number = db.Column(db.String, nullable=False)
    bill_date = db.Column(db.DateTime, nullable=False)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    bill_type = db.Column(db.Enum(BillType), nullable=False)
    amount = db.Column(db.Decimal(15, 2), nullable=False)
    status = db.Column(db.Enum(BillStatus), nullable=False)
    paid_amount = db.Column(db.Decimal(15, 2), default=Decimal("0.00"))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable
    deleted_at = db.Column(db.DateTime)

    org = db.relationship(
        "Organization", back_populates="bills", cascade="save-update, merge"
    )

    serialize_rules = ("-org.bills",)


class Adjustment(db.Model, SerializerMixin):
    __tablename__ = "adjustments"

    adjustment_id = db.Column(db.Integer, primary_key=True)
    adjusted_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    # Model name
    table_name = db.Column(db.String(255), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.String(255), nullable=False)
    new_value = db.Column(db.String(255), nullable=False)
    reason = db.Column(db.String(400), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship(
        "User", back_populates="adjustments", cascade="save-update, merge"
    )

    serialize_rules = ("-user.adjustments",)


# PatientBill after full payment (=many)
class PaidBill(db.Model, SerializerMixin):
    __tablename__ = "paid_bills"

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    patient_number = db.Column(db.String(255), nullable=False, unique=True)
    # Personal number (ID / Passport)
    patient_id = db.Column(db.Integer, nullable=False)
    patient_name = db.Column(db.String(255), nullable=False)
    patient_gender = db.Column(db.Enum(GenderOption), nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    patient_phone_number = db.Column(db.String, nullable=False)
    bill_date = db.Column(db.DateTime, nullable=False)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    bill_type = db.Column(db.Enum(BillType), nullable=False)
    amount = db.Column(db.Decimal(15, 2), nullable=False)
    status = db.Column(db.Enum(BillStatus), nullable=False)
    paid_amount = db.Column(db.Decimal(15, 2), default=Decimal("0.00"))
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

    serialize_rules = ("-org.bills",)


# Transactions table (=many) - Transactions on total bill for an organization [full or partial payments]
#  [ ] Transactions table
class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    # outstanding_balance before the transaction
    previous_outstanding_balance = db.Column(db.Decimal(15, 2), nullable=False)
    # amount to be deducted from the outstanding balance
    transaction_amount = db.Column(db.Decimal(15, 2), nullable=False)
    # outstanding_balance after the transaction
    final_balance = db.Column(db.Decimal(15, 2), nullable=False)
    receipt_url = db.Column(db.String(300), nullable=False)
    transaction_date = db.Column(db.DateTime, nullable=False)

    org = db.relationship(
        "Organization", back_populates="transactions", cascade="save-update, merge"
    )

    serialize_rules = ("-org.transactions",)


# Organization Table (-one)
class Organization(db.Model, SerializerMixin):
    __tablename__ = "organizations"

    org_id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(255), nullable=False)
    org_email = db.Column(db.String(255), nullable=False, unique=True)
    org_phone_number = db.Column(db.String(255), nullable=False, unique=True)
    org_type = db.Column(db.Enum(OrganizationType), nullable=False)
    outstanding_balance = db.Column(db.Decimal(15, 2), default=Decimal("0.00"))
    # [ ] soft delete flag
    deleted_at = db.Column(db.DateTime)  # Nullable

    bills = db.relationship(
        "PatientBill", back_populates="org", cascade="save-update, merge"
    )
    paid_bills = db.relationship(
        "PaidBill", back_populates="org", cascade="save-update, merge"
    )
    transactions = db.relationship(
        "Transaction", back_populates="org", cascade="save-update, merge"
    )

    serialize_rules = ("-bills.org", "-transactions.org", "-paid_bills.org")


# [x] RELATIONSHIPS
