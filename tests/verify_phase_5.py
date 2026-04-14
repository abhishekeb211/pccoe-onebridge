"""
Phase 5 Verification Tests
- Phase 5: Version Control & CI/CD Setup

Tests verify CONTRIBUTING.md content, CI/CD configuration references,
and implementation artifacts (requirements.txt, test infrastructure).
"""
import pytest
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPhase5VersionControlCICD:
    """Phase 5: Verify version control documentation and CI/CD artifacts."""

    @pytest.fixture(autouse=True)
    def load_contributing(self):
        path = os.path.join(PROJECT_ROOT, "CONTRIBUTING.md")
        assert os.path.isfile(path), "CONTRIBUTING.md must exist"
        with open(path, "r", encoding="utf-8") as f:
            self.contributing = f.read()

    def test_contributing_defines_git_flow(self):
        """CONTRIBUTING.md must define Git Flow branching strategy."""
        assert "Git Flow" in self.contributing

    def test_contributing_defines_branch_naming(self):
        """Must define branch naming conventions (main, staging, feature/)."""
        assert "main" in self.contributing
        assert "staging" in self.contributing
        assert "feature/" in self.contributing

    def test_contributing_defines_commit_conventions(self):
        """Must define commit message conventions."""
        assert "feat:" in self.contributing or "Commit" in self.contributing
        assert "fix:" in self.contributing

    def test_contributing_defines_cicd_pipeline(self):
        """Must reference CI/CD pipeline configuration."""
        assert "CI/CD" in self.contributing or "ci.yml" in self.contributing

    def test_contributing_security_scan_requirement(self):
        """CI pipeline must enforce security scanning."""
        assert "Security Scan" in self.contributing or "security" in self.contributing.lower()

    def test_contributing_accessibility_scan_requirement(self):
        """CI pipeline must enforce accessibility scanning."""
        assert "Accessibility" in self.contributing

    def test_requirements_txt_exists(self):
        """requirements.txt must exist for reproducible installs."""
        path = os.path.join(PROJECT_ROOT, "requirements.txt")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "fastapi" in content.lower()
        assert "sqlalchemy" in content.lower()

    def test_tests_directory_exists(self):
        """tests/ directory must exist with verification scripts."""
        tests_dir = os.path.join(PROJECT_ROOT, "tests")
        assert os.path.isdir(tests_dir)
        test_files = [f for f in os.listdir(tests_dir) if f.startswith("verify_")]
        assert len(test_files) >= 10, f"Expected 10+ test files, found {len(test_files)}"

    def test_implementation_tracking_document(self):
        """implementation.md must exist for phase tracking."""
        path = os.path.join(PROJECT_ROOT, "implementation.md")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) >= 5000, "Implementation doc must be substantive"
