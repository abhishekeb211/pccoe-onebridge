# Entity Relationship Model (Phase 4)

Below is the Entity Relationship Diagram (ERD) visualizing the precise PostgreSQL/SQLite architecture bridging the components written in `database_schema.py`.

```mermaid
erDiagram
    STUDENT {
        int id PK
        string prn UK
        string name
        string email UK
        enum branch
        int year_of_study
        boolean is_disadvantaged
        boolean has_disability
        text accessibility_requirements
    }

    SUPPORT_TICKET {
        int id PK
        int student_id FK
        string category
        string predicted_department_id
        text description
        enum status
        boolean urgent_flag
        datetime created_at
    }

    FACILITY_BOOKING {
        int id PK
        int student_id FK
        string facility_name
        datetime booking_time
        boolean accessibility_override_applied
    }

    OPPORTUNITY {
        int id PK
        string type
        string title
        string target_branches
        string target_years
        boolean requires_disability_status
        datetime deadline
    }

    %% Relationships
    STUDENT ||--o{ SUPPORT_TICKET : "creates"
    STUDENT ||--o{ FACILITY_BOOKING : "reserves"
    
    %% AI Match Engine Context Boundary
    STUDENT }o--o{ OPPORTUNITY : "AI dynamically matches (Many-to-Many logic handled off-DB via Gemini)"
```
