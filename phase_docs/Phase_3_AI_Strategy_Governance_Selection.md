# Phase 3: AI Strategy & Governance Selection

## 1. Module Overview
**Functionality**: Determine the boundaries for the AI models.
**Working Mechanism**: Distinguishes inputs handled by the Local Agent (privacy-first) versus external outputs required from Gemini via OpenRouter.

## 2. Detailed Tasks
- `[x]` Review system requirements against PRD for this phase.
- `[x]` Establish initial sandbox/development branch for 3.
- `[x]` Execute Core Task: Finalize API limits, data anonymization rules before LLM querying, and local NLP model selections.
- `[x]` Perform unit testing on the specific modules integrated.
- `[x]` Conduct accessibility and security review before requesting a merge.

## 3. Requirements
**Functional Requirements:**
- Must successfully fulfill the working mechanism: Distinguishes inputs handled by the Local Agent (privacy-first) versus external outputs required from Gemini via OpenRouter..
- Output must be integrated securely and without latency impacting the main thread.

**Non-Functional Requirements:**
- **Performance:** Sub-200ms response time for local functions, optimized async calls for external ones.
- **Privacy:** Anonymize all data if interfacing with external LLMs.
- **Accessibility:** Ensure all new UI complies with WCAG 2.1 AA standards.

## 4. Libraries & Tech Stack
- Supabase SDK (Data Verification)
- OpenRouter API SDK
- Google Generative AI bindings
- HuggingFace Transformers (Local agent)
- Git & GitHub CLI (Version Control)

