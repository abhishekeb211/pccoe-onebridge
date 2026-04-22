"""
Phase 1-3 Verification Tests (JSON Version)
- Phase 1: Requirement Crystallization (PRD.md)
- Phase 2: System Architecture Design (architecture.md, ERD.md)
- Phase 3: AI Strategy & Governance Selection (ai_governance.md)

Tests verify that planning deliverables exist and contain required content.
"""
import pytest
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhase1RequirementCrystallization:
    @pytest.fixture(autouse=True)
    def load_prd(self):
        path = os.path.join(PROJECT_ROOT, "PRD.md")
        assert os.path.isfile(path), "PRD.md must exist"
        with open(path, "r", encoding="utf-8") as f:
            self.prd = f.read()

    def test_prd_content_integrity(self):
        assert "Business Requirements" in self.prd or "Vision" in self.prd
        assert "Student" in self.prd
        assert "disabilit" in self.prd.lower() or "accessible" in self.prd.lower()
        assert "JSON" in self.prd or "registry" in self.prd.lower()

    def test_project_phases_document_exists(self):
        path = os.path.join(PROJECT_ROOT, "project_phases.md")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 1" in content
        assert "Phase 40" in content

class TestPhase2ArchitectureDesign:
    @pytest.fixture(autouse=True)
    def load_docs(self):
        arch_path = os.path.join(PROJECT_ROOT, "architecture.md")
        assert os.path.isfile(arch_path), "architecture.md must exist"
        with open(arch_path, "r", encoding="utf-8") as f:
            self.architecture = f.read()

    def test_architecture_persistence_layer(self):
        """Architecture must define the JSON persistence layer."""
        assert "JSON" in self.architecture
        assert "registry" in self.architecture.lower()
        assert "json_db" in self.architecture

    def test_erd_document_exists(self):
        path = os.path.join(PROJECT_ROOT, "ERD.md")
        assert os.path.isfile(path)

class TestPhase3AIGovernance:
    @pytest.fixture(autouse=True)
    def load_doc(self):
        path = os.path.join(PROJECT_ROOT, "ai_governance.md")
        assert os.path.isfile(path), "ai_governance.md must exist"
        with open(path, "r", encoding="utf-8") as f:
            self.governance = f.read()

    def test_governance_privacy_standards(self):
        assert "Local" in self.governance
        assert "Privacy" in self.governance
        assert "PII" in self.governance or "sanitiz" in self.governance.lower()
