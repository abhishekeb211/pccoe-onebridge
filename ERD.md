# OneBridge JSON Data Structure Spec (No-SQL Pivot)

This document maps the JSON structure and logical relationships within the 100% Flat-File Registry.

## 1. Core Data Flow logic
- All data is stored in the `data/` directory as managed JSON objects.
- Business logic maintains "Logical Foreign Keys" (e.g. `student_id` in `tickets.json` maps to `id` in `students.json`).
- Persistence is handled by `json_db.py` with thread-safe file locking.

## 2. Principal Data Registries

### 2.1 Students (`students.json`)
```json
{
  "id": 1,
  "prn": "2024CS001",
  "name": "Abhishek B",
  "email": "abhishek@pccoe.edu.in",
  "branch": "Computer Engineering",
  "year_of_study": 3,
  "role": "student",
  "is_disadvantaged": false,
  "has_disability": false
}
```

### 2.2 Support Tickets (`tickets.json`)
```json
{
  "id": 101,
  "student_id": 1,
  "category": "Academic",
  "description": "Difficulty accessing LMS modules",
  "status": "Submitted",
  "predicted_department_id": "it_operations_desk",
  "urgent_flag": false,
  "created_at": "2026-04-20T00:00:00Z"
}
```

### 2.3 Opportunities (`opportunities.json`)
```json
{
  "id": 501,
  "type": "internship",
  "title": "Google STEP 2025",
  "target_branches": "Computer Engineering,IT",
  "target_years": "2,3",
  "deadline": "2026-05-30T23:59:59Z"
}
```

## 3. High-Performance Indexing
While there are no SQL indexes, the `JSONDatabase.find_one` and `JSONDatabase.find_many` methods provide efficient O(n) filtering for local file sizes expected in this platform (<10k records).
- **Primary Key**: The `id` field is auto-incremented during insertion.
- **Unique Constraint**: The `prn` field is treated as a unique logical index for student lookups.
