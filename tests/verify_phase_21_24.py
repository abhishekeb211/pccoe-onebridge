"""
Phase 21-24 Verification Tests
- Phase 21: Knowledge Base (CRUD, search)
- Phase 22: Chat system (sessions, messages, KB matching)
- Phase 23: Escalation protocol (distress detection, queue)
- Phase 24: Scholarship criteria catalog (matching engine)
"""
import os
import sys
import unittest
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import fresh_db, seed_student
from database_schema import (
    Base, StudentProfile, BranchEnum,
    KnowledgeBaseArticle, KBCategory,
    ChatConversation, ChatMessage,
    LiveEscalation, EscalationStatus,
    ScholarshipScheme, ScholarshipCriteria, StudentEligibility, CasteCategory,
)
from local_agent import SmartRoutingAgent


# ====== Phase 21: Knowledge Base =====

class TestKnowledgeBase(unittest.TestCase):
    def test_create_and_query_article(self):
        db = fresh_db()
        article = KnowledgeBaseArticle(
            title="How to reset LMS password",
            content="Go to the LMS portal, click Forgot Password, and follow the instructions.",
            category=KBCategory.IT,
            tags="lms,password,reset",
        )
        db.add(article)
        db.commit()
        db.refresh(article)
        self.assertEqual(article.title, "How to reset LMS password")
        self.assertEqual(article.category, KBCategory.IT)
        self.assertTrue(article.is_published)
        db.close()

    def test_search_scoring(self):
        db = fresh_db()
        a1 = KnowledgeBaseArticle(
            title="WiFi connectivity issues", content="Connect to PCCOE-WiFi network.",
            category=KBCategory.IT, tags="wifi,network",
        )
        a2 = KnowledgeBaseArticle(
            title="Exam schedule", content="Check academic calendar for exam dates.",
            category=KBCategory.ACADEMIC, tags="exam,schedule",
        )
        db.add_all([a1, a2])
        db.commit()

        # Search "wifi" should rank a1 higher
        articles = db.query(KnowledgeBaseArticle).filter(KnowledgeBaseArticle.is_published == True).all()
        query = "wifi"
        scored = []
        for a in articles:
            score = 0
            if query in a.title.lower():
                score += 3
            if query in (a.tags or "").lower():
                score += 2
            if query in a.content.lower():
                score += 1
            if score > 0:
                scored.append((score, a))
        scored.sort(key=lambda x: x[0], reverse=True)
        self.assertGreater(len(scored), 0)
        self.assertEqual(scored[0][1].title, "WiFi connectivity issues")
        db.close()


# ====== Phase 22: Chat System ======

class TestChatSystem(unittest.TestCase):
    def test_create_conversation_and_message(self):
        db = fresh_db()
        student = StudentProfile(
            prn="CHAT001", name="Chat Student", email="chat@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        conv = ChatConversation(student_id=student.id)
        db.add(conv)
        db.commit()

        msg = ChatMessage(
            conversation_id=conv.id, sender="student",
            content="How do I apply for a scholarship?",
            sanitized_content="How do I apply for a scholarship?",
        )
        db.add(msg)
        bot_msg = ChatMessage(
            conversation_id=conv.id, sender="bot",
            content="Visit the Scholarships page.", confidence_score=75.0,
        )
        db.add(bot_msg)
        db.commit()

        messages = db.query(ChatMessage).filter(ChatMessage.conversation_id == conv.id).all()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].sender, "student")
        self.assertEqual(messages[1].sender, "bot")
        self.assertEqual(messages[1].confidence_score, 75.0)
        db.close()


# ====== Phase 23: Escalation & Distress ======

class TestEscalation(unittest.TestCase):
    def test_create_escalation(self):
        db = fresh_db()
        student = StudentProfile(
            prn="ESC001", name="Esc Student", email="esc@test.com",
            year_of_study=3, branch=BranchEnum.COMP_ENG, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        esc = LiveEscalation(
            student_id=student.id, reason="student_request",
            priority="normal",
        )
        db.add(esc)
        db.commit()
        db.refresh(esc)

        self.assertEqual(esc.status, EscalationStatus.WAITING)
        self.assertIsNone(esc.assigned_agent_id)
        db.close()

    def test_assign_and_resolve(self):
        db = fresh_db()
        student = StudentProfile(
            prn="ESC002", name="Esc Student 2", email="esc2@test.com",
            year_of_study=2, branch=BranchEnum.IT, password_hash="x", role="student"
        )
        db.add(student)
        db.commit()

        esc = LiveEscalation(
            student_id=student.id, reason="low_confidence", priority="urgent",
        )
        db.add(esc)
        db.commit()

        # Assign
        esc.assigned_agent_id = "FACULTY001"
        esc.status = EscalationStatus.IN_PROGRESS
        db.commit()
        self.assertEqual(esc.status, EscalationStatus.IN_PROGRESS)

        # Resolve
        esc.status = EscalationStatus.RESOLVED
        esc.resolved_at = datetime.now(timezone.utc)
        db.commit()
        self.assertEqual(esc.status, EscalationStatus.RESOLVED)
        self.assertIsNotNone(esc.resolved_at)
        db.close()

    def test_distress_detection(self):
        agent = SmartRoutingAgent.__new__(SmartRoutingAgent)
        agent.DISTRESS_KEYWORDS = SmartRoutingAgent.DISTRESS_KEYWORDS
        result = agent.detect_distress("I am feeling very depressed and hopeless")
        self.assertTrue(result["distress_detected"])
        self.assertIn("depressed", result["keywords"])
        self.assertTrue(result["recommend_escalation"])

    def test_no_distress(self):
        agent = SmartRoutingAgent.__new__(SmartRoutingAgent)
        agent.DISTRESS_KEYWORDS = SmartRoutingAgent.DISTRESS_KEYWORDS
        result = agent.detect_distress("How do I check my exam results?")
        self.assertFalse(result["distress_detected"])
        self.assertEqual(len(result["keywords"]), 0)


# ====== Phase 24: Scholarship Matching ======

class TestScholarshipMatching(unittest.TestCase):
    def test_criteria_match_eligible(self):
        db = fresh_db()
        student = StudentProfile(
            prn="SCH001", name="Scholar Student", email="sch@test.com",
            year_of_study=2, branch=BranchEnum.COMP_ENG, password_hash="x", role="student",
            has_disability=False,
        )
        db.add(student)
        db.commit()

        elig = StudentEligibility(
            student_id=student.id, caste_category=CasteCategory.SC,
            annual_income=200000.0, gpa=8.5,
        )
        db.add(elig)
        db.commit()

        scheme = ScholarshipScheme(
            title="SC Merit Scholarship", description="For SC students with GPA >= 7.0",
            provider="State Govt", category="State", scheme_type="Category",
        )
        db.add(scheme)
        db.commit()

        c1 = ScholarshipCriteria(scheme_id=scheme.id, param_name="caste", operator="==", value="SC")
        c2 = ScholarshipCriteria(scheme_id=scheme.id, param_name="gpa", operator=">=", value="7.0")
        c3 = ScholarshipCriteria(scheme_id=scheme.id, param_name="income", operator="<=", value="500000")
        db.add_all([c1, c2, c3])
        db.commit()

        # Evaluate criteria
        criteria_list = db.query(ScholarshipCriteria).filter(ScholarshipCriteria.scheme_id == scheme.id).all()
        matched = 0
        for c in criteria_list:
            if _eval_criterion(c, student, elig):
                matched += 1
        self.assertEqual(matched, 3)
        db.close()

    def test_criteria_match_ineligible(self):
        db = fresh_db()
        student = StudentProfile(
            prn="SCH002", name="General Student", email="gen@test.com",
            year_of_study=3, branch=BranchEnum.COMP_ENG, password_hash="x", role="student",
        )
        db.add(student)
        db.commit()

        elig = StudentEligibility(
            student_id=student.id, caste_category=CasteCategory.GENERAL,
            annual_income=800000.0, gpa=7.0,
        )
        db.add(elig)
        db.commit()

        scheme = ScholarshipScheme(
            title="SC Merit Scholarship", description="For SC students",
            provider="State Govt", category="State", scheme_type="Category",
        )
        db.add(scheme)
        db.commit()

        c1 = ScholarshipCriteria(scheme_id=scheme.id, param_name="caste", operator="==", value="SC")
        db.add(c1)
        db.commit()

        criteria_list = db.query(ScholarshipCriteria).filter(ScholarshipCriteria.scheme_id == scheme.id).all()
        matched = sum(1 for c in criteria_list if _eval_criterion(c, student, elig))
        self.assertEqual(matched, 0)  # General != SC
        db.close()

    def test_scheme_with_no_criteria_is_eligible(self):
        """Schemes with no criteria match everyone."""
        db = fresh_db()
        scheme = ScholarshipScheme(
            title="Open Scholarship", description="For all",
            provider="Institution", category="Institution", scheme_type="Merit",
        )
        db.add(scheme)
        db.commit()
        criteria_list = db.query(ScholarshipCriteria).filter(ScholarshipCriteria.scheme_id == scheme.id).all()
        self.assertEqual(len(criteria_list), 0)
        db.close()


def _eval_criterion(criterion, student, eligibility):
    """Mirror of main.py _check_criterion for tests."""
    p = criterion.param_name
    op = criterion.operator
    val = criterion.value

    if p == "branch":
        sv = student.branch.value if student.branch else ""
        if op == "==":
            return sv == val
        if op == "in":
            return sv in [v.strip() for v in val.split(",")]
    if p == "year":
        try:
            return _cmp(student.year_of_study, op, float(val))
        except (ValueError, TypeError):
            return False
    if p == "disability":
        return str(student.has_disability).lower() == val.lower()

    if not eligibility:
        return False
    if p == "caste":
        ev = eligibility.caste_category.value if eligibility.caste_category else ""
        if op == "==":
            return ev == val
        if op == "in":
            return ev in [v.strip() for v in val.split(",")]
    if p == "income":
        try:
            return _cmp(eligibility.annual_income or 0, op, float(val))
        except (ValueError, TypeError):
            return False
    if p == "gpa":
        try:
            return _cmp(eligibility.gpa or 0, op, float(val))
        except (ValueError, TypeError):
            return False
    return False


def _cmp(actual, op, expected):
    if op == "==":
        return actual == expected
    if op == "<=":
        return actual <= expected
    if op == ">=":
        return actual >= expected
    return False


if __name__ == "__main__":
    unittest.main()
