from ..extensions import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.sql import func


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
allowed_audit_tables = ("users", "patient_bills", "transactions", "organizations")

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
    # [x] Model Level Validation

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