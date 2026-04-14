from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum, Float, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone
import enum
import os
from dotenv import load_dotenv

# Load Supabase/Postgres credentials from environment
load_dotenv()

# Standard PostgreSQL connection format for Supabase:
# postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/postgres")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BranchEnum(enum.Enum):
    COMP_ENG = "Computer Engineering"
    IT = "Information Technology"
    MECH = "Mechanical"
    CIVIL = "Civil"
    ETC = "E&TC"

class TicketStatus(enum.Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    ACTION_REQUIRED = "Action Required"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"

class StudentProfile(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(50), default="student")
    
    branch = Column(Enum(BranchEnum), nullable=False)
    year_of_study = Column(Integer, nullable=False) # 1, 2, 3, 4
    
    # EOC / Accessibility Triggers
    is_disadvantaged = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    accessibility_requirements = Column(Text, nullable=True) 
    
    tickets = relationship("SupportTicket", back_populates="student")
    facility_bookings = relationship("FacilityBooking", back_populates="student")
    notifications = relationship("Notification", back_populates="student")

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    category = Column(String(50), nullable=False)
    predicted_department_id = Column(String(50)) 
    
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.SUBMITTED)
    urgent_flag = Column(Boolean, default=False)
    assigned_to = Column(String(100), nullable=True)
    transition_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    student = relationship("StudentProfile", back_populates="tickets")

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False) 
    title = Column(String(200), nullable=False)
    
    target_branches = Column(String(255)) 
    target_years = Column(String(50))     
    requires_disability_status = Column(Boolean, default=False)
    
    deadline = Column(DateTime, nullable=False)

class FacilityBooking(Base):
    __tablename__ = "facility_bookings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    facility_name = Column(String(100), nullable=False)
    
    booking_time = Column(DateTime, nullable=False)
    accessibility_override_applied = Column(Boolean, default=False)

    student = relationship("StudentProfile", back_populates="facility_bookings")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default="info")  # info, success, warning, urgent
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile", back_populates="notifications")


# --- Phase 21: Knowledge Base ---

class KBCategory(enum.Enum):
    IT = "IT"
    ACADEMIC = "Academic"
    FINANCE = "Finance"
    CAMPUS = "Campus"
    EOC = "EOC"

class KnowledgeBaseArticle(Base):
    __tablename__ = "kb_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(Enum(KBCategory), nullable=False)
    tags = Column(String(500), nullable=True)  # comma-separated
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# --- Phase 22: Chat System ---

class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile")
    messages = relationship("ChatMessage", back_populates="conversation")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    sender = Column(String(20), nullable=False)  # "student" or "bot" or "agent"
    content = Column(Text, nullable=False)
    sanitized_content = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    matched_kb_id = Column(Integer, ForeignKey("kb_articles.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    conversation = relationship("ChatConversation", back_populates="messages")


# --- Phase 23: Live Agent Escalation ---

class EscalationStatus(enum.Enum):
    WAITING = "Waiting"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"

class LiveEscalation(Base):
    __tablename__ = "live_escalations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=True)
    reason = Column(String(50), nullable=False)  # low_confidence, distress, student_request, eoc_flag
    confidence_at_escalation = Column(Float, nullable=True)
    assigned_agent_id = Column(String(100), nullable=True)
    status = Column(Enum(EscalationStatus), default=EscalationStatus.WAITING)
    priority = Column(String(20), default="normal")  # normal, urgent, eoc_emergency
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    student = relationship("StudentProfile")


# --- Phase 24: Scholarship Criteria Catalog ---

class CasteCategory(enum.Enum):
    GENERAL = "General"
    OBC = "OBC"
    SC = "SC"
    ST = "ST"
    EWS = "EWS"
    NT = "NT"

class ScholarshipScheme(Base):
    __tablename__ = "scholarship_schemes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    provider = Column(String(200), nullable=True)
    award_amount = Column(Float, nullable=True)
    deadline = Column(DateTime, nullable=True)
    category = Column(String(50), nullable=False)  # State, Central, Private, Institution
    scheme_type = Column(String(50), nullable=False)  # Merit, Need-based, Category
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    criteria = relationship("ScholarshipCriteria", back_populates="scheme")

class ScholarshipCriteria(Base):
    __tablename__ = "scholarship_criteria"

    id = Column(Integer, primary_key=True, index=True)
    scheme_id = Column(Integer, ForeignKey("scholarship_schemes.id"), nullable=False)
    param_name = Column(String(50), nullable=False)  # caste, income, gpa, branch, disability, year
    operator = Column(String(10), nullable=False)  # ==, <=, >=, in
    value = Column(String(200), nullable=False)  # JSON-encoded for lists

    scheme = relationship("ScholarshipScheme", back_populates="criteria")

class StudentEligibility(Base):
    __tablename__ = "student_eligibility"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    caste_category = Column(Enum(CasteCategory), nullable=True)
    annual_income = Column(Float, nullable=True)
    gpa = Column(Float, nullable=True)
    gender = Column(String(20), nullable=True)
    is_verified = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile")


# --- Phase 25: AI Profile Match History ---

class StudentOpportunityMatch(Base):
    __tablename__ = "student_opportunity_matches"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    opportunity_id = Column(Integer, nullable=False)  # References opportunities or scholarship_schemes
    opportunity_type = Column(String(30), nullable=False)  # opportunity, scholarship
    match_percentage = Column(Float, nullable=False)
    match_factors = Column(Text, nullable=True)  # JSON: {branch, year, gpa, caste, income}
    reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile")


# --- Phase 26: Application Tracker ---

class ApplicationStatusEnum(enum.Enum):
    APPLIED = "Applied"
    DOCS_SUBMITTED = "Documents Submitted"
    DECISION_PENDING = "Decision Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

class ApplicationRecord(Base):
    __tablename__ = "application_records"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    opportunity_id = Column(Integer, nullable=False)
    opportunity_type = Column(String(30), nullable=False)  # opportunity, scholarship
    opportunity_title = Column(String(300), nullable=False)
    status = Column(Enum(ApplicationStatusEnum), default=ApplicationStatusEnum.APPLIED)
    deadline = Column(DateTime, nullable=True)
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile")
    documents = relationship("ApplicationDocument", back_populates="application")

class ApplicationDocument(Base):
    __tablename__ = "application_documents"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("application_records.id"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # resume, sop, transcript, certificate
    file_path = Column(String(500), nullable=False)
    validation_state = Column(String(20), default="pending")  # pending, approved, rejected
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("ApplicationRecord", back_populates="documents")


# --- Phase 27: Career/Fellowship Inventory ---

class CareerListing(Base):
    __tablename__ = "career_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    listing_type = Column(String(50), nullable=False)  # internship, fellowship, full_time
    source = Column(String(100), nullable=True)  # internal, linkedin, internshala
    target_branches = Column(String(255), nullable=True)  # comma-separated
    target_years = Column(String(50), nullable=True)  # e.g. "3,4"
    link = Column(String(500), nullable=True)
    deadline = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Phase 28: Readiness Review History ---

class ReadinessReview(Base):
    __tablename__ = "readiness_reviews"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    document_type = Column(String(30), nullable=False)  # resume, sop
    opportunity_title = Column(String(300), nullable=True)
    feedback = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    student = relationship("StudentProfile")


# --- Phase 29: Faculty Approval Flow ---

class ApprovalStatusEnum(enum.Enum):
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REVISION_REQUESTED = "Revision Requested"

class FacultyEndorsement(Base):
    __tablename__ = "faculty_endorsements"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("application_records.id"), nullable=False)
    faculty_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    status = Column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    remarks = Column(Text, nullable=True)
    digital_signature = Column(String(500), nullable=True)
    requested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    acted_at = Column(DateTime, nullable=True)

    application = relationship("ApplicationRecord")


# --- Phase 30: Resource Inventory System ---

class CampusResource(Base):
    __tablename__ = "campus_resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    resource_type = Column(String(50), nullable=False)  # lab, makerspace, library, seminar_hall
    building = Column(String(100), nullable=True)
    floor = Column(String(20), nullable=True)
    seating_capacity = Column(Integer, nullable=True)
    has_heavy_machinery = Column(Boolean, default=False)
    is_accessible = Column(Boolean, default=True)
    equipment_list = Column(Text, nullable=True)  # JSON list
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Phase 31: Booking & Contingency Engine ---

class BookingStatusEnum(enum.Enum):
    CONFIRMED = "Confirmed"
    WAITLISTED = "Waitlisted"
    CANCELLED = "Cancelled"

class ResourceBooking(Base):
    __tablename__ = "resource_bookings"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("campus_resources.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    booking_date = Column(DateTime, nullable=False)
    start_time = Column(String(5), nullable=False)  # HH:MM
    end_time = Column(String(5), nullable=False)  # HH:MM
    status = Column(Enum(BookingStatusEnum), default=BookingStatusEnum.CONFIRMED)
    purpose = Column(String(300), nullable=True)
    accessibility_priority = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resource = relationship("CampusResource")
    student = relationship("StudentProfile")


# --- Phase 32: Confidential Mode Subsystems ---

class ConfidentialGrievance(Base):
    __tablename__ = "confidential_grievances"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    category = Column(String(100), nullable=False)  # discrimination, harassment, accessibility
    description_encrypted = Column(Text, nullable=False)
    encryption_key_hint = Column(String(100), nullable=True)
    status = Column(String(30), default="submitted")  # submitted, under_review, resolved
    assigned_eoc_officer = Column(String(100), nullable=True)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    student = relationship("StudentProfile")


# --- Phase 33: Disability Request Protocol ---

class DisabilityRequestType(enum.Enum):
    SCRIBE = "Scribe"
    RAMP_ACCESS = "Ramp Access"
    FORMAT_CHANGE = "Format Change"
    WHEELCHAIR_DESK = "Wheelchair Desk"
    SIGN_INTERPRETER = "Sign Language Interpreter"
    OTHER = "Other"

class DisabilityRequest(Base):
    __tablename__ = "disability_requests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    request_type = Column(Enum(DisabilityRequestType), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=True)
    urgency = Column(String(20), default="high")  # critical, high, medium
    status = Column(String(30), default="submitted")  # submitted, acknowledged, in_progress, resolved
    assigned_to = Column(String(100), nullable=True)
    fast_tracked = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    student = relationship("StudentProfile")


# --- Phase 34: Accessibility Physical Overlays ---

class AccessibilityAlert(Base):
    __tablename__ = "accessibility_alerts"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("campus_resources.id"), nullable=False)
    alert_type = Column(String(100), nullable=False)  # broken_elevator, no_wheelchair_desk, no_ramp, construction
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100), nullable=True)  # admin who toggled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resource = relationship("CampusResource")


# --- Phase 35: Accessibility Audit Log ---

class AccessibilityAudit(Base):
    __tablename__ = "accessibility_audits"

    id = Column(Integer, primary_key=True, index=True)
    page_or_view = Column(String(200), nullable=False)
    audit_type = Column(String(50), nullable=False)  # aria_labels, keyboard_nav, color_contrast, screen_reader
    status = Column(String(20), default="pending")  # pending, pass, fail, partial
    findings = Column(Text, nullable=True)
    audited_by = Column(String(100), nullable=True)
    audited_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Phase 37: Inclusion Analytics Generation ---

class InclusionReport(Base):
    __tablename__ = "inclusion_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False)  # grievance, scholarship, engagement, full
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    data_json = Column(Text, nullable=False)  # JSON blob of aggregated analytics
    generated_by = Column(String(100), nullable=True)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Phase 38: Integration Test Tracking ---

class IntegrationTestRun(Base):
    __tablename__ = "integration_test_runs"

    id = Column(Integer, primary_key=True, index=True)
    scenario_name = Column(String(200), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, passed, failed
    steps_total = Column(Integer, default=0)
    steps_passed = Column(Integer, default=0)
    error_details = Column(Text, nullable=True)
    executed_by = Column(String(100), nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


# --- Phase 39: Security Hardening ---

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # failed_login, rate_limit, suspicious_input, token_expired, prompt_injection
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    source_ip = Column(String(45), nullable=True)
    user_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Phase 40: Deployment & Health ---

class DeploymentRecord(Base):
    __tablename__ = "deployment_records"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    environment = Column(String(30), nullable=False)  # dev, staging, production
    status = Column(String(20), default="pending")  # pending, deploying, live, rolled_back
    deployed_by = Column(String(100), nullable=True)
    release_notes = Column(Text, nullable=True)
    deployed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    health_status = Column(String(20), default="unknown")  # healthy, degraded, down, unknown


def init_db():
    """Create all tables in the database. Called on startup from main.py."""
    Base.metadata.create_all(bind=engine)
