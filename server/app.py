from flask import Flask, request, make_response
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, User, PatientBill, Organization
from datetime import datetime
from dotenv import load_dotenv
from flask_migrate import Migrate

# from rich import print

app = Flask(__name__)
load_dotenv()
migrate = Migrate(app, db)

database_uri = os.getenv("DEVELOPMENT_DATABASE_URI")  # Get Database uri from .env file
if not database_uri:
    raise ValueError("The environment variable 'DEVELOPMENT_DATABASE_URI' is not set")

# [x] DATABASE URI TO BE A ENV VARIABLE

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

api = Api(app)
db.init_app(app)

# [ ] CORS

# [ ] User authentication using PYJWT


# Get, Patch, & Delete a specific user
class UserAPI(Resource):
    def get(self, u_id):
        try:
            user = User.query.filter_by(user_id = u_id).first()
            if not user:
                return make_response({"error":"User not found"}, 404)
            
            return make_response(user.to_dict(), 200)
        except Exception as e:
            return make_response({"error":str(e)},500)

    def patch(self, u_id):
        pass

    def delete(self, u_id):
        pass


api.add_resource(UserAPI, "/user<int:u_id>")


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
            data = request.get_json()                      # Retreive form data

            #Data Validation
            required_fields = ["patient_name","patient_gender","patient_age","patient_contact","bill_date","organization_id","bill_type","amount"]
            for field in required_fields:
                if field not in data:
                    return make_response({"error":f"Missing data: {field}"}, 400)

            patient_name = data["patient_name"]
            patient_gender = data["patient_gender"]
            patient_age = data["patient_age"]
            patient_contact = data["patient_contact"]
            bill_date = data["bill_date"]
            organization_id = data["organization_id"]
            bill_type = data["bill_type"]
            amount = data["amount"]
            created_at = datetime.now().astimezone()       # Set created_at to current time

            new_bill = PatientBill(
                patient_name = patient_name,
                patient_gender = patient_gender,
                patient_age = patient_age,
                patient_contact = patient_contact,
                bill_date = bill_date,
                organization_id = organization_id,
                bill_type = bill_type,
                amount = amount,
                created_at = created_at
            )

            db.session.add(new_bill)
            db.session.commit()
            response_body = {"message": "Bill created successfully!"}
            return make_response(response_body,200)

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
