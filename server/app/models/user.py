from app.extensions import db
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from app.utils.enums import UserRole


# Users Table
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

    # serialize_rules = (
    #     "-logs.user",
    #     "-logs",
    #     "-adjustments",
    #     "-voids",
    #     "-password",
    # )  # Exclude user.logs & user.adjustments
    serialize_only = ("user_id","user_name","user_role","email")
