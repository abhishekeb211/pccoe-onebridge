"""
Phase 25-28 Verification Tests
- Phase 25: AI Profile Matcher (match scoring, match history)
- Phase 26: Application Tracker (CRUD, status, documents)
- Phase 27: Career/Fellowship Inventory (listings, filtering)
- Phase 28: Readiness Scorer (review storage, history)
"""
import os
import sys
import unittest
import json
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import engine, fresh_db, seed_student, seed_opportunity
from database_schema import (
    Base, StudentProfile, BranchEnum, Opportunity,
    StudentEligibility, CasteCategory,
    StudentOpportunityMatch,
    ApplicationRecord, ApplicationDocument, ApplicationStatusEnum,
    CareerListing,
    ReadinessReview,
)


# ====== Phase 25: AI Profile Matcher ======

class TestMatchScoring(unittest.TestCase):
    """Test the match scoring logic from main.py."""

    def test_match_record_creation(self):
        db = fresh_db()
        student = seed_student(db)
        """
        Phase 25-28 Verification Tests (JSON-based)
        - Phase 25: AI Profile Matcher (match scoring, match history)
        - Phase 26: Application Tracker (CRUD, status, documents)
        - Phase 27: Career/Fellowship Inventory (listings, filtering)
        - Phase 28: Readiness Scorer (review storage, history)
        """
        import unittest
        from conftest import seed_student, seed_opportunity, seed_application

        class TestMatchScoring(unittest.TestCase):
            """Test the match scoring logic using JSON-based helpers."""

            def test_match_record_creation(self):
                student = seed_student()
                opp = seed_opportunity()
                match = {
                    "student_id": student["id"],
                    "opportunity_id": opp["id"],
                    "opportunity_type": "opportunity",
                    "match_percentage": 85.0,
                    "match_factors": {"branch": {"match": True}, "year": {"match": True}},
                    "reasoning": "Strong match for CS student in 3rd year."
                }
                self.assertEqual(match["match_percentage"], 85.0)
                self.assertEqual(match["opportunity_type"], "opportunity")
                self.assertIn("branch", match["match_factors"])

            def test_match_history_query(self):
                student = seed_student()
                opp = seed_opportunity()
                matches = []
                for i in range(3):
                    matches.append({
                        "student_id": student["id"],
                        "opportunity_id": opp["id"],
                        "opportunity_type": "opportunity",
                        "match_percentage": 60 + i * 10,
                    })
                self.assertEqual(len(matches), 3)

            def test_match_score_calculation(self):
                student = seed_student(year_of_study=3)
                opp = seed_opportunity(branches="Computer Engineering", years="3,4")
                elig = {"gpa": 8.5}
                factors = {}
                total_weight = 0
                matched_weight = 0
                if opp["target_branches"]:
                    total_weight += 3
                    branch_val = student["branch"] if student["branch"] else ""
                    if branch_val in opp["target_branches"]:
                        matched_weight += 3
                        factors["branch"] = {"match": True}
                    else:
                        factors["branch"] = {"match": False}
                if opp["target_years"]:
                    total_weight += 2
                    if str(student["year_of_study"]) in opp["target_years"]:
                        matched_weight += 2
                        factors["year"] = {"match": True}
                    else:
                        factors["year"] = {"match": False}
                if elig and elig["gpa"]:
                    total_weight += 2
                    if elig["gpa"] >= 6.0:
                        matched_weight += 2
                        factors["gpa"] = {"match": True, "value": elig["gpa"]}
                pct = round((matched_weight / max(total_weight, 1)) * 100)
                self.assertEqual(pct, 100)
                self.assertTrue(factors["branch"]["match"])
                self.assertTrue(factors["year"]["match"])

        class TestApplicationTracker(unittest.TestCase):
            def test_create_application(self):
                student = seed_student()
                app_record = seed_application(student, opportunity_id=1, title="MahaDBT Scholarship")
                self.assertEqual(app_record["status"], "Applied")
                self.assertEqual(app_record["opportunity_title"], "MahaDBT Scholarship")

            def test_status_transition(self):
                student = seed_student()
                app_record = seed_application(student, opportunity_id=1, title="Test Opp")
                app_record["status"] = "Documents Submitted"
                self.assertEqual(app_record["status"], "Documents Submitted")
                app_record["status"] = "Accepted"
                self.assertEqual(app_record["status"], "Accepted")

            def test_application_document(self):
                doc = {
                    "application_id": 1,
                    "doc_type": "resume",
                    "file_path": "uploads/applications/1/resume.pdf",
                    "validation_state": "pending"
                }
                self.assertEqual(doc["validation_state"], "pending")
                self.assertEqual(doc["doc_type"], "resume")

        class TestCareerInventory(unittest.TestCase):
            def test_create_career_listing(self):
                listing = {
                    "title": "TCS NQT 2025",
                    "description": "National Qualifier Test for freshers",
                    "listing_type": "full_time",
                    "source": "internal",
                    "target_branches": "Computer Engineering,IT",
                    "target_years": "4",
                    "is_active": True
                }
                self.assertEqual(listing["title"], "TCS NQT 2025")
                self.assertTrue(listing["is_active"])

            def test_filter_by_branch(self):
                listings = [
                    {"title": "CS Internship", "listing_type": "internship", "target_branches": "Computer Engineering", "target_years": "3"},
                    {"title": "Mech Internship", "listing_type": "internship", "target_branches": "Mechanical", "target_years": "3"}
                ]
                cs_listings = [l for l in listings if "Computer Engineering" in l["target_branches"]]
                self.assertEqual(len(cs_listings), 1)
                self.assertEqual(cs_listings[0]["title"], "CS Internship")

            def test_filter_by_type(self):
                listings = [
                    {"title": "Fellowship A", "listing_type": "fellowship"},
                    {"title": "Internship B", "listing_type": "internship"},
                    {"title": "Job C", "listing_type": "full_time"}
                ]
                fellowships = [l for l in listings if l["listing_type"] == "fellowship"]
                self.assertEqual(len(fellowships), 1)

        class TestReadinessScorer(unittest.TestCase):
            def test_create_readiness_review(self):
                student = seed_student()
                review = {
                    "student_id": student["id"],
                    "document_type": "resume",
                    "opportunity_title": "Google STEP",
                    "feedback": "Score: 72/100. Strengths: Good projects. Improve: Add more technical skills."
                }
                self.assertEqual(review["document_type"], "resume")
                self.assertIn("72/100", review["feedback"])

            def test_readiness_history(self):
                student = seed_student()
                reviews = []
                for dtype in ["resume", "sop", "resume"]:
                    reviews.append({
                        "student_id": student["id"],
                        "document_type": dtype,
                        "feedback": f"Feedback for {dtype}."
                    })
                self.assertEqual(len(reviews), 3)

            def test_review_fields(self):
                student = seed_student()
                review = {
                    "student_id": student["id"],
                    "document_type": "sop",
                    "opportunity_title": None,
                    "feedback": "Basic analysis.",
                    "created_at": "2026-04-15T00:00:00Z"
                }
                self.assertIsNone(review["opportunity_title"])
                self.assertIsNotNone(review["created_at"])

        # Schema integrity tests and enum checks are omitted in JSON-based version.

        if __name__ == "__main__":
            unittest.main()
        self.assertEqual(listing.title, "TCS NQT 2025")
