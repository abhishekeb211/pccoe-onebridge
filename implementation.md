# PCCOE OneBridge: Implementation Details

A unified **student success and inclusion platform** for **PCCOE** that supports students from **1st year to 4th year**, across **all branches**, while also integrating **Equal Opportunity Cell (EOC)** services.

---

## 1. Core Architecture (No-SQL Pivot)

**PCCOE OneBridge** functions as a **single digital ecosystem** using a distributed JSON registry for high portability and speed.

### A. Data Persistence
- **Registry Engine**: `json_db.py` handles thread-safe read/write operations with file-level locking.
- **Storage**: All data resides in `data/*.json` (e.g., `students.json`, `tickets.json`).
- **Validation**: Strict schema enforcement via **Pydantic v2**.

### B. Student Requirements Module
- **Registry**: `tickets.json`
- **Working**: 
    - Text Classification via Local AI for routing.
    - Status tracking: *Submitted, Under Review, Approved, Resolved*.
    - Escalation logic based on JSON timestamp audits.

### C. Scholarships Hub
- **Registry**: `scholarships.json` and `applications.json`.
- **Smart Engine**: A **Scholarship Match Engine** suggests the most relevant schemes by comparing the Student Profile (JSON) against scholarship criteria (JSON) using AI-assisted matching.

---

## 2. Accessibility-First Design
The platform is built with **universal design** principles:
- Screen reader compatibility.
- High contrast and Large font modes.
- Keyboard-only navigation event listeners.

---

## 3. User Roles (RBAC)
- **Student**: Submit requirements, apply for opportunities.
- **Faculty Mentor**: Review student concerns and endorse applications.
- **EOC Admin**: Manage grievances and specialized welfare schemes.
- **Super Admin**: System-wide configuration and analytics.
