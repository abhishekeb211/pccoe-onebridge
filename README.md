# PCCOE OneBridge — Student Success & Inclusion Platform

[![Deploy to GitHub Pages](https://github.com/abhishekeb211/pccoe-onebridge/actions/workflows/main_pipeline.yml/badge.svg)](https://github.com/abhishekeb211/pccoe-onebridge/actions/workflows/main_pipeline.yml)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://abhishekeb211.github.io/pccoe-onebridge/)

OneBridge is a unified digital platform designed for **Pimpri Chinchwad College of Engineering (PCCOE)**. It focuses on academic support, professional growth, facility access, and inclusive student welfare.

## 🚀 Live Demo

Experience the platform immediately on GitHub Pages:
**[https://abhishekeb211.github.io/pccoe-onebridge/](https://abhishekeb211.github.io/pccoe-onebridge/)**

> [!NOTE]
> The live demo runs in **Demo Mode**. It uses local snapshots and mock data to showcase the full UI experience without requiring a backend server.

## 🚀 Deployment & CI/CD

### GitHub Actions
- Linting, testing, accessibility audits, and deployment are automated via `.github/workflows/main_pipeline.yml`.
- Docker image is built and pushed to GitHub Container Registry on every push.
- (Optional) Deploys to Fly.io if `FLY_API_TOKEN` is set in repository secrets.

### Docker
- Build and run locally:
  ```bash
  docker build -t special-students-app .
  docker run -p 8000:8000 special-students-app
  ```

### Fly.io
- Configure `fly.toml` and set `FLY_API_TOKEN` in repository secrets.
- Deploy via GitHub Actions or locally with:
  ```bash
  flyctl deploy
  ```

## ✨ Key Features

- **Academic Dashboard**: Unified view of attendance, deadlines, and notifications.
- **Opportunities Hub**: AI-matched scholarships, internships, and job postings.
- **Inclusive Support (EOC)**: Dedicated tools for the Equal Opportunity Cell, including confidential grievance filing and accessibility accommodations.
- **Resource Booking**: Digital access to labs, libraries, and seminar halls.
- **Smart Knowledge Base**: AI-assisted help desk for campus-related inquiries.
- **Accessibility First**: WCAG 2.1 compliant design with high-contrast and large-font modes.

## 🛠️ Technology Stack

- **Frontend**: Vanilla HTML5/CSS3/JS
- **Backend**: Python (FastAPI), Pydantic v2 Models
- **Persistence**: Synchronized JSON Registry (data/*.json)
- **Deployment**: GitHub Actions & GitHub Pages (Static), Docker (Production)

## 📦 Getting Started

### Local Development (Static Mode)
Simply open `index.html` in any modern browser or use a simple static server:
```bash
python -m http.server 3000
```

### Full Stack Setup (Backend Mode)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the JSON Registry:
   ```bash
   python -c "from database_schema import init_db; init_db()"
   ```
3. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
4. Access the platform at `http://localhost:8000/index.html`.

## 📄 Documentation

- [Deployment Guide](DEPLOYMENT.md) — How to host on GitHub Pages or VPS.
- [Architecture Overview](architecture.md) — System design and data flow.
- [Data Registry](ERD.md) — JSON specification and logical links.
- [Governance & AI Policy](ai_governance.md) — Responsible AI and PII handling.

## Error Monitoring & Analytics

### Sentry Integration

- **Frontend**: Sentry is initialized in `app.js` (see top of file). Replace the DSN with your Sentry project DSN.
- **Backend**: Sentry is initialized in `main.py` using `sentry_sdk` and the ASGI middleware. Set the `SENTRY_DSN` environment variable or edit the placeholder in code.

To enable Sentry:
- Create a free account at [sentry.io](https://sentry.io/)
- Create a project for both frontend (browser JS) and backend (Python/FastAPI)
- Replace the DSN placeholders in `app.js` and `main.py` with your actual DSNs
- (Optional) Set `SENTRY_DSN` in your deployment environment for backend

## GitHub Pages Deployment (Static Frontend)

### Step-by-Step Plan

1. **Preparation**
   - Ensure all static files ([index.html], [styles.css], [app.js], [data/]) are present and referenced in [index.html].
   - No backend dependencies required for static mode.
   - Initialize and push to a GitHub repository if not already done.

2. **GitHub Pages Configuration**
   - Enable GitHub Pages in repository settings, set source to "GitHub Actions".
   - Ensure `.github/workflows/main_pipeline.yml` exists and is correct.

3. **CI/CD Pipeline & Automated Checks**
   - Linting (HTML, CSS, JS), accessibility, and security scans run via GitHub Actions.
   - Static site is deployed using GitHub Actions workflows.

4. **Verification**
   - Automated: All QA jobs pass, deployment job succeeds.
   - Manual: Visit deployed site, verify navigation, mock data, accessibility, and no missing assets.

5. **Feedback Loop**
   - If checks fail, review logs, fix, and redeploy.
   - If manual verification fails, document and fix issues, then redeploy.

6. **Blockers & Issues**
   - Ensure workflow file name matches documentation ([DEPLOYMENT.md], [README.md]).
   - Ensure all referenced files exist (e.g., `api.js`).
   - Backend-only features are not available in static mode.

7. **Documentation Updates**
   - Update [DEPLOYMENT.md] and [README.md] for workflow file name and static asset requirements.
   - Document Demo Mode limitations and any missing files.

### Checklist
- [ ] All static files present and referenced.
- [ ] GitHub repository created and code pushed.
- [ ] GitHub Pages enabled with "GitHub Actions" as the source.
- [ ] Workflow file exists and is correct.
- [ ] All automated QA checks pass.
- [ ] Site loads and works in Demo Mode at the GitHub Pages URL.
- [ ] Accessibility and navigation verified manually.
- [ ] Documentation is up to date and accurate.
- [ ] Any issues found are documented and fixed, then redeployed.

---
Built with ❤️ for PCCOE.
