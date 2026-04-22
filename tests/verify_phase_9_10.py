"""
Phase 9-10 Verification Tests (JSON Version)
- Phase 9: Authentication, JWT, and Ticket Lifecycle Engine
- Phase 10: Role-Based Access Control (RBAC) System
"""
import pytest
from datetime import datetime, timezone, timedelta
from conftest import seed_student
from database_schema import (
    StudentProfile, SupportTicket, TicketStatus, BranchEnum,
)
from json_db import db

# ============================================================================
# Phase 9: Authentication & JWT + Ticket Lifecycle Engine
# ============================================================================

class TestAuthModule:
    def test_jwt_token_creation(self):
        """JWT token creation must produce a valid string."""
        from auth import create_access_token
        token = create_access_token(data={"sub": "TEST001", "roles": ["student"]})
        assert isinstance(token, str)
        assert len(token) > 20

    def test_jwt_token_decode(self):
        """JWT token must decode back to original claims."""
        from auth import create_access_token, SECRET_KEY, ALGORITHM
        from jose import jwt
        token = create_access_token(
            data={"sub": "TEST002", "roles": ["student", "eoc_eligible"]},
            expires_delta=timedelta(minutes=30),
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "TEST002"
        assert "student" in payload["roles"]
        assert "exp" in payload

    def test_password_hashing(self):
        """Password hash must verify correctly."""
        from auth import get_password_hash, verify_password
        plain = "SecurePass123"
        try:
            hashed = get_password_hash(plain)
            assert hashed != plain
            assert verify_password(plain, hashed) is True
            assert verify_password("WrongPass", hashed) is False
        except (ValueError, AttributeError):
            pytest.skip("bcrypt version incompatible with passlib")

    def test_role_builder(self):
        """_build_roles must derive roles from student profile."""
        from auth import _build_roles

        class MockStudent:
            role = "student"
            is_disadvantaged = False
            has_disability = False

        roles = _build_roles(MockStudent())
        assert "student" in roles
        assert "eoc_eligible" not in roles

    def test_role_builder_eoc_eligible(self):
        """Disadvantaged/disabled students should get eoc_eligible role."""
        from auth import _build_roles

        class MockStudent:
            role = "student"
            is_disadvantaged = True
            has_disability = False

        roles = _build_roles(MockStudent())
        assert "eoc_eligible" in roles


class TestTicketLifecycle:
    def test_valid_state_transitions(self):
        """Valid ticket state transitions must succeed."""
        from ticket_lifecycle import TicketStatus as TLS, lifecycle_manager

        # SUBMITTED -> UNDER_REVIEW
        result = lifecycle_manager.advance_status(TLS.SUBMITTED, TLS.UNDER_REVIEW)
        assert result == TLS.UNDER_REVIEW

    def test_invalid_state_transition_raises(self):
        """Invalid ticket state transitions must raise ValueError."""
        from ticket_lifecycle import TicketStatus as TLS, lifecycle_manager

        with pytest.raises(ValueError, match="Illegal State Transition"):
            lifecycle_manager.advance_status(TLS.SUBMITTED, TLS.RESOLVED)

    def test_coordinator_assignment_high_confidence(self):
        """High confidence (>=80%) should auto-assign to correct department."""
        from ticket_lifecycle import lifecycle_manager

        assert lifecycle_manager.assign_coordinator(90.0, "IT Technical Support") == "it_operations_desk"
        assert lifecycle_manager.assign_coordinator(85.0, "EOC Confidential") == "vip_eoc_admin_1"

    def test_sla_breach_detection_json(self):
        """Tickets older than SLA limit should be candidate for escalation."""
        from ticket_lifecycle import lifecycle_manager

        student = seed_student(prn="SLA910")
        # Create old ticket (4 days old)
        old_time = datetime.now(timezone.utc) - timedelta(days=4)
        ticket = SupportTicket(
            id=0,
            student_id=student["id"],
            category="academic",
            description="Old ticket for SLA test",
            status=TicketStatus.SUBMITTED,
            created_at=old_time,
        )
        db.insert(ticket)

        # Audit
        count = lifecycle_manager.audit_escalations()
        assert count >= 1
        
        updated = db.get_by_id(SupportTicket, ticket.id)
        assert updated.status == TicketStatus.ESCALATED


# ============================================================================
# Phase 10: Role-Based Access Control (RBAC)
# ============================================================================

class TestRBACSystem:
    def test_rbac_checker_allows_valid_roles(self):
        from role_manager import RoleChecker
        checker = RoleChecker(["eoc_admin", "super_admin"])
        user = {"prn": "ADM001", "roles": ["eoc_admin"]}
        assert checker(user) == user

    def test_rbac_checker_blocks_invalid_roles(self):
        from role_manager import RoleChecker
        from fastapi import HTTPException
        checker = RoleChecker(["eoc_admin", "super_admin"])
        user = {"prn": "STU001", "roles": ["student"]}
        with pytest.raises(HTTPException) as exc_info:
            checker(user)
        assert exc_info.value.status_code == 403
