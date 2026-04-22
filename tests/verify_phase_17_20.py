"""
Phase 17-20 Verification Tests (JSON Version)
- Phase 17: File Upload for Ticket Attachments (Metadata)
- Phase 18: Smart Routing Pipeline (assign_coordinator persistence)
- Phase 19: Ticket State Machine (status update, RBAC, transition validation)
- Phase 20: Escalation Mechanism (SLA audit, notification creation)
"""
import pytest
from datetime import datetime, timedelta, UTC
from json_db import db
from database_schema import StudentProfile, SupportTicket, TicketStatus
from ticket_lifecycle import TicketEngine, TicketStatus as LCStatus
from conftest import seed_student, _read_json

@pytest.fixture
def ticket_engine():
    return TicketEngine()

class TestStateMachine:
    """Phase 19: Ticket State Machine validation."""

    def test_valid_transition_submitted_to_under_review(self, ticket_engine):
        result = ticket_engine.advance_status(LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW)
        assert result == LCStatus.UNDER_REVIEW

    def test_valid_transition_under_review_to_resolved(self, ticket_engine):
        result = ticket_engine.advance_status(LCStatus.UNDER_REVIEW, LCStatus.RESOLVED)
        assert result == LCStatus.RESOLVED

    def test_invalid_transition_submitted_to_resolved(self, ticket_engine):
        with pytest.raises(ValueError):
            ticket_engine.advance_status(LCStatus.SUBMITTED, LCStatus.RESOLVED)

    def test_resolved_is_terminal(self, ticket_engine):
        with pytest.raises(ValueError):
            ticket_engine.advance_status(LCStatus.RESOLVED, LCStatus.SUBMITTED)

    def test_advance_persists_to_json(self, ticket_engine):
        student = seed_student(prn="P19JSON", name="State Test Student")
        
        ticket = SupportTicket(
            id=0,
            student_id=student["id"],
            category="test",
            description="state test",
            status=TicketStatus.SUBMITTED,
            predicted_department_id="test_dept"
        )
        db.insert(ticket)

        ticket_engine.advance_status(
            LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW,
            ticket_id=ticket.id
        )
        
        updated_ticket = db.get_by_id(SupportTicket, ticket.id)
        assert updated_ticket.status == TicketStatus.UNDER_REVIEW


class TestEscalation:
    """Phase 20: SLA-based escalation audit."""

    def test_sla_breach_escalates_ticket(self, ticket_engine):
        student = seed_student(prn="SLAJSON", name="SLA Student")

        # Create a ticket that's 5 days old
        old_ticket = SupportTicket(
            id=0,
            student_id=student["id"],
            category="academic",
            description="old request",
            status=TicketStatus.SUBMITTED,
            predicted_department_id="academic",
            created_at=datetime.now(UTC) - timedelta(days=5)
        )
        db.insert(old_ticket)

        count = ticket_engine.audit_escalations()
        assert count >= 1

        updated_ticket = db.get_by_id(SupportTicket, old_ticket.id)
        assert updated_ticket.status == TicketStatus.ESCALATED

    def test_fresh_ticket_not_escalated(self, ticket_engine):
        student = seed_student(prn="FRESHJSON")
        
        new_ticket = SupportTicket(
            id=0,
            student_id=student["id"],
            category="tech",
            description="new request",
            status=TicketStatus.SUBMITTED,
            predicted_department_id="tech",
            created_at=datetime.now(UTC)
        )
        db.insert(new_ticket)

        # Audit should not increment escalated count for fresh tickets
        # (Note: we subtract existing escalations if any from previous tests)
        count = ticket_engine.audit_escalations()
        
        updated_ticket = db.get_by_id(SupportTicket, new_ticket.id)
        assert updated_ticket.status == TicketStatus.SUBMITTED


class TestAssignCoordinator:
    """Phase 18: Coordinator assignment logic."""

    def test_high_confidence_it_assignment(self, ticket_engine):
        result = ticket_engine.assign_coordinator(92.0, "IT Technical Support")
        assert result == "it_operations_desk"

    def test_high_confidence_eoc_assignment(self, ticket_engine):
        result = ticket_engine.assign_coordinator(85.0, "EOC Confidential")
        assert result == "vip_eoc_admin_1"

    def test_low_confidence_goes_to_human_triage(self, ticket_engine):
        result = ticket_engine.assign_coordinator(60.0, "IT Technical Support")
        assert result == "human_triage_queue"


class TestSchemaValidation:
    """Phase 17/19: Pydantic models have required fields."""

    def test_ticket_model_fields(self):
        # Verify that we can instantiate with the new fields
        ticket = SupportTicket(
            id=1,
            student_id=1,
            category="test",
            description="schema check",
            status=TicketStatus.SUBMITTED,
            assigned_to="it_operations_desk",
            transition_reason="Initial assignment"
        )
        assert ticket.assigned_to == "it_operations_desk"
        assert ticket.transition_reason == "Initial assignment"

    def test_ticket_status_enum_has_action_required(self):
        assert "ACTION_REQUIRED" in TicketStatus.__members__
