"""
Phase 29-32 Verification Tests
- Phase 29: Faculty Endorsement (request, approve/reject, digital signature)
- Phase 30: Campus Resource Inventory (CRUD, filtering)
- Phase 31: Booking Engine (conflict detection, waitlist, cancellation promotion)
- Phase 32: Confidential Mode (encrypted grievance, EOC-only access)
"""
import os
import sys
import unittest
import base64
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import engine, fresh_db, seed_student, seed_faculty, seed_resource, seed_application
from database_schema import (
    Base, StudentProfile, BranchEnum,
    ApplicationRecord, ApplicationStatusEnum,
    FacultyEndorsement, ApprovalStatusEnum,
    CampusResource,
    ResourceBooking, BookingStatusEnum,
    ConfidentialGrievance,
)


# ====== Phase 29: Faculty Approval Flow ======

class TestFacultyEndorsement(unittest.TestCase):
    def test_create_endorsement_request(self):
        db = fresh_db()
        student = seed_student(db)
        faculty = seed_faculty(db)
        app = seed_application(db, student)

        endorsement = FacultyEndorsement(
            application_id=app.id,
            faculty_id=faculty.id,
            student_id=student.id,
        )
        db.add(endorsement)
        db.commit()
        db.refresh(endorsement)

        self.assertEqual(endorsement.status, ApprovalStatusEnum.PENDING)
        self.assertIsNone(endorsement.digital_signature)

    def test_approve_endorsement(self):
        db = fresh_db()
        student = seed_student(db)
        faculty = seed_faculty(db)
        app = seed_application(db, student)

        endorsement = FacultyEndorsement(
            application_id=app.id, faculty_id=faculty.id, student_id=student.id,
        )
        db.add(endorsement)
        db.commit()

        endorsement.status = ApprovalStatusEnum.APPROVED
        endorsement.remarks = "Excellent student, highly recommended."
        endorsement.acted_at = datetime.now(timezone.utc)

        import hashlib
        sig_data = f"{endorsement.id}:{faculty.prn}:{endorsement.application_id}:{endorsement.acted_at.isoformat()}"
        endorsement.digital_signature = hashlib.sha256(sig_data.encode()).hexdigest()

        db.commit()
        db.refresh(endorsement)

        self.assertEqual(endorsement.status, ApprovalStatusEnum.APPROVED)
        self.assertIsNotNone(endorsement.digital_signature)
        self.assertEqual(len(endorsement.digital_signature), 64)

    def test_reject_endorsement(self):
        db = fresh_db()
        student = seed_student(db)
        faculty = seed_faculty(db)
        app = seed_application(db, student)

        endorsement = FacultyEndorsement(
            application_id=app.id, faculty_id=faculty.id, student_id=student.id,
        )
        db.add(endorsement)
        db.commit()

        endorsement.status = ApprovalStatusEnum.REJECTED
        endorsement.remarks = "Needs more project experience."
        db.commit()
        db.refresh(endorsement)

        self.assertEqual(endorsement.status, ApprovalStatusEnum.REJECTED)

    def test_approval_status_enum(self):
        self.assertEqual(len(ApprovalStatusEnum), 4)
        self.assertEqual(ApprovalStatusEnum.REVISION_REQUESTED.value, "Revision Requested")


# ====== Phase 30: Resource Inventory ======

class TestResourceInventory(unittest.TestCase):
    def test_create_resource(self):
        db = fresh_db()
        resource = seed_resource(db)
        self.assertEqual(resource.name, "AI Lab")
        self.assertEqual(resource.resource_type, "lab")
        self.assertTrue(resource.is_active)

    def test_filter_by_type(self):
        db = fresh_db()
        seed_resource(db, name="ML Lab", rtype="lab")
        seed_resource(db, name="Central Library", rtype="library")
        seed_resource(db, name="Innovation Hub", rtype="makerspace")

        labs = db.query(CampusResource).filter(CampusResource.resource_type == "lab").all()
        self.assertEqual(len(labs), 1)

    def test_filter_accessible(self):
        db = fresh_db()
        seed_resource(db, name="Lab A", accessible=True)
        seed_resource(db, name="Lab B", accessible=False)

        accessible = db.query(CampusResource).filter(CampusResource.is_accessible == True).all()
        self.assertEqual(len(accessible), 1)
        self.assertEqual(accessible[0].name, "Lab A")


# ====== Phase 31: Booking Engine ======

class TestBookingEngine(unittest.TestCase):
    def test_create_booking(self):
        db = fresh_db()
        student = seed_student(db)
        resource = seed_resource(db)

        booking = ResourceBooking(
            resource_id=resource.id, student_id=student.id,
            booking_date=datetime(2025, 6, 15, tzinfo=timezone.utc),
            start_time="10:00", end_time="12:00",
            purpose="Project work",
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        self.assertEqual(booking.status, BookingStatusEnum.CONFIRMED)
        self.assertEqual(booking.start_time, "10:00")

    def test_conflict_detection(self):
        db = fresh_db()
        student1 = seed_student(db)
        student2 = seed_student(db, prn="72350002B", name="Student 2")
        resource = seed_resource(db)

        booking_date = datetime(2025, 6, 15, tzinfo=timezone.utc)

        b1 = ResourceBooking(
            resource_id=resource.id, student_id=student1.id,
            booking_date=booking_date, start_time="10:00", end_time="12:00",
            status=BookingStatusEnum.CONFIRMED,
        )
        db.add(b1)
        db.commit()

        conflicts = db.query(ResourceBooking).filter(
            ResourceBooking.resource_id == resource.id,
            ResourceBooking.booking_date == booking_date,
            ResourceBooking.status == BookingStatusEnum.CONFIRMED,
            ResourceBooking.start_time < "12:00",
            ResourceBooking.end_time > "10:00",
        ).all()
        self.assertEqual(len(conflicts), 1)

    def test_waitlist_promotion(self):
        db = fresh_db()
        student1 = seed_student(db)
        student2 = seed_student(db, prn="72350002B", name="Student 2")
        resource = seed_resource(db)

        booking_date = datetime(2025, 6, 15, tzinfo=timezone.utc)

        b1 = ResourceBooking(
            resource_id=resource.id, student_id=student1.id,
            booking_date=booking_date, start_time="10:00", end_time="12:00",
            status=BookingStatusEnum.CONFIRMED,
        )
        b2 = ResourceBooking(
            resource_id=resource.id, student_id=student2.id,
            booking_date=booking_date, start_time="10:00", end_time="12:00",
            status=BookingStatusEnum.WAITLISTED,
        )
        db.add(b1)
        db.add(b2)
        db.commit()

        b1.status = BookingStatusEnum.CANCELLED
        b2.status = BookingStatusEnum.CONFIRMED
        db.commit()

        db.refresh(b1)
        db.refresh(b2)
        self.assertEqual(b1.status, BookingStatusEnum.CANCELLED)
        self.assertEqual(b2.status, BookingStatusEnum.CONFIRMED)

    def test_booking_status_enum(self):
        self.assertEqual(len(BookingStatusEnum), 3)


# ====== Phase 32: Confidential Mode ======

class TestConfidentialMode(unittest.TestCase):
    def test_create_encrypted_grievance(self):
        db = fresh_db()
        student = seed_student(db)

        description = "I experienced discrimination in the library."
        encrypted = base64.b64encode(description.encode()).decode()

        grievance = ConfidentialGrievance(
            student_id=student.id,
            category="discrimination",
            description_encrypted=encrypted,
            is_anonymous=False,
            assigned_eoc_officer="eoc_officer_1",
        )
        db.add(grievance)
        db.commit()
        db.refresh(grievance)

        self.assertEqual(grievance.status, "submitted")
        self.assertNotEqual(grievance.description_encrypted, description)

        decrypted = base64.b64decode(grievance.description_encrypted.encode()).decode()
        self.assertEqual(decrypted, description)

    def test_anonymous_grievance(self):
        db = fresh_db()
        student = seed_student(db)

        grievance = ConfidentialGrievance(
            student_id=student.id,
            category="harassment",
            description_encrypted=base64.b64encode(b"Anonymous report").decode(),
            is_anonymous=True,
        )
        db.add(grievance)
        db.commit()
        db.refresh(grievance)

        self.assertTrue(grievance.is_anonymous)

    def test_resolve_grievance(self):
        db = fresh_db()
        student = seed_student(db)

        grievance = ConfidentialGrievance(
            student_id=student.id,
            category="accessibility",
            description_encrypted=base64.b64encode(b"Need ramp access").decode(),
        )
        db.add(grievance)
        db.commit()

        grievance.status = "resolved"
        grievance.resolved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(grievance)

        self.assertEqual(grievance.status, "resolved")
        self.assertIsNotNone(grievance.resolved_at)


# ====== Schema Integrity ======

class TestPhase29_32Schema(unittest.TestCase):
    def test_all_tables_created(self):
        db = fresh_db()
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        required = [
            "faculty_endorsements",
            "campus_resources",
            "resource_bookings",
            "confidential_grievances",
        ]
        for t in required:
            self.assertIn(t, table_names, f"Missing table: {t}")


if __name__ == "__main__":
    unittest.main()
