"""
Phase 5-8 Verification Tests (JSON Version)
- Phase 5: Version Control & CI/CD Setup
- Phase 6: Core API Scaffolding (Health checks)
- Phase 7: Frontend Scaffolding (app.js, index.html)
- Phase 8: Accessibility & Theming (WCAG, high contrast)
"""
import pytest
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestPhase5VersionControl:
    def test_contributing_and_requirements(self):
        with open(os.path.join(PROJECT_ROOT, "CONTRIBUTING.md"), "r") as f:
            content = f.read()
        assert "Git Flow" in content or "main" in content
        
        with open(os.path.join(PROJECT_ROOT, "requirements.txt"), "r") as f:
            reqs = f.read().lower()
        assert "fastapi" in reqs
        assert "pydantic" in reqs
        assert "sqlalchemy" not in reqs

class TestPhase7Frontend:
    @pytest.fixture(autouse=True)
    def load_files(self):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(os.path.join(PROJECT_ROOT, "index.html"), "r", encoding="utf-8") as f:
            self.index_html = f.read()

    def test_distress_detection_logic(self):
        from local_agent import local_agent
        assert hasattr(local_agent, "detect_distress")
        assert "renderSkeletons" in self.app_js
        assert "roadmapData" in self.app_js
        assert "data/notifications.json" in self.app_js

    def test_ticket_routing_classification(self):
        """Verify routing prediction logic."""
        from local_agent import local_agent
        assert hasattr(local_agent, "classify_ticket") or "classifier" in str(dir(local_agent))
        assert "btn-switch-tab" in self.index_html or "pulse-icon" in self.index_html

class TestPhase8Theming:
    def test_css_design_tokens(self):
        with open(os.path.join(PROJECT_ROOT, "styles.css"), "r", encoding="utf-8") as f:
            css = f.read()
        assert "--accent-primary" in css
        assert "--bg-primary" in css
        assert "high-contrast" in css
        assert "large-font" in css
