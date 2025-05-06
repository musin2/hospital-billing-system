from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
# from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
api = Api(
    title="Hospital Billing System API",
    description="API for managing the bills of patients and the organizations that represent them",
)
# [ ] CORS
# cors = CORS()
