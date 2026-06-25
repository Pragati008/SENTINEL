from fastapi import FastAPI, UploadFile, File
from typing import Optional
import joblib
import shutil
import os
import uuid
from ocr_engine import correlate_documents

app = FastAPI()

pipeline = joblib.load("document_fraud_model_xgb.pkl")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_risk_tier(score: float) -> str:
    if score >= 75:
        return "low"
    elif score >= 50:
        return "medium"
    elif score >= 25:
        return "high"
    else:
        return "reject"

@app.post("/module3/analyze-uploaded-documents")
async def analyze_uploaded_documents(
    salary_slip: Optional[UploadFile] = File(None),
    itr: Optional[UploadFile] = File(None),
    bank_statement: Optional[UploadFile] = File(None),
    aadhaar: Optional[UploadFile] = File(None),
    pan: Optional[UploadFile] = File(None)
):
    try:
        session_id = str(uuid.uuid4())[:8]
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)

        # Save uploaded files
        doc_paths = {}
        for doc_type, upload in [
            ("salary_slip", salary_slip),
            ("itr", itr),
            ("bank_statement", bank_statement),
            ("aadhaar", aadhaar),
            ("pan", pan)
        ]:
            if upload:
                path = os.path.join(session_dir, f"{doc_type}.pdf")
                with open(path, "wb") as f:
                    shutil.copyfileobj(upload.file, f)
                doc_paths[doc_type] = path

        # Run OCR correlation
        ocr_result = correlate_documents(doc_paths)
        checks = ocr_result["consistency_checks"]

        # Build feature dict for ML model
        import pandas as pd
        features = {
            "annual_inc": 0,
            "emp_title": "Unknown",
            "verification_status": "Not Verified",
            "address": "Unknown",
            "application_type": "INDIVIDUAL",
            "dti": 0,
            "loan_amnt": 0,
            "installment": 0,
            "loan_status": "Current",
            "pan_match": checks.get("pan_match", 1),
            "aadhaar_name_match": checks.get("aadhaar_name_match", 1),
            "address_match": checks.get("address_match", 1),
            "employer_match": checks.get("employer_match", 1),
            "salary_itr_match": checks.get("salary_itr_match", 1),
            "bank_salary_match": checks.get("bank_salary_match", 1),
            "metadata_suspicious": checks.get("metadata_suspicious", 0),
            "edited_in_photoshop": checks.get("edited_in_photoshop", 0),
            "ocr_confidence": ocr_result.get("ocr_confidence", 85),
            "income_difference_pct": ocr_result.get("income_difference_pct")
        }

        df = pd.DataFrame([features])
        fraud_probability = float(pipeline.predict_proba(df)[:, 1][0])
        is_fraud = int(fraud_probability >= 0.5)
        consistency_score = round((1 - fraud_probability) * 100, 2)
        risk_tier = get_risk_tier(consistency_score)

        # Cleanup temp files
        shutil.rmtree(session_dir)

        return {
            "module": "document_fraud_correlation",
            "fraud_probability": round(fraud_probability, 3),
            "is_document_fraud": is_fraud,
            "document_correlation_score": float(consistency_score),
            "risk_tier": str(risk_tier),
            "total_flags": int(len(ocr_result["flags"])),
            "flags": [str(f) for f in ocr_result["flags"]],
            "extracted_entities": {
                doc: {
                    k: str(v) if v is not None else None
                    for k, v in ent.items()
                    if k != "raw_text_length"
                }
                for doc, ent in ocr_result["extracted_entities"].items()
            },
            "income_difference_pct": ocr_result.get("income_difference_pct")
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health_check():
    return {"status": "Module 3 OCR API is running"}