from enum import Enum
from flask_sqlalchemy import SQLAlchemy
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


print(OrganizationType.corporation.name)


# Users table
class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_role = db.Column(db.Enum(UserRole), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)


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
    patient_contact = db.Column(db.String, nullable=False)
    bill_date = db.Column(db.DateTime, nullable=False)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    bill_type = db.Column(db.Enum(BillType), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now().astimezone())
    updated_at = db.Column(db.DateTime)

    org = db.relationship("Organization", back_populates="bills", cascade="all")

    serialize_rules = ("-org.bills",)

# Transactions table (=many) - Transactions on total bill for an organization [full or partial payments]
#  [ ] Transactions table
class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"


# Organization Table (-one)
class Organization(db.Model, SerializerMixin):
    __tablename__ = "organizations"

    org_id = db.Column(db.Integer, primary_key=True)
    org_name = db.Column(db.String(255), nullable=False)
    org_email = db.Column(db.String(255), nullable=False, unique=True)
    org_phone_number = db.Column(db.String(255), nullable=False, unique=True)
    org_type = db.Column(db.Enum(OrganizationType), nullable=False)
    outstanding_balance = db.Column(db.Decimal(15, 2), default=Decimal("0.00"))

    bills = db.relationship(
        "PatientBill", back_populates="org", cascade="all, delete-orphan"
    )

    serialize_rules = ("-bills.org",)


# [x] RELATIONSHIPS
