import logging
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
        logger.info("Initializing Distil-BART zero-shot classifier model locally...")
        # Leveraging facebook/bart-large-mnli or distilbart
        # NOTE: Model downloads dynamically on first run into local memory.
        self.classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")
        
        # Pre-determined PCCOE College Routing Categories
        self.categories = [
            "IT Technical Support (WiFi, LMS, Passwords)",
            "Academic Advising (Exam, Syllabus, Mentorship)",
            "Financial Aid & Scholarships",
            "Emergency Wellbeing & Counseling",
            "EOC Confidential Disability Services",
            "Facilities & Housing"
        ]

    def classify_ticket(self, text_description: str) -> dict:
        """
        Executes routing dynamically against local memory. Sub-200ms theoretical latency depending on hardware.
        """
        start_time = logging.time.time() if hasattr(logging, 'time') else 0
        
        # Inference
        result = self.classifier(text_description, candidate_labels=self.categories)
        
        # Analytics
        top_category = result["labels"][0]
        confidence = round(result["scores"][0] * 100, 2)
        
        logger.info(f"Routed '{text_description[:20]}...' -> {top_category} ({confidence}%)")
        
        return {
            "predicted_department": top_category,
            "confidence_score": confidence,
            "is_eoc_flag": "EOC" in top_category or "Emergency" in top_category
        }

# Singleton Instantitation
local_agent = SmartRoutingAgent()
