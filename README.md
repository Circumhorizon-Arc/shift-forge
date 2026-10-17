# Health Sense — AI-Powered Healthcare & Well-Being Platform

A serious, presentation-ready healthcare platform built for the IIITD Hackathon (Theme 4: Healthcare & Well-Being). **Health Sense** helps users organize clinical records, understand diagnostic lab reports through plain-language AI-assisted explanations, track biomarker trends over time, and prepare structured questions for doctor consultations.

---

## 1. Project Overview

Medical laboratory reports are filled with complex scientific notation, reference ranges, and dense abbreviations. Patients often struggle to interpret their results, leading to unnecessary anxiety or overlooked warning signs.

**Health Sense** bridges this health literacy gap by:
1. Parsing uploaded laboratory reports (PDF, JPG, PNG).
2. Generating neutral, plain-language summaries and educational explanations.
3. Distinguishing numerical facts extracted from the report from AI educational explanations.
4. Providing actionable questions for patients to discuss with their healthcare professional.
5. Providing longitudinal health trend tracking (heart rate, blood pressure, glucose, weight, temperature).
6. Managing clinical appointments and health reminders.

> **Important Healthcare Safety Note:**  
> Health Sense is **not a doctor**. It does not diagnose medical conditions, prescribe medication, recommend changing treatment, or provide definitive clinical conclusions. All content is strictly educational and non-diagnostic.

---

## 2. Monorepo Architecture

```
shift-forge/
├── src/                    # Frontend: React 19 + TypeScript + Tailwind CSS (Vite)
├── backend/                # Backend: FastAPI + PostgreSQL + SQLAlchemy + Alembic
├── ai-service/             # AI Service: PyMuPDF + Gemini + Tesseract OCR
├── public/                 # Static assets
└── package.json            # Frontend scripts
```

---

## 3. Running the Backend API

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate       # Windows
source .venv/bin/activate      # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)
- **Automated Tests (13/13 Passed):** `pytest -v`

---

## 4. Running the Frontend (React + Vite)

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 5. Connecting Frontend to Real Backend

In `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API=false
```
All UI components will immediately display live data from your real backend!
