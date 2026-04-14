"""
Phase 4 Verification Tests
- Phase 4: Database Schema Engineering

Tests verify all 28 models, 9 enums, relationships, and constraints
using the shared in-memory SQLite database from conftest.
"""
import pytest
from sqlalchemy import inspect
from conftest import engine  # shared engine for inspect() calls
from database_schema import (
    Base, StudentProfile, SupportTicket, Opportunity, FacilityBooking,
    Notification, KnowledgeBaseArticle, ChatConversation, ChatMessage,
    LiveEscalation, ScholarshipScheme, ScholarshipCriteria, StudentEligibility,
    StudentOpportunityMatch, ApplicationRecord, ApplicationDocument,
    CareerListing, ReadinessReview, FacultyEndorsement, CampusResource,
    ResourceBooking, ConfidentialGrievance, DisabilityRequest,
    AccessibilityAlert, AccessibilityAudit, InclusionReport,
    IntegrationTestRun, SecurityEvent, DeploymentRecord,
    BranchEnum, TicketStatus, KBCategory, EscalationStatus,
    CasteCategory, ApplicationStatusEnum, ApprovalStatusEnum,
    BookingStatusEnum, DisabilityRequestType
)


# ============================================================================
# Schema Structure Tests
# ============================================================================

class TestPhase4SchemaStructure:
    """Verify all 28 tables are created with correct names."""

    def test_all_28_tables_exist(self):
        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        expected = {
            "students", "support_tickets", "opportunities", "facility_bookings",
            "notifications", "kb_articles", "chat_conversations", "chat_messages",
            "live_escalations", "scholarship_schemes", "scholarship_criteria",
            "student_eligibility", "student_opportunity_matches",
            "application_records", "application_documents", "career_listings",
            "readiness_reviews", "faculty_endorsements", "campus_resources",
            "resource_bookings", "confidential_grievances", "disability_requests",
            "accessibility_alerts", "accessibility_audits", "inclusion_reports",
            "integration_test_runs", "security_events", "deployment_records",
        }
        missing = expected - tables
        assert not missing, f"Missing tables: {missing}"

    def test_students_table_has_required_columns(self):
        inspector = inspect(engine)
        cols = {c["name"] for c in inspector.get_columns("students")}
        required = {"id", "prn", "name", "email", "branch", "year_of_study"}
        assert required.issubset(cols), f"Missing columns: {required - cols}"

    def test_support_tickets_has_foreign_key(self):
        inspector = inspect(engine)
        fks = inspector.get_foreign_keys("support_tickets")
        referred_tables = {fk["referred_table"] for fk in fks}
        assert "students" in referred_tables


# ============================================================================
# Enum Verification
# ============================================================================

class TestPhase4Enums:
    """Verify all 9 enum types have correct members."""

    def test_branch_enum(self):
        members = [e.value for e in BranchEnum]
        assert len(members) == 5
        assert BranchEnum.COMP_ENG in BranchEnum

    def test_ticket_status_enum(self):
        assert TicketStatus.SUBMITTED in TicketStatus
        assert TicketStatus.ESCALATED in TicketStatus
        assert len(list(TicketStatus)) == 5

    def test_kb_category_enum(self):
        assert KBCategory.IT in KBCategory
        assert KBCategory.EOC in KBCategory

    def test_escalation_status_enum(self):
        assert EscalationStatus.WAITING in EscalationStatus
        assert EscalationStatus.RESOLVED in EscalationStatus

    def test_caste_category_enum(self):
        members = list(CasteCategory)
        assert len(members) == 6
        assert CasteCategory.SC in CasteCategory
        assert CasteCategory.EWS in CasteCategory

    def test_application_status_enum(self):
        assert ApplicationStatusEnum.ACCEPTED in ApplicationStatusEnum
        assert ApplicationStatusEnum.REJECTED in ApplicationStatusEnum

    def test_approval_status_enum(self):
        assert ApprovalStatusEnum.PENDING in ApprovalStatusEnum
        assert ApprovalStatusEnum.APPROVED in ApprovalStatusEnum

    def test_booking_status_enum(self):
        assert BookingStatusEnum.CONFIRMED in BookingStatusEnum
        assert BookingStatusEnum.WAITLISTED in BookingStatusEnum

    def test_disability_request_type_enum(self):
        assert DisabilityRequestType.SCRIBE in DisabilityRequestType
        assert DisabilityRequestType.SIGN_INTERPRETER in DisabilityRequestType
        assert len(list(DisabilityRequestType)) == 6


# ============================================================================
# Relationship & CRUD Tests
# ============================================================================

class TestPhase4Relationships:
    """Verify ORM relationships and bidirectional navigation."""

    def _make_student(self, db, prn="2024CS001"):
        s = StudentProfile(
            prn=prn, name="Test Student", email=f"{prn}@pccoe.edu.in",
            branch=BranchEnum.COMP_ENG, year_of_study=1
        )
        db.add(s)
        db.flush()
        return s

    def test_student_ticket_relationship(self, db):
        student = self._make_student(db)
        ticket = SupportTicket(
            student_id=student.id, category="IT",
            description="LMS Login Issue", status=TicketStatus.SUBMITTED
        )
        db.add(ticket)
        db.flush()
        assert len(student.tickets) == 1
        assert student.tickets[0].description == "LMS Login Issue"
        assert ticket.student.prn == "2024CS001"

    def test_student_notification_relationship(self, db):
        student = self._make_student(db, prn="2024CS002")
        notif = Notification(
            student_id=student.id, title="Welcome", message="Welcome!", type="info"
        )
        db.add(notif)
        db.flush()
        assert len(student.notifications) == 1
        assert notif.student.prn == "2024CS002"

    def test_scholarship_criteria_relationship(self, db):
        scheme = ScholarshipScheme(
            title="Merit Award", provider="PCCOE",
            award_amount=50000.0, category="Institution", scheme_type="Merit"
        )
        db.add(scheme)
        db.flush()
        crit = ScholarshipCriteria(
            scheme_id=scheme.id, param_name="gpa", operator=">=", value="8.5"
        )
        db.add(crit)
        db.flush()
        assert len(scheme.criteria) == 1
        assert crit.scheme.title == "Merit Award"

    def test_application_document_relationship(self, db):
        student = self._make_student(db, prn="2024CS003")
        app = ApplicationRecord(
            student_id=student.id, opportunity_id=1,
            opportunity_type="scholarship", opportunity_title="Merit Award",
            status=ApplicationStatusEnum.APPLIED
        )
        db.add(app)
        db.flush()
        doc = ApplicationDocument(
            application_id=app.id, doc_type="transcript",
            file_path="/uploads/transcript.pdf"
        )
        db.add(doc)
        db.flush()
        assert len(app.documents) == 1
        assert doc.application.status == ApplicationStatusEnum.APPLIED

    def test_chat_conversation_messages(self, db):
        student = self._make_student(db, prn="2024CS004")
        conv = ChatConversation(student_id=student.id)
        db.add(conv)
        db.flush()
        msg = ChatMessage(
            conversation_id=conv.id, sender="student", content="Hello"
        )
        db.add(msg)
        db.flush()
        assert len(conv.messages) == 1
        assert conv.messages[0].sender == "student"
