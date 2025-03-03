from flask import Flask, request, make_response
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, User, PatientBill, Organization
from datetime import datetime
from dotenv import load_dotenv
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash

# from rich import print

app = Flask(__name__)
load_dotenv()
migrate = Migrate(app, db)

database_uri = os.getenv("DEVELOPMENT_DATABASE_URI")  # Get Database uri from .env file
if not database_uri:
    raise ValueError("The environment variable 'DEVELOPMENT_DATABASE_URI' is not set")

# [x] DATABASE URI TO BE A ENV VARIABLE

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

api = Api(app)
db.init_app(app)

# [ ] CORS

# [ ] User authentication using PYJWT


# Get, Patch, & Delete a specific user
class UserAPI(Resource):
    def get(self, u_id):
        try:
            if (
                u_id is None or not isinstance(u_id, int) or u_id < 0
            ):  # Validate url parameter (user id)
                return make_response({"error": "Invalid User ID"}, 400)

            user = User.query.filter_by(user_id=u_id).first()
            if not user:
                return make_response({"error": "User not found"}, 404)

            return make_response(user.to_dict(), 200)

        except Exception as e:
            return make_response(
                {"error": str(e)}, 500
            )  # Return error message if something goes wrong

    def patch(self, u_id):
        try:
            if u_id is None or not isinstance(u_id, int) or u_id < 0:
                return make_response({"error": "Invalid User ID"}, 400)

            user = User.query.filter_by(user_id=u_id).first()
            if not user:
                return make_response({"error": "User not found"}, 404)

            updated_user = request.get_json()  # Get Json data from the request
            # Validate JSON data
            if (
                updated_user is None
                or not isinstance(updated_user, dict)
                or not updated_user
            ):
                return make_response({"error": "Invalid JSON data"}, 400)

            for attribute in updated_user:
                if hasattr(
                    user, attribute
                ):  # Check if attribute exists in the user instance
                    setattr(
                        user, attribute, updated_user[attribute]
                    )  # Dynamically set 'user' instance attributes
                else:
                    return make_response(
                        {"error": f"Attribute '{attribute}' not found"}, 400
                    )
            db.session.commit()  # Commit changes to the database
            return make_response({"message": "User updated successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)

    def delete(self, u_id):
        try:
            if u_id is None or not isinstance(u_id, int) or u_id < 0:
                return make_response({"error": "Invalid User ID"}, 400)

            user = User.query.filter_by(user_id=u_id).first()
            if not user:
                return make_response({"error": "User not found"}, 404)

            db.session.delete(user)
            db.session.commit()
            return make_response({"message": "User deleted successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


api.add_resource(UserAPI, "/user<int:u_id>")


# Create new user
class NewUser(Resource):
    def post(self):
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
            required_fields = ["user_name", "user_role", "email", "password"]
            for field in required_fields:
                if field not in new_user_data:
                    return make_response({"error": f"Missing data: {field}"}, 400)

            # Generate password hash
            hashed_password = generate_password_hash(
                new_user_data["password"], method="pbkdf2:sha256"
            )
            user = User(
                user_name=new_user_data["user_name"],
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


api.add_resource(NewUser, "/user")


# Get all bills & create a new bill
class Bills(Resource):
    # Get all bills
    def get(self):
        try:
            bills = PatientBill.query.all()

            if not bills:
                return make_response({"message": "Bills not found"}, 404)
            return make_response([bill.to_dict() for bill in bills], 200)

        except Exception as e:
            return make_response(
                {"error": str(e)}, 500
            )  # Return error message with status code 500 if something goes wrong

    # Create a new bill
    def post(self):
        try:
            data = request.get_json()  # Retreive form data

            # Data Validation
            required_fields = [
                "patient_id",
                "patient_name",
                "patient_gender",
                "patient_age",
                "patient_contact",
                "bill_date",
                "organization_id",
                "bill_type",
                "amount",
            ]
            for field in required_fields:
                if field not in data:
                    return make_response({"error": f"Missing data: {field}"}, 400)

            patient_id = data["patient_id"]
            patient_name = data["patient_name"]
            patient_gender = data["patient_gender"]
            patient_age = data["patient_age"]
            patient_contact = data["patient_contact"]
            bill_date = data["bill_date"]
            organization_id = data["organization_id"]
            bill_type = data["bill_type"]
            amount = data["amount"]
            created_at = datetime.now().astimezone()  # Set created_at to current time

            new_bill = PatientBill(
                patient_id=patient_id,
                patient_name=patient_name,
                patient_gender=patient_gender,
                patient_age=patient_age,
                patient_contact=patient_contact,
                bill_date=bill_date,
                organization_id=organization_id,
                bill_type=bill_type,
                amount=amount,
                created_at=created_at,
            )

            db.session.add(new_bill)
            db.session.commit()
            response_body = {"message": "Bill created successfully!"}
            return make_response(response_body, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


api.add_resource(Bills, "/bills")


# Patch, delete & get individual bill using id parameter
class Bill(Resource):
    def patch(
        self, b_id
    ):  # [ ] Updated at => get current time - datetime.now().astimezone()
        pass

    def delete(self, b_id):
        pass

    def get(self, b_id):
        pass


api.add_resource(Bill, "/bill<int:b_id>")


# Get all organizations and create a new organization (corporate client)
class Organizations(Resource):
    def get(self):
        pass

    def post(self):
        pass


api.add_resource(Organizations, "/orgs")


# Get, Patch, & Delete a specific organization
class OrganizationAPI(Resource):
    def get(self, o_id):
        pass

    def patch(self, o_id):
        pass

    def delete(self, o_id):
        pass


api.add_resource(OrganizationAPI, "/org<int:o_id>")


# [ ] Invoice generator


if __name__ == "__main__":
    app.run(port=5000, debug=True)  # [ ] Remove debug mode for production
