# Product Requirements Document (PRD): PCCOE OneBridge

## 1. Executive Summary
**PCCOE OneBridge** is a unified digital platform combining student lifecycle management (academics, support, facilities) with an inclusive opportunity engine (scholarships, fellowships, EOC). The system serves engineering students from 1st to 4th year and is distinctively engineered for accessibility, assisting socially disadvantaged and disabled students.

## 2. Target Audience & Roles
1. **Primary End-Users:**
   - 1st-4th Year Engineering Students (all branches).
   - Students with Disabilities (visual, auditory, motor or cognitive).
   - Socio-economically disadvantaged groups requiring EOC (Equal Opportunity Cell) assistance.
2. **Administrative & Supporting Roles:**
   - EOC Advisors & Grievance Admins.
   - Faculty Mentors & Department Coordinators.
   - Placement Cell Officers & Scholarships Officers.
   - Facility Managers (Labs, Library, Hostels).

## 3. Scope of the Platform
### In-Scope (MVP mapped to Architecture)
- Centralized ticketing system for administrative requests (Smart Routing).
- 3-Tier Help Desk (Technical, Academic, Wellbeing).
- AI-driven Scholarship and Fellowship Match Engines.
- Interactive Year-wise Internship/Job Dashboards.
- Digital Facility Booking System and Accessibility Override tags.
- Dedicated Confidential EOC Integration for grievance redressal and scribe requests.

### Out-of-Scope (for current build)
- Complete replacement of external state government portals (e.g., MahaDBT). We only bridge and track applications.
- Payroll generation for faculties or fee transaction gateways (handled by existing ERPs).

## 4. Key Business Logic Rules
- **Access Rule 1:** Only students mapped to 'Disabled' or 'Disadvantaged' tags or manually flagged by a mentor can access specific Confidential EOC Grievance nodes.
- **Access Rule 2:** 1st Year Jobs feed restricts display of full-time campus placements; restricts 4th Year feeds from introductory bootcamps to reduce noise.
- **Booking Rule 1:** Facility bookings labeled with 'Accessibility Required' bypass standard queue waitlists automatically.

## 5. Non-Functional Requirements (NFRs)
- **NFR-1 Applicability/Accessibility:** System must strictly adhere to WCAG 2.1 Level AA guidelines. Heavy testing using keyboard-only interaction and screen readers (NVDA/JAWS) is essential. High-Contrast mode must exist.
- **NFR-2 Speed & Performance:** The Core UI (Vanilla JS SPA) must load within <1.2 seconds globally. Local agent NLP categorizations must take < 200ms. External Gemini API calls should render using streaming or complete within 2000ms.
- **NFR-3 Privacy & Security:** OpenRouter API keys strictly held backend. The platform must never send PII (Personally Identifiable Information like full names/contact info) to the external Gemini parser.
- **NFR-4 Supabase Integrity:** Data must be synced in real-time using Supabase Realtime for ticket updates. All database actions must be performed via row-level security (RLS) policies.
- **NFR-5 Uptime:** Minimum 99.9% uptime during prime business hours (8 AM - 6 PM IST) aligning with academic operations.

## 6. Success Metrics
- 30% increase in scholarship and fellowship awareness & applications.
- 50% reduction in physical ticket routing to the incorrect department.
- High usability feedback score from the Equal Opportunity Cell.
