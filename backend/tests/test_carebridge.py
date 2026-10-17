import io


def get_auth_token(client, email="carebridge_user@example.com"):
    client.post("/api/v1/auth/register", json={
        "email": email,
        "password": "Password123!",
        "full_name": "CareBridge Patient",
        "role": "patient",
    })
    res = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": "Password123!",
    })
    return res.json()["access_token"]


def test_health_record_tracker(client):
    token = get_auth_token(client, "vitals_patient@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Add Blood Pressure Systolic
    res = client.post("/api/v1/health-records", json={
        "metric_type": "blood_pressure_sys",
        "value": 120.0,
        "unit": "mmHg",
        "notes": "Morning check",
    }, headers=headers)
    assert res.status_code == 201
    assert res.json()["value"] == 120.0

    # Add Glucose
    client.post("/api/v1/health-records", json={
        "metric_type": "glucose",
        "value": 95.0,
        "unit": "mg/dL",
    }, headers=headers)

    # Fetch history
    history_res = client.get("/api/v1/health-records", headers=headers)
    assert history_res.status_code == 200
    assert len(history_res.json()) >= 2

    # Fetch filtered
    glucose_res = client.get("/api/v1/health-records?metric_type=glucose", headers=headers)
    assert glucose_res.status_code == 200
    assert len(glucose_res.json()) == 1
    assert glucose_res.json()[0]["metric_type"] == "glucose"


def test_care_reminders(client):
    token = get_auth_token(client, "reminders_patient@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Create reminder
    res = client.post("/api/v1/reminders", json={
        "title": "Take Vitamin D3 Capsule",
        "description": "After breakfast",
        "due_at": "2026-10-18T09:00:00Z",
    }, headers=headers)
    assert res.status_code == 201
    rem_id = res.json()["id"]
    assert res.json()["is_completed"] is False

    # List reminders
    list_res = client.get("/api/v1/reminders", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Mark completed
    patch_res = client.patch(f"/api/v1/reminders/{rem_id}", json={
        "is_completed": True,
    }, headers=headers)
    assert patch_res.status_code == 200
    assert patch_res.json()["is_completed"] is True
    assert patch_res.json()["completed_at"] is not None


def test_carebridge_medical_report_explainer(client):
    token = get_auth_token(client, "report_patient@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Upload mock lab report
    pdf_text = b"%PDF-1.4 Mock Complete Blood Count Report Hemoglobin 12.8 g/dL Fasting Glucose 108 mg/dL WBC 7400"
    mock_file = io.BytesIO(pdf_text)
    files = {"file": ("blood_report.pdf", mock_file, "application/pdf")}
    data = {"title": "Annual Blood Panel Test"}

    upload_res = client.post("/api/v1/reports", files=files, data=data, headers=headers)
    assert upload_res.status_code == 201
    report_id = upload_res.json()["id"]
    assert upload_res.json()["title"] == "Annual Blood Panel Test"

    # 2. Trigger AI Medical Report Explainer (Centerpiece Feature)
    explain_res = client.post(f"/api/v1/reports/{report_id}/explain", headers=headers)
    assert explain_res.status_code == 200
    data = explain_res.json()

    assert data["report_id"] == report_id
    assert "summary" in data
    assert "plain_language_explanation" in data
    assert "findings" in data
    assert len(data["findings"]) >= 1
    assert "doctor_questions" in data
    assert len(data["doctor_questions"]) >= 1
    assert "disclaimer" in data

    # 3. Retrieve pre-generated summary
    summary_res = client.get(f"/api/v1/reports/{report_id}/summary", headers=headers)
    assert summary_res.status_code == 200
    assert summary_res.json()["report_id"] == report_id
