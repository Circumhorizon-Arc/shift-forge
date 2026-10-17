# 🩺 ShiftForge Healthcare Backend API

> **IIITD Hackathon — Track 4: Healthcare & Well-being**  
> *Theme: Reimagining Healthcare Through Technology*

A production-grade, fast, and scalable FastAPI backend built with PostgreSQL (SQLAlchemy + Alembic), Google Gemini AI integration, role-based JWT authentication, file upload processing for medical reports/prescriptions, and interactive Swagger API documentation.

---

## 🚀 Features

- **FastAPI Routes & Authentication**:
  - Secure bcrypt password hashing
  - JWT Access Token generation & expiration
  - Role-Based Access Control (**Patient**, **Doctor**, **Admin**)
- **PostgreSQL Database & Alembic Migrations**:
  - SQLAlchemy ORM models: `User`, `Document`, `AIInteraction`, `Appointment`
  - Automatic Alembic migration setup (`alembic upgrade head`)
  - Zero-config local SQLite fallback for instant development
- **File Validation & Document Processing**:
  - Strict file extension checking (`pdf`, `png`, `jpg`, `jpeg`)
  - Magic byte verification (header checks preventing file spoofing)
  - 10MB size limit enforcement
  - Text & PDF extraction with `pypdf`
- **AI Service Integration (Google Gemini)**:
  - Clinical symptom triage & urgency rating (`low`, `moderate`, `high`, `emergency`)
  - Differential condition suggestions and specialist recommendations
  - Prescription & lab report summarization
  - Resilient heuristic fallback engine (backend never crashes during demo)
- **API Testing, Deployment & Error Handling**:
  - 100% passing automated test suite with `pytest` and `TestClient`
  - Global standardized error handlers (CORS, 422 validation, 401/403 auth, 500 unhandled)
  - Ready-to-deploy `Dockerfile` and `render.yaml` (1-click cloud deployment with PostgreSQL)

---

## 🛠️ Quickstart

### 1. Setup Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Add your `GEMINI_API_KEY` in `.env` (optional: works in heuristic mode even without key).
Set your `DATABASE_URL` (e.g. `postgresql://user:pass@localhost:5432/shiftforge` or keep SQLite for local testing).

### 4. Run Migrations
```bash
alembic upgrade head
```

### 5. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
Open **Interactive Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
Open **Alternative ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Run Automated Tests
```bash
pytest -v
```

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Health & DB connection check | Public |
| `POST` | `/api/v1/auth/register` | Register new user (Patient / Doctor) | Public |
| `POST` | `/api/v1/auth/login` | Login and receive JWT access token | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Bearer Token |
| `POST` | `/api/v1/ai/symptom-check` | AI symptom triage & specialist guidance | Bearer Token |
| `GET` | `/api/v1/ai/history` | User's past triage history | Bearer Token |
| `POST` | `/api/v1/documents/upload` | Upload & AI process prescription/report | Bearer Token |
| `GET` | `/api/v1/documents/` | List medical records | Bearer Token |
| `GET` | `/api/v1/documents/{id}` | View single record | Bearer Token |
| `POST` | `/api/v1/appointments/` | Book doctor appointment | Bearer Token |
| `GET` | `/api/v1/appointments/` | List appointments (role filtered) | Bearer Token |
| `PATCH`| `/api/v1/appointments/{id}`| Update status / doctor notes | Doctor/Admin |
