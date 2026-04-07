# PCCOE OneBridge Version Control & Branching Strategy

## Repository Management
To ensure a secure multi-developer environment and guarantee the integrity of our privacy-first local NLP logic, we strictly follow the **Git Flow** strategy.

### 1. Branching Naming Conventions
- `main` - Highly protected. Holds the production-ready code. Pull Requests (PRs) targeting `main` require at least 1 faculty/administrator review.
- `staging` - Pre-production. Automatically deployed to our internal test servers upon push.
- `feature/*` - Used for building isolated modules (e.g., `feature/module-c-scholarships`).
- `bugfix/*` - Specialized fixes mapping to urgent UI or API tickets.

### 2. Commit Requirements
All commits must follow conventional semantic guidelines:
- `feat: added smart routing logic to local agent`
- `fix: resolved API Gateway 500 error`
- `docs: updated Phase 5 tracking`

### 3. CI/CD Protection
All branches targeting `main` must dynamically pass the `.github/workflows/ci.yml` pipeline, which enforces:
1. **Security Scan:** Halts if APIs or OpenRouter tokens are leaked.
2. **Accessibility Scan:** Drops the build if semantic HTML or aria-labels are removed (ensuring constant compliance with Phase 1 WCAG mappings).
3. **Python Linting:** Ensures our FastApi schema matches Pydantic strict-types.
