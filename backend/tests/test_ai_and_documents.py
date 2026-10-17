import io


def test_symptom_check_endpoint(client):
    # Register and login
    client.post("/api/v1/auth/register", json={
        "email": "aipatient@example.com",
        "password": "Password123!",
        "full_name": "AI Test Patient",
        "role": "patient",
    })
    login_res = client.post("/api/v1/auth/login", json={
        "email": "aipatient@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test Symptom Check
    payload = {
        "query": "I have had a severe throbbing headache and mild fever for 2 days",
        "duration": "2 days",
        "age": 25,
    }
    response = client.post("/api/v1/ai/symptom-check", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "triage_level" in data
    assert "possible_conditions" in data
    assert "recommendations" in data
    assert "suggested_specialist" in data


def test_file_upload_validation_rejects_invalid_extension(client):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "aipatient@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try uploading a .exe or .sh file
    fake_file = io.BytesIO(b"echo 'malicious'")
    files = {"file": ("malicious.sh", fake_file, "text/plain")}
    data = {"title": "Test Exploit", "document_type": "prescription"}

    response = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["error"]


def test_file_upload_valid_document(client):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "aipatient@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload valid text/pdf mock
    pdf_content = b"%PDF-1.4 Mock PDF content with medical prescription Paracetamol 500mg twice daily."
    mock_pdf = io.BytesIO(pdf_content)
    files = {"file": ("prescription.pdf", mock_pdf, "application/pdf")}
    data = {"title": "My Doctor Prescription", "document_type": "prescription"}

    response = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["title"] == "My Doctor Prescription"
    assert res_data["document_type"] == "prescription"
    assert res_data["status"] == "processed"
