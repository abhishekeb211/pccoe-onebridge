"""
Shared pytest configuration and fixtures for PCCOE OneBridge test suite.

Central test infrastructure: SQLite in-memory engine, session management,
seed helpers, and test ordering. All DB test files import from here
instead of defining their own engine/session boilerplate.
"""
import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Environment ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Override DATABASE_URL before any project imports that read it
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from database_schema import (                          # noqa: E402
    Base, StudentProfile, BranchEnum,
    CampusResource, ApplicationRecord, ApplicationStatusEnum, Opportunity,
)

# ── Shared Engine & Session ──────────────────────────────────────────────────
engine = create_engine("sqlite:///:memory:")
Session = sessionmaker(bind=engine)


def fresh_db():
    """Drop and recreate all tables, return a new session.

    Used by unittest-style tests that call fresh_db() in setUp / per-test.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    return Session()


# ── Pytest Fixtures ──────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_db():
    """Autouse: create tables before every test, drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Yield a per-test SQLAlchemy session with automatic close."""
    session = Session()
    yield session
    session.close()


# ── Seed Helpers ─────────────────────────────────────────────────────────────
def seed_student(db, prn="TEST001", name="Test Student", *,
                 branch=BranchEnum.COMP_ENG, year_of_study=2, role="student",
                 email=None, has_disability=False, is_disadvantaged=False,
                 password_hash="fakehash"):
    """Insert and return a StudentProfile.  Accepts keyword overrides."""
    s = StudentProfile(
        prn=prn,
        name=name,
        email=email or f"{prn.lower()}@pccoe.org",
        branch=branch,
        year_of_study=year_of_study,
        role=role,
        has_disability=has_disability,
        is_disadvantaged=is_disadvantaged,
        password_hash=password_hash,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def seed_faculty(db, prn="FAC001", name="Dr. Faculty"):
    """Insert and return a faculty-role StudentProfile."""
    return seed_student(db, prn=prn, name=name, role="faculty")


def seed_resource(db, name="AI Lab", rtype="lab", capacity=30, accessible=True):
    """Insert and return a CampusResource."""
    r = CampusResource(
        name=name,
        building="Main Block",
        floor="2",
        resource_type=rtype,
        seating_capacity=capacity,
        is_accessible=accessible,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def seed_opportunity(db, title="Google STEP Internship",
                     branches="Computer Engineering", years="3,4"):
    """Insert and return an Opportunity."""
    from datetime import datetime, timezone, timedelta
    o = Opportunity(
        title=title,
        type="internship",
        target_branches=branches,
        target_years=years,
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def seed_application(db, student, opportunity_id=1, title="Test Opportunity"):
    """Insert and return an ApplicationRecord."""
    a = ApplicationRecord(
        student_id=student.id,
        opportunity_id=opportunity_id,
        opportunity_type="opportunity",
        opportunity_title=title,
        status=ApplicationStatusEnum.APPLIED,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


# ── Test Ordering ────────────────────────────────────────────────────────────
def pytest_collection_modifyitems(config, items):
    """Run fast tests first; ML-heavy Phase 13-14 tests last."""
    ml_tests = []
    other_tests = []
    for item in items:
        if "phase_13_14" in str(item.fspath):
            ml_tests.append(item)
        else:
            other_tests.append(item)
    items[:] = other_tests + ml_tests
