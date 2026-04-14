import httpx
import re
import os
import time
import logging
from typing import Dict, Any

# Phase 15 & 16: OpenRouter Server Gateway and Context Sanitization Layer

logger = logging.getLogger("OneBridge.OpenRouter")

# System prompt library for role-based AI context injection
SYSTEM_PROMPTS = {
    "student_assist": (
        "You are an AI academic assistant for PCCOE (Pimpri Chinchwad College of Engineering). "
        "Provide helpful, factual guidance about academics, campus services, scholarships, and career resources. "
        "Never reveal personal student data. Keep answers concise and actionable. "
        "If unsure, advise the student to contact the relevant department directly."
    ),
    "ticket_clarify": (
        "You are a support ticket analyst at PCCOE. Given a student's support request, "
        "generate a brief clarifying question or suggest the most relevant department. "
        "Do not guess personal details. Be professional and concise."
    ),
    "eoc_guidance": (
        "You are an Equal Opportunity Cell advisor at PCCOE. Provide sensitive, "
        "empathetic guidance on accessibility accommodations, disability services, and grievance procedures. "
        "Never store or repeat personal identifiers. Always recommend following up with a human EOC coordinator."
    ),
    "readiness_feedback": (
        "You are a career readiness advisor at PCCOE (Pimpri Chinchwad College of Engineering). "
        "Analyze the student's resume or statement of purpose against fellowship/opportunity criteria. "
        "Provide a readiness score (0-100), highlight strengths, identify gaps, and give specific actionable tips. "
        "Be encouraging but honest. Never reveal or store personal identifiers. "
        "Focus on technical skills, project experience, communication clarity, and format quality."
    ),
}


class GeminiOpenRouterGateway:
    """
    Middleware handling External LLM Connectivity.
    Strictly scrubs all Prompts for PII before ever transmitting to OpenRouter to fulfill NFR Privacy Laws.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "dummy-development-key")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-pro"
        
        # Rate limiting state
        self._request_timestamps: list[float] = []
        self.max_requests_per_minute = int(os.getenv("LLM_RATE_LIMIT_RPM", "20"))
        self._total_requests = 0
        self._total_tokens_estimate = 0

        # Phase 16: Anonymization regex pipeline — expanded for comprehensive PII coverage
        self.scrub_rules = [
            # Emails
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
            # Phone/PRN (10-14 digit numbers)
            (r'\b\d{10,14}\b', '[REDACTED_PRN/PHONE]'),
            # Date of birth patterns: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
            (r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', '[REDACTED_DOB]'),
            (r'\b\d{4}[/\-]\d{1,2}[/\-]\d{1,2}\b', '[REDACTED_DOB]'),
            # Aadhaar-style (12 digits with optional spaces)
            (r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[REDACTED_ID]'),
            # Capitalized proper names (heuristic: 2+ consecutive capitalized words not at sentence start)
            (r'(?<=[a-z.,;:]\s)[A-Z][a-z]{2,}\s+[A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})?', '[REDACTED_NAME]'),
            # Names after common prefixes
            (r'(?:Student|Name|Mr\.|Ms\.|Mrs\.|Dr\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', '[REDACTED_NAME]'),
        ]

    def _sanitize(self, text: str) -> str:
        """Applies Privacy Layer before network request."""
        scrubbed = text
        for pattern, replacement in self.scrub_rules:
            scrubbed = re.sub(pattern, replacement, scrubbed)
        return scrubbed

    def _check_rate_limit(self):
        """Enforce requests-per-minute rate limit."""
        now = time.time()
        self._request_timestamps = [t for t in self._request_timestamps if now - t < 60]
        if len(self._request_timestamps) >= self.max_requests_per_minute:
            raise RuntimeError(
                f"Rate limit exceeded: {self.max_requests_per_minute} requests/min. Try again shortly."
            )
        self._request_timestamps.append(now)

    async def generate_response(
        self, system_prompt: str, user_prompt: str, max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Executes external asynchronous logic securely with retry and rate limiting.
        """
        self._check_rate_limit()
        safe_prompt = self._sanitize(user_prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://pccoepune.org",
            "X-Title": "PCCOE OneBridge Alpha",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": safe_prompt}
            ],
            "temperature": 0.2
        }
        
        logger.info("Transmitting sanitized prompt to OpenRouter...")
        
        last_error = None
        for attempt in range(1, max_retries + 2):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.base_url, headers=headers, json=payload, timeout=10.0
                    )
                    response.raise_for_status()
                    data = response.json()

                # Validate response structure
                choices = data.get("choices")
                if not choices or not isinstance(choices, list):
                    raise ValueError("Invalid response: missing 'choices' array")

                message = choices[0].get("message", {})
                content = message.get("content")
                if not content:
                    raise ValueError("Invalid response: empty content")

                # Track usage
                self._total_requests += 1
                usage = data.get("usage", {})
                self._total_tokens_estimate += usage.get("total_tokens", len(safe_prompt.split()) * 2)

                logger.info(
                    f"OpenRouter response OK (attempt {attempt}, "
                    f"tokens ~{usage.get('total_tokens', 'N/A')}, "
                    f"total reqs: {self._total_requests})"
                )

                return {"status": "success", "data": content}

            except httpx.HTTPStatusError as exc:
                last_error = exc
                if exc.response.status_code == 429:
                    logger.warning(f"Rate limited by OpenRouter (attempt {attempt}). Backing off...")
                elif exc.response.status_code >= 500:
                    logger.warning(f"OpenRouter server error {exc.response.status_code} (attempt {attempt}).")
                else:
                    logger.error(f"OpenRouter HTTP error: {exc}")
                    return {"status": "error", "message": f"LLM request failed: {exc.response.status_code}"}
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                logger.warning(f"OpenRouter request error (attempt {attempt}): {exc}")

            # Exponential backoff: skip sleep on last attempt
            if attempt <= max_retries:
                backoff = 2 ** (attempt - 1)
                import asyncio
                await asyncio.sleep(backoff)

        logger.error(f"All {max_retries + 1} attempts failed. Last error: {last_error}")
        return {"status": "error", "message": "Failed to communicate with LLM gateway after retries."}

    def get_usage_stats(self) -> Dict[str, Any]:
        """Returns cumulative usage statistics for monitoring."""
        return {
            "total_requests": self._total_requests,
            "total_tokens_estimate": self._total_tokens_estimate,
            "requests_in_last_minute": len([
                t for t in self._request_timestamps if time.time() - t < 60
            ]),
            "rate_limit_rpm": self.max_requests_per_minute,
        }


# Singleton Instantiation
llm_gateway = GeminiOpenRouterGateway()
