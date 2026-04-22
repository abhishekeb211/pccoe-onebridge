"""
Shared pytest configuration and fixtures for PCCOE OneBridge test suite (JSON version).

All test utilities and seed helpers now use JSON file storage for test data setup and teardown.
No database, engine, or ORM dependencies remain. All test data is isolated per test.
"""
import os
import sys
import pytest
import json
import shutil
import tempfile

# ── Environment ──────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Directory for test JSON data (isolated per test)
TEST_DATA_DIR = os.path.join(PROJECT_ROOT, "tests", "test_data")
os.environ["ONEBRIDGE_DATA_DIR"] = TEST_DATA_DIR

def _reset_test_data():
    if os.path.exists(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR, exist_ok=True)

def _write_json(filename, data):
    with open(os.path.join(TEST_DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def _read_json(filename):
    path = os.path.join(TEST_DATA_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ── Pytest Fixtures ──────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def setup_json_data():
    """Autouse: reset test JSON data before every test."""
    _reset_test_data()
    yield
    _reset_test_data()

# ── Seed Helpers (JSON) ─────────────────────────────────────────────────────
def seed_student(prn="TEST001", name="Test Student", *,
                 branch="Computer Engineering", year_of_study=2, role="student",
                 email=None, has_disability=False, is_disadvantaged=False,
                 password_hash="fakehash"):
    """Insert and return a student dict into students.json."""
    students = _read_json("students.json")
    student = {
        "id": len(students) + 1,
        "prn": prn,
        "name": name,
        "email": email or f"{prn.lower()}@pccoe.org",
        "branch": branch,
        "year_of_study": year_of_study,
        "role": role,
        "has_disability": has_disability,
        "is_disadvantaged": is_disadvantaged,
        "password_hash": password_hash,
    }
    students.append(student)
    _write_json("students.json", students)
    return student


def seed_faculty(prn="FAC001", name="Dr. Faculty"):
    """Insert and return a faculty-role student dict."""
    return seed_student(prn=prn, name=name, role="faculty")


def seed_resource(name="AI Lab", rtype="lab", capacity=30, accessible=True):
    """Insert and return a resource dict into resources.json."""
    resources = _read_json("resources.json")
    resource = {
        "id": len(resources) + 1,
        "name": name,
        "building": "Main Block",
        "floor": "2",
        "resource_type": rtype,
        "seating_capacity": capacity,
        "is_accessible": accessible,
    }
    resources.append(resource)
    _write_json("resources.json", resources)
    return resource


def seed_opportunity(title="Google STEP Internship",
                     branches="Computer Engineering", years="3,4"):
    """Insert and return an opportunity dict into opportunities.json."""
    from datetime import datetime, timezone, timedelta
    opportunities = _read_json("opportunities.json")
    opportunity = {
        "id": len(opportunities) + 1,
        "title": title,
        "type": "internship",
        "target_branches": branches,
        "target_years": years,
        "deadline": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
    }
    opportunities.append(opportunity)
    _write_json("opportunities.json", opportunities)
    return opportunity


def seed_application(student, opportunity_id=1, title="Test Opportunity"):
    """Insert and return an application dict into applications.json."""
    applications = _read_json("applications.json")
    application = {
        "id": len(applications) + 1,
        "student_id": student["id"],
        "opportunity_id": opportunity_id,
        "opportunity_type": "opportunity",
        "opportunity_title": title,
        "status": "Applied",
    }
    applications.append(application)
    _write_json("applications.json", applications)
    return application


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
