from flask import Flask, request, make_response
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db, User, PatientBill, Organization
from datetime import datetime
from dotenv import load_dotenv
from flask_migrate import Migrate

app = Flask(__name__)
load_dotenv()
migrate = Migrate(app, db)
database_uri = os.getenv("DEVELOPMENT_DATABASE_URI")
print(database_uri)

if not database_uri:
    raise ValueError("The environment variable 'DEVELOPMENT_DATABASE_URI' is not set")

# [x] DATABASE URI TO BE A ENV VARIABLE

app.config["SQLALCHEMY_DATABASE_URI"] = database_uri

api = Api(app)
db.init_app(app)

# [ ] User authentication using PYJWT


class Bills(Resource):
    def get(self):
        try:
            with app.app_context():
                bills = PatientBill.query.all()

            if not bills:
                return make_response({"message": "Bills not found"}, 404)
            return make_response([bill.to_dict() for bill in bills], 200)

        except Exception as e:
            return {
                "error": str(e)
            }, 500  # Return error message with status code 500 if something goes wrong


api.add_resource(Bills, "/bills")


# [ ] Invoice generator


if __name__ == "__main__":
    app.run(port=5000, debug=True)
