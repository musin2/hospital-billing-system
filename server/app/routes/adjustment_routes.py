from flask_restx import Resource

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
# [ ] Use previous_outstanding_balance(uneditable / static) and adjusted transaction_amount to set final_balance
class TransactionAdjustment(Resource):
    pass