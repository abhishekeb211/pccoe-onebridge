"""
Phase 11-16 Verification Tests (JSON Version) - Corrected
"""
import pytest
import os
from datetime import datetime, timezone
from conftest import seed_student
from database_schema import (
    Notification, SupportTicket, TicketStatus,
)
from json_db import db

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestDashboardAndNotifications:
    @pytest.fixture(autouse=True)
    def load_app_js(self):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()

    def test_dashboard_components_logic(self):
        assert "fetchData" in self.app_js
        assert "renderAllGrids" in self.app_js

    def test_notification_registry_crud(self):
        student = seed_student(prn="NOTIF111")
        notif = Notification(
            id=1, student_id=student["id"], title="Test Alert", message="Your ticket is processing", type="info"
        )
        db.insert(notif)
        saved = db.get_by_id(Notification, notif.id)
        assert saved.title == "Test Alert"

class TestLocalAISubsystem:
    def test_local_agent_logic(self):
        from local_agent import local_agent
        assert hasattr(local_agent, "classify_ticket")

    def test_ticket_routing_classification(self):
        from local_agent import local_agent
        assert "classifier" in str(dir(local_agent))
