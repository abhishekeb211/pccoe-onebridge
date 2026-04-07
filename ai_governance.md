# AI Strategy & Data Governance - PCCOE OneBridge

This document dictates the absolute boundaries and data compliance rules for all Artificial Intelligence layers executing within the PCCOE OneBridge platform. It implements Phase 3 of the system lifecycle, defining rules for both Local Agents and External Cloud APIs.

---

## 1. Local AI vs External LLM Distinctions

To ensure optimal privacy, particularly surrounding the **Equal Opportunity Cell (EOC)** operations, the platform utilizes a hybrid Dual-Agent design.

### 1.1 The Local NLP Agent (Privacy-First)
* **Designated Models:** `distilbert-base-uncased` (HuggingFace) or `llama3-8b` (Local Ollama Instance).
* **Allowed Use-Cases:**
  * Smart-Routing of student Help Desk tickets (Intent classification).
  * Fast, real-time Help Desk Chatbot processing generic FAQ from the college knowledge base.
  * EOC distress detection (Locally flagging distress language without cloud intervention).
* **Network Constraint:** This model MUST run solely on PCCOE's isolated intranet servers. No connection to public internets is required or permitted for inference.

### 1.2 The External Cloud API (Reasoning-Heavy)
* **Designated Models:** `google/gemini-1.5-pro` and `google/gemini-1.5-flash` accessed STRICTLY via **OpenRouter**.
* **Allowed Use-Cases:**
  * Operating the Scholarship Profile Matcher (Module C).
  * Operating the Fellowship Readiness Scorer (Module D).
* **API Limits:** 
  * Max tokens per request: 1200.
  * Rate limit: Maximum 50 requests per student per day.
  * Timeouts: API gateways must terminate the request and return a standard DOM error if Gemini takes > 3000ms.

---

## 2. Hard Anonymization Rules & Privacy Guardrails

Before ANY string of data is transmitted to OpenRouter (Gemini), it must pass through the `PrivacySanitizer` middleware located on the Backend Server.

### 2.1 Anonymization Regex Scrubbing
The `PrivacySanitizer` must run Regex filters to remove the following specific PII (Personally Identifiable Information) blocks from being sent to external clouds:
- **Names:** Scrubbed using NLP NER (`spaCy` pre-processing).
- **PRN / Student IDs:** Any 8-12 digit sequence.
- **Phone Numbers:** `(\+\d{1,3}[- ]?)?\d{10}`
- **Email Addresses:** `[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}`

**Mechanism:** 
If a student pastes a resume to check their *Fellowship Readiness Score*, the server reads:
> *"My name is Jane Smith, contact: jane@pccoe.edu, PRN: 11029482. I built a predictive model..."*
It transforms it locally before sending to Gemini:
> *"My name is [REDACTED], contact: [REDACTED], PRN: [REDACTED]. I built a predictive model..."*

### 2.2 EOC Strict-Airgap Policy
- **Absolute Rule:** Data categorized as "Confidential Grievance" or specific "Disability Scribe Records" are permanently blocked from leaving the local server. The external gateway middleware must hard-reject ANY payload originating from the EOC module. 

---

## 3. Tech Stack Governance & Management
* **Credentials:** OpenRouter API keys (`OPENROUTER_API_KEY`) will only be mounted securely in the backend backend environment variables.
* **Cost Governance:** A daily maximum spend limit of $5.00 USD will be configured directly inside the OpenRouter API dashboard.
* **LLM Lock-in Avoidance:** Using OpenRouter ensures that if Gemini APIs degrade in speed or raise pricing, PCCOE can flawlessly redirect the API string to a different model (e.g., Claude 3.5 Sonnet) within 60 seconds without altering the core backend pipeline logic.
