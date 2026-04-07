from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

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
    APPROVED = "Approved"
    RESOLVED = "Resolved"

class StudentProfile(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    prn = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    
    branch = Column(Enum(BranchEnum), nullable=False)
    year_of_study = Column(Integer, nullable=False) # 1, 2, 3, 4
    
    # EOC / Accessibility Triggers (Must be protected at API layer)
    is_disadvantaged = Column(Boolean, default=False)
    has_disability = Column(Boolean, default=False)
    accessibility_requirements = Column(Text, nullable=True) # E.g., "Wheelchair", "Scribe"
    
    # Relationships
    tickets = relationship("SupportTicket", back_populates="student")
    facility_bookings = relationship("FacilityBooking", back_populates="student")

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    category = Column(String(50), nullable=False) # E.g. "EOC", "Academic", "IT"
    predicted_department_id = Column(String(50)) # Populated by Local NLP Agent
    
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.SUBMITTED)
    urgent_flag = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student = relationship("StudentProfile", back_populates="tickets")

class Opportunity(Base):
    """Scholarships, Fellowships, Internships"""
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False) # "Scholarship", "Fellowship", "Job"
    title = Column(String(200), nullable=False)
    
    # Filtering markers used by the AI Recommendation Engine
    target_branches = Column(String(255)) # CSV of branches
    target_years = Column(String(50))     # SV of years
    requires_disability_status = Column(Boolean, default=False)
    
    deadline = Column(DateTime, nullable=False)

class FacilityBooking(Base):
    __tablename__ = "facility_bookings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    facility_name = Column(String(100), nullable=False)
    
    booking_time = Column(DateTime, nullable=False)
    accessibility_override_applied = Column(Boolean, default=False) # Bypasses waitlist if true
    
    # Relationships
    student = relationship("StudentProfile", back_populates="facility_bookings")

# Note: In Phase 6 (Backend Scaffolding), Pydantic schemas will be tightly mapped to these SQLAlchemy definitions.
