# PCCOE OneBridge — Student Success & Inclusion Platform

[![Deploy to GitHub Pages](https://github.com/abhishekeb211/pccoe-onebridge/actions/workflows/deploy.yml/badge.svg)](https://github.com/abhishekeb211/pccoe-onebridge/actions/workflows/deploy.yml)
[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://abhishekeb211.github.io/pccoe-onebridge/)

OneBridge is a unified digital platform designed for **Pimpri Chinchwad College of Engineering (PCCOE)**. It focuses on academic support, professional growth, facility access, and inclusive student welfare.

## 🚀 Live Demo

Experience the platform immediately on GitHub Pages:
**[https://abhishekeb211.github.io/pccoe-onebridge/](https://abhishekeb211.github.io/pccoe-onebridge/)**

> [!NOTE]
> The live demo runs in **Demo Mode**. It uses local snapshots and mock data to showcase the full UI experience without requiring a backend server.

## ✨ Key Features

- **Academic Dashboard**: Unified view of attendance, deadlines, and notifications.
- **Opportunities Hub**: AI-matched scholarships, internships, and job postings.
- **Inclusive Support (EOC)**: Dedicated tools for the Equal Opportunity Cell, including confidential grievance filing and accessibility accommodations.
- **Resource Booking**: Digital access to labs, libraries, and seminar halls.
- **Smart Knowledge Base**: AI-assisted help desk for campus-related inquiries.
- **Accessibility First**: WCAG 2.1 compliant design with high-contrast and large-font modes.

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (Custom Design System), JavaScript (ES6+)
- **Backend**: Python (FastAPI), SQLAlchemy, Supabase (Auth/Database)
- **Deployment**: GitHub Actions & GitHub Pages (Static), Docker (Production)

## 📦 Getting Started

### Local Development (Static Mode)
Simply open `index.html` in any modern browser or use a simple static server:
```bash
python -m http.server 3000
```

### Full Stack Setup (with Backend)
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
3. Access the frontend at `http://localhost:8000/index.html` (or via your static server).

## 📄 Documentation

- [Deployment Guide](DEPLOYMENT.md) — How to host on GitHub Pages or VPS.
- [Architecture Overview](architecture.md) — System design and data flow.
- [Database Schema](ERD.md) — Relationship diagram and entity details.
- [Governance & AI Policy](ai_governance.md) — Responsible AI and PII handling.

---
Built with ❤️ for PCCOE.
