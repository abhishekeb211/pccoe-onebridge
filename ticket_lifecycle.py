import logging
from enum import Enum
from datetime import datetime, timedelta, UTC
from json_db import db
from database_schema import SupportTicket, TicketStatus as DBTicketStatus

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
    def advance_status(self, current_status: TicketStatus, target_status: TicketStatus, ticket_id: int = None):
        """
        State Machine validation guaranteeing strict linear processing.
        Optionally persists state change to JSON DB if ticket_id is provided.
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

        # Persist to JSON database if ID provided
        if ticket_id is not None:
            updated = db.update(SupportTicket, ticket_id, status=DBTicketStatus[target_status.name])
            if updated:
                logger.info(f"Ticket #{ticket_id} persisted with status {target_status.name}")

        return target_status

    # Phase 20: Escalation Auto-Job Scrubber
    def audit_escalations(self):
        """
        Cron-like job function mapping internal database timers for NFR compliance.
        Flags SLA breaches automatically overriding standard local priority.
        Queries and updates tickets directly in JSON storage.
        """
        now = datetime.now(UTC)
        escalated_count = 0

        open_tickets = db.get_all(SupportTicket)
        # Filter for non-terminal, non-escalated states
        non_terminal = [DBTicketStatus.SUBMITTED, DBTicketStatus.UNDER_REVIEW, DBTicketStatus.ACTION_REQUIRED]
        
        for ticket in open_tickets:
            if ticket.status in non_terminal:
                if ticket.created_at:
                    created_at = ticket.created_at
                    # Ensure timezone awareness
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=UTC)
                    
                    if (now - created_at).days >= self.SLA_DAYS_LIMIT:
                        logger.critical(f"SLA Breach Intercepted for Ticket #{ticket.id}. Bumping to Faculty Override.")
                        db.update(SupportTicket, ticket.id, status=DBTicketStatus.ESCALATED)
                        escalated_count += 1
        
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
