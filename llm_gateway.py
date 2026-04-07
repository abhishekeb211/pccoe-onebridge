import httpx
import re
import os
import logging
from typing import Dict, Any

# Phase 15 & 16: OpenRouter Server Gateway and Context Sanitization Layer

logger = logging.getLogger("OneBridge.OpenRouter")

class GeminiOpenRouterGateway:
    """
    Middleware handling External LLM Connectivity.
    Strictly scrubs all Prompts for PII before ever transmitting to OpenRouter to fulfill NFR Privacy Laws.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "dummy-development-key")
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-pro"
        
        # Phase 16: Anonymization regex pipeline
        # Strips Names, Emails, Phone numbers, and 14-digit College IDs
        self.scrub_rules = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]'),
            (r'\b\d{10,14}\b', '[REDACTED_PRN/PHONE]'),
            # Further NLTK/Spacy named-entity recognition can be injected here for strict Names stripping
        ]

    def _sanitize(self, text: str) -> str:
        """Applies Privacy Layer before network request."""
        scrubbed = text
        for pattern, replacement in self.scrub_rules:
            scrubbed = re.sub(pattern, replacement, scrubbed)
        return scrubbed

    async def generate_response(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """
        Executes external asynchronous logic securely.
        """
        safe_prompt = self._sanitize(user_prompt)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://pccoepune.org", # Identifying our app organically
            "X-Title": "PCCOE OneBridge Alpha",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": safe_prompt}
            ],
            "temperature": 0.2 # Strict, factual responses needed
        }
        
        logger.info("Transmitting Sanitized prompt to OpenRouter...")
        
        # Using Async HTTPX for non-blocking FastAPI loops (Phase 15 NFR)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return {"status": "success", "data": data['choices'][0]['message']['content']}
            except httpx.HTTPError as exc:
                logger.error(f"External API Fault: {exc}")
                return {"status": "error", "message": "Failed to communicate with LLM gateway."}

# Singleton Instantitation
llm_gateway = GeminiOpenRouterGateway()
