from models import User, PatientBill, Organization, db
from app import app
from datetime import datetime

with app.app_context():
    # Delete all rows from the tables
    try:
        print("Deleting table data...")
        User.query.delete()
        PatientBill.query.delete()
        Organization.query.delete()
        db.session.commit()  # Commit changes
        print("Tables cleared successfully")
    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        print(f"Error clearing tables: {str(e)}")

    # Add data to User table
    try:
        user1 = User(
            user_name="musin",
            user_role="admin",
            email="musin@gmail.com",
            password="musin@123",
        )
        user2 = User(
            user_name="daud",
            user_role="employee",
            email="daud@gmail.com",
            password="daud@123",
        )

        db.session.add_all([user1, user2])  # Add instances to the Session
        db.session.commit()  # Commit changes to the database
        print("Users added successfully")

    except Exception as e:
        print(f"Error seeding Users: {str(e)}")  # print exception as a string
        db.session.rollback()  # roll back incase of an error

    # Add data to Organization table
    try:
        org1 = Organization(org_name="SHA", org_type="insurance")
        org2 = Organization(org_name="Jubilee", org_type="insurance")
        org3 = Organization(org_name="Mzuri Sweets", org_type="corporation")
        org4 = Organization(org_name="Maize Millers", org_type="corporation")

        db.session.add_all([org1, org2, org3, org4])
        db.session.commit()
        print("Organizations added successfully")

        # Add data to PatientBill table
        patbill1 = PatientBill(
            patient_name="James Wock",
            patient_gender="male",
            patient_age=62,
            patient_contact="+254 6378938333",
            bill_date=datetime.strptime("2025-02-12 15:30:00", "%Y-%m-%d %H:%M:%S"),
            organization_id=org1.org_id,
            bill_type="medical",
            amount=64000,
        )
        patbill2 = PatientBill(
            patient_name="Randy Mav",
            patient_gender="male",
            patient_age=29,
            patient_contact="+254 63789444333",
            bill_date=datetime.strptime("2025-05-22 16:37:00", "%Y-%m-%d %H:%M:%S"),
            organization_id=org1.org_id,
            bill_type="medical",
            amount=190000,
        )
        patbill3 = PatientBill(
            patient_name="Katherine Karaja",
            patient_gender="female",
            patient_age=32,
            patient_contact="+25478938333",
            bill_date=datetime.strptime("2023-10-12 19:30:00", "%Y-%m-%d %H:%M:%S"),
            organization_id=org2.org_id,
            bill_type="surgical",
            amount=4000,
        )
        db.session.add_all([patbill1, patbill2, patbill3])
        db.session.commit()
        print("Patient Bills added successfully")
    except Exception as e:
        print(f"Error seeding Organizations or Patient Bills: {str(e)}")
        db.session.rollback()

    print("Seeding complete")
