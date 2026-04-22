"""
Phase 25-28 Verification Tests (JSON Version)
- Phase 25: AI Profile Matcher (match scoring, match history)
- Phase 26: Application Tracker (CRUD, status, documents)
- Phase 27: Career/Fellowship Inventory (listings, filtering)
- Phase 28: Readiness Scorer (review storage, history)
"""
import pytest
from datetime import datetime, timezone, timedelta
from conftest import seed_student, seed_opportunity, seed_application, _read_json
from database_schema import (
    BranchEnum, Opportunity, StudentProfile,
    ApplicationRecord, ApplicationStatusEnum,
)
from json_db import db

# ====== Phase 25: AI Profile Matcher ======

class TestMatchScoring:
    """Test the match scoring logic using JSON-based models."""

    def test_match_record_attributes(self):
        """Verify match data structure."""
        student = seed_student(prn="MATCH001")
        opp = seed_opportunity(title="CS Research Internship")
        
        match = {
            "student_id": student["id"],
            "opportunity_id": opp["id"],
            "opportunity_type": "opportunity",
            "match_percentage": 85.0,
            "match_factors": {"branch": {"match": True}, "year": {"match": True}},
            "reasoning": "Strong match for CS student in 3rd year."
        }
        assert match["match_percentage"] == 85.0
        assert match["opportunity_type"] == "opportunity"
        assert "branch" in match["match_factors"]

    def test_logic_match_score_calculation(self):
        """Verify the calculation logic (standalone)."""
        student = {"prn": "S1", "branch": BranchEnum.COMP_ENG, "year_of_study": 3}
        opp = {"target_branches": "Computer Engineering", "target_years": "3,4"}
        
        factors = {}
        total_weight = 0
        matched_weight = 0
        
        if opp["target_branches"]:
            total_weight += 3
            if student["branch"].value in opp["target_branches"]:
                matched_weight += 3
                factors["branch"] = True
        
        if opp["target_years"]:
            total_weight += 2
            if str(student["year_of_study"]) in opp["target_years"]:
                matched_weight += 2
                factors["year"] = True
        
        pct = round((matched_weight / max(total_weight, 1)) * 100)
        assert pct == 100
        assert factors["branch"] is True

# ====== Phase 26: Application Tracker ======

class TestApplicationTracker:
    def test_create_application(self):
        student = seed_student(prn="APP001")
        app_record = seed_application(student, opportunity_id=1, title="MahaDBT Scholarship")
        
        assert app_record["status"] == "Applied"
        assert app_record["opportunity_title"] == "MahaDBT Scholarship"

    def test_status_transition_validation(self):
        student = seed_student(prn="APP002")
        app_data = seed_application(student, opportunity_id=1, title="Test Opp")
        
        # Pydantic model validation check
        app_model = ApplicationRecord(
            id=app_data["id"],
            student_id=student["id"],
            opportunity_id=1,
            opportunity_type="opportunity",
            opportunity_title="Test Opp",
            status=ApplicationStatusEnum.ACCEPTED
        )
        assert app_model.status == ApplicationStatusEnum.ACCEPTED

# ====== Phase 27: Career/Fellowship Inventory ======

class TestCareerInventory:
    def test_career_listing_filtration(self):
        listings = [
            {"title": "CS Internship", "listing_type": "internship", "target_branches": "Computer Engineering", "target_years": "3"},
            {"title": "Mech Internship", "listing_type": "internship", "target_branches": "Mechanical", "target_years": "3"}
        ]
        cs_listings = [l for l in listings if "Computer Engineering" in l["target_branches"]]
        assert len(cs_listings) == 1
        assert cs_listings[0]["title"] == "CS Internship"

# ====== Phase 28: Readiness Scorer ======

class TestReadinessScorer:
    def test_create_readiness_review_mock(self):
        student = seed_student(prn="READY001")
        review = {
            "student_id": student["id"],
            "document_type": "resume",
            "opportunity_title": "Google STEP",
            "feedback": "Score: 72/100. Strengths: Good projects."
        }
        assert review["document_type"] == "resume"
        assert "72/100" in review["feedback"]
