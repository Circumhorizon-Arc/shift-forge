# Health Sense — AI-Powered Healthcare & Well-Being Platform

A serious, presentation-ready healthcare web application built for a 24-hour hackathon. **Health Sense** helps users organize clinical records, understand diagnostic lab reports through plain-language AI-assisted explanations, track biomarker trends over time, and prepare structured questions for doctor consultations.

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

## 2. Key Features

- **AI-Assisted Report Explanation**:
  - Plain-language summary clearly labeled as an educational overview.
  - Structured Finding Cards with reference range indicators and neutral status ("Within reported reference range" / "Outside the laboratory's stated reference range").
  - "What Does This Mean?" plain-language educational breakdown.
  - Interactive "Questions to Ask Your Doctor" with checklist and one-click copy.
  - Downloadable summary and printable doctor consultation views.
- **Drag-and-Drop Medical Report Upload**:
  - Supports PDF, JPG, and PNG formats up to 25 MB.
  - Multi-stage upload simulation (Uploading → Parsing Observations → Plain-Language AI → Complete).
- **Patient Dashboard**:
  - Summary KPI cards (Reports, Records, Upcoming Appointment, Reminders).
  - Interactive Recharts Heart Rate Trend visualizer.
  - Quick-access Recent Reports and Next Consultation modules.
- **Health Records & Biomarker Trends**:
  - Multi-metric time-series trend visualizer (Heart Rate, Blood Pressure, Fasting Glucose, Weight, Temperature).
  - Modal to log new vital sign measurements with validation.
  - Historical entries table with deletion support.
- **Appointment Management**:
  - Filter by Upcoming and Past Consultations.
  - In-person clinic visits and Telehealth video appointments.
  - Booking modal with validation and instant UI updates.
- **Healthcare Reminders**:
  - Categorized tasks (Doctor Follow-Up, Lab Test Review, Annual Checkup, Medication Refill).
  - One-click completion toggling and deletion.
  - Modal to create reminders with priority flags.
- **Authentication & Settings**:
  - Dedicated `authService` layer for login and registration.
  - Profile management, notification preferences, and privacy controls.
- **Full Responsive Design**:
  - Desktop sidebar + main content layout.
  - Tablet collapsible navigation.
  - Mobile slide-over drawer navigation.

---

## 3. Tech Stack

- **Framework**: [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tool**: [Vite](https://vite.dev/)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com/)
- **Routing**: [React Router v7](https://reactrouter.com/)
- **Charts**: [Recharts](https://recharts.org/)
- **Icons**: [Lucide React](https://lucide.dev/)
- **HTTP Client**: [Axios](https://axios-http.com/)

---

## 4. API-First Architecture

The frontend components **never** directly call `axios` or `fetch`. All data operations flow through a strongly typed service abstraction layer:

```
Component
   ↓
Service (e.g. reportService, healthService, appointmentService, authService)
   ↓
Centralized API Client (src/services/api.ts)
   ↓
Backend API (or Mock Fallback if VITE_USE_MOCK_API=true)
```

### Switching Between Mock and Real Backend

Health Sense includes a configurable environment flag in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_USE_MOCK_API=true
```

- When `VITE_USE_MOCK_API=true`: Services utilize local simulated data with full CRUD state persistence in `localStorage`.
- When `VITE_USE_MOCK_API=false`: Services dispatch live HTTP requests to `VITE_API_BASE_URL` with JWT bearer authorization headers attached automatically via interceptors.

---

## 5. Project Structure

```
shift-forge/
├── src/
│   ├── components/
│   │   ├── layout/            # Sidebar, Header, MobileNavigation, AppLayout
│   │   ├── ui/                # Button, Card, Badge, Modal, Input, Select, etc.
│   │   ├── dashboard/         # StatCard, HealthTrendChart, RecentReports, etc.
│   │   ├── reports/           # FindingCard, DoctorQuestions, ReportUpload, etc.
│   │   └── health/            # HealthChart, HealthRecordFormModal
│   │
│   ├── pages/
│   │   ├── Landing.tsx        # Public landing page with problem/solution/features
│   │   ├── Login.tsx          # Login with authService abstraction
│   │   ├── Register.tsx       # Registration with validation
│   │   ├── Dashboard.tsx      # Patient overview with Recharts trends
│   │   ├── Reports.tsx        # Medical reports list with filtering & search
│   │   ├── UploadReport.tsx   # Drag-and-drop report uploader
│   │   ├── ReportAnalysis.tsx # STAR SCREEN: 5-section AI explanation
│   │   ├── HealthRecords.tsx  # Multi-metric vitals tracking
│   │   ├── Appointments.tsx   # Upcoming/past doctor appointments
│   │   ├── Reminders.tsx      # Healthcare task reminders
│   │   └── Settings.tsx       # Profile, preferences, and privacy
│   │
│   ├── services/
│   │   ├── api.ts             # Central Axios instance & error handler
│   │   ├── authService.ts     # Login, register, profile updates
│   │   ├── reportService.ts   # Report upload, listing, AI analysis
│   │   ├── healthService.ts   # Biomarker metrics and calculations
│   │   ├── appointmentService.ts # Appointment scheduling & listing
│   │   └── reminderService.ts # Reminder CRUD operations
│   │
│   ├── types/                 # Central TypeScript interfaces & barrel
│   ├── data/mock/             # Realistic synthetic clinical mock datasets
│   ├── context/               # AuthContext & ToastContext
│   ├── utils/                 # cn class utility
│   ├── routes/                # React Router index configuration
│   ├── App.tsx
│   └── main.tsx
├── .env.example
├── package.json
└── vite.config.ts
```

---

## 6. Installation & Running Locally

### Prerequisites
- Node.js (v18 or higher; v24 recommended)
- npm (v9 or higher)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Circumhorizon-Arc/shift-forge.git
   cd shift-forge
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   ```

4. **Start the local development server**:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

5. **Build for production**:
   ```bash
   npm run build
   ```

---

## 7. Real Backend Integration Guide

When you are ready to connect your backend services (FastAPI, Express, Django, etc.):

1. In `.env`, set:
   ```env
   VITE_API_BASE_URL=https://your-backend-api.com/api/v1
   VITE_USE_MOCK_API=false
   ```
2. Ensure your backend exposes standard REST endpoints matching the service contracts:
   - `POST /auth/login` → `{ user, token }`
   - `POST /auth/register` → `{ user, token }`
   - `GET /reports` → `MedicalReport[]`
   - `POST /reports/upload` → `multipart/form-data` with `{ report, analysis }`
   - `GET /reports/:id/analysis` → `ReportAnalysis`
   - `GET /health/records` → `HealthRecord[]`
   - `POST /health/records` → `HealthRecord`
   - `GET /appointments` → `Appointment[]`
   - `POST /appointments` → `Appointment`
   - `GET /reminders` → `Reminder[]`
   - `POST /reminders` → `Reminder`
   - `PATCH /reminders/:id/complete` → `Reminder`
3. All UI components will immediately display live data from your real backend without needing any component code modifications!
