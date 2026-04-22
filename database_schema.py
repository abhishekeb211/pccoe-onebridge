from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from datetime import datetime, timezone
from typing import List, Optional
import enum

# --- Unified Domain Enums ---

class BranchEnum(str, enum.Enum):
    COMP_ENG = "Computer Engineering"
    IT = "Information Technology"
    MECH = "Mechanical"
    CIVIL = "Civil"
    ETC = "E&TC"

class TicketStatus(str, enum.Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    ACTION_REQUIRED = "Action Required"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"

class KBCategory(str, enum.Enum):
    IT = "IT"
    ACADEMIC = "Academic"
    FINANCE = "Finance"
    CAMPUS = "Campus"
    EOC = "EOC"

class ApplicationStatusEnum(str, enum.Enum):
    APPLIED = "Applied"
    DOCS_SUBMITTED = "Documents Submitted"
    DECISION_PENDING = "Decision Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"

# --- Models ---

class DisabilityTypeEnum(str, enum.Enum):
    VISUAL = "visual"
    HEARING = "hearing"
    MOBILITY = "mobility"
    COGNITIVE = "cognitive"
    MULTIPLE = "multiple"
    OTHER = "other"

class StudentProfile(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    id: int
    prn: str
    name: str
    email: str
    password_hash: Optional[str] = None
    role: str = "student"
    branch: BranchEnum
    year_of_study: int
    is_disadvantaged: bool = False
    has_disability: bool = False
    disability_type: Optional[DisabilityTypeEnum] = None
    accessibility_requirements: Optional[List[str]] = None

    @model_validator(mode="after")
    def validate_disability(self):
        if self.has_disability and not self.disability_type:
            raise ValueError("disability_type must be set if has_disability is True")
        return self

class SupportTicket(BaseModel):
    id: int
    student_id: int
    category: str
    predicted_department_id: Optional[str] = None
    description: str
    status: TicketStatus = TicketStatus.SUBMITTED
    urgent_flag: bool = False
    assigned_to: Optional[str] = None
    transition_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Opportunity(BaseModel):
    id: int
    type: str
    title: str
    target_branches: Optional[str] = None
    target_years: Optional[str] = None
    requires_disability_status: bool = False
    deadline: datetime

class FacilityBooking(BaseModel):
    id: int
    student_id: int
    facility_name: str
    booking_time: datetime
    accessibility_override_applied: bool = False

class Notification(BaseModel):
    id: int
    student_id: int
    title: str
    message: str
    type: str = "info" # info, success, warning, urgent
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class KnowledgeBaseArticle(BaseModel):
    id: int
    title: str
    content: str
    category: KBCategory
    tags: Optional[str] = None
    is_published: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatMessage(BaseModel):
    id: int
    conversation_id: int
    sender: str # "student", "bot", "agent"
    content: str
    sanitized_content: Optional[str] = None
    confidence_score: Optional[float] = None
    matched_kb_id: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatConversation(BaseModel):
    id: int
    student_id: int
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[ChatMessage] = []

class ScholarshipScheme(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    provider: Optional[str] = None
    award_amount: Optional[float] = None
    deadline: Optional[datetime] = None
    category: str
    scheme_type: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ApplicationRecord(BaseModel):
    id: int
    student_id: int
    opportunity_id: int
    opportunity_type: str
    opportunity_title: str
    status: ApplicationStatusEnum = ApplicationStatusEnum.APPLIED
    deadline: Optional[datetime] = None
    applied_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SecurityEvent(BaseModel):
    id: int
    event_type: str
    severity: str = "medium"
    source_ip: Optional[str] = None
    user_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

def init_db():
    """Validates and creates empty JSON registries for all core models."""
    import os
    import json
    data_dir = os.getenv("ONEBRIDGE_DATA_DIR", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    mapping = {
        "StudentProfile": "students.json",
        "SupportTicket": "tickets.json",
        "Opportunity": "opportunities.json",
        "FacilityBooking": "facility_bookings.json",
        "Notification": "notifications.json",
        "KnowledgeBaseArticle": "knowledge_base.json",
        "ChatConversation": "chat_conversations.json",
        "ChatMessage": "chat_messages.json",
        "ScholarshipScheme": "scholarships.json",
        "ApplicationRecord": "applications.json",
        "SecurityEvent": "security_events.json"
    }
    
    for filename in mapping.values():
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
    
    print(f"OneBridge JSON Registry Initialized at: {data_dir}")
