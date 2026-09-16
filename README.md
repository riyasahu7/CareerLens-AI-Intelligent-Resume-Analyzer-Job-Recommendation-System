<div align="center">

<img src="https://img.shields.io/badge/CareerLens-AI-6366f1?style=for-the-badge&logo=openai&logoColor=white" alt="CareerLens AI"/>

# CareerLens AI
### Intelligent Resume Analyzer & Job Recommendation System

**Understand your resume. Improve your career.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com/atlas)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-CSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)

[Features](#-features) • [Demo](#-demo) • [Tech Stack](#-tech-stack) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [ML Details](#-how-the-ai--ml-works)

---

![CareerLens AI Dashboard](https://raw.githubusercontent.com/yourusername/careerlens-ai/main/docs/dashboard-preview.png)

</div>

---

## 🎯 What is CareerLens AI?

CareerLens AI is a **full-stack, production-ready AI-powered career platform** that helps job seekers:

- 📄 **Parse PDF resumes** and extract structured information automatically
- 🎯 **Score resumes** with an explainable ATS-style scoring engine
- 🔍 **Match against job descriptions** using TF-IDF cosine similarity
- 💡 **Get role recommendations** based on detected skills
- 📚 **Receive a personalised learning plan** for every skill gap
- 🤖 **Get AI feedback** via OpenAI (or rule-based if no API key)

> **Honest disclaimer:** ATS scores are explainable estimates based on defined rules — not a simulation of any proprietary hiring system. Scores do not predict hiring outcomes.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **Authentication** | JWT + bcrypt register/login/logout/change-password |
| 📄 **PDF Upload & Parsing** | pdfplumber + PyPDF2 fallback, graceful failure for scanned PDFs |
| 🔬 **Resume Analysis** | Section detection, skill extraction, contact info check |
| ⭐ **ATS Scoring** | Explainable 0–100 score across 5 weighted categories |
| 🎯 **Job Match** | TF-IDF cosine similarity + skill overlap against any job description |
| 💡 **Role Recommendations** | Scored matches for 9 roles based on skill overlap |
| 📚 **Learning Plan** | Curated tasks, mini-projects & time estimates for each skill gap |
| 🤖 **AI Feedback** | OpenAI integration with transparent rule-based fallback |
| 📊 **Dashboard** | Charts, score trends, skill radar, recent history |
| 🗂️ **History** | Full analysis history with view/delete |
| 🛡️ **Admin Panel** | User management and platform statistics (role-based) |
| 📱 **Responsive** | Works on desktop, tablet, and mobile |

---

## 🖥️ Demo

### Landing Page
> Modern SaaS landing with feature highlights and clear CTAs

### Dashboard
> Real-time stats: total resumes, average ATS score, skill distribution radar chart, score trend bar chart

### Resume Analysis
> Explainable score breakdown, section detection, skill badges, job keyword matching, improvement suggestions

### Recommendations
> Role match cards with score rings, skill gap breakdown, expandable learning plan with practice tasks and mini-projects

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core language |
| **Flask 3** | Web framework |
| **Flask-JWT-Extended** | Token-based authentication |
| **Flask-Bcrypt** | Password hashing |
| **Flask-PyMongo** | MongoDB integration |
| **Flask-CORS** | Cross-origin resource sharing |
| **pdfplumber** | Primary PDF text extraction |
| **PyPDF2** | Fallback PDF extraction |
| **scikit-learn** | TF-IDF vectorization + cosine similarity |
| **NumPy** | Numerical operations |
| **Gunicorn** | Production WSGI server |

### Frontend
| Technology | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite 5** | Build tool |
| **Tailwind CSS 3** | Utility-first styling |
| **React Router 6** | Client-side routing |
| **Recharts** | Dashboard charts (Bar, Radar) |
| **Axios** | HTTP client with interceptors |
| **react-hot-toast** | Toast notifications |
| **react-dropzone** | Drag-and-drop file upload |

### Infrastructure
| Technology | Purpose |
|---|---|
| **MongoDB Atlas** | Cloud database |
| **Render** | Backend deployment |
| **Vercel** | Frontend deployment |

---

## 🏗️ Architecture

```
careerlens-ai/
│
├── backend/                          # Flask REST API
│   ├── app/
│   │   ├── __init__.py               # App factory (create_app)
│   │   ├── config.py                 # Environment-based configuration
│   │   ├── extensions.py             # PyMongo, Bcrypt, JWT, CORS instances
│   │   │
│   │   ├── blueprints/               # Route handlers
│   │   │   ├── auth.py               # Register, login, logout, profile
│   │   │   ├── resumes.py            # Upload, list, get, delete
│   │   │   ├── analysis.py           # Resume analysis, job match, history
│   │   │   ├── recommendations.py    # Role recommendations + learning plan
│   │   │   ├── admin.py              # Admin stats, user management
│   │   │   └── health.py             # Health check endpoint
│   │   │
│   │   ├── services/                 # Business logic (no Flask dependencies)
│   │   │   ├── pdf_extractor.py      # PDF text extraction with fallback
│   │   │   ├── skill_extractor.py    # Rule-based skill detection (100+ skills)
│   │   │   ├── ats_scorer.py         # Explainable ATS scoring engine
│   │   │   ├── tfidf_service.py      # TF-IDF cosine similarity
│   │   │   ├── recommender.py        # Job role recommendation engine
│   │   │   ├── learning_plan.py      # Skill gap + learning plan generator
│   │   │   └── llm_service.py        # OpenAI integration + rule-based fallback
│   │   │
│   │   ├── models/                   # MongoDB document helpers
│   │   │   ├── user.py
│   │   │   ├── resume.py
│   │   │   ├── analysis.py
│   │   │   └── recommendation.py
│   │   │
│   │   └── utils/
│   │       ├── validators.py         # Input validation (email, password, file)
│   │       └── helpers.py            # safe_filename, ObjectId conversion
│   │
│   ├── tests/                        # 26 unit + integration tests
│   │   ├── test_skills.py
│   │   ├── test_tfidf.py
│   │   ├── test_ats.py
│   │   ├── test_pdf.py
│   │   ├── test_recommender.py
│   │   └── test_api.py
│   │
│   ├── requirements.txt
│   ├── run.py                        # Dev server entry point
│   ├── pytest.ini
│   └── render.yaml                   # Render deployment config
│
├── frontend/                         # React + Vite SPA
│   ├── src/
│   │   ├── pages/                    # 13 pages
│   │   │   ├── Landing.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx         # Charts, stats, history
│   │   │   ├── Upload.jsx            # Drag-and-drop PDF upload
│   │   │   ├── Analysis.jsx          # Full analysis results
│   │   │   ├── JobMatch.jsx          # TF-IDF job matching
│   │   │   ├── Recommendations.jsx   # Role cards + learning plan
│   │   │   ├── History.jsx
│   │   │   ├── Profile.jsx
│   │   │   ├── Settings.jsx
│   │   │   ├── Admin.jsx
│   │   │   └── NotFound.jsx
│   │   │
│   │   ├── components/
│   │   │   ├── layout/               # AppLayout, Sidebar, Navbar
│   │   │   ├── ui/                   # ScoreRing, Badge, Skeleton, StatCard, EmptyState
│   │   │   └── ProtectedRoute.jsx
│   │   │
│   │   ├── context/AuthContext.jsx   # JWT auth state + helpers
│   │   ├── services/api.js           # Axios instance with interceptors
│   │   ├── hooks/useApi.js           # Generic loading/error hook
│   │   └── utils/formatters.js       # Date, bytes, score formatters
│   │
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── vercel.json                   # SPA routing for Vercel
│
├── .gitignore
└── README.md
```

---

## 🧠 How the AI / ML Works

### 1. PDF Text Extraction — Rule-based
- **Primary:** `pdfplumber` reads text layer page-by-page
- **Fallback:** `PyPDF2` if pdfplumber returns empty
- **Failure:** Clear user message if PDF is scanned/image-only (no OCR)

### 2. Skill Extraction — Deterministic Rule-based
- Dictionary of **100+ skills** in 8 categories (Languages, Frameworks, Databases, Cloud, ML, Cybersecurity, Tools, Soft Skills)
- Word-boundary regex matching — prevents false positives (`C` ≠ `C++`)
- Only detects skills **explicitly present in text** — nothing is inferred or invented

### 3. ATS Scoring — Explainable Rule-based

```
Category                Weight   Method
─────────────────────── ──────   ──────────────────────────────────
Section Completeness     30%     Regex detection of 8 resume sections
Skill Coverage           25%     +5 points per detected skill (cap 100)
Keyword Match            25%     Job keywords found in resume (if JD given)
Formatting Signals       10%     Bullet points, word count, date formats
Contact Information      10%     Email, phone, LinkedIn, GitHub presence
```

### 4. Job Description Matching — ML (TF-IDF)
- `TfidfVectorizer(ngram_range=(1,2), stop_words='english', sublinear_tf=True)`
- Cosine similarity between resume and JD vectors → 0–100 score
- Top JD keywords cross-referenced against resume text
- **Measures keyword overlap, not semantic understanding**

### 5. Role Recommendations — Rule-based Scoring
```
match_score = (matched_required × 0.7 + matched_nice × 0.3) / max_possible × 100
```
- 9 roles with curated required + nice-to-have skill lists
- Sorted by score descending

### 6. LLM Feedback — Optional (OpenAI)
| Condition | Behaviour | Label shown in UI |
|---|---|---|
| `OPENAI_API_KEY` set | Calls `gpt-4o-mini` with structured JSON prompt | `AI-generated` |
| No API key | Rule-based heuristics (weak verbs, missing sections, etc.) | `Rule-based` |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB Atlas account (free tier works)

### 1. Clone the repository
```bash
git clone https://github.com/riyasahu7/CareerLens-AI-Intelligent-Resume-Analyzer-Job-Recommendation-System.git
cd CareerLens-AI-Intelligent-Resume-Analyzer-Job-Recommendation-System
```

### 2. Backend setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env — fill in MONGO_URI, SECRET_KEY, JWT_SECRET_KEY
```

### 3. Frontend setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# VITE_API_URL is already set for local dev via Vite proxy
```

### 4. Run both servers

**Terminal 1 — Backend:**
```bash
cd backend
.venv\Scripts\activate   # Windows
python run.py
# → http://localhost:5000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# → http://localhost:5173
```

Visit **http://localhost:5173** and register an account.

---

## ⚙️ Environment Variables

### `backend/.env`

```env
FLASK_ENV=development
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MONGO_URI=mongodb+srv://<user>:<password>@cluster.mongodb.net/careerlens?retryWrites=true&w=majority
CORS_ORIGINS=http://localhost:5173
MAX_UPLOAD_MB=5
STORE_RESUME_FILES=false

# Optional — enables AI feedback (leave blank for rule-based)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
```

### `frontend/.env`

```env
VITE_API_URL=http://localhost:5000/api
```

---

## 📡 API Documentation

### Authentication
```
POST   /api/auth/register          Register new user
POST   /api/auth/login             Login → receive JWT
POST   /api/auth/logout            Logout (client discards token)
GET    /api/auth/me                Get current user
PUT    /api/auth/profile           Update full name
PUT    /api/auth/change-password   Change password
```

### Resumes
```
POST   /api/resumes                Upload PDF resume
GET    /api/resumes                List all resumes
GET    /api/resumes/<id>           Get resume metadata
DELETE /api/resumes/<id>           Delete resume + linked analyses
```

### Analysis
```
POST   /api/analysis/resume        Run full resume analysis
POST   /api/analysis/job-match     TF-IDF + skill match vs job description
GET    /api/analysis/history       List all analyses
GET    /api/analysis/<id>          Get analysis details
DELETE /api/analysis/<id>          Delete an analysis
```

### Recommendations
```
POST   /api/recommendations        Generate role recommendations + learning plan
GET    /api/recommendations        List recommendations
GET    /api/recommendations/<id>   Get recommendation details
```

### Admin (admin role required)
```
GET    /api/admin/stats            Platform stats
GET    /api/admin/users            All users list
```

### Health
```
GET    /api/health                 Service + DB health check
```

---

## 🗄️ Database Schema

### Collections

**users**
```json
{
  "email": "string (unique, indexed)",
  "password": "bcrypt hash",
  "full_name": "string",
  "role": "user | admin",
  "is_active": true,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

**resumes**
```json
{
  "user_id": "string",
  "filename": "string (sanitised)",
  "original_filename": "string",
  "extracted_text": "string",
  "file_size_bytes": "number",
  "extraction_method": "pdfplumber | pypdf2 | failed",
  "extraction_success": "boolean",
  "created_at": "datetime"
}
```

**analyses**
```json
{
  "user_id": "string",
  "resume_id": "string",
  "ats_result": { "overall_score": 0, "grade": "A-F", "category_scores": {} },
  "skills": ["Python", "React", "..."],
  "sections": { "contact": true, "experience": true, "..." : false },
  "job_description": "string (optional)",
  "job_match_result": { "tfidf_score": 0, "matched_keywords": [] },
  "llm_feedback": { "source": "llm | rule_based", "suggestions": [] },
  "created_at": "datetime"
}
```

---

## 🧪 Tests

```bash
cd backend
pip install pytest
pytest tests/ -v
```

**26 tests across 5 files:**

| File | Tests | What it covers |
|---|---|---|
| `test_skills.py` | 6 | Skill extraction, categories, edge cases |
| `test_tfidf.py` | 4 | Similarity scoring, keyword matching |
| `test_ats.py` | 5 | ATS scoring, grades, suggestions |
| `test_pdf.py` | 4 | PDF extraction failure handling |
| `test_recommender.py` | 7 | Role matching, learning plan generation |

---

## 🚢 Deployment

### Backend → Render.com

1. Push `backend/` to GitHub
2. New Web Service on [render.com](https://render.com)
3. **Build command:** `pip install -r requirements.txt`
4. **Start command:** `gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2`
5. Add environment variables in Render dashboard

### Frontend → Vercel.com

1. Push `frontend/` to GitHub
2. Import on [vercel.com](https://vercel.com) → Framework: **Vite**
3. Set `VITE_API_URL` = your Render backend URL
4. Deploy — `vercel.json` handles SPA routing

---

## ⚠️ Known Limitations

- **Scanned PDFs** — image-only PDFs cannot be parsed (no OCR). Users receive a clear error message.
- **ATS Score** — explains resume quality across defined dimensions; does not replicate any company's proprietary ATS.
- **Skill detection** — keyword-based; synonyms outside the dictionary are not detected.
- **TF-IDF** — measures keyword frequency overlap, not semantic understanding.
- **LLM feedback** — requires OpenAI API key; rule-based fallback is used otherwise.

---

## 🔮 Future Improvements

- [ ] OCR support for scanned PDFs (Tesseract)
- [ ] Semantic similarity using sentence-transformers
- [ ] Resume version comparison
- [ ] Export analysis as PDF report
- [ ] Email verification & password reset
- [ ] Industry-specific skill dictionaries
- [ ] Multi-language resume support
- [ ] Resume templates and builder

---

## 📁 Project Stats

| Metric | Value |
|---|---|
| Total source files | 79 |
| Backend files | 35 |
| Frontend files | 44 |
| API endpoints | 20+ |
| Skills in dictionary | 100+ |
| Supported job roles | 9 |
| Test cases | 26 |
| Lines of code | ~4,500 |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 👤 Author

Built with ❤️ as a full-stack AI/ML portfolio project.

**Stack:** Flask · React · MongoDB · scikit-learn · TailwindCSS

---

<div align="center">

⭐ **If this project helped you, please give it a star!** ⭐

</div>
