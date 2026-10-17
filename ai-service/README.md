# HealthSense — AI/ML & Medical Report Processing Module

**Team Member 3**: AI/ML Engineer
**Project**: HealthSense — AI-Powered Healthcare & Well-Being Platform (ShiftForge Hackathon)

---

## 1. Module Overview & Responsibilities

This module is the dedicated AI/ML and medical document processing engine for **HealthSense**. It accepts laboratory reports and medical documents in **PDF**, **PNG**, and **JPEG** formats, extracts text and structured clinical findings, and produces cautious, plain-language, patient-friendly explanations with tailored consultation questions for a doctor.

### Key Capabilities
- **Digital PDF Processing**: High-speed vector text extraction with page numbering using PyMuPDF (`pymupdf`).
- **Scanned Document OCR**: Optical character recognition via Tesseract (`pytesseract`) with PIL preprocessing (grayscale conversion, auto-orientation, DPI normalization, contrast enhancement).
- **Hybrid Scanned/Digital PDF Handling**: Transparently detects scanned pages within multi-page PDFs and routes them to OCR while keeping digital pages fast.
- **Deterministic Clinical Findings Parser**: Parses test names, observed values, measurement units, reference ranges, and explicit flags (`HIGH`, `LOW`, `CRITICAL`, `NORMAL`, `*`) without hallucinations. Preserves exact verbatim snippets for full traceability.
- **Prompt Injection Defense & Medical Safety Guardrails**: Treats document content strictly as untrusted clinical data within `<medical_report_content>` tags. Explicitly prohibits autonomous diagnosis, prescription, or treatment adjustments.
- **Flexible LLM Provider Support**: Out-of-the-box support for OpenAI-compatible endpoints (OpenAI, Groq, Ollama, Azure, vLLM), Google Gemini, and a zero-dependency **deterministic Mock LLM** for offline testing and continuous integration without paid API keys.
- **Safe Fallback**: If external LLM APIs time out or fail, gracefully returns structured findings in an extraction-only format without breaking the pipeline.

---

## 2. Directory Structure

```
ai-service/
├── app/
│   ├── __init__.py                # Package exports (process_medical_report, schemas)
│   ├── config.py                  # Pydantic BaseSettings & auto-detection of Tesseract
│   ├── exceptions.py              # Domain-specific custom exceptions
│   ├── schemas.py                 # Pydantic v2 data models for input/output validation
│   ├── extraction/
│   │   ├── __init__.py
│   │   ├── image_ocr.py           # Image loader & Tesseract OCR engine
│   │   ├── pdf_extractor.py       # PyMuPDF digital & scanned hybrid PDF extractor
│   │   └── preprocessing.py       # PIL-based grayscale & contrast enhancement
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── findings_parser.py     # Regex & deterministic clinical findings parser
│   │   └── report_pipeline.py     # Sync & async orchestrators
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── client.py              # Mock, OpenAI, and Gemini clients with JSON recovery
│   │   └── prompts.py             # Safety guardrails & prompt-injection defense prompts
│   └── main.py                    # Standalone FastAPI service with Swagger UI
├── samples/                       # Pre-generated synthetic test documents
│   ├── sample_digital_report.pdf  # Multi-page digital CBC & Metabolic Panel
│   ├── sample_scan_report.png     # Synthetic scanned report image
│   └── sample_scanned_report.pdf  # Synthetic scanned PDF (rasterized)
├── tests/
│   ├── conftest.py                # Synthetic document generator fixtures
│   ├── test_api_endpoints.py      # FastAPI HTTP tests
│   ├── test_findings_parser.py    # Unit tests for deterministic findings extraction
│   ├── test_image_ocr.py          # Unit tests for OCR and image preprocessing
│   ├── test_pdf_extraction.py     # Unit tests for digital, multi-page, & scanned PDFs
│   ├── test_report_pipeline.py    # End-to-end sync, async, error, & safety tests
│   └── test_schemas.py            # Pydantic schema validation tests
├── generate_samples.py            # Utility script to generate synthetic test fixtures
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Pinned Python dependencies
├── .env.example                   # Environment configuration template
└── README.md                      # Comprehensive documentation
```

---

## 3. Integration Guide for Member 2 (Backend Lead)

Member 2 can integrate this module in either of two ways:

### Option A: Direct Python Import (Recommended — Zero Network Overhead)

The pipeline can be invoked in-process within Member 2's existing FastAPI backend without launching a separate service:

```python
from app import process_medical_report, process_medical_report_async

# Synchronous invocation
analysis = process_medical_report(
    file_bytes=uploaded_file_bytes,
    filename="patient_report.pdf",
    content_type="application/pdf",  # Optional
)

# Or asynchronous invocation (recommended inside FastAPI route handlers)
analysis = await process_medical_report_async(
    file_bytes=uploaded_file_bytes,
    filename="patient_report.pdf",
    content_type="application/pdf",
)

# Returns a validated Pydantic ReportAnalysis instance
print(analysis.status)              # "success"
print(analysis.extraction_method)   # "pdf_text" | "ocr_image" | "ocr_scanned_pdf" | "hybrid"
print(analysis.findings)            # List[ExtractedFinding]
print(analysis.summary)             # Plain-language explanation
print(analysis.doctor_questions)    # List[str] consultation questions
print(analysis.disclaimer)          # Clinical disclaimer string
```

### Option B: Standalone HTTP Microservice

Run `ai-service` as an independent FastAPI service on port `8001`:

#### 1. Start Service:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

#### 2. Endpoints:
- `GET /health`: Health check and system capabilities (Tesseract path, OCR readiness, LLM provider).
- `POST /api/v1/report-analysis`: Upload report file via `multipart/form-data`.
- `GET /docs`: Interactive Swagger UI documentation.

#### 3. Example Request (cURL):
```bash
curl -X POST "http://localhost:8001/api/v1/report-analysis" \
  -F "file=@samples/sample_digital_report.pdf"
```

---

## 4. Input & Output Contract

### Accepted File Formats
- **PDF** (`.pdf`) — Digital or scanned
- **PNG** (`.png`)
- **JPEG** (`.jpg`, `.jpeg`)
- **Max File Size**: 25 MB (configurable via `MAX_FILE_SIZE_MB`)

### Response JSON Schema (`ReportAnalysis`)

```json
{
  "status": "success",
  "document_type": "laboratory_report",
  "extraction_method": "pdf_text",
  "extracted_text": "--- Page 1 ---\nHEALTHSENSE DIAGNOSTIC LABORATORY\nHemoglobin 14.2 g/dL 12.0 - 16.0 NORMAL\n...",
  "findings": [
    {
      "test_name": "Hemoglobin",
      "value": "14.2",
      "unit": "g/dL",
      "reference_range": "12.0 - 16.0",
      "reported_flag": "NORMAL",
      "page_number": 1,
      "source_text": "Hemoglobin 14.2 g/dL 12.0 - 16.0 NORMAL"
    },
    {
      "test_name": "Fasting Glucose",
      "value": "114",
      "unit": "mg/dL",
      "reference_range": "70 - 99",
      "reported_flag": "HIGH",
      "page_number": 1,
      "source_text": "Fasting Glucose 114 mg/dL 70 - 99 HIGH"
    }
  ],
  "summary": "This medical report contains 22 identified test measurements. Key parameters include Hemoglobin, Fasting Glucose, HbA1c, Total Cholesterol. Please review all values directly with your healthcare provider.",
  "explanations": [
    {
      "term": "Hemoglobin",
      "explanation": "A protein in your red blood cells that carries oxygen from your lungs to the rest of your body."
    },
    {
      "term": "Fasting Glucose",
      "explanation": "Blood sugar measured after an overnight fast, commonly evaluated for diabetes screening."
    }
  ],
  "doctor_questions": [
    "What do these overall results mean in the context of my symptoms, medical history, and daily routine?",
    "The report notes flags for Fasting Glucose, HbA1c, Total Cholesterol. What might be contributing to these values?",
    "Are there any follow-up tests, dietary adjustments, or lifestyle factors we should review?"
  ],
  "limitations": [],
  "disclaimer": "Informational only; not a substitute for professional medical advice. Always consult a qualified healthcare professional.",
  "metadata": {
    "filename": "sample_digital_report.pdf",
    "page_count": 2,
    "report_date": "2024-10-15",
    "findings_count": 22,
    "processing_time_ms": 28.5,
    "llm_provider": "mock"
  }
}
```

---

## 5. Error Handling Specifications

All errors return structured responses with standard HTTP error codes:

| Exception | HTTP Status | Error Code | Description |
|-----------|-------------|------------|-------------|
| `InvalidFileTypeError` | `400 Bad Request` | `INVALID_FILE_TYPE` | Unsupported file extension or MIME type |
| `EmptyFileError` | `400 Bad Request` | `EMPTY_FILE` | Uploaded document contains 0 bytes |
| `CorruptedFileError` | `400 Bad Request` | `CORRUPTED_FILE` | Unreadable, damaged, or password-encrypted PDF/image |
| `InsufficientTextQualityError` | `422 Unprocessable` | `INSUFFICIENT_TEXT_QUALITY` | Extracted text is illegible or has < 20 characters |
| `FileSizeExceededError` | `413 Payload Too Large`| `FILE_SIZE_EXCEEDED` | File exceeds maximum limit (25 MB) |
| `OCRError` | `500 Server Error` | `OCR_FAILED` | Tesseract failed or is not installed |
| `LLMServiceError` | *Safe fallback* | `LLM_SERVICE_ERROR` | Pipeline falls back to partial extraction-only output |

### Error Response Payload Example
```json
{
  "status": "error",
  "error_code": "INVALID_FILE_TYPE",
  "message": "Invalid file type for 'report.docx'. Allowed formats: .pdf, .png, .jpg, .jpeg",
  "details": {
    "allowed": [".pdf", ".png", ".jpg", ".jpeg"],
    "filename": "report.docx"
  }
}
```

---

## 6. Security & Clinical Guardrails

1. **Prompt Injection Defense**: Document text is isolated inside `<medical_report_content>` tags. The system prompt instructs the model that all content in these tags is untrusted user input, forbidding execution of embedded commands or persona shifts.
2. **Decompression Bomb Protection**: PIL safe pixel ceiling (`Image.MAX_IMAGE_PIXELS = 50_000_000`) prevents denial-of-service via massive images.
3. **No Phantom Hallucinations**: Missing units, reference ranges, and flags remain `None`. The parser never populates missing data with assumed universal values.
4. **No Autonomous Diagnoses**: Prompts and explanations explicitly prohibit diagnosing conditions or recommending changes to medication or dosage.
5. **No Data Leakage in Logs**: Medical document contents and API keys are strictly excluded from standard application logs.
6. **Regulatory Compliance Note**: This prototype has not been certified under HIPAA or GDPR. Production deployment requires dedicated BAA agreements, zero-retention LLM endpoints, and encrypted storage.

---

## 7. Setup & Execution Instructions

### Prerequisites
- Python 3.11+ (Tested on Python 3.13)
- Tesseract OCR:
  - **macOS**: `brew install tesseract`
  - **Ubuntu / Debian**: `sudo apt-get install -y tesseract-ocr`

### Installation
```bash
# 1. Navigate to ai-service directory
cd ai-service

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (optional, defaults to mock mode)
cp .env.example .env
```

### Running Tests
All 41 tests run offline using synthetic reports and mock LLM calls:
```bash
pytest -v
```

### Running the Standalone API
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

---

## 8. Automated Test Results

The test suite contains **41 automated tests** covering all requirements:

```
tests/test_api_endpoints.py::test_health_check_endpoint PASSED           [  2%]
tests/test_api_endpoints.py::test_api_upload_valid_pdf PASSED            [  4%]
tests/test_api_endpoints.py::test_api_upload_invalid_extension PASSED    [  7%]
tests/test_api_endpoints.py::test_api_upload_empty_file PASSED           [  9%]
tests/test_api_endpoints.py::test_api_upload_corrupted_file PASSED       [ 12%]
tests/test_findings_parser.py::test_parse_finding_standard_columnar PASSED [ 14%]
tests/test_findings_parser.py::test_parse_finding_high_flag PASSED       [ 17%]
tests/test_findings_parser.py::test_parse_finding_less_than_reference_range PASSED [ 19%]
tests/test_findings_parser.py::test_parse_finding_pipe_delimited PASSED  [ 21%]
tests/test_findings_parser.py::test_parse_finding_without_unit_or_range PASSED [ 24%]
tests/test_findings_parser.py::test_ignore_header_and_metadata_lines PASSED [ 26%]
tests/test_findings_parser.py::test_extract_report_date PASSED           [ 29%]
tests/test_findings_parser.py::test_extract_findings_from_pages PASSED   [ 31%]
tests/test_image_ocr.py::test_sanitize_extracted_text PASSED             [ 34%]
tests/test_image_ocr.py::test_preprocess_image_returns_grayscale PASSED  [ 36%]
tests/test_image_ocr.py::test_extract_text_from_valid_png_image PASSED   [ 39%]
tests/test_image_ocr.py::test_extract_text_from_valid_jpeg_image PASSED  [ 41%]
tests/test_image_ocr.py::test_empty_image_bytes_raises_empty_error PASSED [ 43%]
tests/test_image_ocr.py::test_corrupted_image_bytes_raises_corrupted_error PASSED [ 46%]
tests/test_pdf_extraction.py::test_digital_pdf_extraction_single_page PASSED [ 48%]
tests/test_pdf_extraction.py::test_digital_pdf_extraction_multipage PASSED [ 51%]
tests/test_pdf_extraction.py::test_empty_pdf_bytes_raises_empty_error PASSED [ 53%]
tests/test_pdf_extraction.py::test_corrupted_pdf_raises_corrupted_error PASSED [ 56%]
tests/test_pdf_extraction.py::test_partially_corrupted_pdf_header PASSED [ 58%]
tests/test_pdf_extraction.py::test_scanned_pdf_ocr_fallback PASSED       [ 60%]
tests/test_report_pipeline.py::test_process_medical_report_success_sync PASSED [ 63%]
tests/test_report_pipeline.py::test_process_medical_report_success_async PASSED [ 65%]
tests/test_report_pipeline.py::test_process_image_report_sync PASSED     [ 68%]
tests/test_report_pipeline.py::test_invalid_file_extension PASSED        [ 70%]
tests/test_report_pipeline.py::test_file_size_exceeded PASSED            [ 73%]
tests/test_report_pipeline.py::test_empty_file_rejected PASSED           [ 75%]
tests/test_report_pipeline.py::test_corrupted_file_rejected PASSED       [ 78%]
tests/test_report_pipeline.py::test_insufficient_text_quality PASSED     [ 80%]
tests/test_report_pipeline.py::test_llm_failure_safe_fallback PASSED     [ 82%]
tests/test_report_pipeline.py::test_extract_json_from_llm_response_markdown PASSED [ 85%]
tests/test_report_pipeline.py::test_prompt_injection_safety PASSED       [ 87%]
tests/test_schemas.py::test_extracted_finding_valid_complete PASSED      [ 90%]
tests/test_schemas.py::test_extracted_finding_nullable_fields PASSED     [ 92%]
tests/test_schemas.py::test_extracted_finding_requires_mandatory_fields PASSED [ 95%]
tests/test_schemas.py::test_report_analysis_schema_complete PASSED       [ 97%]
tests/test_schemas.py::test_error_response_schema PASSED                 [100%]

======================== 41 passed in 1.67s ========================
```

---

## 9. Known Limitations & Hackathon Roadmap

1. **Complex Multi-Column Clinical Tables**: Highly irregular, non-standard tabular layouts without clear delimiter spaces may occasionally be extracted as unstructured text blocks rather than individual key-value pairs.
2. **Handwritten Clinical Notes**: Tesseract OCR specializes in printed and typed text; physician cursive handwriting may produce degraded OCR quality and trigger `InsufficientTextQualityError`.
3. **Multi-lingual Documents**: Standard installation includes English (`eng`) language packs; foreign language reports require additional Tesseract language data (`tesseract-lang`).
4. **Planned Post-Hackathon Enhancements**:
   - Integration of LayoutLMv3 or paddleOCR for complex table boundary detection.
   - Integration with vector database (ChromaDB) for historical lab trend comparisons across multiple patient visits.
