from enum import Enum

class BillType(Enum):
    medical = "Medical"
    surgical = "Surgical"
    maternity = "Maternity"

class GenderOption(Enum):
    male = "Male"
    female = "Female"
    other = "Not specified"

class BillStatus(Enum):
    paid = "paid"
    unpaid = "unpaid"
    partially_paid = "partially_paid"
    void = "void"  # Errored bill (move to voided bills table then create a new one)

class OrganizationType(Enum):
    insurance = "Insurance Company"
    corporation = "Company / Corporation"

class TransactionType(Enum):
    payment = "payment"
    refund = "refund"

class UserRole(Enum):
    admin = "admin"  # can do employee tasks + make adjustments & void bills
    employee = "employee"  # can add bill, add transaction, edit non-financial data
