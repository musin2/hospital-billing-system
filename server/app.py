from flask import Flask, request
from flask_restx import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import os
from models import db
from datetime import datetime

app = Flask(__name__)
# database_uri = os.getenv("DEVELOPMENT_DATABASE_URI")
# print(database_uri)

# if not database_uri:
#     raise ValueError("The environment variable 'DEVELOPMENT_DATABASE_URI' is not set")

# FIXME DATABASE URI TO BE A ENV VARIABLE
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgress@localhost:5432/hbs_db'

api = Api(app)
db.init_app(app)

# [ ] User authentication using PYJWT
@api.route("/bills")
class Bills(Resource):
    def get(self):
        return {"message": "Bills"}

# [ ] Invoice generator



if __name__ == '__main__':
    app.run(port=5000, debug=True)



































































    # if not database_uri: