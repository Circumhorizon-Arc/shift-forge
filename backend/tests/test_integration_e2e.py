import io
from fastapi.testclient import TestClient


def test_full_integration_pipeline(client: TestClient):
    """
    End-to-End Integration Test:
    Verifies that Frontend API contracts, Backend Business Logic,
    and AI Medical Extraction flow seamlessly together.
    """
    # -------------------------------------------------------------
    # 1. Full Authentication Life-Cycle
    # -------------------------------------------------------------
    reg_payload = {
        "fullName": "Sarah Jenkins",
        "email": "sarah.jenkins@healthsense.dev",
        "password": "SecurePassword123!",
        "dateOfBirth": "1994-08-20",
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "token" in reg_data
    token = reg_data["token"]
    assert reg_data["user"]["fullName"] == "Sarah Jenkins"

    headers = {"Authorization": f"Bearer {token}"}

    # Verify Profile
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["user"]["email"] == "sarah.jenkins@healthsense.dev"

    # -------------------------------------------------------------
    # 2. Medical Report Upload & Immediate AI Analysis
    # -------------------------------------------------------------
    # Create sample PDF content with standard clinical lab findings
    report_content = (
        b"%PDF-1.4\n"
        b"HEALTHSENSE DIAGNOSTIC PATHOLOGY LABORATORY\n"
        b"Patient Name: Sarah Jenkins\n"
        b"Report Date: October 18, 2026\n"
        b"Hemoglobin 14.2 g/dL 12.0 - 16.0 NORMAL\n"
        b"Fasting Glucose 118 mg/dL 70 - 99 HIGH\n"
        b"WBC Count 6800 cells/mcL 4500 - 11000 NORMAL\n"
        b"Total Cholesterol 225 mg/dL < 200 HIGH\n"
    )
    report_file = io.BytesIO(report_content)
    files = {"file": ("complete_metabolic_panel.pdf", report_file, "application/pdf")}
    data = {"title": "Metabolic & Blood Panel"}

    upload_res = client.post("/api/v1/reports/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 201
    upload_data = upload_res.json()

    # Verify Report Metadata returned to Frontend
    assert "report" in upload_data
    report = upload_data["report"]
    report_id = report["id"]
    assert report["name"] == "Metabolic & Blood Panel"
    assert report["status"] == "analyzed"
    assert report["findingsCount"] >= 1

    # Verify AI Analysis Payload
    assert "analysis" in upload_data
    analysis = upload_data["analysis"]
    assert analysis["reportId"] == str(report_id)
    assert len(analysis["findings"]) >= 1
    assert "summary" in analysis
    assert len(analysis["doctorQuestions"]) >= 1
    assert "disclaimer" in analysis

    # Test GET /reports for list view
    list_reports_res = client.get("/api/v1/reports", headers=headers)
    assert list_reports_res.status_code == 200
    reports_list = list_reports_res.json()
    assert len(reports_list) >= 1
    assert any(r["id"] == str(report_id) for r in reports_list)

    # Test GET /reports/{id}/analysis
    get_analysis_res = client.get(f"/api/v1/reports/{report_id}/analysis", headers=headers)
    assert get_analysis_res.status_code == 200
    assert get_analysis_res.json()["reportId"] == str(report_id)

    # -------------------------------------------------------------
    # 3. Health Vital Records & Metric Summaries (Recharts data)
    # -------------------------------------------------------------
    # Add Blood Pressure
    bp_res = client.post("/api/v1/health/records", json={
        "metricType": "blood_pressure",
        "value": 118.0,
        "unit": "mmHg",
        "notes": "Optimal resting BP",
    }, headers=headers)
    assert bp_res.status_code == 201
    bp_id = bp_res.json()["id"]

    # Fetch History via frontend route /health/records
    records_res = client.get("/api/v1/health/records?metricType=blood_pressure", headers=headers)
    assert records_res.status_code == 200
    assert len(records_res.json()) >= 1

    # Fetch Summary Statistics via frontend route /health/summary/blood_pressure
    summary_res = client.get("/api/v1/health/summary/blood_pressure", headers=headers)
    assert summary_res.status_code == 200
    assert summary_res.json()["currentValue"] == 118.0
    assert summary_res.json()["unit"] == "mmHg"

    # Delete measurement
    del_bp = client.delete(f"/api/v1/health/records/{bp_id}", headers=headers)
    assert del_bp.status_code == 200

    # -------------------------------------------------------------
    # 4. Care Reminders Flow
    # -------------------------------------------------------------
    rem_res = client.post("/api/v1/reminders", json={
        "title": "Evening Metformin Capsule",
        "description": "Take with dinner",
        "category": "medication-refill",
        "priority": "high",
    }, headers=headers)
    assert rem_res.status_code == 201
    rem_id = rem_res.json()["id"]

    # List
    rems_list = client.get("/api/v1/reminders", headers=headers)
    assert rems_list.status_code == 200
    assert len(rems_list.json()) >= 1

    # Toggle Complete
    toggle_res = client.patch(f"/api/v1/reminders/{rem_id}/complete", json={"completed": True}, headers=headers)
    assert toggle_res.status_code == 200
    assert toggle_res.json()["completed"] is True

    # Delete Reminder
    del_rem = client.delete(f"/api/v1/reminders/{rem_id}", headers=headers)
    assert del_rem.status_code == 200

    # -------------------------------------------------------------
    # 5. Doctor Appointment Booking Flow
    # -------------------------------------------------------------
    apt_res = client.post("/api/v1/appointments", json={
        "doctorName": "Dr. Sarah Chen, MD",
        "specialty": "Internal Medicine",
        "clinicOrHospital": "City Hospital Health Center",
        "notes": "Discuss elevated glucose findings",
    }, headers=headers)
    assert apt_res.status_code == 201
    apt_id = apt_res.json()["id"]

    # List Appointments
    apts_list = client.get("/api/v1/appointments", headers=headers)
    assert apts_list.status_code == 200
    assert any(a["id"] == str(apt_id) for a in apts_list.json())

    # Cancel Appointment
    cancel_res = client.patch(f"/api/v1/appointments/{apt_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # -------------------------------------------------------------
    # 6. Delete Medical Report
    # -------------------------------------------------------------
    del_report_res = client.delete(f"/api/v1/reports/{report_id}", headers=headers)
    assert del_report_res.status_code == 200
