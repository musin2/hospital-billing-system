def serialize_bill(bill):
    rules = (
        "-org.bills",
        "-org.paid_bills",
        "-org.voided_bills",
        "-org.transactions"
    )
    return bill.to_dict(rules=rules)