"""
Phase 6 Verification Tests (JSON Version)
- Core Backend API Scaffolding

Tests verify FastAPI endpoint structure, middleware configuration,
Pydantic models, and JSON-based CRUD patterns.
"""
import pytest
import os
import json
from conftest import seed_student, PROJECT_ROOT, _read_json
# database_schema is now Pydantic-based
from database_schema import (
    StudentProfile, SupportTicket, TicketStatus, BranchEnum,
    Opportunity, FacilityBooking, Notification,
)

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

    def test_database_dependency_stub(self):
        """Database dependency stub must exist for compatibility."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "def get_db()" in content
        assert "return None" in content

    def test_process_time_middleware(self):
        """Request timing middleware must add X-Process-Time header."""
        with open(os.path.join(PROJECT_ROOT, "main.py"), "r", encoding="utf-8") as f:
            content = f.read()
        assert "X-Process-Time" in content


class TestPhase6JSONCRUD:
    """Phase 6: Verify JSON-based CRUD operations work correctly."""

    def test_create_student_and_ticket(self):
        """Student creation and ticket submission must work end-to-end via JSON."""
        student = seed_student(prn="JSON001")
        
        from json_db import db
        ticket = SupportTicket(
            id=0,
            student_id=student["id"],
            category="IT",
            description="LMS Login Issue - JSON Scaffold Test",
            status=TicketStatus.SUBMITTED,
        )
        db.insert(ticket)

        saved_tickets = _read_json("tickets.json")
        assert len(saved_tickets) >= 1
        assert any(t["description"] == ticket.description for t in saved_tickets)

    def test_notification_crud(self):
        """Notification creation must work in JSON."""
        student = seed_student(prn="NOTIF001")
        from json_db import db

        notif = Notification(
            id=0,
            student_id=student["id"],
            title="Welcome",
            message="Welcome to OneBridge!",
            type="success",
        )
        db.insert(notif)
        
        saved_notifs = _read_json("notifications.json")
        assert len(saved_notifs) >= 1
        assert any(n["title"] == "Welcome" for n in saved_notifs)

    def test_all_core_json_files_init(self):
        """All core Phase 6 data models must have corresponding JSON files."""
        from database_schema import init_db
        init_db()
        
        core_files = [
            "students.json", "tickets.json", "opportunities.json",
            "facility_bookings.json", "notifications.json",
        ]
        test_data_dir = os.path.join(PROJECT_ROOT, "tests", "test_data")
        # Note: initialization in backend uses 'data/' but conftest uses 'tests/test_data/'
        # We verify existence in the test data dir
        for f in core_files:
            path = os.path.join(test_data_dir, f)
            # Files are created on first write, so we ensure seed helpers created them
            assert os.path.exists(path), f"Missing core JSON file: {f}"
