from werkzeug.security import generate_password_hash
from models import (
    db,
    User,
    PatientBill,
    Organization,
    PaidBill,
    Transaction,
    VoidBill,
    Adjustment,
    AuditLog,
    UserRole,
    BillType,
    OrganizationType,
    GenderOption,
    BillStatus,
    TransactionType,
)
from datetime import datetime, date
from decimal import Decimal
from app import app

def seed_data():
    with app.app_context():
        try:
            print("Deleting table data...")
            # Clear tables in proper order to avoid foreign key conflicts
            tables = [
                VoidBill,
                PaidBill,
                Transaction,
                PatientBill,
                Adjustment,
                AuditLog,
                User,
                Organization,
            ]
            for table in tables:
                db.session.query(table).delete()
            db.session.commit()
            print("Tables cleared successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing tables: {str(e)}")
            return

        try:
            # Seed Users
            user1 = User(
                user_name="muhsin",
                user_role=UserRole.admin.value,
                email="muhsin@gmail.com",
                password=generate_password_hash("muhsin@123"),
            )
            user2 = User(
                user_name="wanjiku",
                user_role=UserRole.employee.value,
                email="wanjiku@gmail.com",
                password=generate_password_hash("wanjiku@123"),
            )

            db.session.add_all([user1, user2])
            db.session.commit()
            print("Users added successfully")

            # Seed Organizations (initial balances will be updated after bills are added)
            sha = Organization(
                    org_name="SHA",
                    org_email="sha@email.com",
                    org_phone_number="+254700111222",
                    org_type=OrganizationType.insurance.value,
                    outstanding_balance=Decimal("0.00"),  # Temporary, will update
                )
            jubilee = Organization(
                    org_name="Jubilee Insurance",
                    org_email="jubilee@email.com",
                    org_phone_number="+254722333444",
                    org_type=OrganizationType.insurance.value,
                    outstanding_balance=Decimal("0.00"),  # Temporary
                )
            aar = Organization(
                    org_name="AAR",
                    org_email="aar@email.com",
                    org_phone_number="+254733555666",
                    org_type=OrganizationType.corporation.value,
                    outstanding_balance=Decimal("0.00"),  # Temporary
                )
            britam = Organization(
                    org_name="Britam",
                    org_email="britam@email.com",
                    org_phone_number="+254744777888",
                    org_type=OrganizationType.insurance.value,
                    outstanding_balance=Decimal("0.00"),  # Will remain zero (no bills)
                )
            db.session.add_all([sha,jubilee,aar,britam])
            db.session.commit()
            print("Organizations added successfully")

            # Seed Patient Bills (with amounts that will affect outstanding balances)
                # SHA bills (total: 106,000)
            bill1 = PatientBill(
                    patient_number="7536",
                    patient_id="648354653",
                    patient_name="James Mwangi",
                    patient_gender=GenderOption.male.value,
                    patient_age=62,
                    patient_phone_number="+254712345678",
                    bill_date=date(2025, 2, 12),
                    organization_id=sha.org_id,
                    bill_type=BillType.medical.value,
                    amount=Decimal("64000.00"),
                    status=BillStatus.unpaid.value,
                    paid_amount=Decimal("0.00"),
                )
            bill2 = PatientBill(
                    patient_number="9345",
                    patient_id="928374651092",
                    patient_name="Mercy Atieno",
                    patient_gender=GenderOption.female.value,
                    patient_age=34,
                    patient_phone_number="+254745678901",
                    bill_date=date(2025, 4, 18),
                    organization_id=sha.org_id,
                    bill_type=BillType.medical.value,
                    amount=Decimal("42000.00"),
                    status=BillStatus.unpaid.value,
                    paid_amount=Decimal("0.00"),
                )
                # Jubilee bills (total: 190,000)
            bill3 = PatientBill(
                    patient_number="7829",
                    patient_id="738347483678",
                    patient_name="Grace Wambui",
                    patient_gender=GenderOption.female.value,
                    patient_age=29,
                    patient_phone_number="+254723456789",
                    bill_date=date(2025, 5, 22),
                    organization_id=jubilee.org_id,
                    bill_type=BillType.medical.value,
                    amount=Decimal("190000.00"),
                    status=BillStatus.unpaid.value,
                    paid_amount=Decimal("0.00"),
                )
                # AAR bills (total: 85,000)
            bill4 = PatientBill(
                    patient_number="8912",
                    patient_id="837465123987",
                    patient_name="Peter Kariuki",
                    patient_gender=GenderOption.male.value,
                    patient_age=45,
                    patient_phone_number="+254734567890",
                    bill_date=date(2025, 3, 15),
                    organization_id=aar.org_id,
                    bill_type=BillType.surgical.value,
                    amount=Decimal("85000.00"),
                    status=BillStatus.unpaid.value,
                    paid_amount=Decimal("0.00"),
                )
            db.session.add_all([bill2,bill3,bill4])
            db.session.commit()
            print("Patient Bills added successfully")

            # Seed Transactions (will reduce outstanding balances)
            transactions = [
                # SHA payment (64,000 paid)
                Transaction(
                    organization_id=sha.org_id,
                    transaction_type=TransactionType.payment.value,
                    previous_outstanding_balance=Decimal("106000.00"),
                    transaction_amount=Decimal("64000.00"),
                    final_balance=Decimal("42000.00"),  # 106,000 - 64,000
                    receipt_url="https://example.com/receipts/1",
                    transaction_date=date(2025, 2, 15),
                ),
                # Jubilee payment (50,000 paid)
                Transaction(
                    organization_id=jubilee.org_id,
                    transaction_type=TransactionType.payment.value,
                    previous_outstanding_balance=Decimal("190000.00"),
                    transaction_amount=Decimal("50000.00"),
                    final_balance=Decimal("140000.00"),  # 190,000 - 50,000
                    receipt_url="https://example.com/receipts/2",
                    transaction_date=date(2025, 5, 25),
                ),
            ]
            db.session.add_all(transactions)

            # Update outstanding balances after transactions
            # Calculate and update outstanding balances
            sha.outstanding_balance = Decimal("42000.00")  # 64,000 + 42,000 - 64,000
            jubilee.outstanding_balance = Decimal("140000.00")  # 190,000 - 50,000
            aar.outstanding_balance = Decimal("85000.00")  # 85,000

            db.session.commit()
            print("Transactions added successfully")

            # Seed Paid Bills (marking the SHA bill as fully paid)
            sha_transaction = Transaction.query.filter_by(
                organization_id=sha.org_id
            ).first()
            paid_bill = PaidBill(
                    bill_id=bill1.bill_id,
                    patient_number=bill1.patient_number,
                    patient_id=bill1.patient_id,
                    patient_name=bill1.patient_name,
                    patient_gender=bill1.patient_gender,
                    patient_age=bill1.patient_age,
                    patient_phone_number=bill1.patient_phone_number,
                    bill_date=bill1.bill_date,
                    organization_id=bill1.organization_id,
                    bill_type=bill1.bill_type,
                    amount=bill1.amount,
                    status=BillStatus.paid.value,
                    paid_amount=bill1.amount,
                    transaction_id=sha_transaction.transaction_id,
                )
            db.session.add(paid_bill)

            # Update the bill status and paid amount
            bill1.status = BillStatus.paid.value
            bill1.paid_amount = bill1.amount
            db.session.commit()
            print("Paid Bills added successfully")

        except Exception as e:
            db.session.rollback()
            print(f"Error during seeding: {str(e)}")
            raise
        finally:
            db.session.close()

        print("Seeding complete")


if __name__ == "__main__":
    seed_data()
