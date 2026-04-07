import logging
from enum import Enum
from datetime import datetime, timedelta

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
    def advance_status(self, current_status: TicketStatus, target_status: TicketStatus):
        """
        State Machine validation guaranteeing strict linear processing.
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
        return target_status

    # Phase 20: Escalation Auto-Job Scrubber
    def audit_escalations(self, open_tickets: list):
        """
        Cron-like job function mapping internal database timers for NFR compliance.
        Flags SLA breaches automatically overriding standard local priority.
        """
        now = datetime.utcnow()
        escalated_count = 0
        
        for ticket in open_tickets:
            # We assume 'ticket' dict maps to database_schema.py Ticket Models
            if ticket['status'] in [TicketStatus.RESOLVED.value, TicketStatus.ESCALATED.value]:
                continue
                
            elapsed_time = now - ticket.get('created_at', now)
            
            if elapsed_time.days >= self.SLA_DAYS_LIMIT:
                # Trigger Auto Escalate Action 
                logger.critical(f"SLA Breach Intercepted for Ticket #{ticket.get('id')}. Bumping to Faculty Override.")
                ticket['status'] = TicketStatus.ESCALATED.value
                ticket['escalation_reason'] = "Timeout / 72+ Hours Unresolved"
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
