from flask import Flask, request, make_response
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, User, PatientBill, Organization, AuditLog, Adjustment, PaidBill, VoidBill
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

# Function that validates the object passed from the validation decorator 
def check_record(object):
    if object is None:
        return make_response({"error":"Record not found"},404)
    if not isinstance(object,(Organization,User,Transaction,AuditLog,PatientBill,Adjustment,PaidBill,VoidBill)):
        return make_response({"error":"Invalid record type"},404)
    # Check if record is voided
    if hasattr(object,"voided_at") and object.voided_at is not None:
        return make_response({"error":"Record is  invalid (void)"},400)
    return None

# Decorator function for validation when looking up records with URL parameter
def validation(funct):
    @wraps(funct)
    def wrapper(*args,**kwargs):
        id = kwargs.get('id')
        table = kwargs.get('table')
        record = None
        
        if id is None or not isinstance(id, int) or id < 0:
            return make_response({"error":f"Invalid {table} ID"},400)
        
        if table == "Organization":
            record =  Organization.query.filter_by(org_id = id).first()	
        elif table == "User":
            record = User.query.filter_by(user_id = id).first()
        elif table == "Transaction":
            record = Transaction.query.filter_by(transaction_id = id).first()
        elif table == "AuditLog":
            record = AuditLog.query.filter_by(log_id = id).first()
        elif table == "PatientBill":
            record = PatientBill.query.filter_by(bill_id = id).first()
        elif table == "Adjustment":
            record = Adjustment.query.filter_by(adjustment_id = id).first()
        elif table == "PaidBill":
            record = PaidBill.query.filter_by(bill_id = id).first()
        elif table == "VoidBill":
            record = VoidBill.query.filter_by(bill_id = id).first()
        else:
            return make_response({"error":"Invalid Table"},400)
        error_response = check_record(record)
		
        if error_response:
            return error_response
        kwargs['record'] = record
        return funct(*args, **kwargs)
    return wrapper


# [x] Modify functions that use validation decorator with table_name & all url parameters = id
# Get, Patch, & Delete a specific user
class UserAPI(Resource):

    @validation
    def get(self, id, record, table = "User"):
        try:
            return make_response(record.to_dict(), 200)

        except Exception as e:
            # Return error message if something goes wrong
            return make_response({"error": str(e)}, 500)
        
    # [ ] Fill AuditLog table before applying the changes
    # [ ] Check dynamic setting of attributes (is appropriate / secure ?)
    @validation
    def patch(self, id, record, table = "User"):
        try:
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
            
            allowed_fields = ("user_name","user_role", "email", "password")


            for attribute in updated_user:
                if attribute not in allowed_fields:
                    return make_response({"error":f"Cannot update User's '{attribute}'"},403)
                # Check if attribute exists in the user instance
                if hasattr(record, attribute):
                    # Dynamically set 'user' instance attributes
                    # [ ] Check if hashing code is accurate
                    if attribute == "password":
                        updated_user[attribute] = generate_password_hash(attribute,method="pbkdf2:sha256")
                    # if attribute == "user_role":
                    #   
                    setattr(record, attribute, updated_user[attribute])
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
    def delete(self, id, record, table = "User"):
        try:
            db.session.delete(record)
            db.session.commit()
            return make_response({"message": "User deleted successfully"}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)

api.add_resource(UserAPI, "/user/<int:id>")


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
            #[ ] Validate data type for each field
            required_fields = ["user_name", "user_role", "email", "password"]
            for field in required_fields:
                if field not in new_user_data:
                    return make_response({"error": f"Missing data: {field}"}, 400)
                
            # Validate password length
            if len(new_user_data["password"]) < 6:
                return make_response({"error":"Password must be more than 6 characters long"},400)
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
            print(bill_type)
            print(patient_gender)
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

# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# Patch, delete & get individual bill using id parameter
class Bill(Resource):

    # [x] Updated at => func.now() - database level
    # [ ] void billl ->  Move Bill to VoidBill , fill adjustments / AuditLog table 
    # [ ] Delete voided PatientBill ?
    # Organization.outstanding_balance - void Bill amount
    # Bill is void if the wrong patient or amount was recorded
    # Bill can only be voided by an admin (controlled visibility?)
    # ** Case of previous_balance & final_balance in 'Transactions' table???? (*adjustment?)
    # [ ] Non-financial data editing
    # [ ] Fill AuditLog table before applying the changes
    # [ ] Recalculate 'Organization' outsanding_balance when org_id is changed (subtract amount from previous, add amount to new org)
    @validation
    def patch(self, id, record, table = "PatientBill"):
        pass

    @validation
    def delete(self, id, record, table = "PatientBill"):
        # [ ] Cannot Delete Bill??
        pass

    @validation
    def get(self, id, record, table = "PatientBill"):
        try:
            # [ ] Bill ID
            record = PatientBill.query.filter_by(bill_id=id).first()
            return make_response(record.to_dict(), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)


api.add_resource(Bill, "/bill/<int:id>")

# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# For duplicate / invalid bills, 
class Void(Resource):
    pass

api.add_resource(Void, "/void/<int:id>")

# Get all organizations and create a new organization (corporate client)
class Organizations(Resource):
    def get(self):
        pass

    def post(self):
        pass

api.add_resource(Organizations, "/orgs")

# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
# Get, Patch, & Delete a specific organization
class OrganizationAPI(Resource):
    
    @validation
    def get(self, id, record, table = "Organization"):
        try:
            return make_response(record.to_dict(), 200)
        except Exception as e:
            return make_response({"error": str(e)}, 500)

    # [ ] Non critical(financial) fields are editable by the admin
    # [ ] Fill AuditLog before applying the changes
    @validation
    def patch(self, id, record, table = "Organization"):
        pass

    @validation
    def delete(self, id, record, table = "Organization"):
        try:
            # [ ] Deactivate organization -> NO DELETION  (user cannot add new PatientBill for new organization)  
            # db.session.delete(org)
            # db.session.commit()
            # return make_response({"message": "Organization deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"error": str(e)}, 500)


api.add_resource(OrganizationAPI, "/org/<int:id>")

class Transactions(Resource):
    def get():
        pass

# [ ] Reversing Transaction for wrong Organization
# If a transaction is recorded incorrectly, create a reversing transaction (-ve transaction amount??)
                                         # Then create the correct transaction 
# [ ] Validate that the previous_outstanding_balance in the Transactions table matches the actual balance(outstanding_balance) at the time of the transaction
# [ ] Handle concurrency / multiple transactions on the same org
# amount - paid_amount = amount to be deducted from transaction amount
# Iterate through the unpaid bills and mark them as paid / partially_paid (FIFO - start with oldest bill)
# [ ] Deduct the transaction amount(var x) after each bill has been allocated payment until x = 0 OR all bills for that organization are paid
# [ ] What happens when transaction amount is greater than outstanding_balance and all bills are paid
        # partially pay single bill with negative (-) amount = overpay
        # sum of unpaid bills = -(overpay) 
        # outstanding_balance = -(overpay) 
# [ ] Subtract remaining_amount (amount - paid_amount) from var x
# [ ] Update paid_amount in 'PatientBill' table
# [ ] Move PateintBill to PaidBill (sequential - via date) & change bill status*** if transaction amount > or = PatientBill amount 
                                                                                    # If not, bill status = partially_paid 
# [ ] Refunds (for inaccurate / overpaid transactions)
# [ ] Update outstanding_balance in 'Organization' table (outstanding_balance - transaction_amount)
    def post():
        pass

api.add_resource(Transactions,"/transactions")

# [ ] Modify functions that use validation decorator with table_name & all url parameters = id
class Transaction(Resource):
    # [ ] Fill AuditLog Table before applying changes
    # [ ] Changing Organization_id will require reversal of previous transaction, reinstation of PaidBills, and re-allocation of PatientBills
    @validation
    def patch(self, id, record, table = "Transaction"):
        pass

    @validation
    def get(self, id, record, table = "Transaction"):
        pass

api.add_resource(Transaction,"/transaction/<int:id>")


# [ ] Adjustments (admin only feature)
# Adjustments create a record for a change in critical-fields (financial data) and apply the change
    # [ ] Recalculate outstanding_balance after PatientBill adjustment
class BillAdjustment(Resource):
    pass

# [ ] Changing transaction amount will require require PaidBills to move back to PatientBill
# [ ] Manually run code to assign payment to bills *
# Reduce complexity by only using organization table for the outstanding_balance
# Status changed to unpaid, paid_amount = 0, and payments to be re-allocated
# Recalculation of outstanding_balance
class TransactionAdjustment(Resource):
    pass



# [ ] Invoice generator


if __name__ == "__main__":
    app.run(port=5000, debug=True)  # [ ] Remove debug mode for production
