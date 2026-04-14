import logging
from enum import Enum
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Phase 18 / 19 / 20: Ticket Smart Routing, State Lifecycle, and Escalation Mechanisms

logger = logging.getLogger("OneBridge.TicketEngine")

# Phase 19: Strict State Machine Enums mapping lifecycle constraints
class TicketStatus(Enum):
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review" 
    ACTION_REQUIRED = "Action Required"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"

class TicketEngine:
    def __init__(self):
        self.SLA_DAYS_LIMIT = 3
    
    # Phase 19: Prevent arbitrary Logic leaps
    def advance_status(self, current_status: TicketStatus, target_status: TicketStatus, ticket_obj=None, db: Session = None):
        """
        State Machine validation guaranteeing strict linear processing.
        Optionally persists state change to DB if ticket_obj and db are provided.
        """
        valid_flows = {
            TicketStatus.SUBMITTED: [TicketStatus.UNDER_REVIEW, TicketStatus.ESCALATED],
            TicketStatus.UNDER_REVIEW: [TicketStatus.ACTION_REQUIRED, TicketStatus.RESOLVED, TicketStatus.ESCALATED],
            TicketStatus.ACTION_REQUIRED: [TicketStatus.UNDER_REVIEW, TicketStatus.RESOLVED],
            TicketStatus.ESCALATED: [TicketStatus.UNDER_REVIEW, TicketStatus.RESOLVED],
            TicketStatus.RESOLVED: [] # Terminal State
        }
        
        if target_status not in valid_flows[current_status]:
            error_msg = f"Illegal State Transition Flagged: Cannot map {current_status.name} -> {target_status.name}."
            logger.warning(error_msg)
            raise ValueError(error_msg)
            
        logger.info(f"State Validated: {current_status.name} -> {target_status.name}")

        # Persist to database if session provided
        if ticket_obj is not None and db is not None:
            from database_schema import TicketStatus as DBTicketStatus
            db_status = DBTicketStatus[target_status.name]
            ticket_obj.status = db_status
            db.commit()
            db.refresh(ticket_obj)
            logger.info(f"Ticket #{ticket_obj.id} persisted with status {target_status.name}")

        return target_status

    # Phase 20: Escalation Auto-Job Scrubber
    def audit_escalations(self, db: Session = None):
        """
        Cron-like job function mapping internal database timers for NFR compliance.
        Flags SLA breaches automatically overriding standard local priority.
        When db is provided, queries and updates tickets directly in Supabase.
        """
        now = datetime.utcnow()
        escalated_count = 0

        if db is not None:
            from database_schema import SupportTicket as DBTicket, TicketStatus as DBTicketStatus
            open_tickets = db.query(DBTicket).filter(
                DBTicket.status.notin_([DBTicketStatus.RESOLVED, DBTicketStatus.ESCALATED])
            ).all()

            for ticket in open_tickets:
                if ticket.created_at and (now - ticket.created_at).days >= self.SLA_DAYS_LIMIT:
                    logger.critical(f"SLA Breach Intercepted for Ticket #{ticket.id}. Bumping to Faculty Override.")
                    ticket.status = DBTicketStatus.ESCALATED
                    escalated_count += 1

            if escalated_count > 0:
                db.commit()
        
        return escalated_count

    # Phase 18: Map Local Classifier outputs dynamically to database owners
    def assign_coordinator(self, confidence_score: float, predicted_category: str):
        """
        Requires 80%+ Neural Network confidence to auto-execute an action without human handoff.
        """
        if confidence_score >= 80.0:
            if "IT Technical Support" in predicted_category:
                return "it_operations_desk"
            if "EOC Confidential" in predicted_category:
                return "vip_eoc_admin_1"
            if "Academic" in predicted_category:
                return "faculty_student_affairs"
        
        return "human_triage_queue"

# Global instantiator
lifecycle_manager = TicketEngine()
