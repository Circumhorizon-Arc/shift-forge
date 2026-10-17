# 🌉 CareBridge AI — Smart Healthcare Assistant

> **IIITD Hackathon — Track 4: Healthcare & Well-being**  
> *Theme: Reimagining Healthcare Through Technology*

CareBridge AI is an AI-powered patient support and healthcare coordination platform designed to improve healthcare accessibility, affordability, and quality of care. It provides patients with one unified place to understand complex medical reports, track vital health records, manage doctor appointments, and receive intelligent clinical guidance.

---

## 🌟 Core Pillars & Features

### 1. 🔬 AI Medical Report Explainer (The Centerpiece Demo Feature)
- **Report Upload:** Supports PDF reports & medical scans with strict magic-byte validation.
- **High-Fidelity Extraction:** Text extraction powered by **PyMuPDF (`fitz`)** and **`pypdf`**.
- **Diagnostic Findings Breakdown:** Extracts individual test names, values, measurement units, and reference intervals (flagging abnormal findings).
- **Plain-Language Explanation:** AI translates complex medical jargon into clear, reassuring language without hallucinating.
- **Consultation Preparation:** Generates 3-5 tailored, actionable questions the patient can discuss with their doctor.
- **Medical Guardrails:** Clear clinical disclaimer; acts as an educational and organizational assistant.

### 2. 📊 Health Tracker (Vitals & Measurement Trends)
- Logs measurements: Blood Pressure, Fasting Glucose, Heart Rate, Weight, BMI.
- Historical data retrieval endpoint tailored for frontend charting libraries (**Recharts**).

### 3. ⏰ Care Reminders & Teleconsultation Appointments
- Track follow-up visits, diagnostic reminders, and daily medication schedules.
- Doctor-patient appointment booking with status management and clinical notes.

### 4. 🤖 AI Clinical Symptom Triage
- 4-Tier urgency triage: `low` (green), `moderate` (yellow), `high` (orange), `emergency` (red).
- Suggests appropriate medical specialists (e.g. Cardiologist, ENT, General Physician).
- Resilient heuristic fallback engine guarantees 100% demo uptime.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **FastAPI (Python)** | Asynchronous REST APIs, auto OpenAPI / Swagger documentation |
| **Database** | **PostgreSQL (SQLAlchemy 2.0 + Alembic)** | Relational data integrity, schema migrations, SQLite local fallback |
| **Document Processing** | **PyMuPDF + Pillow + pypdf** | PDF parsing, table extraction, header inspection |
| **AI Engine** | **Google Gemini (`gemini-1.5-flash`)** | Grounded report explanation, triage reasoning & consultation generation |
| **Security** | **Bcrypt + PyJWT (HTTPBearer)** | 12-round password hashing, stateless token auth, Role-Based Access Control |
| **Testing** | **pytest + TestClient** | 100% passing automated test suite |

---

## 📡 API Endpoints (CareBridge AI Blueprint)

| Method | Endpoint | Description | Auth |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register new account (patient / doctor) | Public |
| `POST` | `/api/v1/auth/login` | Authenticate & retrieve JWT Bearer token | Public |
| `GET` | `/api/v1/auth/me` | Fetch authenticated user profile | Bearer |
| `POST` | `/api/v1/reports` | Upload medical report (PDF/Image) | Bearer |
| `GET` | `/api/v1/reports` | List patient's uploaded reports | Bearer |
| `GET` | `/api/v1/reports/{id}` | Retrieve report details | Bearer |
| `POST` | `/api/v1/reports/{id}/explain` | **Trigger AI Report Explainer & Doctor Questions** | Bearer |
| `GET` | `/api/v1/reports/{id}/summary` | Retrieve pre-generated AI report summary | Bearer |
| `POST` | `/api/v1/health-records` | Add health vital measurement (BP, Glucose, etc.) | Bearer |
| `GET` | `/api/v1/health-records` | Retrieve measurement history (for charts) | Bearer |
| `POST` | `/api/v1/reminders` | Create medication or follow-up reminder | Bearer |
| `GET` | `/api/v1/reminders` | List active & completed reminders | Bearer |
| `PATCH`| `/api/v1/reminders/{id}` | Update or mark reminder completed | Bearer |
| `POST` | `/api/v1/ai/symptom-check` | AI symptom triage & specialist guidance | Bearer |
| `POST` | `/api/v1/appointments/` | Book doctor appointment | Bearer |
| `GET` | `/api/v1/appointments/` | List appointments (role filtered) | Bearer |
| `GET` | `/health` | Health & database readiness check | Public |

---

## 🚀 Running Locally

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate       # Windows
source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Run Tests
```bash
pytest -v
```
