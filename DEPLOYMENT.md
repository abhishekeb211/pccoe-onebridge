# PCCOE OneBridge — Deployment Guide

## GitHub Pages (Static Frontend)

The frontend works as a standalone static site with mock data when the backend API is unavailable.

### Setup Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: PCCOE OneBridge"
   git remote add origin https://github.com/<your-username>/pccoe-onebridge.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**
   - Go to **Settings → Pages** in your repository.
   - > [!IMPORTANT]
   - > Under **Build and deployment > Source**, you MUST select **"GitHub Actions"** from the dropdown menu. 
   - > By default, GitHub often sets this to "Deploy from a branch", which will NOT work with our custom workflow.
   - Once set to "GitHub Actions", the workflow at `.github/workflows/main_pipeline.yml` will automatically trigger on every push to the `main` branch.

3. **Access Your Site**
   - URL: `https://<your-username>.github.io/pccoe-onebridge/`
   - The site runs in **Demo Mode** — all views use mock data.
   - Login with any username/password to access the dashboard.


### Demo Mode Features
- All 14 navigation views fully functional
- Realistic Indian education mock data (scholarships, careers, resources)
- Knowledge Base with 18 FAQs across 6 categories
- Chatbot with offline KB search
- Light/Dark theme toggle
- WCAG 2.1 AA accessible

### Notes
- Python backend (`main.py`) is not deployed to GitHub Pages
- API calls gracefully fall back to mock data
- File uploads and real-time features require the backend server

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

## Full Stack (Local Development)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Then open `index.html` in a browser, or serve with:
```bash
python -m http.server 3000
```

## Docker & Fly.io Deployment

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

### CI/CD
- Linting, testing, accessibility audits, and deployment are automated via `.github/workflows/main_pipeline.yml`.
- Docker image is built and pushed to GitHub Container Registry on every push.
- (Optional) Deploys to Fly.io if `FLY_API_TOKEN` is set in repository secrets.
