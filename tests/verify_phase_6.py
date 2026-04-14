"""
Phase 6 Verification Tests
- Core Backend API Scaffolding

Tests verify FastAPI endpoint structure, middleware configuration,
Pydantic models, and database CRUD patterns without importing main.py
(which triggers init_db() and requires a live PostgreSQL connection).
"""
import pytest
import os
from sqlalchemy import inspect
from conftest import engine, seed_student
from database_schema import (
    Base, StudentProfile, SupportTicket, TicketStatus, BranchEnum,
    Opportunity, FacilityBooking, Notification,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPhase6APIScaffolding:
    """Phase 6: Verify FastAPI backend scaffolding patterns."""

    def test_main_py_exists(self):
        """main.py must exist as the core API entry point."""
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "main.py"))

    def test_main_py_has_fastapi_app(self):
        """main.py must define a FastAPI application instance."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "FastAPI(" in content
        assert 'app = FastAPI(' in content

    def test_cors_middleware_configured(self):
        """CORS middleware must be configured for cross-origin requests."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "CORSMiddleware" in content
        assert "add_middleware" in content

    def test_health_endpoint_defined(self):
        """Health check endpoint must be defined."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert '/health' in content
        assert 'check_health' in content or 'health' in content

    def test_ticket_submission_endpoint(self):
        """Ticket submission endpoint must exist."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert '/api/v1/tickets' in content
        assert 'submit_ticket' in content

    def test_pydantic_models_defined(self):
        """Pydantic request models must be defined for API validation."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "class TicketSubmission(BaseModel)" in content
        assert "description: str" in content
        assert "student_prn: str" in content

    def test_database_dependency_injection(self):
        """Database session dependency injection must be configured."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "def get_db()" in content or "get_db" in content
        assert "Depends(get_db)" in content

    def test_process_time_middleware(self):
        """Request timing middleware must add X-Process-Time header."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "X-Process-Time" in content


class TestPhase6DatabaseCRUD:
    """Phase 6: Verify database CRUD operations work correctly."""

    def test_create_student_and_ticket(self, db):
        """Student creation and ticket submission must work end-to-end."""
        student = seed_student(db)

        ticket = SupportTicket(
            student_id=student.id,
            category="IT",
            description="LMS Login Issue - API Scaffold Test",
            status=TicketStatus.SUBMITTED,
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        assert ticket.id is not None
        assert ticket.student_id == student.id
        assert ticket.status == TicketStatus.SUBMITTED

    def test_student_ticket_relationship(self, db):
        """Student-ticket relationship must work bidirectionally."""
        student = seed_student(db)

        db.add(SupportTicket(
            student_id=student.id,
            category="Academic",
            description="Course registration help",
            status=TicketStatus.SUBMITTED,
        ))
        db.commit()
        db.refresh(student)

        assert len(student.tickets) == 1
        assert student.tickets[0].category == "Academic"

    def test_facility_booking_crud(self, db):
        """Facility booking must support CRUD operations."""
        from datetime import datetime, timezone
        student = seed_student(db, prn="FAC001")

        booking = FacilityBooking(
            student_id=student.id,
            facility_name="Central Library Study Room",
            booking_time=datetime(2026, 4, 10, 14, 0, tzinfo=timezone.utc),
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)

        assert booking.id is not None
        assert booking.facility_name == "Central Library Study Room"

    def test_notification_crud(self, db):
        """Notification creation must work."""
        student = seed_student(db, prn="NOTIF001")

        notif = Notification(
            student_id=student.id,
            title="Welcome",
            message="Welcome to OneBridge!",
            type="success",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.id is not None
        assert notif.is_read is False

    def test_all_core_tables_exist(self, db):
        """All core Phase 6 tables must be created."""
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        core_tables = [
            "students", "support_tickets", "opportunities",
            "facility_bookings", "notifications",
        ]
        for t in core_tables:
            assert t in tables, f"Missing core table: {t}"
