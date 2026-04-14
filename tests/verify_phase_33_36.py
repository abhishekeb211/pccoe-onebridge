"""
Phase 33-36 Verification Tests
- Phase 33: Disability Request Protocol (fast-track, urgency ordering)
- Phase 34: Accessibility Physical Overlays (alerts on resources)
- Phase 35: Universal Screen Flow Audits (audit recording, summaries)
- Phase 36: Administrative Portal Views (aggregate metrics, student/ticket queries, CSV export)
"""
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import engine, fresh_db, seed_student, seed_resource
from database_schema import (
    Base, StudentProfile, BranchEnum, SupportTicket, TicketStatus,
    CampusResource, ApplicationRecord,
    DisabilityRequest, DisabilityRequestType,
    AccessibilityAlert, AccessibilityAudit,
    ResourceBooking, BookingStatusEnum,
    ConfidentialGrievance,
)


# ====== Phase 33: Disability Request Protocol ======

class TestDisabilityRequest(unittest.TestCase):
    def test_create_fast_track_request(self):
        db = fresh_db()
        student = seed_student(db, has_disability=True)

        req = DisabilityRequest(
            student_id=student.id,
            request_type=DisabilityRequestType.SCRIBE,
            description="Need a scribe for mid-semester exam",
            location="Exam Hall 3",
            urgency="critical",
            fast_tracked=True,
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        self.assertEqual(req.status, "submitted")
        self.assertTrue(req.fast_tracked)
        self.assertEqual(req.urgency, "critical")
        self.assertEqual(req.request_type, DisabilityRequestType.SCRIBE)

    def test_request_type_enum_values(self):
        self.assertEqual(len(DisabilityRequestType), 6)
        self.assertEqual(DisabilityRequestType.RAMP_ACCESS.value, "Ramp Access")
        self.assertEqual(DisabilityRequestType.SIGN_INTERPRETER.value, "Sign Language Interpreter")

    def test_resolve_request(self):
        db = fresh_db()
        student = seed_student(db, has_disability=True)

        req = DisabilityRequest(
            student_id=student.id,
            request_type=DisabilityRequestType.WHEELCHAIR_DESK,
            urgency="high",
        )
        db.add(req)
        db.commit()

        req.status = "resolved"
        req.resolved_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(req)

        self.assertEqual(req.status, "resolved")
        self.assertIsNotNone(req.resolved_at)

    def test_urgency_ordering(self):
        db = fresh_db()
        student = seed_student(db)

        for urgency in ["medium", "critical", "high"]:
            db.add(DisabilityRequest(
                student_id=student.id,
                request_type=DisabilityRequestType.OTHER,
                urgency=urgency,
            ))
        db.commit()

        requests = db.query(DisabilityRequest).all()
        urgency_order = {"critical": 0, "high": 1, "medium": 2}
        sorted_reqs = sorted(requests, key=lambda r: urgency_order.get(r.urgency, 3))

        self.assertEqual(sorted_reqs[0].urgency, "critical")
        self.assertEqual(sorted_reqs[1].urgency, "high")
        self.assertEqual(sorted_reqs[2].urgency, "medium")


# ====== Phase 34: Accessibility Physical Overlays ======

class TestAccessibilityAlerts(unittest.TestCase):
    def test_create_alert(self):
        db = fresh_db()
        resource = seed_resource(db)

        alert = AccessibilityAlert(
            resource_id=resource.id,
            alert_type="broken_elevator",
            description="Elevator in Main Block out of service since April 1",
            created_by="admin@pccoe.org",
        )
        db.add(alert)
        db.commit()
        db.refresh(alert)

        self.assertTrue(alert.is_active)
        self.assertEqual(alert.alert_type, "broken_elevator")

    def test_deactivate_alert(self):
        db = fresh_db()
        resource = seed_resource(db)

        alert = AccessibilityAlert(
            resource_id=resource.id,
            alert_type="no_ramp",
        )
        db.add(alert)
        db.commit()

        alert.is_active = False
        db.commit()
        db.refresh(alert)

        self.assertFalse(alert.is_active)

    def test_multiple_alerts_per_resource(self):
        db = fresh_db()
        resource = seed_resource(db)

        db.add(AccessibilityAlert(resource_id=resource.id, alert_type="broken_elevator"))
        db.add(AccessibilityAlert(resource_id=resource.id, alert_type="no_wheelchair_desk"))
        db.commit()

        active = db.query(AccessibilityAlert).filter(
            AccessibilityAlert.resource_id == resource.id,
            AccessibilityAlert.is_active == True,
        ).all()
        self.assertEqual(len(active), 2)

    def test_fully_accessible_check(self):
        db = fresh_db()
        resource = seed_resource(db, accessible=True)

        # No active alerts => fully accessible
        active_alerts = db.query(AccessibilityAlert).filter(
            AccessibilityAlert.resource_id == resource.id,
            AccessibilityAlert.is_active == True,
        ).all()
        fully_accessible = resource.is_accessible and len(active_alerts) == 0
        self.assertTrue(fully_accessible)

        # Add alert => not fully accessible
        db.add(AccessibilityAlert(resource_id=resource.id, alert_type="construction"))
        db.commit()

        active_alerts = db.query(AccessibilityAlert).filter(
            AccessibilityAlert.resource_id == resource.id,
            AccessibilityAlert.is_active == True,
        ).all()
        fully_accessible = resource.is_accessible and len(active_alerts) == 0
        self.assertFalse(fully_accessible)


# ====== Phase 35: Accessibility Audits ======

class TestAccessibilityAudits(unittest.TestCase):
    def test_create_audit(self):
        db = fresh_db()

        audit = AccessibilityAudit(
            page_or_view="dashboard",
            audit_type="aria_labels",
            status="pass",
            findings="All interactive elements have proper ARIA labels.",
            audited_by="qa_team",
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)

        self.assertEqual(audit.status, "pass")
        self.assertEqual(audit.page_or_view, "dashboard")

    def test_audit_status_values(self):
        db = fresh_db()

        for status in ["pass", "fail", "partial"]:
            db.add(AccessibilityAudit(
                page_or_view="test_page",
                audit_type="keyboard_nav",
                status=status,
            ))
        db.commit()

        audits = db.query(AccessibilityAudit).all()
        statuses = {a.status for a in audits}
        self.assertEqual(statuses, {"pass", "fail", "partial"})

    def test_audit_summary_aggregation(self):
        db = fresh_db()

        db.add(AccessibilityAudit(page_or_view="dashboard", audit_type="aria_labels", status="pass"))
        db.add(AccessibilityAudit(page_or_view="dashboard", audit_type="keyboard_nav", status="fail"))
        db.add(AccessibilityAudit(page_or_view="support", audit_type="color_contrast", status="pass"))
        db.add(AccessibilityAudit(page_or_view="support", audit_type="screen_reader", status="partial"))
        db.commit()

        audits = db.query(AccessibilityAudit).all()
        pages = {}
        for a in audits:
            if a.page_or_view not in pages:
                pages[a.page_or_view] = {"pass": 0, "fail": 0, "partial": 0}
            pages[a.page_or_view][a.status] += 1

        self.assertEqual(pages["dashboard"]["pass"], 1)
        self.assertEqual(pages["dashboard"]["fail"], 1)
        self.assertEqual(pages["support"]["partial"], 1)


# ====== Phase 36: Administrative Portal ======

class TestAdminPortal(unittest.TestCase):
    def test_aggregate_student_counts(self):
        db = fresh_db()
        seed_student(db, prn="S001", has_disability=True)
        seed_student(db, prn="S002", has_disability=False)
        seed_student(db, prn="S003", has_disability=True)

        total = db.query(StudentProfile).count()
        with_disability = db.query(StudentProfile).filter(StudentProfile.has_disability == True).count()

        self.assertEqual(total, 3)
        self.assertEqual(with_disability, 2)

    def test_ticket_status_aggregation(self):
        db = fresh_db()
        student = seed_student(db)

        db.add(SupportTicket(student_id=student.id, category="IT", description="Test", status=TicketStatus.SUBMITTED))
        db.add(SupportTicket(student_id=student.id, category="EOC", description="Test2", status=TicketStatus.ESCALATED))
        db.add(SupportTicket(student_id=student.id, category="IT", description="Test3", status=TicketStatus.RESOLVED))
        db.commit()

        total = db.query(SupportTicket).count()
        open_count = db.query(SupportTicket).filter(
            SupportTicket.status.in_([TicketStatus.SUBMITTED, TicketStatus.UNDER_REVIEW])
        ).count()
        escalated = db.query(SupportTicket).filter(SupportTicket.status == TicketStatus.ESCALATED).count()

        self.assertEqual(total, 3)
        self.assertEqual(open_count, 1)
        self.assertEqual(escalated, 1)

    def test_student_filter_by_branch(self):
        db = fresh_db()
        seed_student(db, prn="S001")  # COMP_ENG
        seed_student(db, prn="S002")  # COMP_ENG

        filtered = db.query(StudentProfile).filter(
            StudentProfile.branch == BranchEnum.COMP_ENG
        ).count()
        self.assertEqual(filtered, 2)

    def test_csv_export_format(self):
        """Verify CSV generation logic produces correct headers and rows."""
        db = fresh_db()
        s = seed_student(db, prn="CSV001", name="CSV Test Student")

        import io
        import csv
        students = db.query(StudentProfile).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["PRN", "Name", "Email", "Branch", "Year", "Role", "Has Disability", "Is Disadvantaged"])
        for st in students:
            writer.writerow([
                st.prn, st.name, st.email,
                st.branch.value if st.branch else "",
                st.year_of_study, st.role,
                st.has_disability, st.is_disadvantaged,
            ])

        csv_content = output.getvalue()
        self.assertIn("PRN", csv_content)
        self.assertIn("CSV001", csv_content)
        self.assertIn("CSV Test Student", csv_content)
        lines = csv_content.strip().split("\n")
        self.assertEqual(len(lines), 2)  # header + 1 data row


# ====== Schema Integrity ======

class TestPhase33_36Schema(unittest.TestCase):
    def test_all_tables_created(self):
        db = fresh_db()
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        required = [
            "disability_requests",
            "accessibility_alerts",
            "accessibility_audits",
        ]
        for t in required:
            self.assertIn(t, table_names, f"Missing table: {t}")


if __name__ == "__main__":
    unittest.main()
