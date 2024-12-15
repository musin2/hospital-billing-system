from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

# [ ] MODELS
class UserRole(Enum):
    admin = "admin"
    employee = "employee"

class BillType(Enum):
    medical = 'Medical'
    surgical = 'Surgical'

class OrganizationType(Enum):
    insurance = 'Insurance Company'
    association = 'Association'
    corporation = 'Company / Corporation'

class User(SerializerMixin):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable = False)
    user_role = db.Column(db.Enum(UserRole), nullable = False)
    email = db.Column(db.String(255), nullable = False, unique = True)
    password = db.Column(db.String(200), nullable = False)

class PatientBill(SerializerMixin):
    __tablename__ = 'patient_bills'

    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(255), nullable = False)
    bill_date = db.Column(db.DateTime, nullable = False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    bill_type = db.Column(db.Enum(BillType), nullable = False)
    amount = db.Column (db.Integer)
    created_at = db.Column(db.DateTime, default = datetime.now().astimezone())
    updated_at = db.Column(db.Datetime)

class Organization(SerializerMixin):
    __tablename__ = 'organizations'

    org_id = db.Column(db.Integer, primary_key = True)
    org_name = db.Column(db.String(255), nullable = False)
    org_type = db.Column(db.Enum(OrganizationType), nullable = False)

# [ ] RELATIONSHIPS