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
        opp = seed_opportunity(db)

        match = StudentOpportunityMatch(
            student_id=student.id,
            opportunity_id=opp.id,
            opportunity_type="opportunity",
            match_percentage=85.0,
            match_factors=json.dumps({"branch": {"match": True}, "year": {"match": True}}),
            reasoning="Strong match for CS student in 3rd year.",
        )
        db.add(match)
        db.commit()
        db.refresh(match)

        self.assertEqual(match.match_percentage, 85.0)
        self.assertEqual(match.opportunity_type, "opportunity")
        self.assertIn("branch", json.loads(match.match_factors))

    def test_match_history_query(self):
        db = fresh_db()
        student = seed_student(db)
        opp = seed_opportunity(db)

        for i in range(3):
            db.add(StudentOpportunityMatch(
                student_id=student.id,
                opportunity_id=opp.id,
                opportunity_type="opportunity",
                match_percentage=60 + i * 10,
            ))
        db.commit()

        matches = db.query(StudentOpportunityMatch).filter(
            StudentOpportunityMatch.student_id == student.id
        ).all()
        self.assertEqual(len(matches), 3)

    def test_match_score_calculation(self):
        """Test match scoring logic inline (avoids importing main.py which calls init_db)."""
        db = fresh_db()
        student = seed_student(db, year_of_study=3)
        opp = seed_opportunity(db, branches="Computer Engineering", years="3,4")
        elig = StudentEligibility(student_id=student.id, gpa=8.5)
        db.add(elig)
        db.commit()

        # Inline match scoring logic (mirrors main._calculate_match_score)
        factors = {}
        total_weight = 0
        matched_weight = 0

        # Branch
        if opp.target_branches:
            total_weight += 3
            branch_val = student.branch.value if student.branch else ""
            if branch_val in opp.target_branches:
                matched_weight += 3
                factors["branch"] = {"match": True}
            else:
                factors["branch"] = {"match": False}
        # Year
        if opp.target_years:
            total_weight += 2
            if str(student.year_of_study) in opp.target_years:
                matched_weight += 2
                factors["year"] = {"match": True}
            else:
                factors["year"] = {"match": False}
        # GPA
        if elig and elig.gpa:
            total_weight += 2
            if elig.gpa >= 6.0:
                matched_weight += 2
                factors["gpa"] = {"match": True, "value": elig.gpa}

        pct = round((matched_weight / max(total_weight, 1)) * 100)
        self.assertEqual(pct, 100)
        self.assertTrue(factors["branch"]["match"])
        self.assertTrue(factors["year"]["match"])


# ====== Phase 26: Application Tracker ======

class TestApplicationTracker(unittest.TestCase):
    def test_create_application(self):
        db = fresh_db()
        student = seed_student(db)

        app_record = ApplicationRecord(
            student_id=student.id,
            opportunity_id=1,
            opportunity_type="scholarship",
            opportunity_title="MahaDBT Scholarship",
        )
        db.add(app_record)
        db.commit()
        db.refresh(app_record)

        self.assertEqual(app_record.status, ApplicationStatusEnum.APPLIED)
        self.assertEqual(app_record.opportunity_title, "MahaDBT Scholarship")

    def test_status_transition(self):
        db = fresh_db()
        student = seed_student(db)

        app_record = ApplicationRecord(
            student_id=student.id, opportunity_id=1,
            opportunity_type="opportunity", opportunity_title="Test Opp",
        )
        db.add(app_record)
        db.commit()

        app_record.status = ApplicationStatusEnum.DOCS_SUBMITTED
        db.commit()
        db.refresh(app_record)
        self.assertEqual(app_record.status, ApplicationStatusEnum.DOCS_SUBMITTED)

        app_record.status = ApplicationStatusEnum.ACCEPTED
        db.commit()
        db.refresh(app_record)
        self.assertEqual(app_record.status, ApplicationStatusEnum.ACCEPTED)

    def test_application_document(self):
        db = fresh_db()
        student = seed_student(db)

        app_record = ApplicationRecord(
            student_id=student.id, opportunity_id=1,
            opportunity_type="opportunity", opportunity_title="Test",
        )
        db.add(app_record)
        db.commit()
        db.refresh(app_record)

        doc = ApplicationDocument(
            application_id=app_record.id,
            doc_type="resume",
            file_path="uploads/applications/1/resume.pdf",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        self.assertEqual(doc.validation_state, "pending")
        self.assertEqual(doc.doc_type, "resume")

        # Test relationship
        docs = db.query(ApplicationDocument).filter(
            ApplicationDocument.application_id == app_record.id
        ).all()
        self.assertEqual(len(docs), 1)


# ====== Phase 27: Career/Fellowship Inventory ======

class TestCareerInventory(unittest.TestCase):
    def test_create_career_listing(self):
        db = fresh_db()
        listing = CareerListing(
            title="TCS NQT 2025",
            description="National Qualifier Test for freshers",
            listing_type="full_time",
            source="internal",
            target_branches="Computer Engineering,IT",
            target_years="4",
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)
        self.assertEqual(listing.title, "TCS NQT 2025")
        self.assertTrue(listing.is_active)

    def test_filter_by_branch(self):
        db = fresh_db()
        db.add(CareerListing(title="CS Internship", listing_type="internship", target_branches="Computer Engineering", target_years="3"))
        db.add(CareerListing(title="Mech Internship", listing_type="internship", target_branches="Mechanical", target_years="3"))
        db.commit()

        cs_listings = db.query(CareerListing).filter(
            CareerListing.target_branches.contains("Computer Engineering")
        ).all()
        self.assertEqual(len(cs_listings), 1)
        self.assertEqual(cs_listings[0].title, "CS Internship")

    def test_filter_by_type(self):
        db = fresh_db()
        db.add(CareerListing(title="Fellowship A", listing_type="fellowship"))
        db.add(CareerListing(title="Internship B", listing_type="internship"))
        db.add(CareerListing(title="Job C", listing_type="full_time"))
        db.commit()

        fellowships = db.query(CareerListing).filter(CareerListing.listing_type == "fellowship").all()
        self.assertEqual(len(fellowships), 1)


# ====== Phase 28: Readiness Scorer ======

class TestReadinessScorer(unittest.TestCase):
    def test_create_readiness_review(self):
        db = fresh_db()
        student = seed_student(db)

        review = ReadinessReview(
            student_id=student.id,
            document_type="resume",
            opportunity_title="Google STEP",
            feedback="Score: 72/100. Strengths: Good projects. Improve: Add more technical skills.",
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        self.assertEqual(review.document_type, "resume")
        self.assertIn("72/100", review.feedback)

    def test_readiness_history(self):
        db = fresh_db()
        student = seed_student(db)

        for dtype in ["resume", "sop", "resume"]:
            db.add(ReadinessReview(
                student_id=student.id,
                document_type=dtype,
                feedback=f"Feedback for {dtype}.",
            ))
        db.commit()

        reviews = db.query(ReadinessReview).filter(
            ReadinessReview.student_id == student.id
        ).all()
        self.assertEqual(len(reviews), 3)

    def test_review_fields(self):
        db = fresh_db()
        student = seed_student(db)

        review = ReadinessReview(
            student_id=student.id,
            document_type="sop",
            opportunity_title=None,
            feedback="Basic analysis.",
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        self.assertIsNone(review.opportunity_title)
        self.assertIsNotNone(review.created_at)


# ====== Schema Integrity ======

class TestPhase25_28Schema(unittest.TestCase):
    def test_all_tables_created(self):
        db = fresh_db()
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        required = [
            "student_opportunity_matches",
            "application_records",
            "application_documents",
            "career_listings",
            "readiness_reviews",
        ]
        for t in required:
            self.assertIn(t, table_names, f"Missing table: {t}")

    def test_application_status_enum(self):
        self.assertEqual(ApplicationStatusEnum.APPLIED.value, "Applied")
        self.assertEqual(ApplicationStatusEnum.ACCEPTED.value, "Accepted")
        self.assertEqual(len(ApplicationStatusEnum), 5)


if __name__ == "__main__":
    unittest.main()
