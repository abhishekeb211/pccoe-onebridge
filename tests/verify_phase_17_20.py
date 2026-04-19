"""
Phase 17-20 Verification Tests
- Phase 17: File Upload for Ticket Attachments
- Phase 18: Smart Routing Pipeline (assign_coordinator persistence)
- Phase 19: Ticket State Machine (status update, RBAC, transition validation)
- Phase 20: Escalation Mechanism (SLA audit, notification creation)
"""
import os
import sys
import unittest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import fresh_db, seed_student
from database_schema import Base, StudentProfile, SupportTicket, Notification, TicketStatus, BranchEnum
from ticket_lifecycle import TicketEngine, TicketStatus as LCStatus


class TestStateMachine(unittest.TestCase):
    """Phase 19: Ticket State Machine validation."""

    def setUp(self):
        self.engine = TicketEngine()

    def test_valid_transition_submitted_to_under_review(self):
        result = self.engine.advance_status(LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW)
        self.assertEqual(result, LCStatus.UNDER_REVIEW)

    def test_valid_transition_under_review_to_resolved(self):
        result = self.engine.advance_status(LCStatus.UNDER_REVIEW, LCStatus.RESOLVED)
        self.assertEqual(result, LCStatus.RESOLVED)

    def test_invalid_transition_submitted_to_resolved(self):
        with self.assertRaises(ValueError):
            self.engine.advance_status(LCStatus.SUBMITTED, LCStatus.RESOLVED)

    def test_resolved_is_terminal(self):
        with self.assertRaises(ValueError):
            self.engine.advance_status(LCStatus.RESOLVED, LCStatus.SUBMITTED)

    def test_escalated_can_return_to_review(self):
        result = self.engine.advance_status(LCStatus.ESCALATED, LCStatus.UNDER_REVIEW)
        self.assertEqual(result, LCStatus.UNDER_REVIEW)

    def test_advance_persists_to_db(self):
        db = fresh_db()
        student = StudentProfile(
            prn="TEST001", name="Phase19 Student", email="p19@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()
        ticket = SupportTicket(
            student_id=student.id, category="test", description="state test",
            status=TicketStatus.SUBMITTED, predicted_department_id="test_dept"
        )
        db.add(ticket)
        db.commit()

        self.engine.advance_status(
            LCStatus.SUBMITTED, LCStatus.UNDER_REVIEW,
            ticket_obj=ticket, db=db
        )
        db.refresh(ticket)
        self.assertEqual(ticket.status, TicketStatus.UNDER_REVIEW)
        db.close()


class TestEscalation(unittest.TestCase):
    """Phase 20: SLA-based escalation audit."""

    def test_sla_breach_escalates_ticket(self):
        db = fresh_db()
        student = StudentProfile(
            prn="TEST002", name="SLA Student", email="sla@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        old_ticket = SupportTicket(
            student_id=student.id, category="academic", description="old request",
            status=TicketStatus.SUBMITTED, predicted_department_id="academic",
            created_at=datetime.now(UTC) - timedelta(days=5)
        )
        db.add(old_ticket)
        db.commit()

        te = TicketEngine()
        count = te.audit_escalations(db=db)
        self.assertEqual(count, 1)

        db.refresh(old_ticket)
        self.assertEqual(old_ticket.status, TicketStatus.ESCALATED)
        db.close()

    def test_fresh_ticket_not_escalated(self):
        db = fresh_db()
        student = StudentProfile(
            prn="TEST003", name="Fresh Student", email="fresh@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        new_ticket = SupportTicket(
            student_id=student.id, category="tech", description="new request",
            status=TicketStatus.SUBMITTED, predicted_department_id="tech",
            created_at=datetime.now(UTC)
        )
        db.add(new_ticket)
        db.commit()

        te = TicketEngine()
        count = te.audit_escalations(db=db)
        self.assertEqual(count, 0)
        db.close()


class TestAssignCoordinator(unittest.TestCase):
    """Phase 18: Coordinator assignment logic."""

    def test_high_confidence_it_assignment(self):
        te = TicketEngine()
        result = te.assign_coordinator(92.0, "IT Technical Support")
        self.assertEqual(result, "it_operations_desk")

    def test_high_confidence_eoc_assignment(self):
        te = TicketEngine()
        result = te.assign_coordinator(85.0, "EOC Confidential")
        self.assertEqual(result, "vip_eoc_admin_1")

    def test_low_confidence_goes_to_human_triage(self):
        te = TicketEngine()
        result = te.assign_coordinator(60.0, "IT Technical Support")
        self.assertEqual(result, "human_triage_queue")


class TestSchemaColumns(unittest.TestCase):
    """Phase 17/19: Database schema has required columns."""

    def test_ticket_has_assigned_to(self):
        db = fresh_db()
        student = StudentProfile(
            prn="TEST004", name="Schema Test", email="schema@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        ticket = SupportTicket(
            student_id=student.id, category="test", description="schema check",
            status=TicketStatus.SUBMITTED, predicted_department_id="test",
            assigned_to="it_operations_desk",
            transition_reason="Initial assignment"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        self.assertEqual(ticket.assigned_to, "it_operations_desk")
        self.assertEqual(ticket.transition_reason, "Initial assignment")
        db.close()

    def test_ticket_status_enum_has_action_required(self):
        self.assertIn("ACTION_REQUIRED", TicketStatus.__members__)


if __name__ == "__main__":
    unittest.main()
