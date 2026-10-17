import json
import logging
from typing import Dict, Any, List
import google.generativeai as genai
from app.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini if key is provided
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL

    def _get_model(self):
        if not self.api_key:
            return None
        return genai.GenerativeModel(self.model_name)

    def symptom_triage(
        self,
        query: str,
        duration: str = None,
        age: int = None,
        gender: str = None,
        existing_conditions: str = None,
    ) -> Dict[str, Any]:
        """Performs AI-assisted medical symptom triage and guidance."""
        model = self._get_model()

        prompt = f"""
You are an expert AI clinical triage assistant for a healthcare platform.
Analyze the following patient symptom report carefully:
- Symptoms / Complaint: {query}
- Duration: {duration or 'Not specified'}
- Patient Age: {age or 'Not specified'}
- Gender: {gender or 'Not specified'}
- Pre-existing Conditions: {existing_conditions or 'None reported'}

Your goals:
1. Determine triage level: choose strictly one of ["low", "moderate", "high", "emergency"].
   - "emergency": Chest pain, sudden numbness/paralysis, severe breathing difficulty, massive bleeding, loss of consciousness.
   - "high": High fever > 103F, severe persistent abdominal pain, deep cuts, vomiting blood.
   - "moderate": Persistent cough for > 1 week, moderate fever, rash with discomfort, ear infection.
   - "low": Mild cold, minor scratch, mild tension headache, fatigue without fever.
2. List 2-4 possible benign or clinical conditions (as possibilities to discuss with a doctor).
3. Provide actionable recommendations (first-aid, comfort measures, hydration, what red flags to monitor).
4. Recommend the most appropriate medical specialist (e.g. "Cardiologist", "General Physician", "Dermatologist", "Pediatrician").
5. Provide a short urgency message for the patient.

RESPOND ONLY IN VALID RAW JSON with no markdown wrapping, with these exact keys:
{{
  "triage_level": "low" | "moderate" | "high" | "emergency",
  "possible_conditions": ["Condition 1", "Condition 2"],
  "recommendations": "Detailed advice...",
  "suggested_specialist": "Specialist Name",
  "urgency_message": "Clear timeframe when patient should see a doctor."
}}
"""
        if model:
            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                # Clean markdown backticks if any
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                data = json.loads(raw_text.strip())
                return self._format_triage_result(data)
            except Exception as e:
                logger.warning(f"Gemini API call failed, falling back to heuristic triage: {e}")

        # Intelligent Fallback Engine (guarantees hackathon demo works even if API key is not configured)
        return self._heuristic_triage(query)

    def _format_triage_result(self, data: dict) -> dict:
        level = data.get("triage_level", "moderate").lower()
        colors = {
            "low": "green",
            "moderate": "yellow",
            "high": "orange",
            "emergency": "red",
        }
        return {
            "triage_level": level,
            "triage_color": colors.get(level, "yellow"),
            "possible_conditions": data.get("possible_conditions", ["Clinical evaluation required"]),
            "recommendations": data.get("recommendations", "Consult with a certified physician for accurate diagnosis."),
            "suggested_specialist": data.get("suggested_specialist", "General Physician"),
            "urgency_message": data.get("urgency_message", "Please seek medical guidance at your earliest convenience."),
        }

    def _heuristic_triage(self, query: str) -> dict:
        q = query.lower()
        if any(w in q for w in ["chest pain", "heart attack", "unconscious", "cannot breathe", "stroke", "paralysis"]):
            level = "emergency"
            color = "red"
            conditions = ["Acute Coronary Syndrome / Cardiac Event", "Severe Respiratory Distress"]
            specialist = "Emergency Medicine / Cardiologist"
            urgency = "IMMEDIATE: Please call emergency ambulance (112 / 911) or visit the nearest ER immediately!"
            advice = "Do not drive yourself. Sit upright, stay calm, and seek immediate emergency care."
        elif any(w in q for w in ["high fever", "vomiting blood", "severe pain", "fracture", "broken"]):
            level = "high"
            color = "orange"
            conditions = ["Acute Infection / High Grade Pyrexia", "Trauma / Acute Abdomen"]
            specialist = "Internal Medicine / Urgent Care"
            urgency = "Seek medical care within the next 2 to 6 hours."
            advice = "Rest, stay hydrated with electrolyte solution, and arrange transport to a clinic."
        elif any(w in q for w in ["fever", "cough", "throat", "headache", "stomach", "pain"]):
            level = "moderate"
            color = "yellow"
            conditions = ["Viral Upper Respiratory Infection", "Tension Headache / Gastritis"]
            specialist = "General Physician"
            urgency = "Book an appointment with a doctor within 24 to 48 hours if symptoms persist."
            advice = "Hydrate well, rest, monitor body temperature, and avoid self-medicating with antibiotics."
        else:
            level = "low"
            color = "green"
            conditions = ["Minor Malaise / Fatigue", "Mild Allergic or Muscular Strain"]
            specialist = "General Physician"
            urgency = "Monitor symptoms over the next 2-3 days; consult a doctor if condition worsens."
            advice = "Adequate sleep, balanced nutrition, and mild hydration."

        return {
            "triage_level": level,
            "triage_color": color,
            "possible_conditions": conditions,
            "recommendations": advice,
            "suggested_specialist": specialist,
            "urgency_message": urgency,
        }

    def analyze_medical_document(self, text_content: str, doc_type: str = "prescription") -> dict:
        """Analyzes extracted text from prescriptions or lab reports."""
        model = self._get_model()

        prompt = f"""
You are an expert medical AI assistant. Analyze this {doc_type} text:
\"\"\"{text_content[:4000]}\"\"\"

Provide:
1. A concise plain-language summary of what the document contains.
2. Key findings, medicines prescribed (with dosage/frequency if mentioned), or abnormal lab values.
3. Recommended patient next steps / questions to ask their doctor.

RESPOND ONLY IN VALID RAW JSON with no markdown wrapping, with these exact keys:
{{
  "summary": "Plain language summary",
  "key_findings": ["Item 1", "Item 2"],
  "suggested_actions": ["Action 1", "Action 2"]
}}
"""
        if model:
            try:
                response = model.generate_content(prompt)
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                return json.loads(raw_text.strip())
            except Exception as e:
                logger.warning(f"Gemini API call failed for document: {e}")

        # Fallback summary
        lines = [line.strip() for line in text_content.splitlines() if line.strip()]
        preview_findings = lines[:5] if lines else ["Document uploaded successfully."]
        return {
            "summary": f"Uploaded {doc_type} processed. Extracted {len(text_content)} characters.",
            "key_findings": preview_findings,
            "suggested_actions": [
                "Review findings with your attending healthcare provider.",
                "Store this document in your digital health records.",
            ],
        }


ai_service = AIService()
