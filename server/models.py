from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, CheckConstraint
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


allowed_audit_tables = ("users", "patient_bills", "transactions", "organizations")
allowed_adjustment_tables = ("patient_bills", "transactions")
restricted_auditlog_columns = (
    "user_id",
    "bill_id",
    "amount",
    "status",
    "paid_amount",
    "created_at",
    "updated_at",
    "transaction_id",
    "previous_outstanding_balance",
    "transaction_amount",
    "final_balance",
    "org_id",
    "outstanding_balance",
)
allowed_adjustment_columns = ("amount", "paid_amount", "transaction_amount")

print(OrganizationType.corporation.name)
print(BillStatus.unpaid.name)


# Users table
# [ ] Confirm if columns are complete
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.String(15), nullable=False)
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

    @validates("user_role")
    def validate_user_role(self, key, user_role):
        if user_role not in [
            r.value for r in UserRole
        ]:  # Checks value of user_role column against the values in the Enum(UserRole)
            raise ValueError(f"Invalid Role: {user_role}")
        return user_role

    serialize_rules = (
        "-logs.user",
        "-logs",
        "-adjustments",
    )  # Exclude user.logs & user.adjustments


# @event.listens_for(User, 'before_insert')
# @event.listens_for(User, 'before_update')
# def validate_user_role(mapper, connection, target):
#     if target.user_role not in [g.value for g in UserRole]:     #Checks value of user_role column against the values in the Enum(UserRole)
#         raise ValueError(f"Invalid Role: {target.user_role}")


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
    # [ ] Edited values are Integers / Numeric
    new_value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship("User", back_populates="logs", cascade="save-update, merge")
    # [ ] Model Level Validation

    serialize_rules = ("-user.logs",)

    @validates("table_name")
    def validate_tablename(self, key, table_name):
        if table_name not in allowed_audit_tables:
            raise ValueError(f"Invalid table name: {table_name}")
        return table_name

    @validates("column_name")
    def validate_column_name(self, key, column_name):
        if column_name in restricted_auditlog_columns:
            raise ValueError(f"This column can not be edited: {column_name}")
        return column_name


# Bills Table (=many)
class PatientBill(db.Model, SerializerMixin):
    __tablename__ = "patient_bills"

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    patient_number = db.Column(db.String(50), nullable=False, unique=True)
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
        info={"check_constraint": "paid_amount >= 0"},
    )
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(
        db.DateTime, default=func.now(), onupdate=func.now()
    )  # Nullable

    org = db.relationship(
        "Organization", back_populates="bills", cascade="save-update, merge"
    )
    # [ ] Model Level Validation

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


# Tracks edits made to financial data by admins
class Adjustment(db.Model, SerializerMixin):
    __tablename__ = "adjustments"

    adjustment_id = db.Column(db.Integer, primary_key=True)
    adjusted_by = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    # Model name
    table_name = db.Column(db.String(255), nullable=False)
    column_name = db.Column(db.String(255), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    # Adjustments are only for financial data (numbers)
    old_value = db.Column(db.Numeric(15, 2), nullable=False)
    new_value = db.Column(db.Numeric(15, 2), nullable=False)
    reason = db.Column(db.String(400), nullable=False)
    timestamp = db.Column(db.DateTime, default=func.now())

    user = db.relationship(
        "User", back_populates="adjustments", cascade="save-update, merge"
    )
    # [ ] Model Level Validation

    serialize_rules = ("-user.adjustments",)

    @validates("table_name")
    def validate_table(self, key, table):
        if table not in allowed_adjustment_tables:
            raise ValueError(f"Invalid Table Name: {table}")
        return table

    @validates("column_name")
    def validate_column(self, key, column):
        if column not in allowed_adjustment_columns:
            raise ValueError(f"Cannot adjust column: {column}")


# PatientBill after full payment (=many)
class PaidBill(db.Model, SerializerMixin):
    __tablename__ = "paid_bills"

    bill_id = db.Column(db.Integer, primary_key=True)
    # Inpatient / Outpatient number
    patient_number = db.Column(db.String(50), nullable=False, unique=True)
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


# Errenous bills that have been voided
class VoidBill(db.Model, SerializerMixin):
    __tablename__ = "void_bills"

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
        info={"check_constraint": "paid_amount >= 0"},
    )
    # transaction_id should be nullable in the case where a bill is not fully paid
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"))
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
    previous_outstanding_balance = db.Column(db.Numeric(15, 2), nullable=False)
    # amount to be deducted from the outstanding balance
    transaction_amount = db.Column(
        db.Numeric(15, 2), nullable=False, info={"check_constraint": "amount >= 0"}
    )
    # outstanding_balance after the transaction
    final_balance = db.Column(db.Numeric(15, 2), nullable=False)
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
    outstanding_balance = db.Column(db.Numeric(15, 2), default=Decimal("0.00"))
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
