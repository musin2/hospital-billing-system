from app.utils import validate_record
from flask_restx import Resource

class Transactions(Resource):
    def get():
        pass

    def post():
        pass

api.add_resource(Transactions, "/transactions") 

class Transaction(Resource):
    # [ ] Fill AuditLog Table before applying changes
    # [ ] Changing Organization_id will require reversal of previous transaction, reinstation of PaidBills, and re-allocation of PatientBills
    @validate_record
    def patch(self, id, record, table="Transaction"):
        pass

    @validate_record
    def get(self, id, record, table="Transaction"):
        pass


api.add_resource(Transaction, "/transaction/<int:id>")