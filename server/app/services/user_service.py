from flask import make_response,request
from flask_restx import marshal
from app.extensions import db
from app.utils.validation import validate_email,validate_password
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.api_models.user_models import user_model

def get_user_by_id(record):
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
                # [x] Validate password server side? (frontend): length, characters, etc
                password=hashed_password,
            )

            db.session.add(user)
            db.session.commit()
            user_data = marshal(user.to_dict(), user_model)
            return make_response({"message": "User created successfully", "user": user_data}, 201)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)

def update_user_data(record):
        try:
            if record is None:
                 return make_response({"error":"User not found"}, 404)
            # [ ] Admin only edits - all
            # [ ] Check if current user is an admin
            # If not, return an error message
            updated_user = request.get_json()  # Get Json data from the request
            # Validate JSON data
            if (
                updated_user is None
                or not isinstance(updated_user, dict)
                or not updated_user
            ):
                return make_response({"error": "Invalid JSON data"}, 400)

            allowed_fields = ("user_name", "user_role", "email", "password")

            for attribute in updated_user:
                if attribute not in allowed_fields:
                    return make_response(
                        {"error": f"Cannot update User's '{attribute}'"}, 403
                    )
                # Check if attribute exists in the user instance
                if hasattr(record, attribute):
                    # Dynamically set 'user' instance attributes
                    if attribute == "password":
                        is_password_valid, password_errors = validate_password(
                            updated_user[attribute]
                        )
                        if not is_password_valid:
                            return make_response(
                                {"error": password_errors}, 400
                            )  # Returns a ***list*** of errors
                        updated_user[attribute] = generate_password_hash(
                            updated_user[attribute], method="pbkdf2:sha256"
                        )
                    if attribute == "email":
                        is_email_valid, email_errors = validate_email(
                            updated_user[attribute]
                        )
                        if not is_email_valid:
                            return make_response({"error": email_errors}, 400)
                    # [x] validate if user_role is in the enum

                    setattr(record, attribute, updated_user[attribute])
                else:
                    return make_response(
                        {"error": f"Attribute '{attribute}' not found"}, 400
                    )
            db.session.commit()  # Commit changes to the database
            user_data = marshal(record,user_model)    
            return make_response({"message": "User updated successfully","user":user_data}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)
        
def delete_user(record):
    try:
        user_data = record.to_dict()
        db.session.delete(record)
        db.session.commit()
        return make_response({"message": "User deleted successfully","user":user_data}, 200)

    except Exception as e:
        db.session.rollback()
        return make_response({"error": str(e)}, 500)
    
def get_all_users():
    try:
        users = User.query.all()
        if not users:
            return make_response({"error": "Users not found"}, 404)
        
        response_body = [user.to_dict() for user in users]
        return make_response({"users": response_body},200)

    except Exception as e:
        return make_response({"error":str(e)},500)