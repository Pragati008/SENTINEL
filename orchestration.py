"""
SENTINEL Orchestrator  —  runs on port 8005
Coordinates: Module 2 (Ghost Borrower) + Module 4 (Fraud Graph) + Scoring Engine.

Module 1 (KYC Deepfake) is called DIRECTLY from the Streamlit frontend because it
requires multipart/form-data (binary video upload) which cannot be forwarded as JSON.
Its result is attached to the API response as  "kyc_result"  by the frontend,
and the frontend also passes  deepfake_score / deepfake_flags  here via the payload
so the scoring engine can incorporate KYC into the final trust score.
"""

from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import httpx
import asyncio

app = FastAPI(title="SENTINEL Orchestrator", version="2.0")

# ==========================================
# MODULE ENDPOINTS
# ==========================================

MODULE2_URL      = "http://127.0.0.1:8000/module2/ghost-borrower"
MODULE4_ADD_URL  = "http://127.0.0.1:8001/module4/add-application"
MODULE4_ANALYZE_URL = "http://127.0.0.1:8001/module4/analyze"
SCORING_URL      = "http://127.0.0.1:8002/scoring/trust-score"

# ==========================================
# INPUT SCHEMA
# ==========================================

class ApplicationInput(BaseModel):
    application_id: str
    loan_type: str          # "personal" or "msme"
    loan_amount: float

    # ── Module 1 result forwarded from frontend ──
    # Frontend calls /analyze-video directly, then passes the parsed fields here
    deepfake_score: Optional[float] = None          # 0-100 trust score from inference.py
    deepfake_confidence: Optional[float] = None     # raw deepfake probability %
    deepfake_prediction: Optional[str] = None       # "REAL" | "SUSPICIOUS" | "DEEPFAKE"
    deepfake_flags: Optional[List[str]] = []

    # ── Module 2 — Ghost Borrower (MSME only) ──
    business_type: Optional[str] = None
    business_age_months: Optional[int] = None
    loan_purpose: Optional[str] = None
    stated_annual_turnover: Optional[float] = None
    avg_monthly_bank_credit: Optional[float] = None
    turnover_bank_ratio: Optional[float] = None
    num_employees_stated: Optional[float] = None
    gst_returns_filed_last_12: Optional[int] = None
    gst_filing_consistency: Optional[float] = None
    num_companies_director_linked: Optional[int] = None
    any_linked_company_defaulted: Optional[int] = None
    address_type: Optional[str] = None
    num_businesses_at_same_address: Optional[int] = None
    address_verified: Optional[int] = None
    years_of_itr_filed: Optional[float] = None
    itr_turnover_match: Optional[int] = None
    existing_loans: Optional[int] = None
    loan_to_turnover_ratio: Optional[float] = None
    application_hour: Optional[int] = None

    # ── Module 4 — Fraud Graph ──
    phone: Optional[str] = None
    email: Optional[str] = None
    device_id: Optional[str] = None
    address: Optional[str] = None
    pan: Optional[str] = None
    is_flagged: Optional[bool] = False


# ==========================================
# ORCHESTRATOR ENDPOINT
# ==========================================

@app.post("/orchestrate/analyze")
async def orchestrate(data: ApplicationInput):
    results = {}
    errors  = {}

    async with httpx.AsyncClient(timeout=30) as client:

        # ── MODULE 2: Ghost Borrower (MSME only) ──
        module2_result = None
        if data.loan_type.lower() == "msme" and data.business_type is not None:
            try:
                m2_payload = {
                    "business_type":                data.business_type,
                    "business_age_months":          data.business_age_months,
                    "loan_amount_requested":        data.loan_amount,
                    "loan_purpose":                 data.loan_purpose or "working capital",
                    "stated_annual_turnover":       data.stated_annual_turnover,
                    "avg_monthly_bank_credit":      data.avg_monthly_bank_credit,
                    "turnover_bank_ratio":          data.turnover_bank_ratio,
                    "num_employees_stated":         data.num_employees_stated,
                    "gst_returns_filed_last_12":    data.gst_returns_filed_last_12,
                    "gst_filing_consistency":       data.gst_filing_consistency,
                    "num_companies_director_linked":data.num_companies_director_linked,
                    "any_linked_company_defaulted": data.any_linked_company_defaulted,
                    "address_type":                 data.address_type,
                    "num_businesses_at_same_address":data.num_businesses_at_same_address,
                    "address_verified":             data.address_verified,
                    "years_of_itr_filed":           data.years_of_itr_filed,
                    "itr_turnover_match":           data.itr_turnover_match,
                    "existing_loans":               data.existing_loans,
                    "loan_to_turnover_ratio":       data.loan_to_turnover_ratio,
                    "application_hour":             data.application_hour or 10,
                }
                r2 = await client.post(MODULE2_URL, json=m2_payload)
                module2_result = r2.json()
                results["module2"] = module2_result
            except Exception as e:
                errors["module2"] = str(e)
        else:
            results["module2"] = {"skipped": True, "reason": "Not applicable for personal loans"}

        # ── MODULE 4: Fraud Graph ──
        module4_result = None
        try:
            m4_add_payload = {
                "application_id": data.application_id,
                "is_flagged":     data.is_flagged,
                "phone":          data.phone,
                "email":          data.email,
                "device_id":      data.device_id,
                "address":        data.address,
                "pan":            data.pan,
            }
            await client.post(MODULE4_ADD_URL, json=m4_add_payload)

            r4 = await client.post(f"{MODULE4_ANALYZE_URL}/{data.application_id}")
            module4_result = r4.json()
            results["module4"] = module4_result
        except Exception as e:
            errors["module4"] = str(e)

    # ── Build scoring payload ──
    ghost_score = None
    ghost_flags = []
    if module2_result and not module2_result.get("skipped"):
        ghost_prob  = module2_result.get("ghost_probability", 0)
        ghost_score = round((1 - ghost_prob) * 100, 2)
        ghost_flags = module2_result.get("flags", [])

    graph_score = None
    graph_flags = []
    fraud_ring  = False
    if module4_result:
        graph_risk  = module4_result.get("graph_risk_score", 0)
        graph_score = round(100 - graph_risk, 2)
        raw_conns   = module4_result.get("flagged_connections", [])
        graph_flags = [
            f"Linked to flagged application {c['application_id']} via {c['shared_via']}"
            for c in raw_conns
        ]
        fraud_ring  = module4_result.get("fraud_ring_suspected", False)

    # ── Module 1 fields forwarded from frontend ──
    deepfake_score = data.deepfake_score        # already 0-100 trust score
    deepfake_flags = data.deepfake_flags or []

    # Build informative flag string if the prediction is bad
    if data.deepfake_prediction and data.deepfake_prediction != "REAL":
        conf_str = f" ({data.deepfake_confidence:.1f}% confidence)" if data.deepfake_confidence else ""
        deepfake_flags = [f"KYC prediction: {data.deepfake_prediction}{conf_str}"] + deepfake_flags

    # ── Scoring engine ──
    scoring_result = None
    try:
        scoring_payload = {
            "application_id":           data.application_id,
            "loan_type":                data.loan_type.lower(),
            "deepfake_score":           deepfake_score,
            "document_correlation_score": None,         # not yet integrated
            "ghost_borrower_score":     ghost_score,
            "fraud_graph_score":        graph_score,
            "deepfake_flags":           deepfake_flags,
            "document_flags":           [],
            "ghost_borrower_flags":     ghost_flags,
            "fraud_graph_flags":        graph_flags,
            "fraud_ring_suspected":     fraud_ring,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            rs = await client.post(SCORING_URL, json=scoring_payload)
            scoring_result = rs.json()
    except Exception as e:
        errors["scoring"] = str(e)

    return {
        "application_id":   data.application_id,
        "loan_type":        data.loan_type,
        "module_results":   results,
        "trust_report":     scoring_result,
        "errors":           errors if errors else None,
    }


@app.get("/")
def health_check():
    return {
        "status": "SENTINEL Orchestrator v2 running",
        "modules": {
            "module1_kyc":         "Called directly by frontend (binary upload)",
            "module2_ghost":       MODULE2_URL,
            "module4_fraud_graph": MODULE4_ANALYZE_URL,
            "scoring_engine":      SCORING_URL,
        }
    }