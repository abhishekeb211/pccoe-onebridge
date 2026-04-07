# Technical Architecture: PCCOE OneBridge (Phase 2 Update)

## 1. System Overview & Traffic Flow Blueprint

This document standardizes the exact Data Flow Diagrams (DFD) and Unified Modeling Language (UML) Sequence logic dictating how PCCOE OneBridge securely manages traffic between the DOM (Front-End), the core API gateway, the private internal resources, and the external LLM cloud networks.

### 1.1 High-Level Data Flow Diagram (DFD Level 0)

```mermaid
graph TD
    %% User Nodes
    Student((Student User))
    Admin((EOC/Faculty Admin))

    %% Frontend App
    SPA[PCCOE OneBridge Vanilla SPA]

    %% Main Backend
    subgraph PCCOE Secure Intranet [PCCOE Secure Internal Network]
        Gateway[Python/Express API Gateway]
        DB[(Core Relational Database)]
        LocalAI[[Local NLP Agent - HuggingFace/Ollama]]
    end

    %% External Systems
    subgraph External Cloud [External AI Cloud]
        OpenRouter((OpenRouter Gateway))
        Gemini[Google Gemini API]
    end

    %% Flow Path
    Student -- HTTPS / WSS --> SPA
    Admin -- HTTPS / WSS --> SPA
    
    SPA -- REST JSON --> Gateway
    Gateway -- SQL/ORM --> DB
    
    Gateway -- Internal gRPC/REST --> LocalAI
    Gateway -- HTTPS/TLS (Anonymized Data) --> OpenRouter
    OpenRouter --> Gemini
```

---

## 2. Security & Firewall Boundaries

To ensure strict compliance with the **WCAG & Privacy PRD bounds (Phase 1)**, the network relies on air-gapped mentalities for EOC transactions:
- **Rule 1:** The Frontend SPA NEVER possesses or has access to external API Keys.
- **Rule 2:** The API Gateway acts as a strict sanitizer. All JSON payloads are stripped of `StudentID` strings and replaced with Hash UUIDs before transmission to the External Cloud.
- **Rule 3:** Direct database queries bypass external layers entirely using the `LocalAI` for smart routing logic.

---

## 3. Detailed UML Sequence Diagrams

### 3.1 Smart Routing & Helpdesk Sequence (Using Local AI)
This handles basic student requirements and ticket escalation without touching cloud APIs, ensuring sub-200ms performance as dictated by the NFR rules.

```mermaid
sequenceDiagram
    participant User as Student DOM
    participant API as API Gateway
    participant AI as Local NLP Agent
    participant DB as SQLite/PostgreSQL
    
    User->>API: POST /api/v1/tickets {description: "Need wheel-chair access"}
    activate API
    API->>AI: Text Classification {payload: "Need wheel-chair access"}
    activate AI
    AI-->>API: Returns Category: "EOC_PHYSICAL_ACCESS", Priority: "URGENT"
    deactivate AI
    
    API->>DB: INSERT Ticket WITH (Category, Priority)
    activate DB
    DB-->>API: 201 Created (TicketID: 8842)
    deactivate DB
    
    API-->>User: 201 Success Response JSON
    deactivate API
```

### 3.2 Generative Resume/Fellowship Scorer (Using Gemini API)
This maps the complex processing of checking an applicant's resume against Fellowship parameters.

```mermaid
sequenceDiagram
    participant User as Student DOM
    participant API as API Gateway
    participant Sanitizer as Backend Privacy Middleware
    participant Cloud as Gemini via OpenRouter
    
    User->>API: POST /api/v1/fellowships/evaluate {resume_text, fellowship_id}
    activate API
    API->>Sanitizer: Strip Name, Contact, Email 
    activate Sanitizer
    Sanitizer-->>API: Returns Anonymized Text
    deactivate Sanitizer
    
    API->>Cloud: POST/OpenRouter {prompt: anonymized_text + scoring criteria}
    activate Cloud
    Note over API,Cloud: 2000ms max latency window
    Cloud-->>API: JSON Response {score: 85, feedback: "Enhance SOP"}
    deactivate Cloud
    
    API-->>User: Renders Feedback to SPA Module D
    deactivate API
```

---

## 4. Accessibility Traffic
The frontend dynamically polls the backend to track accessibility issues (e.g. Broken Elevators).
If a facility manager flags a component, the database broadcasts an event. When a visually impaired user accesses the frontend SPA, the DOM automatically adjusts ARIA roles reading out real-time contingency blockers via the standard DOM API integrations.
