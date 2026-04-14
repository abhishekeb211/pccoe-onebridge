"""
Phase 11-12 Verification Tests
- Phase 11: Dynamic Dashboard UI Assembly
- Phase 12: Notification & Alerting Engine

Tests verify dashboard view structures, notification handling,
and database models for notifications.
"""
import pytest
import os
from datetime import datetime, timezone
from conftest import seed_student
from database_schema import (
    Base, StudentProfile, SupportTicket, TicketStatus, BranchEnum,
    Notification, FacilityBooking, Opportunity,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================================
# Phase 11: Dynamic Dashboard UI Assembly
# ============================================================================

class TestDashboardUI:
    @pytest.fixture(autouse=True)
    def load_app_js(self):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_dashboard_generator_exists(self):
        """generateDashboard function must exist."""
        assert "generateDashboard" in self.app_js

    def test_dashboard_has_ticket_card(self):
        """Dashboard must have active tickets snapshot card."""
        assert "dashboard-tickets" in self.app_js
        assert "Active Tickets" in self.app_js

    def test_dashboard_has_opportunities_card(self):
        """Dashboard must have AI-matched opportunities card."""
        assert "dashboard-opportunities" in self.app_js
        assert "New Opportunities" in self.app_js or "Opportunities" in self.app_js

    def test_dashboard_has_facility_card(self):
        """Dashboard must show facility booking info."""
        assert "Facility Access" in self.app_js or "facility" in self.app_js.lower()

    def test_dashboard_eoc_conditional_card(self):
        """Dashboard must conditionally show EOC card for eligible students."""
        assert "needsEOC" in self.app_js
        assert "EOC Quick Actions" in self.app_js or "eoc-brand" in self.app_js

    def test_async_data_loader(self):
        """Dashboard must load data asynchronously after render."""
        assert "loadDashboardData" in self.app_js

    def test_dashboard_ticket_data(self, db):
        """Verify ticket data can be queried for dashboard display."""
        student = seed_student(db)
        for i in range(3):
            db.add(SupportTicket(
                student_id=student.id,
                category="academic",
                description=f"Test ticket {i+1}",
                status=TicketStatus.SUBMITTED if i < 2 else TicketStatus.RESOLVED,
            ))
        db.commit()

        active = db.query(SupportTicket).filter(
            SupportTicket.student_id == student.id,
            SupportTicket.status != TicketStatus.RESOLVED,
        ).count()
        assert active == 2

    def test_dashboard_opportunities_data(self, db):
        """Verify opportunities can be queried for dashboard display."""
        db.add(Opportunity(
            type="scholarship", title="Test Scholarship",
            target_branches="Computer Engineering",
            deadline=datetime(2026, 12, 31, tzinfo=timezone.utc),
        ))
        db.add(Opportunity(
            type="internship", title="Test Internship",
            target_branches="Computer Engineering",
            deadline=datetime(2026, 6, 30, tzinfo=timezone.utc),
        ))
        db.commit()

        opps = db.query(Opportunity).all()
        assert len(opps) == 2


# ============================================================================
# Phase 12: Notification & Alerting Engine
# ============================================================================

class TestNotificationEngine:
    @pytest.fixture(autouse=True)
    def load_app_js(self):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_notification_function_exists(self):
        """showNotification function must exist and be globally accessible."""
        assert "window.showNotification" in self.app_js

    def test_notification_types(self):
        """Notification must support info, urgent, and success types."""
        assert '"info"' in self.app_js
        assert '"urgent"' in self.app_js
        assert '"success"' in self.app_js

    def test_toast_container_setup(self):
        """Toast container must be created with aria-live for accessibility."""
        assert "toast-container" in self.app_js
        assert "aria-live" in self.app_js

    def test_notification_auto_cleanup(self):
        """Notifications must auto-remove after timeout."""
        assert "setTimeout" in self.app_js
        assert "removeChild" in self.app_js

    def test_screen_reader_announcement(self):
        """Notifications must announce to screen readers via routeAnnouncer."""
        assert "routeAnnouncer" in self.app_js

    def test_notification_model_crud(self, db):
        """Notification model must support CRUD operations."""
        student = seed_student(db)

        notif = Notification(
            student_id=student.id,
            title="Test Alert",
            message="Your ticket has been resolved",
            type="success",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.id is not None
        assert notif.title == "Test Alert"
        assert notif.is_read is False

    def test_notification_types_in_model(self, db):
        """Multiple notification types must be storable."""
        student = seed_student(db, prn="NOTIF002")
        for ntype in ["info", "success", "warning", "urgent"]:
            db.add(Notification(
                student_id=student.id,
                title=f"{ntype.title()} Notification",
                message=f"This is a {ntype} notification",
                type=ntype,
            ))
        db.commit()

        notifs = db.query(Notification).filter_by(student_id=student.id).all()
        assert len(notifs) == 4

    def test_notification_read_tracking(self, db):
        """Notification read status must be trackable."""
        student = seed_student(db, prn="NOTIF003")
        notif = Notification(
            student_id=student.id,
            title="Unread Alert",
            message="Please review",
            type="info",
        )
        db.add(notif)
        db.commit()

        assert notif.is_read is False
        notif.is_read = True
        db.commit()
        db.refresh(notif)
        assert notif.is_read is True

    def test_student_notification_relationship(self, db):
        """Student must have relationship to notifications."""
        student = seed_student(db, prn="NOTIF004")
        db.add(Notification(
            student_id=student.id,
            title="Rel Test",
            message="Testing relationship",
            type="info",
        ))
        db.commit()
        db.refresh(student)

        assert len(student.notifications) == 1
        assert student.notifications[0].title == "Rel Test"
