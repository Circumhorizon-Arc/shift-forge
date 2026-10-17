# HealthSense AI

**An AI-powered patient support and healthcare coordination platform.**

HealthSense AI is a hackathon prototype designed to help people understand medical report terminology, organize health information, track basic measurements, and prepare for conversations with healthcare professionals.

> **Important medical disclaimer:** HealthSense AI is an educational and organizational tool, not a medical device or substitute for professional medical advice, diagnosis, or treatment. It must not be used to make treatment decisions or as an emergency service. AI-generated explanations can be incomplete or incorrect; users should discuss their reports with a qualified healthcare professional.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Proposed Solution](#proposed-solution)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Overview](#api-overview)
- [Privacy and Safety](#privacy-and-safety)
- [Development Roadmap](#development-roadmap)
- [Team Contributions](#team-contributions)
- [Contributing](#contributing)
- [License](#license)

## Problem Statement

Medical reports often contain technical terms, laboratory values, units, and reference ranges that can be difficult for patients to interpret. Patients may also find it challenging to keep their records organized, monitor measurements over time, and remember follow-up appointments.

## Proposed Solution

HealthSense AI brings selected patient-support workflows into one web application. Its main feature is an AI-assisted medical report explainer that extracts available information from an uploaded report and presents a structured, plain-language explanation. Supporting features can help users maintain basic health records and organize follow-ups.

The prototype is intended to improve understanding and organization—not to diagnose conditions or replace clinicians.

## Key Features

### MVP (core scope)

- **Medical report upload:** Accept supported PDF and image files with server-side file validation.
- **Text extraction:** Extract text from digital PDFs and use OCR for supported scanned documents.
- **Structured findings:** Present extracted test names, values, units, reference ranges, and dates when available.
- **Plain-language explanations:** Generate an AI-assisted explanation grounded in extracted report content.
- **Consultation questions:** Suggest questions users may wish to discuss with a healthcare professional.
- **Report history:** Allow an authenticated user to view their own previously processed reports.

### Optional extensions

- **Health tracking:** Record user-entered measurements and display trends over time.
- **Follow-up reminders:** Organize appointment and follow-up reminders.
- **Multilingual explanations:** Provide supported-language explanations with appropriate quality checks.
- **Accessibility improvements:** Use readable layouts, clear language, keyboard navigation, and responsive design.

## Technology Stack

The proposed stack may change during development. Replace or remove technologies that are not actually used in the implementation.

| Layer | Proposed technology | Purpose |
|---|---|---|
| Frontend | React + TypeScript | User interface and dashboard |
| Styling | Tailwind CSS | Responsive styling |
| Charts | Recharts | Health measurement trends |
| Backend | Python + FastAPI | REST API and application logic |
| Validation | Pydantic | Request and response validation |
| Database | PostgreSQL | Users, report metadata, findings, and records |
| ORM / migrations | SQLAlchemy + Alembic | Database access and schema changes |
| PDF extraction | PyMuPDF | Extract text from digital PDFs |
| OCR | Tesseract OCR + Pillow | Extract text from supported scanned reports |
| AI | An LLM API or a suitable self-hosted model | Plain-language explanations |
| Testing | pytest | Backend and service tests |
| Version control | Git + GitHub | Collaboration and change tracking |
| Deployment | A hosting platform compatible with the chosen stack | Demo and application hosting |

Redis, Celery, Docker, and a vector database are optional. Add them only when the project needs them.

## System Architecture

```text
User
  |
  v
React + TypeScript frontend
  |
  | HTTPS / REST API
  v
FastAPI backend
  |                 |
  v                 v
PostgreSQL       Document processing
                 (PDF extraction / OCR)
                       |
                       v
                Structured extracted data
                       |
                       v
                 AI explanation service
                       |
                       v
             Validated explanation response
                       |
                       v
              Frontend results and history
```

The document-processing and AI components can initially be Python modules within the backend. They do not need to be separate microservices for a hackathon prototype.

## Project Structure

One possible starting structure is:

```text
carebridge-ai/
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
├── backend/
│   ├── src/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── config/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   │   ├── document_service.py
│   │   │   └── ai_service.py
│   │   └── utils/
│   ├── tests/
│   ├── migrations/
│   └── requirements.txt
├── docs/
├── .gitignore
├── .env.example
└── README.md
```

This is a suggested structure, not a claim that all directories or features have already been implemented.

## Getting Started

### Prerequisites

Install the tools required for the components you intend to run:

- Git
- Python 3.11 or a compatible version supported by your dependencies
- Node.js LTS and npm
- PostgreSQL
- Tesseract OCR, if OCR for scanned documents is enabled
- An API key for the selected AI provider, if using an external AI service

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd shift-forge
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

### 2. Configure the backend

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies after creating `requirements.txt`:

```bash
pip install -r requirements.txt
```

Configure the backend environment variables as described below. Create the database and apply the migrations once the project's database configuration and migrations are in place.

Start the development server (assuming the FastAPI application is exposed as `src.main:app`):

```bash
uvicorn src.main:app --reload
```

The API documentation is typically available at:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

These commands and paths may need adjustment to match the implemented project structure.

### 3. Configure the frontend

Open a second terminal:

```bash
cd frontend
npm install
```

Create a frontend environment file if required by your setup, then start the development server:

```bash
npm run dev
```

Use the local URL printed by the development server. Configure the frontend API base URL to point to the backend.

> The repository is a project blueprint until implementation files are added. Setup commands, scripts, routes, and environment variable names must match the actual code before the project is considered runnable.

## Environment Variables

Keep secrets in local environment files and hosting-provider secret settings. Never commit real API keys, passwords, database credentials, tokens, or patient data.

An illustrative `.env.example` might contain:

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/carebridge
SECRET_KEY=replace-with-a-long-random-secret
AI_PROVIDER=replace-with-your-provider
AI_API_KEY=
AI_MODEL=
FRONTEND_ORIGIN=http://localhost:5173
MAX_UPLOAD_SIZE_MB=10
```

These names are examples. Update them to match the application configuration. Use a strong generated secret for `SECRET_KEY`; do not use the example value in production. Keep `.env` files out of version control.

## API Overview

The following routes are proposed API contracts. They are not guaranteed to exist until implemented.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a user |
| `POST` | `/api/v1/auth/login` | Authenticate a user |
| `GET` | `/api/v1/auth/me` | Return the current user's profile |
| `POST` | `/api/v1/reports` | Upload a medical report |
| `GET` | `/api/v1/reports` | List the current user's reports |
| `GET` | `/api/v1/reports/{id}` | Retrieve an authorized report |
| `POST` | `/api/v1/reports/{id}/explain` | Request an AI-assisted explanation |
| `GET` | `/api/v1/reports/{id}/summary` | Retrieve a saved explanation |
| `POST` | `/api/v1/health-records` | Add a health measurement |
| `GET` | `/api/v1/health-records` | Retrieve health measurements |
| `POST` | `/api/v1/appointments` | Create an appointment or reminder |
| `GET` | `/api/v1/appointments` | List the current user's appointments |

Use authentication and server-side authorization for private resources. The backend must verify ownership on every report, finding, and health-record request; knowing an ID must never grant access.

## Privacy and Safety

Healthcare information is sensitive. Privacy and safety must be considered from the beginning, even for a hackathon prototype.

- Use synthetic or properly de-identified data for demonstrations and tests.
- Collect and retain only the information needed for the feature.
- Use HTTPS in deployment and restrict access to private records.
- Validate file types and sizes; do not trust a filename or client-supplied MIME type alone.
- Store uploaded files outside publicly served directories and use access-controlled file storage.
- Keep API keys and credentials on the server, never in frontend code or source control.
- Avoid sending direct identifiers or unnecessary report content to external AI providers.
- Clearly distinguish text extracted from a report from AI-generated explanations.
- Preserve source values and units; do not invent missing results or reference ranges.
- Treat AI output as potentially inaccurate and encourage users to consult qualified professionals.
- Provide an appropriate deletion process for user data and uploaded files.
- Do not present the application as a diagnostic, treatment, or emergency-response system.

Before handling real patient data, assess applicable privacy, security, and healthcare requirements for the deployment location and intended use.

## Development Roadmap

### Phase 1 — Core prototype

- [ ] Build the main dashboard and report upload flow.
- [ ] Add backend API validation and secure file handling.
- [ ] Extract text from supported PDF reports.
- [ ] Add OCR for supported scanned reports, if time permits.
- [ ] Display structured findings and their source values.
- [ ] Generate and validate plain-language explanations.
- [ ] Test the complete flow using synthetic reports.

### Phase 2 — Supporting features

- [ ] Add user accounts and protected report history.
- [ ] Add manual health measurements and charts.
- [ ] Add appointment or follow-up reminders.
- [ ] Improve mobile usability and accessibility.

### Phase 3 — Further development

- [ ] Add carefully evaluated multilingual support.
- [ ] Improve evaluation with a diverse set of synthetic test reports.
- [ ] Add monitoring, error reporting, and deployment hardening.
- [ ] Assess security, privacy, and applicable regulatory obligations before any real-world clinical use.

## Team Contributions

Update this section with actual team members and their contributions.

| Name | Area | Responsibilities |
|---|---|---|
| Shubhankit Shukla | Frontend | Dashboard, upload flow, report results, responsive UI |
| Sonu Kumar | Backend | API routes, database, authentication, file handling |
| Muhammad Suhail Jalal | AI / document processing | PDF/OCR extraction, explanation workflow, evaluation |
| Sunsuvan Bakshi | Integration and QA | End-to-end testing, deployment, demo preparation |

## Contributing

1. Create a branch for your change.
2. Keep changes focused and describe the purpose in your commit message.
3. Do not commit secrets, credentials, real medical reports, or personal health information.
4. Add or update tests for changed behavior.
5. Open a pull request and describe how the change was tested.

## License

No license has been selected yet. Add a `LICENSE` file and update this section once the project team has chosen a license. Do not assume that the code is open source until a license is provided.
