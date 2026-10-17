# 🌉 CareBridge AI — Smart Healthcare Assistant

> **IIITD Hackathon Project**  
> **Theme 4:** Healthcare & Well-being (Reimagining Healthcare Through Technology)  
> **Mission:** Empowering patients to understand medical reports, track health vitals, manage appointments, and receive intelligent clinical triage guidance.

---

## 🌟 The Centerpiece: AI Medical Report Explainer
- **High-Fidelity PDF/OCR Extraction:** Powered by **PyMuPDF (`fitz`)** and `pypdf`.
- **Diagnostic Findings Breakdown:** Extracts test names, reported values, units, and standard reference intervals.
- **Plain-Language Explanations:** Explains what clinical terms mean without medical jargon.
- **Doctor Consultation Questions:** Generates personalized questions patients can discuss with their clinician.
- **Clinical Safety Guardrails:** Clear educational disclaimer; no unauthorized prescriptions or self-diagnosis.

---

## 📊 Complete Feature Matrix
1. **AI Medical Report Explainer:** `/api/v1/reports` & `/api/v1/reports/{id}/explain`
2. **Health Tracker (Vitals for Charts):** `/api/v1/health-records`
3. **Care Reminders (Medications & Follow-ups):** `/api/v1/reminders`
4. **Clinical Symptom Triage:** `/api/v1/ai/symptom-check`
5. **Doctor-Patient Appointments:** `/api/v1/appointments`
6. **Authentication & Security:** `/api/v1/auth/register` & `/api/v1/auth/login`

---

## 🚀 Running the Project

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
- **Automated Tests (100% Passing):** `pytest -v`