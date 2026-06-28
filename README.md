# SENTINEL
### Real-time Layered Fraud Intelligence for Banking

SENTINEL is an AI-powered loan fraud detection platform designed for financial institutions to identify fraudulent applications before loan approval.

The platform combines Identity Verification, Document Intelligence, Business Fraud Detection, and Network Analysis into a unified fraud intelligence pipeline. Each module independently analyzes risk signals and feeds them into a centralized Trust Scoring Engine, which generates an explainable trust score (0–100) along with risk-tiered recommendations.

Instead of relying solely on manual verification, SENTINEL provides automated fraud assessment using machine learning, OCR, graph analytics, and rule-based intelligence.

---

## Table of Contents

1. System Architecture
2. Core Fraud Detection Modules
3. Trust Scoring Engine
4. Application Workflow & UI
5. Technology Stack
6. Vision
---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                     │
│                     app.py (:8501)                      │
└───────┬──────────────────────────┬──────────────────────┘
        │                          │
        │ multipart/form-data      │ JSON
        ▼                          ▼
┌───────────────┐        ┌──────────────────────┐
│   Module 1    │        │    Orchestrator       │
│  KYC Deepfake │        │   orchestrate.py      │
│   api.py      │        │      (:8005)          │
│   (:8003)     │        └──────┬─────────────┬──┘
│               │               │    |        │
│ EfficientNet  │        ┌──────┘    |        └──────┐
│     B3        │        ▼           ▼               ▼
└───────────────┘  ┌───────────┐ ┌────────────┐  ┌──────────┐
                   │ Module 2  │ │  Module 3  │  │ Module 4 │
                   │  Ghost    │ │Multimodule │  │  Fraud   │
                   │ Borrower  │ | Correlation|  │  Graph   │
                   │  (:8000)  │ |  (:8004)   |  │  (:8001) │
                   └─────┬─────┘ └────┬───────┘  └────┬─────┘
                         │            │               │
                         └────────────┬───────────────┘
                                      ▼
                             ┌─────────────────┐
                             │  Scoring Engine │
                             │    (:8002)      │
                             └─────────────────┘
```

Module 1 is called **directly from the frontend** (not through the orchestrator) because it accepts a binary video file upload (`multipart/form-data`) which cannot be forwarded as JSON. Its trust score is then injected into the orchestrator's JSON payload so the scoring engine receives all four module scores.

---

## Modules

### Module 1 — KYC Verification & Deepfake Detection
Validates applicant identity during onboarding and detects synthetic or manipulated media.

#### Features
Face matching between live capture and ID document
Deepfake detection using visual artifact analysis
Identity consistency verification
KYC risk scoring
#### Outputs
Deepfake confidence score
Identity verification result
Fraud indicators
Module trust score

---

### Module 2 — Ghost Borrower Detection
Detects potentially fake MSMEs and shell entities created to obtain fraudulent loans.

#### Features
GST filing behavior analysis
Director linkage evaluation
Address risk assessment
Turnover consistency validation
Business profile fraud prediction
#### Model
Random Forest Classifier
Trained on synthetic MSME profiles with engineered fraud indicators
#### Outputs
Fraud probability score
Ghost borrower risk level
Explainable fraud signals

---

### 3. Multi-Document OCR Correlation

Extracts and cross-validates information from submitted financial and identity documents.

#### Documents Supported
Aadhaar Card
PAN Card
Salary Slips
Income Tax Returns (ITR)
Bank Statements
#### Features
OCR-based text extraction
Cross-document entity matching
Income consistency checks
Address verification
Employer verification
Metadata tampering detection
#### Outputs
Extracted entities
Document mismatch flags
Fraud probability
Document trust score

---

### Module 4 — Fraud Graph Intelligence

Identifies hidden relationships between applications using shared entities.

#### Tracked Entities
Phone Numbers
PAN Numbers
Device IDs
Email IDs
Addresses
#### Features
Shared entity detection
Historical fraud linkage analysis
Fraud ring identification
Network risk assessment
#### Outputs
Linked applications
Shared entities
Fraud ring alerts
Graph risk score

---

## Scoring Engine

The Trust Scoring Engine combines outputs from all fraud modules into a unified decision framework.

#### Inputs
KYC Verification Score
OCR Correlation Score
Ghost Borrower Score
Fraud Graph Score

#### Functionality
Weighted score aggregation
Risk tier classification
Explainable fraud reporting
Recommendation generation

| Risk Tier | Score Range |
|---|---|
| LOW | 75–100 |
| MEDIUM | 50–74 |
| HIGH | 25–49 |
| REJECT | 0–24 |

Weights are configurable per loan type from the Settings page (Admin only).

---

## Application WorkFlow

```
Step 1 — Basic Details      Enter applicant name, PAN, phone, email, loan type & amount
        ↓
Step 2 — Document Upload    Salary slip, ITR, bank statement, Aadhaar, PAN card (+ GST for MSME)
        ↓
Step 3 — KYC Video          Upload applicant face video (MP4/MOV/AVI, max 50MB, min 10s)
        ↓
Step 4 — Run Analysis
        ├── Frontend → POST /analyze-video (port 8003)
        │       Video bytes uploaded directly as multipart/form-data
        │       ← prediction, confidence, trust_score, flagged_frames
        │
        ├── Frontend extracts deepfake fields → injects into orchestrator JSON payload
        │
        └── Frontend → POST /orchestrate/analyze (port 8005)
                Orchestrator → Module 2 Ghost Borrower (port 8000)  [MSME only]
                Orchestrator → Module 3 Multimodule Correlation (port 8004)
                Orchestrator → Module 4 Fraud Graph   (port 8001)
                Orchestrator → Scoring Engine          (port 8002)
                ← trust_score, risk_tier, module flags
        ↓
Application Detail Page     Full trust report with per-module scores, all flags, officer decision panel
```

If any module is offline, the frontend falls back to demo mode with simulated scores and displays a warning — it never crashes.

---

### UI

| Page | Route key | Description |
|---|---|---|
| Login | — | Role-based tabs (Loan Officer / Admin) with credential validation |
| Dashboard | `dashboard` | Summary stats, recent applications table, live fraud alerts |
| Applications | `applications` | Filterable list with approve / reject / view actions |
| Application Detail | `application_detail` | Full trust report, 4 module cards, all flags, officer decision |
| New Application | `new_application` | 4-step wizard: details → documents → KYC video → run analysis |
| Analytics | `analytics` | Charts: daily volume, risk distribution, flag frequency, trends |
| Settings | `settings` | Module config, scoring weights, user management (Admin), loan limits |

---

## Technology Stack
| Layer | Technologies |
|--------|-------------|
| Frontend | Streamlit |
| Backend APIs | FastAPI |
| Machine Learning | Scikit-learn, XGBoost |
| OCR & Document Processing | PyTesseract, PyMuPDF |
| Graph Analytics | NetworkX |
| Data Processing | Pandas, NumPy |
| Model Storage | Joblib |
| Development | Python |
| Version Control | Git, GitHub |

---

## Vision

SENTINEL aims to provide financial institutions with an intelligent fraud prevention platform capable of detecting identity fraud, synthetic applicants, document manipulation, ghost businesses, and organized fraud rings before loan disbursement.

By combining AI, OCR, graph analytics, and explainable risk scoring, SENTINEL enables faster underwriting decisions, reduced fraud losses, and greater confidence in digital lending workflows.
