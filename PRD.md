# Business Requirements Document (PRD): PCCOE OneBridge

## 1. Project Vision
To create a high-performance, accessible, and AI-driven Student Success Platform for PCCOE, focusing on unified access to scholarships, career opportunities, and an intelligent grievance helpdesk. The system is designed to empower every Student, including those with disabilities and from disadvantaged backgrounds, ensuring equal opportunity and support throughout their academic journey.

## 2. Core Pillars
- **Inclusivity & Accessibility**: Native-level support for students with disabilities and disadvantaged backgrounds.
- **AI-Driven Efficiency**: Local and Cloud-based AI for ticket routing and profile matching.
- **Privacy First**: Zero-PII transmission to external cloud services.
- **Portable Architecture**: 100% JSON-based persistence for simple deployment and high speed.

## 3. Key Features
- **Smart Helpdesk**: Local AI categorizes and routes student issues to the correct department.
- **AI Profile Matcher**: Matches students with Scholarships and Internships based on academic data.
- **Equal Opportunity Cell (EOC) Portal**: Confidential grievance handling for specifically-abled students.
- **Resource Booking**: Seamless reservation of campus labs and facilities.

## 4. Technical Stack (Phase 3 Updated)
- **Frontend**: Vanilla HTML/CSS/JS SPA (WCAG 2.1 AA Compliant).
- **Backend**: FastAPI (Python).
- **Persistence Layer**: 100% Synchronized JSON Registry (`data/*.json`).
- **Validation Engine**: Pydantic v2 Models.
- **AI Routing**: Local Distil-BART models.

## 5. Non-Functional Requirements (NFR)
- **Performance**: Sub-200ms local routing.
- **Security**: Air-gapped confidentiality for EOC data.
- **Uptime**: 99.9% during academic hours.
