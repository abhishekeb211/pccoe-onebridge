"""
Phase 13-14 Verification Tests
- Phase 13: Local Agent Initialization (SmartRoutingAgent, background model loading)
- Phase 14: AI Smart Routing Classifier (classification, fallback, distress, KB matching)

These tests load the actual NLP model (~12s first run) for integration verification.
"""
import pytest
import os
import threading

os.environ["DATABASE_URL"] = "sqlite:///tests/test_phase13.db"

from local_agent import SmartRoutingAgent


# Shared agent instance (model loads once for all tests)
@pytest.fixture(scope="module")
def agent():
    a = SmartRoutingAgent()
    a._ready.wait(timeout=60)
    return a


# ============================================================================
# Phase 13: Local Agent Initialization
# ============================================================================

class TestPhase13LocalAgentInit:
    """Phase 13: Verify the local NLP agent initializes correctly."""

    def test_agent_loads_in_background_thread(self):
        """Model loading uses a background thread via threading.Event."""
        a = SmartRoutingAgent()
        assert isinstance(a._ready, threading.Event)
        # Wait for it to finish (may already be cached)
        a._ready.wait(timeout=60)
        assert a._ready.is_set()

    def test_agent_has_classifier_after_init(self, agent):
        """After initialization, the classifier pipeline must be available."""
        assert agent.classifier is not None

    def test_agent_has_six_routing_categories(self, agent):
        """Agent must define exactly 6 routing categories."""
        assert len(agent.categories) == 6
        expected = {
            "IT Technical Support (WiFi, LMS, Passwords)",
            "Academic Advising (Exam, Syllabus, Mentorship)",
            "Financial Aid & Scholarships",
            "Emergency Wellbeing & Counseling",
            "EOC Confidential Disability Services",
            "Facilities & Housing",
        }
        assert set(agent.categories) == expected

    def test_classify_returns_required_keys(self, agent):
        """classify_ticket must return predicted_department, confidence_score, is_eoc_flag."""
        result = agent.classify_ticket("I can't log into the LMS portal")
        assert "predicted_department" in result
        assert "confidence_score" in result
        assert "is_eoc_flag" in result

    def test_confidence_is_float_percentage(self, agent):
        """Confidence score must be a float percentage in (0, 100]."""
        result = agent.classify_ticket("Need help with exam syllabus")
        assert isinstance(result["confidence_score"], float)
        assert 0.0 < result["confidence_score"] <= 100.0


# ============================================================================
# Phase 14: AI Smart Routing Classifier
# ============================================================================

class TestPhase14SmartRouting:
    """Phase 14: Verify routing accuracy, fallback logic, distress detection, KB matching."""

    def test_eoc_flag_detection(self, agent):
        """EOC-related queries must set is_eoc_flag or route to EOC Confidential."""
        result = agent.classify_ticket(
            "I need EOC confidential disability services for my wheelchair access grievance"
        )
        assert result["is_eoc_flag"] or "EOC" in result["predicted_department"], \
            f"Expected EOC routing, got: {result['predicted_department']}"

    def test_fallback_keyword_it(self):
        """Keyword fallback must route IT keywords when model is unavailable."""
        agent = SmartRoutingAgent.__new__(SmartRoutingAgent)
        agent.classifier = None
        agent.categories = []
        result = agent._fallback("My wifi is not working on campus")
        assert "IT Technical Support" in result["predicted_department"]

    def test_fallback_keyword_financial(self):
        """Keyword fallback must route financial keywords correctly."""
        agent = SmartRoutingAgent.__new__(SmartRoutingAgent)
        agent.classifier = None
        agent.categories = []
        result = agent._fallback("I need fee refund for my scholarship tuition")
        assert "Financial" in result["predicted_department"]

    def test_fallback_returns_valid_structure(self):
        """Fallback results must have the same structure as model results."""
        agent = SmartRoutingAgent.__new__(SmartRoutingAgent)
        agent.classifier = None
        agent.categories = []
        result = agent._fallback("Some general query")
        assert "predicted_department" in result
        assert "confidence_score" in result
        assert "is_eoc_flag" in result

    def test_detect_distress(self, agent):
        """detect_distress must flag crisis language."""
        result = agent.detect_distress("I feel suicidal and hopeless, I want to end it all")
        assert result["distress_detected"] is True
        assert result["recommend_escalation"] is True
        assert len(result["keywords"]) > 0

    def test_detect_distress_safe_text(self, agent):
        """detect_distress must not flag normal text."""
        result = agent.detect_distress("I need help registering for next semester courses")
        assert result["distress_detected"] is False

    def test_match_kb_keywords(self, agent):
        """match_kb_keywords must score and rank knowledge base articles."""
        articles = [
            {"id": 1, "title": "LMS Login Guide", "content": "Reset your LMS password using SSO portal"},
            {"id": 2, "title": "Fee Payment", "content": "Pay fees online via the finance portal"},
            {"id": 3, "title": "WiFi Setup", "content": "Connect to campus wifi network using credentials"},
        ]
        results = agent.match_kb_keywords("How do I connect to wifi?", articles)
        assert len(results) > 0
        # Returns (score, article) tuples sorted by score descending
        score, top_article = results[0]
        assert score > 0
        assert top_article["id"] == 3

    def test_routing_departments_in_valid_set(self, agent):
        """All routing results must map to one of the 6 known categories."""
        queries = [
            "My laptop crashed during exam",
            "I need financial aid for tuition",
            "The classroom projector is broken",
        ]
        valid = set(agent.categories) | {"IT Technical Support"}  # fallback uses short name
        for q in queries:
            result = agent.classify_ticket(q)
            assert any(cat in result["predicted_department"] for cat in valid) or \
                result["predicted_department"] in valid, \
                f"'{result['predicted_department']}' not a valid category"
