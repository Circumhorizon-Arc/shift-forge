# 🩺 ShiftForge — Healthcare & Well-being Platform

> **IIITD Hackathon Project**  
> **Theme 4:** Reimagining Healthcare Through Technology  
> **Objective:** Develop technology-driven solutions to improve healthcare accessibility, affordability, and quality of care via AI-assisted guidance, smart digital health management, and remote consultations.

---

## 🏗️ Project Architecture

```
shift-forge/
├── .gitignore
├── README.md
└── backend/
    ├── app/
    │   ├── core/           # Security (JWT, bcrypt) & RBAC Dependencies
    │   ├── models/         # PostgreSQL SQLAlchemy Models (User, Document, AIInteraction, Appointment)
    │   ├── routes/         # FastAPI Routers (Auth, AI, Documents, Appointments, Health)
    │   ├── schemas/        # Pydantic v2 validation models
    │   ├── services/       # File validation, PDF parser & Google Gemini AI service
    │   ├── config.py       # Pydantic settings & env management
    │   ├── database.py     # Database engine & session generator
    │   └── main.py         # App factory, CORS, exception handlers
    ├── alembic/            # Database schema migrations
    ├── tests/              # 100% passing automated test suite (pytest)
    ├── Dockerfile          # Containerized deployment
    ├── render.yaml         # 1-click cloud deployment with PostgreSQL
    └── requirements.txt    # Python dependencies
```

---

## 🚀 Running the Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate       # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

- **Interactive API Docs (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Testing
```bash
cd backend
pytest -v
```