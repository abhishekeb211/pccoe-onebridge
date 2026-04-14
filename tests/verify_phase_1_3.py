"""
Phase 1-3 Verification Tests
- Phase 1: Requirement Crystallization (PRD.md)
- Phase 2: System Architecture Design (architecture.md, ERD.md)
- Phase 3: AI Strategy & Governance Selection (ai_governance.md)

Tests verify that planning deliverables exist and contain required content.
"""
import pytest
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ============================================================================
# Phase 1: Requirement Crystallization
# ============================================================================

class TestPhase1RequirementCrystallization:
    """Phase 1: Verify PRD and project planning artifacts."""

    @pytest.fixture(autouse=True)
    def load_prd(self):
        path = os.path.join(PROJECT_ROOT, "PRD.md")
        assert os.path.isfile(path), "PRD.md must exist"
        with open(path, "r", encoding="utf-8") as f:
            self.prd = f.read()

    def test_prd_has_executive_summary(self):
        """PRD must contain an executive summary."""
        assert "Executive Summary" in self.prd

    def test_prd_defines_target_audience(self):
        """PRD must define target audience and user roles."""
        assert "Target Audience" in self.prd or "Roles" in self.prd
        assert "Student" in self.prd
        assert "EOC" in self.prd

    def test_prd_mentions_accessibility(self):
        """PRD must address accessibility for disabled students."""
        assert "disabilit" in self.prd.lower() or "accessible" in self.prd.lower()

    def test_prd_mentions_scholarship(self):
        """PRD must address scholarship/opportunity features."""
        assert "scholarship" in self.prd.lower() or "opportunity" in self.prd.lower()

    def test_prd_minimum_length(self):
        """PRD must be substantive (at least 2000 characters)."""
        assert len(self.prd) >= 2000, f"PRD too short: {len(self.prd)} chars"

    def test_project_phases_document_exists(self):
        """project_phases.md must exist defining all 40 phases."""
        path = os.path.join(PROJECT_ROOT, "project_phases.md")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "Phase 1" in content
        assert "Phase 40" in content

    def test_phase_docs_directory_exists(self):
        """phase_docs/ directory must contain individual phase documents."""
        phase_docs = os.path.join(PROJECT_ROOT, "phase_docs")
        assert os.path.isdir(phase_docs)
        files = os.listdir(phase_docs)
        assert len(files) >= 40, f"Expected 40+ phase docs, found {len(files)}"


# ============================================================================
# Phase 2: System Architecture Design
# ============================================================================

class TestPhase2ArchitectureDesign:
    """Phase 2: Verify architecture documentation and ERD."""

    @pytest.fixture(autouse=True)
    def load_docs(self):
        arch_path = os.path.join(PROJECT_ROOT, "architecture.md")
        assert os.path.isfile(arch_path), "architecture.md must exist"
        with open(arch_path, "r", encoding="utf-8") as f:
            self.architecture = f.read()

    def test_architecture_has_system_overview(self):
        """Architecture doc must have a system overview."""
        assert "System Overview" in self.architecture or "Overview" in self.architecture

    def test_architecture_defines_data_flow(self):
        """Architecture must define data flow (DFD or sequence diagrams)."""
        assert "Data Flow" in self.architecture or "DFD" in self.architecture or "mermaid" in self.architecture

    def test_architecture_mentions_frontend(self):
        """Architecture must describe the frontend layer."""
        assert "Frontend" in self.architecture or "front-end" in self.architecture.lower()

    def test_architecture_mentions_backend(self):
        """Architecture must describe the backend/API layer."""
        assert "API" in self.architecture or "Backend" in self.architecture

    def test_architecture_mentions_database(self):
        """Architecture must describe the database layer."""
        assert "database" in self.architecture.lower() or "Supabase" in self.architecture or "PostgreSQL" in self.architecture

    def test_erd_document_exists(self):
        """Entity Relationship Diagram document must exist."""
        path = os.path.join(PROJECT_ROOT, "ERD.md")
        assert os.path.isfile(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content) >= 500

    def test_architecture_minimum_length(self):
        """Architecture doc must be substantive (at least 3000 characters)."""
        assert len(self.architecture) >= 3000


# ============================================================================
# Phase 3: AI Strategy & Governance Selection
# ============================================================================

class TestPhase3AIGovernance:
    """Phase 3: Verify AI strategy and data governance documentation."""

    @pytest.fixture(autouse=True)
    def load_doc(self):
        path = os.path.join(PROJECT_ROOT, "ai_governance.md")
        assert os.path.isfile(path), "ai_governance.md must exist"
        with open(path, "r", encoding="utf-8") as f:
            self.governance = f.read()

    def test_governance_defines_local_vs_external(self):
        """Governance must distinguish local AI from external LLM usage."""
        assert "Local" in self.governance
        assert "External" in self.governance or "Cloud" in self.governance or "OpenRouter" in self.governance

    def test_governance_addresses_privacy(self):
        """Governance must address privacy requirements."""
        assert "privacy" in self.governance.lower() or "Privacy" in self.governance

    def test_governance_mentions_pii_scrubbing(self):
        """Governance must address PII sanitization before external API calls."""
        has_pii = "PII" in self.governance or "pii" in self.governance.lower()
        has_sanitiz = "sanitiz" in self.governance.lower() or "scrub" in self.governance.lower() or "redact" in self.governance.lower()
        assert has_pii or has_sanitiz, "Governance must address PII handling"

    def test_governance_mentions_model_selection(self):
        """Governance must specify which AI models are selected."""
        has_model = any(m in self.governance.lower() for m in [
            "distilbert", "gemini", "llama", "huggingface", "openrouter",
        ])
        assert has_model, "Governance must specify AI model selections"

    def test_governance_addresses_eoc(self):
        """Governance must address EOC-specific data handling."""
        assert "EOC" in self.governance

    def test_governance_minimum_length(self):
        """Governance doc must be substantive (at least 2000 characters)."""
        assert len(self.governance) >= 2000
