from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.orm import validates
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from decimal import Decimal

db = SQLAlchemy()


class UserRole(Enum):
    admin = "admin"  # can do employee tasks + make adjustments & void bills
    employee = "employee"  # can add bill, add transaction, edit non-financial data


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
    void = "void"  # Errored bill (move to voided bills table then create a new one)


class TransactionType(Enum):
    payment = "payment"
    refund = "refund"


print(OrganizationType.corporation.name)
print(BillStatus.unpaid.name)


# Users table
# [ ] Confirm if columns are complete
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Enum(UserRole), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)

    logs = db.relationship(
        "AuditLog", back_populates="user", cascade="save-update, merge"
    )
    adjustments = db.relationship(
        "Adjustment", back_populates="user", cascade="save-update, merge"
    )
    voids = db.relationship(
        "VoidBill", back_populates="user", cascade="save-update, merge"
    )

    # [ ] Model Level Validation
    @validates("email")
    def validate_email(self, key, email):
        if "@" not in email:
            raise ValueError("Invalid email address")
        return email
    
    # @validates("user_role")
    # def validate_role(self, key, user_role):
    #     if not isinstance(user_role,UserRole):
    #         raise ValueError("Invalid role")
    #     return user_role

    @validates("user_name")
    def validate_name(self, key, name):
        if not isinstance(name,str) or name is None:
            raise ValueError("Invalid Username: must be a string")

    serialize_rules = (
        "-logs.user",
        "-logs",
        "-adjustments",
    )  # Exclude user.logs & user.adjustments

# Tracks edits made to non-financial data
class AuditLog(db.Model, SerializerMixin):
    __tablename__ = "auditlogs"

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    # Action that was taken on the record (**EDIT ONLY)
    # action = db.Column(db.String(255), nullable=False)
    # Model name
    table_name = db.Column(db.String(255), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    old_value = db.Column(db.String(255), nullable=False)
    new_value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship("User", back_populates="logs", cascade="save-update, merge")
    # [ ] Model Level Validation

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
    # amount can only be adjusted by Admin
    amount = db.Column(db.Decimal(15, 2), nullable=False)
    # Status can not be edited
    status = db.Column(db.Enum(BillStatus), nullable=False)
    # paid_amount = amount in the case of complete payment; otherwise, it is partail payment
    paid_amount = db.Column(db.Decimal(15, 2), default=Decimal("0.00"))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable

    org = db.relationship(
        "Organization", back_populates="bills", cascade="save-update, merge"
    )
    # [ ] Model Level Validation

    serialize_rules = ("-org.bills",)

# Tracks edits made to financial data by admins
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
    # [ ] Model Level Validation

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


# Errenous bills that have been voided
class VoidBill(db.Model, SerializerMixin):
    __tablename__ = "paid_bills"

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    voided_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
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
    # [ ] Set voided timestamp when bill status = void
    voided_at = db.Column(db.DateTime)

    org = db.relationship(
        "Organization", back_populates="paid_bills", cascade="save-update, merge"
    )
    user = db.relationship("User", back_populates="voids", cascade="save-update, merge")

    serialize_rules = ("-org.bills",)


# Transactions table (=many) - Transactions on total bill for an organization [full or partial payments]
#  [x] Transactions table
class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    #  **
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
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
    paid_bills = db.relationship(
        "PaidBill", back_populates="transaction", cascade="save-update, merge"
    )
    # [ ] Model Level Validation

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
    # deleted_at = db.Column(db.DateTime)  # Nullable

    bills = db.relationship(
        "PatientBill", back_populates="org", cascade="save-update, merge"
    )
    paid_bills = db.relationship(
        "PaidBill", back_populates="org", cascade="save-update, merge"
    )
    transactions = db.relationship(
        "Transaction", back_populates="org", cascade="save-update, merge"
    )
    # [ ] Model Level Validation

    serialize_rules = ("-bills.org", "-transactions.org", "-paid_bills.org")


# [x] RELATIONSHIPS
