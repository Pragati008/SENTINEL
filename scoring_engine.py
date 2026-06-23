from pydantic import BaseModel
from typing import Optional

# Weight configurations per loan type
WEIGHTS = {
    "personal": {
        "deepfake": 0.35,
        "document_correlation": 0.40,
        "ghost_borrower": 0.00,
        "fraud_graph": 0.25
    },
    "msme": {
        "deepfake": 0.20,
        "document_correlation": 0.25,
        "ghost_borrower": 0.30,
        "fraud_graph": 0.25
    }
}

# Risk tier thresholds
def get_risk_tier(score: float) -> str:
    if score >= 75:
        return "low"
    elif score >= 50:
        return "medium"
    elif score >= 25:
        return "high"
    else:
        return "reject"

def get_recommended_action(risk_tier: str) -> str:
    actions = {
        "low": "Proceed with loan approval",
        "medium": "Flag for manual review by senior officer",
        "high": "Reject — high fraud risk detected",
        "reject": "Immediate rejection — critical fraud signals"
    }
    return actions[risk_tier]

class ModuleScores(BaseModel):
    loan_type: str  # "personal" or "msme"
    application_id: str

    # Each module returns a score 0-100
    # 100 = completely clean, 0 = definitely fraud
    deepfake_score: Optional[float] = None
    document_correlation_score: Optional[float] = None
    ghost_borrower_score: Optional[float] = None
    fraud_graph_score: Optional[float] = None

    # Raw module outputs for the trust report
    deepfake_flags: Optional[list] = []
    document_flags: Optional[list] = []
    ghost_borrower_flags: Optional[list] = []
    fraud_graph_flags: Optional[list] = []
    fraud_ring_suspected: Optional[bool] = False

def calculate_trust_score(data: ModuleScores) -> dict:
    loan_type = data.loan_type.lower()

    if loan_type not in WEIGHTS:
        return {"error": f"Unknown loan type: {loan_type}. Use 'personal' or 'msme'"}

    weights = WEIGHTS[loan_type]

    # Collect available module scores
    module_results = {}

    if data.deepfake_score is not None:
        module_results["deepfake"] = data.deepfake_score

    if data.document_correlation_score is not None:
        module_results["document_correlation"] = data.document_correlation_score

    if data.ghost_borrower_score is not None and loan_type == "msme":
        module_results["ghost_borrower"] = data.ghost_borrower_score

    if data.fraud_graph_score is not None:
        module_results["fraud_graph"] = data.fraud_graph_score

    # Recalculate weights for only available modules
    # (in case some modules haven't been built yet)
    available_weight_total = sum(
        weights[module] for module in module_results
    )

    if available_weight_total == 0:
        return {"error": "No module scores provided"}

    # Weighted average
    weighted_sum = sum(
        module_results[module] * weights[module]
        for module in module_results
    )
    trust_score = round(weighted_sum / available_weight_total, 2)

    # Risk tier and recommendation
    risk_tier = get_risk_tier(trust_score)
    recommended_action = get_recommended_action(risk_tier)

    # Collect all flags across modules
    all_flags = []

    if data.deepfake_flags:
        all_flags.extend([f"[Identity] {f}" for f in data.deepfake_flags])

    if data.document_flags:
        all_flags.extend([f"[Document] {f}" for f in data.document_flags])

    if data.ghost_borrower_flags:
        all_flags.extend([f"[Business] {f}" for f in data.ghost_borrower_flags])

    if data.fraud_graph_flags:
        all_flags.extend([f"[Network] {f}" for f in data.fraud_graph_flags])

    if data.fraud_ring_suspected:
        all_flags.append("[Network] Fraud ring suspected — application linked to known fraud cluster")

    # Per module summary for trust report
    module_summary = {}

    if "deepfake" in module_results:
        module_summary["deepfake_detection"] = {
            "score": module_results["deepfake"],
            "weight_applied": f"{int(weights['deepfake'] * 100)}%",
            "flags": data.deepfake_flags or []
        }

    if "document_correlation" in module_results:
        module_summary["document_correlation"] = {
            "score": module_results["document_correlation"],
            "weight_applied": f"{int(weights['document_correlation'] * 100)}%",
            "flags": data.document_flags or []
        }

    if "ghost_borrower" in module_results:
        module_summary["ghost_borrower_detection"] = {
            "score": module_results["ghost_borrower"],
            "weight_applied": f"{int(weights['ghost_borrower'] * 100)}%",
            "flags": data.ghost_borrower_flags or []
        }

    if "fraud_graph" in module_results:
        module_summary["fraud_graph_intelligence"] = {
            "score": module_results["fraud_graph"],
            "weight_applied": f"{int(weights['fraud_graph'] * 100)}%",
            "flags": data.fraud_graph_flags or []
        }

    return {
        "application_id": data.application_id,
        "loan_type": loan_type,
        "trust_score": trust_score,
        "risk_tier": risk_tier,
        "recommended_action": recommended_action,
        "total_flags": len(all_flags),
        "all_flags": all_flags,
        "module_summary": module_summary,
        "fraud_ring_suspected": data.fraud_ring_suspected
    }


# Quick test
if __name__ == "__main__":

    # Test 1 — MSME loan, all modules present, high fraud
    print("=== Test 1: MSME high fraud application ===")
    result = calculate_trust_score(ModuleScores(
        application_id="APP004_NEW",
        loan_type="msme",
        deepfake_score=20,
        document_correlation_score=30,
        ghost_borrower_score=15,
        fraud_graph_score=0,
        deepfake_flags=["Face edge artifacts detected", "Unnatural blink rate"],
        document_flags=["Salary slip income does not match ITR", "Employer name mismatch"],
        ghost_borrower_flags=["Irregular GST filing", "Suspicious registered address"],
        fraud_graph_flags=["Linked to 2 previously flagged applications"],
        fraud_ring_suspected=True
    ))
    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n=== Test 2: Personal loan, clean application ===")
    result2 = calculate_trust_score(ModuleScores(
        application_id="APP010_CLEAN",
        loan_type="personal",
        deepfake_score=95,
        document_correlation_score=88,
        ghost_borrower_score=None,
        fraud_graph_score=92,
        deepfake_flags=[],
        document_flags=[],
        ghost_borrower_flags=[],
        fraud_graph_flags=[]
    ))
    for key, value in result2.items():
        print(f"{key}: {value}")

    print("\n=== Test 3: Personal loan, medium risk ===")
    result3 = calculate_trust_score(ModuleScores(
        application_id="APP011_MED",
        loan_type="personal",
        deepfake_score=60,
        document_correlation_score=55,
        fraud_graph_score=70,
        document_flags=["Address mismatch between Aadhaar and salary slip"]
    ))
    for key, value in result3.items():
        print(f"{key}: {value}")
from fastapi import FastAPI

app = FastAPI()

@app.post("/scoring/trust-score")
def get_trust_score(data: ModuleScores):
    return calculate_trust_score(data)

@app.get("/")
def health_check():
    return {"status": "Scoring Engine is running"}