import logging
import time
import threading
from transformers import pipeline

# Phase 13 & 14: Local AI Zero-Shot Agent

# Configure local logger for NFRs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OneBridge.LocalAgent")

class SmartRoutingAgent:
    """
    Offline zero-shot classifier relying natively on HuggingFace transformers.
    Maintains Absolute Privacy per Phase 1 bounds (EOC data is never pushed to cloud).
    """
    def __init__(self):
        self.classifier = None
        self._ready = threading.Event()
        
        # Pre-determined PCCOE College Routing Categories
        self.categories = [
            "IT Technical Support (WiFi, LMS, Passwords)",
            "Academic Advising (Exam, Syllabus, Mentorship)",
            "Financial Aid & Scholarships",
            "Emergency Wellbeing & Counseling",
            "EOC Confidential Disability Services",
            "Facilities & Housing"
        ]

        # Background initialization to avoid blocking startup
        thread = threading.Thread(target=self._load_model, daemon=True)
        thread.start()

    def _load_model(self):
        try:
            logger.info("Initializing Distil-BART zero-shot classifier model locally...")
            self.classifier = pipeline(
                "zero-shot-classification",
                model="valhalla/distilbart-mnli-12-3"
            )
            self._ready.set()
            logger.info("Local NLP model loaded and ready.")
        except Exception as exc:
            logger.error(f"Failed to load local NLP model: {exc}")
            self._ready.set()  # Unblock callers so they get the fallback

    def classify_ticket(self, text_description: str) -> dict:
        """
        Executes routing dynamically against local memory. Sub-200ms theoretical latency depending on hardware.
        Returns fallback routing if model is unavailable.
        """
        # Wait up to 30s for model to be ready on first call
        if not self._ready.wait(timeout=30):
            logger.warning("Model initialization timed out — returning fallback routing.")
            return self._fallback(text_description)

        if self.classifier is None:
            logger.warning("Model not available — returning fallback routing.")
            return self._fallback(text_description)

        try:
            start_time = time.time()
            result = self.classifier(text_description, candidate_labels=self.categories)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)

            top_category = result["labels"][0]
            confidence = round(result["scores"][0] * 100, 2)

            logger.info(f"Routed '{text_description[:20]}...' -> {top_category} ({confidence}%) [{elapsed_ms}ms]")

            return {
                "predicted_department": top_category,
                "confidence_score": confidence,
                "is_eoc_flag": "EOC" in top_category or "Emergency" in top_category
            }
        except Exception as exc:
            logger.error(f"Classification error: {exc}")
            return self._fallback(text_description)

    def _fallback(self, text_description: str) -> dict:
        """Keyword-based fallback when NLP model is unavailable."""
        text_lower = text_description.lower()
        if any(kw in text_lower for kw in ["eoc", "disability", "discrimination", "grievance"]):
            return {"predicted_department": "EOC Confidential Disability Services", "confidence_score": 50.0, "is_eoc_flag": True}
        if any(kw in text_lower for kw in ["wifi", "lms", "password", "login", "network"]):
            return {"predicted_department": "IT Technical Support (WiFi, LMS, Passwords)", "confidence_score": 50.0, "is_eoc_flag": False}
        if any(kw in text_lower for kw in ["exam", "syllabus", "mentor", "marks", "grade"]):
            return {"predicted_department": "Academic Advising (Exam, Syllabus, Mentorship)", "confidence_score": 50.0, "is_eoc_flag": False}
        if any(kw in text_lower for kw in ["scholarship", "fee", "financial", "payment"]):
            return {"predicted_department": "Financial Aid & Scholarships", "confidence_score": 50.0, "is_eoc_flag": False}
        return {"predicted_department": "General", "confidence_score": 25.0, "is_eoc_flag": False}

    # Phase 23: Distress detection for human hand-off
    DISTRESS_KEYWORDS = [
        "suicide", "harm", "die", "kill", "hopeless", "desperate",
        "emergency", "urgent", "please help", "can't take it", "abuse",
        "harass", "assault", "threat", "panic", "depressed",
    ]

    def detect_distress(self, text: str) -> dict:
        """Check for distress keywords in student messages. Returns escalation recommendation."""
        text_lower = text.lower()
        matched = [kw for kw in self.DISTRESS_KEYWORDS if kw in text_lower]
        if matched:
            logger.warning(f"Distress keywords detected: {matched}")
            return {"distress_detected": True, "keywords": matched, "recommend_escalation": True}
        return {"distress_detected": False, "keywords": [], "recommend_escalation": False}

    # Phase 21: Simple KB keyword search (for use in chatbot without DB)
    def match_kb_keywords(self, query: str, articles: list) -> list:
        """Score KB articles against a query using keyword matching. Returns sorted (score, article) list."""
        query_words = query.lower().split()
        scored = []
        for article in articles:
            score = 0
            title_l = (article.get("title", "") if isinstance(article, dict) else getattr(article, "title", "")).lower()
            content_l = (article.get("content", "") if isinstance(article, dict) else getattr(article, "content", "")).lower()
            tags_l = (article.get("tags", "") if isinstance(article, dict) else getattr(article, "tags", "") or "").lower()
            for word in query_words:
                if word in title_l:
                    score += 3
                if word in tags_l:
                    score += 2
                if word in content_l:
                    score += 1
            if score > 0:
                scored.append((score, article))
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored

# Singleton Instantiation
local_agent = SmartRoutingAgent()
