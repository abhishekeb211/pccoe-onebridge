"""
Phase 4 Verification Tests (JSON Version)
- Phase 4: JSON Data Registry and Pydantic Schema Engineering

Tests verify all core Pydantic models, Enums, and the initialization
 of the JSON file-based storage registry.
"""
import pytest
import os
from database_schema import (
    StudentProfile, SupportTicket, Opportunity, FacilityBooking,
    Notification, KnowledgeBaseArticle, ChatConversation, ChatMessage,
    ScholarshipScheme, ApplicationRecord, SecurityEvent,
    BranchEnum, TicketStatus, KBCategory, ApplicationStatusEnum,
    init_db
)
from json_db import db

# ============================================================================
# Schema Structure Tests (Pydantic & JSON Registry)
# ============================================================================

class TestPhase4RegistryStructure:
    """Verify the JSON Registry is correctly mapped and initialized."""

    def test_all_core_registries_initialized(self):
        """init_db must create the core JSON files."""
        init_db()
        expected_files = [
            "students.json", "tickets.json", "opportunities.json",
            "facility_bookings.json", "notifications.json", "knowledge_base.json",
            "chat_conversations.json", "scholarships.json", "applications.json",
            "security_events.json"
        ]
        data_dir = db.data_dir
        for f in expected_files:
            assert os.path.exists(os.path.join(data_dir, f)), f"Missing registry file: {f}"

    def test_student_model_validation(self):
        """StudentProfile must have required fields as per Pydantic model."""
        s = StudentProfile(
            id=1, prn="2024CS001", name="Test Student", email="test@pccoe.edu.in",
            branch=BranchEnum.COMP_ENG, year_of_study=1
        )
        assert s.prn == "2024CS001"
        assert s.role == "student"

    def test_support_ticket_model_validation(self):
        """SupportTicket must validate required fields."""
        t = SupportTicket(
            id=1, student_id=1, category="IT", description="Issue"
        )
        assert t.status == TicketStatus.SUBMITTED
        assert t.urgent_flag is False

# ============================================================================
# Enum Verification
# ============================================================================

class TestPhase4Enums:
    """Verify all core enum types for the JSON system."""

    def test_branch_enum(self):
        members = [e.value for e in BranchEnum]
        assert len(members) == 5
        assert BranchEnum.COMP_ENG.value == "Computer Engineering"

    def test_ticket_status_enum(self):
        assert TicketStatus.SUBMITTED.value == "Submitted"
        assert TicketStatus.ESCALATED.value == "Escalated"

    def test_kb_category_enum(self):
        assert KBCategory.IT.value == "IT"
        assert KBCategory.EOC.value == "EOC"

    def test_application_status_enum(self):
        assert ApplicationStatusEnum.ACCEPTED.value == "Accepted"
        assert ApplicationStatusEnum.REJECTED.value == "Rejected"

# ============================================================================
# Relationship Verification (Model Composition)
# ============================================================================

class TestPhase4ModelComposition:
    """Verify model containment (replaces ORM relationships)."""

    def test_chat_conversation_composition(self):
        """Conversations can contain messages as a list property."""
        from database_schema import ChatMessage
        msg = ChatMessage(id=1, conversation_id=1, sender="student", content="Hi")
        conv = ChatConversation(id=1, student_id=1, messages=[msg])
        assert len(conv.messages) == 1
        assert conv.messages[0].content == "Hi"
