from app.extensions import db
from enum import Enum
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy import CheckConstraint

class TransactionType(Enum):
    payment = "payment"
    refund = "refund"


# Transactions table (=many) - Transactions on total bill for an organization [full or partial payments]
class Transaction(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    __table_args__ = (CheckConstraint("transaction_amount >= 0", name="check_transaction_amount_positive"),)

    transaction_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(
        db.Integer, db.ForeignKey("organizations.org_id"), nullable=False
    )
    #  **
    transaction_type = db.Column(db.String(20), nullable=False)
    # outstanding_balance before the transaction
    previous_outstanding_balance = db.Column(db.Numeric(15, 2), nullable=False)
    # amount to be deducted from the outstanding balance
    transaction_amount = db.Column(
        db.Numeric(15, 2),
        nullable=False,
        info={"check_constraint": "transaction_amount >= 0"},
    )
    # outstanding_balance after the transaction
    final_balance = db.Column(db.Numeric(15, 2), nullable=False)
    receipt_url = db.Column(db.String(300), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)

    org = db.relationship(
        "Organization", back_populates="transactions", cascade="save-update, merge"
    )
    paid_bills = db.relationship(
        "PaidBill", back_populates="transaction", cascade="save-update, merge"
    )

    serialize_rules = ("-org.transactions",)

    # Model Level Validation
    @validates("transaction_type")
    def validate_type(self, key, type):
        if type not in [t.value for t in TransactionType]:
            raise ValueError(f"Invalid Transaction Type: {type}")
        return type