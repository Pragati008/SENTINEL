from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import pickle

app = FastAPI()

# Load model, imputer and encoders
with open("ghost_borrower_model.pkl", "rb") as f:
    model = pickle.load(f)

with open("ghost_borrower_imputer.pkl", "rb") as f:
    imputer = pickle.load(f)

with open("ghost_borrower_encoders.pkl", "rb") as f:
    encoders = pickle.load(f)

# Input schema
class BusinessProfile(BaseModel):
    business_type: str
    business_age_months: int
    loan_amount_requested: float
    loan_purpose: str
    stated_annual_turnover: float
    avg_monthly_bank_credit: float
    turnover_bank_ratio: float
    num_employees_stated: Optional[float] = None
    gst_returns_filed_last_12: int
    gst_filing_consistency: Optional[float] = None
    num_companies_director_linked: int
    any_linked_company_defaulted: int
    address_type: str
    num_businesses_at_same_address: int
    address_verified: int
    years_of_itr_filed: Optional[float] = None
    itr_turnover_match: int
    existing_loans: int
    loan_to_turnover_ratio: float
    application_hour: int

@app.post("/module2/ghost-borrower")
def detect_ghost_borrower(profile: BusinessProfile):
    try:
        # Convert input to dataframe
        input_dict = profile.dict()
        df = pd.DataFrame([input_dict])

        # Encode categorical columns
        df["business_type"] = encoders["business_type"].transform(df["business_type"])
        df["loan_purpose"] = encoders["loan_purpose"].transform(df["loan_purpose"])
        df["address_type"] = encoders["address_type"].transform(df["address_type"])

        # Impute missing values
        df_imputed = imputer.transform(df)
        df_imputed = pd.DataFrame(df_imputed, columns=df.columns)

        # Predict
        proba = model.predict_proba(df_imputed)[:, 1][0]
        is_ghost = int(proba >= 0.3)

        # Build flags for explainability
        flags = []
        if profile.business_age_months < 12 and profile.loan_amount_requested > 1000000:
            flags.append("Very young business requesting large loan")
        if profile.gst_returns_filed_last_12 < 6:
            flags.append("Irregular GST filing history")
        if profile.turnover_bank_ratio < 0.4 or profile.turnover_bank_ratio > 2.5:
            flags.append("Bank credits inconsistent with stated turnover")
        if profile.num_companies_director_linked > 5:
            flags.append("Director linked to many other companies")
        if profile.any_linked_company_defaulted == 1:
            flags.append("A linked company has prior loan default")
        if profile.address_type in ["residential", "virtual office"] and profile.num_businesses_at_same_address > 10:
            flags.append("Suspicious registered address")
        if profile.itr_turnover_match == 0 and (profile.years_of_itr_filed or 0) < 2:
            flags.append("ITR does not match stated turnover")
        if profile.loan_to_turnover_ratio > 0.8:
            flags.append("Loan amount too high relative to turnover")

        # Risk tier
        if proba >= 0.7:
            risk_tier = "high"
        elif proba >= 0.4:
            risk_tier = "medium"
        else:
            risk_tier = "low"

        return {
            "module": "ghost_borrower_detection",
            "ghost_probability": round(float(proba), 3),
            "is_ghost": is_ghost,
            "risk_tier": risk_tier,
            "flags": flags,
            "flag_count": len(flags)
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def health_check():
    return {"status": "Module 2 — Ghost Borrower Detection is running"}