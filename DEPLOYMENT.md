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
   - Once set to "GitHub Actions", the workflow at `.github/workflows/deploy.yml` will automatically trigger on every push to the `main` branch.

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

## Full Stack (Local Development)

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Then open `index.html` in a browser, or serve with:
```bash
python -m http.server 3000
```
