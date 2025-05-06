from flask import make_response,request
from app.extensions import db
from app.utils.validation import validate_email,validate_password
from werkzeug.security import generate_password_hash
from app.models.user import User

def get_user_by_id(id,record):
    try:
            return make_response(record.to_dict(), 200)

    except Exception as e:
            # Return error message if something goes wrong
            return make_response({"error": str(e)}, 500)
    
def create_new_user():
        try:
            new_user_data = request.get_json()
            # Validate JSON data
            if (
                new_user_data is None
                or not new_user_data
                or not isinstance(new_user_data, dict)
            ):
                return make_response({"error": "Invalid JSON data"}, 400)
            # Validate user data
            # [ ] Validate data type for each field
            required_fields = ["user_name", "user_role", "email", "password"]
            for field in required_fields:
                if field not in new_user_data:
                    return make_response({"error": f"Missing data: {field}"}, 400)

            # Validate password
            is_password_valid, password_errors = validate_password(
                new_user_data["password"]
            )
            if not is_password_valid:
                return make_response({"error": password_errors}, 400)
            # Password validation returns a list of errors => error[]

            # Validate email
            is_email_valid, email_errors = validate_email(new_user_data["email"])
            if not is_email_valid:
                return make_response({"error": email_errors}, 400)

            # Generate password hash
            hashed_password = generate_password_hash(
                new_user_data["password"], method="pbkdf2:sha256"
            )
            user = User(
                user_name=new_user_data["user_name"],  # Raises KeyError if missing
                user_role=new_user_data["user_role"],
                email=new_user_data["email"],
                # [x] Hash the password first
                # [ ] Validate password client side? (frontend): length, characters, etc
                password=hashed_password,
            )

            db.session.add(user)
            db.session.commit()
            return make_response({"message": "User created successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)
