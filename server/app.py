from flask import Flask, request, make_response
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, User, PatientBill, Organization
from datetime import datetime
from dotenv import load_dotenv
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from functools import wraps

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
    # Decorator funcion for validation
    def validation(funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            # Get u_id from kwargs
            u_id = kwargs.get("u_id")
            # Validate url parameter (user id)
            if u_id is None or not isinstance(u_id, int) or u_id < 0:
                return make_response({"error": "Invalid User ID"}, 400)

            user = User.query.filter_by(user_id=u_id).first()
            if not user:
                return make_response({"error": "User not found"}, 404)
            # Pass user object to the decorated function
            kwargs["user"] = user
            return funct(*args, **kwargs)

        return wrapper

    @validation
    def get(self, u_id, user):
        try:
            return make_response(user.to_dict(), 200)

        except Exception as e:
            # Return error message if something goes wrong
            return make_response({"error": str(e)}, 500)
    # [ ] Fill AuditLog table before applying the changes
    # [ ] Check dynamic setting of attributes (is appropriate / secure ?)
    @validation
    def patch(self, u_id, user):
        try:
            updated_user = request.get_json()  # Get Json data from the request
            # Validate JSON data
            if (
                updated_user is None
                or not isinstance(updated_user, dict)
                or not updated_user
            ):
                return make_response({"error": "Invalid JSON data"}, 400)

            for attribute in updated_user:
                # Check if attribute exists in the user instance
                if hasattr(user, attribute):
                    # Dynamically set 'user' instance attributes
                    setattr(user, attribute, updated_user[attribute])
                else:
                    return make_response(
                        {"error": f"Attribute '{attribute}' not found"}, 400
                    )
            db.session.commit()  # Commit changes to the database
            return make_response({"message": "User updated successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)

    @validation
    def delete(self, u_id, user):
        try:
            db.session.delete(user)
            db.session.commit()
            return make_response({"message": "User deleted successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


api.add_resource(UserAPI, "/user/<int:u_id>")


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
            # Filter for soft-deletion
            bills = PatientBill.query.all()

            if not bills:
                return make_response({"message": "Bills not found"}, 404)
            return make_response([bill.to_dict() for bill in bills], 200)

        except Exception as e:
            # Return error message with status code 500 if something goes wrong
            return make_response({"error": str(e)}, 500)

    # Create a new bill
    def post(self):
        try:
            data = request.get_json()  # Retreive form data

            # Data Validation
            required_fields = [
                "patient_number",
                "patient_id",
                "patient_name",
                "patient_gender",
                "patient_age",
                "patient_phone_number",
                "bill_date",
                "organization_id",
                "bill_type",
                "amount",
            ]
            # [ ] additional validation in database ? with column data types
            for field in required_fields:
                if field not in data:
                    return make_response({"error": f"Missing data: {field}"}, 400)

            patient_number = data["patient_number"]
            patient_id = data["patient_id"]
            patient_name = data["patient_name"]
            patient_gender = data["patient_gender"]
            patient_age = data["patient_age"]
            patient_phone_number = data["patient_phone_number"]
            bill_date = data["bill_date"]
            organization_id = data["organization_id"]
            bill_type = data["bill_type"]
            amount = data["amount"]
            created_at = datetime.now().astimezone()  # Set created_at to current time

            new_bill = PatientBill(
                patient_number=patient_number,
                patient_id=patient_id,
                patient_name=patient_name,
                patient_gender=patient_gender,
                patient_age=patient_age,
                patient_phone_number=patient_phone_number,
                bill_date=bill_date,
                organization_id=organization_id,
                bill_type=bill_type,
                amount=amount,
                created_at=created_at,
            )
            # [ ] update outstanding_balance in 'Organization' table
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
    def validation(funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            b_id = kwargs.get("b_id")

            if b_id is None or not isinstance(b_id, str) or b_id < 0:
                return make_response({"error": "Invalid Bill ID"}, 400)

            bill = PatientBill.query.filter_by(bill_id=b_id).first()
            # [ ] Check if bill is soft_deleted
            if not bill:
                return make_response({"error": "Bill not found"}, 404)

            kwargs["bill"] = bill

            return funct(*args, **kwargs)

        return wrapper

    # [x] Updated at => func.now() - database level
    # [ ] void billl ->  Move Bill to VoidBill , fill adjustments / AuditLog table 
    # [ ] Delete voided PatientBill ?
    # Organization.outstanding_balance - void Bill amount
    # Bill is void if the wrong patient or amount was recorded
    # Bill can only be voided by an admin (controlled visibility?)
    # ** Case of previous_balance & final_balance in 'Transactions' table???? (*adjustment?)
    # [ ] Non-financial data editing
    # [ ] Fill AuditLog table before applying the changes
    def patch(self, b_id, bill):
        pass

    def delete(self, b_id, bill):
        # [ ] Cannot Delete Bill??
        pass

    @validation
    def get(self, b_id, bill):
        try:
            # [ ] Bill ID
            bill = PatientBill.query.filter_by(bill_id=b_id).first()
            return make_response(bill.to_dict(), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


api.add_resource(Bill, "/bill/<int:b_id>")


# Get all organizations and create a new organization (corporate client)
class Organizations(Resource):
    def get(self):
        pass

    def post(self):
        pass


api.add_resource(Organizations, "/orgs")


# Get, Patch, & Delete a specific organization
class OrganizationAPI(Resource):
    # Validation decorator
    def validation(funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            o_id = kwargs.get("o_id")
            if o_id is None or not isinstance(o_id, int) or o_id < 0:
                return make_response({"error": "Invalid Organization ID"}, 400)

            org = Organization.query.filter_by(org_id=o_id).first()
            if not org:
                return make_response({"error": "Organization not found"}, 404)

            # Pass org object to the decorated function
            kwargs["org"] = org
            return funct(*args, **kwargs)

        return wrapper

    @validation
    def get(self, o_id, org):
        try:
            return make_response(org.to_dict(), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    # [ ] Non critical(financial) fields are editable by the admin
    # [ ] Fill AuditLog before applying the changes
    @validation
    def patch(self, o_id, org):
        pass

    @validation
    def delete(self, o_id, org):
        try:
            # [ ] Deactivate organization -> NO DELETION  (user cannot add new PatientBill for new organization)  
            # db.session.delete(org)
            # db.session.commit()
            # return make_response({"message": "Organization deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


api.add_resource(OrganizationAPI, "/org/<int:o_id>")

class Transactions(Resource):
    def get():
        pass

# [ ] Reversing Transaction for wrong Organization
# If a transaction is recorded incorrectly, create a reversing transaction (-ve transaction amount??)
# [ ] Validate that the previous_outstanding_balance in the Transactions table matches the actual balance(outstanding_balance) at the time of the transaction
# [ ] Handle concurrency / multiple transactions on the same org
# Iterate through the unpaid bills and mark them as paid / partially_paid (FIFO - start with oldest bill)
# [ ] Deduct the transaction amount(var x) after each bill has been allocated payment until x = 0 OR all bills for that organization are paid
# [ ] Subtract remaining_amount (amount - paid_amount) from var x
# [ ] Update paid_amount in 'PatientBill' table
# [ ] Move PateintBill to PaidBill (sequential - via date) & change bill status*** if transaction amount > or = PatientBill amount 
                                                                                    # If not, bill status = partially_paid 
# [ ] Refunds (for inaccurate / overpaid transactions)
# [ ] Update outstanding_balance in 'Organization' table (outstanding_balance - transaction_amount)
    def post():
        pass

api.add_resource(Transactions,"/transactions")

class Transaction(Resource):
    # [ ] Fill AuditLog Table before applying changes
    # [ ] Changing Organization_id will require reversal of previous transaction, reinstation of PaidBills, and re-allocation of PatientBills
    def patch():
        pass

    def get():
        pass

api.add_resource(Transaction,"/transaction/<int:id>")


# [ ] Adjustments (admin only feature)
# Adjustments create a record for a change in critical-fields (financial data) and apply the change
    # [ ] Recalculate outstanding_balance after PatientBill adjustment
class BillAdjustment(Resource):
    pass

# [ ] Changing transaction amount will require require PaidBills to move back to PatientBill
# Status changed to unpaid, paid_amount = 0, and payments to be re-allocated
# Recalculation of outstanding_balance
class TransactionAdjustment(Resource):
    pass



# [ ] Invoice generator


if __name__ == "__main__":
    app.run(port=5000, debug=True)  # [ ] Remove debug mode for production
