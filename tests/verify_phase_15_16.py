"""
Phase 15-16 Verification Tests
- Phase 15: OpenRouter API Gateway Setup (LLM connectivity, rate limiting, retry logic)
- Phase 16: AI Context Injection & Sanitization (PII scrubbing, system prompts)

Tests verify the LLM gateway configuration, PII sanitization pipeline,
system prompt library, rate limiting, and usage tracking.
"""
import pytest
import re
import time


# ============================================================================
# Phase 15: OpenRouter API Gateway Setup
# ============================================================================

class TestOpenRouterGateway:
    def test_gateway_singleton_exists(self):
        """LLM gateway singleton must be importable."""
        from llm_gateway import llm_gateway
        assert llm_gateway is not None

    def test_gateway_model_configuration(self):
        """Gateway must be configured with Gemini Pro model."""
        from llm_gateway import llm_gateway
        assert "gemini" in llm_gateway.model.lower()

    def test_gateway_base_url(self):
        """Gateway must point to OpenRouter API."""
        from llm_gateway import llm_gateway
        assert "openrouter.ai" in llm_gateway.base_url

    def test_rate_limiter_initialization(self):
        """Rate limiter must be initialized with configurable RPM."""
        from llm_gateway import llm_gateway
        assert hasattr(llm_gateway, "max_requests_per_minute")
        assert llm_gateway.max_requests_per_minute > 0
        assert hasattr(llm_gateway, "_request_timestamps")

    def test_rate_limit_enforcement(self):
        """Rate limit must block when exceeded."""
        from llm_gateway import GeminiOpenRouterGateway
        gw = GeminiOpenRouterGateway()
        gw.max_requests_per_minute = 3

        # Simulate 3 requests
        for _ in range(3):
            gw._check_rate_limit()

        # 4th should raise
        with pytest.raises(RuntimeError, match="Rate limit exceeded"):
            gw._check_rate_limit()

    def test_usage_stats_tracking(self):
        """Usage stats must track request counts."""
        from llm_gateway import GeminiOpenRouterGateway
        gw = GeminiOpenRouterGateway()

        stats = gw.get_usage_stats()
        assert "total_requests" in stats
        assert "total_tokens_estimate" in stats
        assert "requests_in_last_minute" in stats
        assert "rate_limit_rpm" in stats
        assert stats["total_requests"] == 0

    def test_system_prompts_defined(self):
        """System prompt library must contain required prompt types."""
        from llm_gateway import SYSTEM_PROMPTS
        required = ["student_assist", "ticket_clarify", "eoc_guidance", "readiness_feedback"]
        for key in required:
            assert key in SYSTEM_PROMPTS, f"Missing system prompt: {key}"
            assert len(SYSTEM_PROMPTS[key]) > 50, f"System prompt too short: {key}"

    def test_system_prompts_content_quality(self):
        """System prompts must mention PCCOE and key guidelines."""
        from llm_gateway import SYSTEM_PROMPTS
        assert "PCCOE" in SYSTEM_PROMPTS["student_assist"]
        assert "personal" in SYSTEM_PROMPTS["student_assist"].lower()
        assert "empathetic" in SYSTEM_PROMPTS["eoc_guidance"].lower() or "sensitive" in SYSTEM_PROMPTS["eoc_guidance"].lower()


# ============================================================================
# Phase 16: AI Context Injection & Sanitization
# ============================================================================

class TestPIISanitization:
    def test_email_redaction(self):
        """Emails must be redacted before LLM transmission."""
        from llm_gateway import llm_gateway
        text = "Contact me at student@pccoepune.org for details"
        result = llm_gateway._sanitize(text)
        assert "student@pccoepune.org" not in result
        assert "[REDACTED_EMAIL]" in result

    def test_phone_number_redaction(self):
        """Phone numbers (10+ digits) must be redacted."""
        from llm_gateway import llm_gateway
        text = "My phone is 9876543210 and PRN is 20240100012345"
        result = llm_gateway._sanitize(text)
        assert "9876543210" not in result
        assert "20240100012345" not in result
        assert "[REDACTED_PRN/PHONE]" in result

    def test_dob_redaction_dd_mm_yyyy(self):
        """Dates of birth in DD/MM/YYYY format must be redacted."""
        from llm_gateway import llm_gateway
        text = "My DOB is 15/03/2002"
        result = llm_gateway._sanitize(text)
        assert "15/03/2002" not in result
        assert "[REDACTED_DOB]" in result

    def test_dob_redaction_iso_format(self):
        """Dates in YYYY-MM-DD format must be redacted."""
        from llm_gateway import llm_gateway
        text = "Born on 2002-03-15"
        result = llm_gateway._sanitize(text)
        assert "2002-03-15" not in result
        assert "[REDACTED_DOB]" in result

    def test_aadhaar_redaction(self):
        """Aadhaar-style 12-digit IDs must be redacted."""
        from llm_gateway import llm_gateway
        text = "Aadhaar: 1234 5678 9012"
        result = llm_gateway._sanitize(text)
        assert "1234 5678 9012" not in result

    def test_name_redaction_after_prefix(self):
        """Names following common prefixes (Student, Mr., etc.) must be redacted."""
        from llm_gateway import llm_gateway
        text = "Student Abhishek Bhosale needs disability accommodation"
        result = llm_gateway._sanitize(text)
        assert "Abhishek" not in result
        assert "Bhosale" not in result
        assert "[REDACTED_NAME]" in result

    def test_sanitizer_preserves_non_pii_content(self):
        """Non-PII content must be preserved after sanitization."""
        from llm_gateway import llm_gateway
        text = "I need help with my scholarship application for engineering"
        result = llm_gateway._sanitize(text)
        assert "scholarship" in result
        assert "engineering" in result
        assert "help" in result

    def test_multiple_pii_types_in_single_text(self):
        """Multiple PII types in one text must all be redacted."""
        from llm_gateway import llm_gateway
        text = "Student Rahul Kumar, email rahul@pccoe.org, phone 9876543210, DOB 01/01/2000"
        result = llm_gateway._sanitize(text)
        assert "rahul@pccoe.org" not in result
        assert "9876543210" not in result
        assert "01/01/2000" not in result

    def test_scrub_rules_structure(self):
        """Scrub rules must be a list of (pattern, replacement) tuples."""
        from llm_gateway import llm_gateway
        assert isinstance(llm_gateway.scrub_rules, list)
        assert len(llm_gateway.scrub_rules) >= 5  # At least 5 scrub rules
        for rule in llm_gateway.scrub_rules:
            assert len(rule) == 2  # (pattern, replacement)
            # Verify pattern is valid regex
            re.compile(rule[0])
