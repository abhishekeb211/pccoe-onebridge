"""
Phase 7-8 Verification Tests
- Phase 7: Frontend Application Scaffolding (SPA structure, routing, state management)
- Phase 8: Accessibility & Theming Core Foundations (WCAG 2.1 AA, high contrast, large font)

These tests verify the structural integrity of the frontend codebase
by parsing the JavaScript and CSS files for required patterns.
"""
import pytest
import os
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPhase7FrontendScaffolding:
    """Phase 7: Verify SPA architecture, routing, and state management."""

    @pytest.fixture(autouse=True)
    def load_files(self):
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(os.path.join(PROJECT_ROOT, "index.html"), "r", encoding="utf-8") as f:
            self.index_html = f.read()
        with open(os.path.join(PROJECT_ROOT, "api.js"), "r", encoding="utf-8") as f:
            self.api_js = f.read()

    def test_global_state_store_exists(self):
        """GlobalState must have user, ui, subscribe, setState, notify."""
        assert "const GlobalState" in self.app_js
        assert "subscribe(callback)" in self.app_js
        assert "setState(newState)" in self.app_js
        assert "notify()" in self.app_js

    def test_spa_route_switch_exists(self):
        """SPA must have a switch/case routing mechanism."""
        assert "switch(route)" in self.app_js or "switch (route)" in self.app_js
        required_routes = ["dashboard", "opportunities", "facilities", "support", "login"]
        for route in required_routes:
            assert f"case '{route}'" in self.app_js, f"Missing route: {route}"

    def test_session_management(self):
        """Session save/clear/restore functions must exist."""
        assert "function saveSession" in self.app_js or "saveSession" in self.app_js
        assert "function clearSession" in self.app_js or "clearSession" in self.app_js
        assert "sessionStorage" in self.app_js

    def test_api_service_exists(self):
        """Centralized API service with fetchJSON and setToken must exist."""
        assert "ApiService" in self.api_js
        assert "fetchJSON" in self.api_js
        assert "setToken" in self.api_js

    def test_index_html_structure(self):
        """index.html must have nav, main app container, accessibility FABs, and script tags."""
        assert '<nav class="glass-nav"' in self.index_html
        assert 'id="app-root"' in self.index_html
        assert 'role="tablist"' in self.index_html
        assert "api.js" in self.index_html
        assert "app.js" in self.index_html

    def test_login_view_generator(self):
        """Login view must exist with form and authentication handling."""
        assert "generateLogin" in self.app_js
        assert "handleLoginSubmit" in self.app_js
        assert "login-form" in self.app_js

    def test_view_generators_exist(self):
        """Core view generator functions must exist for key features."""
        generators = [
            "generateDashboard", "generateOpportunities",
            "generateFacilities", "generateSupport",
        ]
        for gen in generators:
            assert gen in self.app_js, f"Missing view generator: {gen}"

    def test_loading_and_error_helpers(self):
        """Loading spinner and error display helpers must exist."""
        assert "renderLoading" in self.app_js
        assert "renderError" in self.app_js


class TestPhase8AccessibilityTheming:
    """Phase 8: Verify WCAG 2.1 AA compliance foundations and theming system."""

    @pytest.fixture(autouse=True)
    def load_files(self):
        with open(os.path.join(PROJECT_ROOT, "styles.css"), "r", encoding="utf-8") as f:
            self.styles_css = f.read()
        with open(os.path.join(PROJECT_ROOT, "app.js"), "r", encoding="utf-8") as f:
            self.app_js = f.read()
        with open(os.path.join(PROJECT_ROOT, "index.html"), "r", encoding="utf-8") as f:
            self.index_html = f.read()

    def test_css_custom_properties_defined(self):
        """CSS must define design tokens via custom properties."""
        required_vars = ["--primary", "--secondary", "--accent", "--bg-base", "--text-primary"]
        for var in required_vars:
            assert var in self.styles_css, f"Missing CSS custom property: {var}"

    def test_high_contrast_mode(self):
        """High contrast mode must override color variables for WCAG compliance."""
        assert "body.high-contrast" in self.styles_css
        # High contrast should use pure black/white
        assert "#000000" in self.styles_css
        assert "#FFFFFF" in self.styles_css

    def test_large_font_mode(self):
        """Large font mode must be available for visual accessibility."""
        assert "body.large-font" in self.styles_css or "large-font" in self.styles_css

    def test_screen_reader_only_class(self):
        """Screen-reader-only class must exist for hidden but accessible content."""
        assert ".sr-only" in self.styles_css

    def test_aria_attributes_in_html(self):
        """HTML must use ARIA attributes for assistive technology."""
        assert 'aria-label=' in self.index_html
        assert 'aria-live=' in self.index_html or 'aria-live=' in self.app_js
        assert 'role="tablist"' in self.index_html
        assert 'role="tab"' in self.index_html

    def test_skip_link_exists(self):
        """Skip-to-content link must exist for keyboard navigation."""
        assert "skip-link" in self.index_html or "Skip to main content" in self.index_html

    def test_focus_management(self):
        """Focus management must be implemented for route changes."""
        assert "focus()" in self.app_js
        assert "tabindex" in self.app_js

    def test_route_announcer_for_screen_readers(self):
        """Screen reader route announcer must exist for SPA navigation."""
        assert "routeAnnouncer" in self.app_js

    def test_accessibility_fab_buttons(self):
        """Floating action buttons for accessibility must exist."""
        assert "accessibility-fab" in self.index_html
        assert "emergency-fab" in self.index_html

    def test_eoc_theming_variables(self):
        """EOC-specific theming variables must be defined."""
        assert "--eoc-brand" in self.styles_css
        assert "--eoc-brand-light" in self.styles_css
