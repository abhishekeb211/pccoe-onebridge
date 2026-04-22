"""
Phase 21-40 Verification Tests (JSON Version) - Corrected
"""
import pytest
import os
from datetime import datetime, timezone
from conftest import seed_student, seed_resource
from database_schema import (
    KnowledgeBaseArticle, ChatConversation, ChatMessage,
    ScholarshipScheme, FacilityBooking, SecurityEvent
)
from json_db import db

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestHelpdeskAndMatching:
    def test_kb_article_registry(self):
        article = KnowledgeBaseArticle(
            id=1, title="WiFi Setup", content="Connect to PCCOE", category="IT"
        )
        db.insert(article)
        assert db.get_by_id(KnowledgeBaseArticle, 1).title == "WiFi Setup"

    def test_distress_detection_logic(self):
        from local_agent import local_agent
        assert hasattr(local_agent, "detect_distress")

class TestFacilitiesAndApprovals:
    def test_facility_booking_json(self):
        student = seed_student(prn="FAC101")
        res = seed_resource(name="Conference Hall")
        booking = FacilityBooking(
            id=1, student_id=student["id"], facility_name="Conference Hall",
            booking_time=datetime.now(timezone.utc)
        )
        db.insert(booking)
        assert db.get_by_id(FacilityBooking, 1).facility_name == "Conference Hall"

class TestSystemIntegrity:
    def test_security_event_logging(self):
        event = SecurityEvent(
            id=1, event_type="login_failure", severity="high", details="Invalid PRN"
        )
        db.insert(event)
        assert db.get_by_id(SecurityEvent, 1).event_type == "login_failure"
