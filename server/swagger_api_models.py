from flask_restx import fields


# api = Api(app, title="Hospital Billing System API", description="API for managing the bills of patients and the organizations that represent them")
# Model for user creation
def create_user_model(namespace):
    return namespace.model(
        "User",
        {
            "user_id": fields.Integer(description="User ID"),
            "user_name": fields.String(
                required=True, description="Full name of the user"
            ),
            "user_role": fields.String(
                required=True, description="Role of the user (e.g., Admin, Clerk)"
            ),
            "email": fields.String(required=True, description="User email"),
            "password": fields.String(required=True, description="Hashed password"),
        },
    )


# Model for displaying user info
def create_user_public_model(namespace):
    return namespace.model(
        "UserPublic",
        {
            "user_id": fields.Integer(
                readonly=True, description="The unique identifier of the user"
            ),
            "user_name": fields.String(
                required=True,
                description="The full name of the user",
                min_length=1,
                max_length=255,
            ),
            "user_role": fields.String(
                required=True,
                description="The role of the user in the system (e.g., Admin, Employee)",
            ),
            "email": fields.String(
                required=True, description="The user's email address (must be unique)"
            ),
        },
    )
