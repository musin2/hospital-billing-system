from ..extensions import db
from sqlalchemy.orm import validates
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

allowed_adjustment_tables = ("patient_bills", "transactions")
allowed_adjustment_columns = ("amount", "paid_amount", "transaction_amount")

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
    # [x] Model Level Validation

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