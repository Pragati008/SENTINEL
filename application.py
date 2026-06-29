import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time
import requests

st.set_page_config(
    page_title="SENTINEL — Real-time layered fraud intelligence for banking",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# GLOBAL STYLING
# ==========================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0F1117; }

    section[data-testid="stMain"] { background-color: #0F1117; }

    section[data-testid="stSidebar"] {
        background-color: #1A1D27;
        border-right: 1px solid #2A2D3E;
    }
    section[data-testid="stSidebar"] * { color: #D1D5DB; }

    /* Sidebar */
    .sidebar-logo {
        padding: 20px 0 24px 0;
        text-align: center;
        border-bottom: 1px solid #2A2D3E;
        margin-bottom: 20px;
    }
    .sidebar-logo .brand {
        font-size: 18px; font-weight: 700;
        color: #FFFFFF; letter-spacing: 3px;
    }
    .sidebar-logo .tagline {
        font-size: 10px; color: #4B5563;
        letter-spacing: 1px; margin-top: 3px;
    }
    .sidebar-user {
        padding: 12px 16px; background: #0F1117;
        border-radius: 8px; margin-bottom: 24px;
    }
    .sidebar-user .name { font-size: 13px; font-weight: 600; color: #FFFFFF; }
    .sidebar-user .role { font-size: 11px; color: #6B7280; margin-top: 2px; }

    /* Login — single unified card */
    .login-card {
        width: 420px;
        background: #1A1D27;
        border-radius: 16px;
        border: 1px solid #2A2D3E;
        padding: 40px;
        margin: 80px auto 0 auto;
    }
    .sentinel-logo { text-align: center; margin-bottom: 24px; }
    .sentinel-logo .shield { font-size: 40px; display: block; margin-bottom: 8px; }
    .sentinel-logo .brand { font-size: 24px; font-weight: 700; color: #FFFFFF; letter-spacing: 3px; }
    .sentinel-logo .tagline { font-size: 12px; color: #6B7280; letter-spacing: 1px; margin-top: 4px; }
    .divider { border: none; border-top: 1px solid #2A2D3E; margin: 0 0 20px 0; }

    /* Strip Streamlit's own form container entirely so it merges with the card */
    [data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }
    .error-box {
        background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3);
        border-radius: 8px; padding: 12px 16px; color: #FCA5A5; font-size: 13px; margin-top: 12px;
    }
    .footer-note { text-align: center; color: #4B5563; font-size: 12px; margin-top: 24px; }

    /* Page titles */
    .page-title { font-size: 22px; font-weight: 700; color: #FFFFFF; margin-bottom: 4px; }
    .page-subtitle { font-size: 13px; color: #6B7280; margin-bottom: 28px; }

    /* Cards */
    .card {
        background: #1A1D27; border: 1px solid #2A2D3E;
        border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
    }
    .card-title {
        font-size: 13px; font-weight: 600; color: #9CA3AF;
        text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 16px;
        padding-bottom: 10px; border-bottom: 1px solid #2A2D3E;
    }

    /* Stat cards */
    .stat-card {
        background: #1A1D27; border: 1px solid #2A2D3E;
        border-radius: 12px; padding: 20px 24px; height: 100%;
    }
    .stat-card .label {
        font-size: 12px; color: #6B7280; font-weight: 500;
        letter-spacing: 0.5px; text-transform: uppercase;
    }
    .stat-card .value {
        font-size: 32px; font-weight: 700; color: #FFFFFF;
        margin: 6px 0 4px; line-height: 1;
    }
    .stat-card .delta { font-size: 12px; color: #6B7280; }
    .stat-card .delta.up { color: #34D399; }
    .stat-card .delta.down { color: #F87171; }

    /* Section headers */
    .section-header {
        font-size: 15px; font-weight: 600; color: #FFFFFF;
        margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid #2A2D3E;
    }

    /* Badges */
    .badge { display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.3px; }
    .badge-low { background: rgba(52,211,153,0.15); color: #34D399; }
    .badge-medium { background: rgba(251,191,36,0.15); color: #FBB824; }
    .badge-high { background: rgba(248,113,113,0.15); color: #F87171; }
    .badge-reject { background: rgba(239,68,68,0.2); color: #EF4444; }

    /* Alert cards */
    .alert-card {
        background: rgba(239,68,68,0.05); border: 1px solid rgba(239,68,68,0.2);
        border-radius: 10px; padding: 14px 16px; margin-bottom: 10px;
    }
    .alert-card .alert-title { font-size: 13px; font-weight: 600; color: #F87171; margin-bottom: 4px; }
    .alert-card .alert-body { font-size: 12px; color: #9CA3AF; line-height: 1.5; }

    /* Module cards */
    .module-card {
        background: #0F1117; border: 1px solid #2A2D3E;
        border-radius: 10px; padding: 16px; height: 100%;
    }
    .module-title { font-size: 12px; font-weight: 600; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 10px; }
    .module-score { font-size: 28px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
    .module-label { font-size: 11px; color: #6B7280; margin-bottom: 12px; }
    .module-flag { font-size: 11px; color: #F87171; padding: 3px 0; border-bottom: 1px solid #1E2130; margin-bottom: 4px; }

    /* Flag items */
    .flag-item { padding: 8px 12px; border-radius: 6px; margin-bottom: 6px; font-size: 12px; line-height: 1.5; }
    .flag-identity { background: rgba(139,92,246,0.1); color: #A78BFA; border-left: 3px solid #8B5CF6; }
    .flag-document { background: rgba(251,191,36,0.1); color: #FBB824; border-left: 3px solid #FBB824; }
    .flag-business { background: rgba(248,113,113,0.1); color: #F87171; border-left: 3px solid #F87171; }
    .flag-network { background: rgba(239,68,68,0.15); color: #EF4444; border-left: 3px solid #EF4444; }

    /* Info rows */
    .info-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #1E2130; font-size: 13px; }
    .info-label { color: #6B7280; }
    .info-value { color: #FFFFFF; font-weight: 500; }

    /* Trust score */
    .trust-score-big { font-size: 64px; font-weight: 700; line-height: 1; margin-bottom: 4px; }
    .trust-label { font-size: 12px; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; }
    .risk-tier-badge { display: inline-block; padding: 6px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-top: 10px; letter-spacing: 0.5px; }

    /* Summary bar */
    .summary-bar {
        background: #1A1D27; border: 1px solid #2A2D3E;
        border-radius: 10px; padding: 12px 20px; margin-bottom: 16px;
        display: flex; gap: 32px;
    }
    .summary-item .s-label { font-size: 11px; color: #6B7280; text-transform: uppercase; letter-spacing: 0.5px; }
    .summary-item .s-value { font-size: 18px; font-weight: 700; color: #FFFFFF; }

    /* Step bar */
    .step-bar { display: flex; align-items: center; margin-bottom: 28px; gap: 0; }
    .step { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 500; }
    .step-circle { width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 700; }
    .step-active .step-circle { background: #3B82F6; color: white; }
    .step-done .step-circle { background: #34D399; color: white; }
    .step-inactive .step-circle { background: #2A2D3E; color: #6B7280; }
    .step-active .step-label { color: #3B82F6; }
    .step-done .step-label { color: #34D399; }
    .step-inactive .step-label { color: #4B5563; }
    .step-line { flex: 1; height: 1px; background: #2A2D3E; margin: 0 8px; }
    .step-line-done { background: #34D399; }

    /* Upload status */
    .upload-status-ok { font-size: 12px; color: #34D399; padding: 6px 10px; background: rgba(52,211,153,0.1); border-radius: 6px; margin-top: 4px; }
    .required-badge { font-size: 10px; color: #F87171; background: rgba(248,113,113,0.1); padding: 2px 6px; border-radius: 4px; margin-left: 6px; }

    /* Analytics */
    .flag-bar-item { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #1E2130; }
    .flag-bar-label { font-size: 12px; color: #9CA3AF; width: 260px; flex-shrink: 0; }
    .flag-bar-track { flex: 1; height: 6px; background: #2A2D3E; border-radius: 3px; overflow: hidden; }
    .flag-bar-fill { height: 100%; border-radius: 3px; }
    .flag-bar-count { font-size: 12px; color: #6B7280; width: 30px; text-align: right; }

    /* Settings */
    .user-row { display: flex; align-items: center; gap: 14px; padding: 12px 16px; background: #0F1117; border-radius: 8px; border: 1px solid #2A2D3E; margin-bottom: 8px; }
    .user-avatar { width: 36px; height: 36px; background: #2A2D3E; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; }
    .user-name { font-size: 13px; color: #FFFFFF; font-weight: 500; }
    .user-role { font-size: 11px; color: #6B7280; margin-top: 2px; }
    .user-status-active { font-size: 11px; color: #34D399; background: rgba(52,211,153,0.1); padding: 2px 8px; border-radius: 10px; margin-left: auto; }
    .user-status-inactive { font-size: 11px; color: #6B7280; background: #2A2D3E; padding: 2px 8px; border-radius: 10px; margin-left: auto; }
    .info-banner { background: rgba(59,130,246,0.08); border: 1px solid rgba(59,130,246,0.2); border-radius: 8px; padding: 12px 16px; font-size: 12px; color: #93C5FD; margin-bottom: 20px; }
    .warning-banner { background: rgba(251,191,36,0.08); border: 1px solid rgba(251,191,36,0.2); border-radius: 8px; padding: 12px 16px; font-size: 12px; color: #FBB824; margin-bottom: 20px; }

    /* Inputs */
    .stTextInput > div > div > input {
        background-color: #0F1117 !important; border: 1px solid #2A2D3E !important;
        border-radius: 8px !important; color: #FFFFFF !important;
        padding: 12px 16px !important; font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important; }
    .stTextInput label { color: #9CA3AF !important; font-size: 13px !important; font-weight: 500 !important; }
    .stSelectbox > div > div { background-color: #0F1117 !important; border: 1px solid #2A2D3E !important; border-radius: 8px !important; color: #FFFFFF !important; }
    .stSelectbox label { color: #9CA3AF !important; font-size: 13px !important; font-weight: 500 !important; }
    .stNumberInput > div > div > input { background-color: #0F1117 !important; border: 1px solid #2A2D3E !important; color: #FFFFFF !important; border-radius: 8px !important; }
    .stNumberInput label { color: #9CA3AF !important; font-size: 12px !important; }
    .stTextArea textarea { background-color: #0F1117 !important; border: 1px solid #2A2D3E !important; color: #FFFFFF !important; border-radius: 8px !important; font-size: 13px !important; }
    .stTextArea label { color: #9CA3AF !important; font-size: 12px !important; }
    .stFileUploader > div { background-color: #0F1117 !important; border: 1px dashed #2A2D3E !important; border-radius: 8px !important; }
    .stSlider label { color: #9CA3AF !important; font-size: 12px !important; }
    .stToggle label { color: #9CA3AF !important; font-size: 13px !important; }

    /* Buttons — primary */
    div[data-testid="stButton"] > button {
        border-radius: 8px !important; font-size: 13px !important;
        font-weight: 500 !important; border: none !important;
        background: #3B82F6 !important; color: white !important;
    }
    div[data-testid="stButton"] > button:hover { background: #2563EB !important; }

    /* Secondary buttons — inactive login tab */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #1E2130 !important;
        color: #6B7280 !important;
        border: 1px solid #2A2D3E !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: #2A2D3E !important;
        color: #D1D5DB !important;
    }

    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }

    /* Fix 2: hide ALL sidebar collapse/expand controls so sidebar stays pinned open.
       Covers: << arrow inside sidebar, > arrow when collapsed, any collapse button variant. */
    button[data-testid="collapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarCollapseButton"] button {
        display: none !important;
        visibility: hidden !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }
    /* Pin sidebar always open at fixed width */
    section[data-testid="stSidebar"] {
        min-width: 260px !important;
        max-width: 260px !important;
        transform: translateX(0) !important;
        left: 0 !important;
        transition: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# CONSTANTS & HELPERS
# ==========================================
 
ORCHESTRATOR_URL = "http://127.0.0.1:8005/orchestrate/analyze"
MODULE1_URL      = "http://127.0.0.1:8003/analyze-video"   # KYC deepfake module


def call_orchestrator(payload: dict) -> dict:
    """Call the SENTINEL orchestrator (modules 2, 4, scoring)."""
    try:
        resp = requests.post(ORCHESTRATOR_URL, json=payload, timeout=90)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot reach SENTINEL backend (port 8005). Is the orchestrator running?"}
    except requests.exceptions.Timeout:
        return {"error": "Orchestrator timed out after 90s."}
    except Exception as e:
        return {"error": str(e)}


def call_kyc_module(video_bytes: bytes, filename: str) -> dict:
    """POST the KYC video to Module 1 as multipart/form-data."""
    try:
        files = {"video": (filename, video_bytes, "video/mp4")}
        resp  = requests.post(MODULE1_URL, files=files, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        if result is None:
            return {"error": "Module 1 returned no data. Check /analyze-video endpoint."}
        return result
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot reach KYC module (port 8003). Is Module 1 running?"}
    except requests.exceptions.Timeout:
        return {"error": "KYC module timed out after 120s. Video may be too large."}
    except Exception as e:
        return {"error": str(e)}


def parse_api_results(api_response: dict, loan_type: str, kyc_result: dict = None) -> dict:
    """Convert raw orchestrator JSON + kyc_result into the analysis dict for the detail page."""
    trust = api_response.get("trust_report") or {}
    mods  = api_response.get("module_results") or {}
    errs  = api_response.get("errors") or {}

    # ---- Module 1: KYC ----
    kyc = kyc_result or {}
    if kyc and "error" not in kyc and kyc.get("result") != "No Face Detected":
        kyc_prediction = kyc.get("prediction", "Unknown")
        kyc_trust      = kyc.get("trust_score", None)
        kyc_confidence = kyc.get("confidence", 0)
        kyc_risk       = kyc.get("risk_level", "")
        flagged_frames = kyc.get("flagged_frames", [])
        kyc_flags = []
        if flagged_frames:
            kyc_flags.append(f"{len(flagged_frames)} frame(s) flagged as potentially synthetic")
        if kyc_confidence > 80:
            kyc_flags.append(f"High deepfake confidence: {kyc_confidence:.1f}%")
        if kyc_prediction == "DEEPFAKE":
            kyc_flags.append("Face classified as AI-generated by EfficientNet-B3 model")
        elif kyc_prediction == "SUSPICIOUS":
            kyc_flags.append("Face shows suspicious artefacts — inconclusive result")
        deepfake = {
            "score": kyc_trust, "result": kyc_prediction.title(),
            "confidence": kyc_confidence, "risk_level": kyc_risk, "flags": kyc_flags,
        }
    elif kyc.get("result") == "No Face Detected":
        deepfake = {"score": 0, "result": "No Face Detected", "confidence": 0,
                    "flags": ["No face found in KYC video frames"]}
    elif "error" in kyc:
        deepfake = {"score": None, "result": "Module error", "confidence": 0,
                    "flags": [f"KYC module error: {kyc['error']}"]}
    else:
        deepfake = {"score": None, "result": "Not analysed", "confidence": 0, "flags": []}

    # ---- Module 2: Ghost Borrower ----
    m2 = mods.get("module2") or {}
    if m2.get("skipped") or loan_type.lower() != "msme":
        ghost = {"score": None, "flags": [], "applicable": False}
    else:
        gp = m2.get("ghost_probability", 0)
        ghost = {
            "score": round((1 - gp) * 100),
            "flags": m2.get("flags", []),
            "applicable": True,
            "risk_label": m2.get("risk_label", ""),
        }

    # ---- Module 4: Fraud Graph ----
    m4 = mods.get("module4") or {}
    graph_risk  = m4.get("graph_risk_score", 0)
    raw_conns   = m4.get("flagged_connections", [])
    graph_flags = [f"Linked to {c.get('application_id','?')} via {c.get('shared_via','?')}" for c in raw_conns]
    graph = {
        "score":  round(100 - graph_risk),
        "linked": len(raw_conns),
        "ring":   m4.get("fraud_ring_suspected", False),
        "flags":  graph_flags,
    }

    # ---- Scoring engine ----
    ts_score  = trust.get("trust_score")
    ts_tier   = trust.get("risk_tier", "").lower()
    ts_action = trust.get("recommended_action", "")

    document = {"score": None, "flags": []}

    for mod_name, err_msg in errs.items():
        if "module2" in mod_name: ghost["flags"].append(f"⚠ Module error: {err_msg}")
        elif "module4" in mod_name: graph["flags"].append(f"⚠ Module error: {err_msg}")

    return {
        "deepfake": deepfake, "document": document,
        "ghost": ghost, "graph": graph,
        "trust_score": ts_score, "risk_tier": ts_tier or None,
        "action": ts_action, "raw_response": api_response,
    }

USERS = {
    "officer@sentinel.bank": {"password": "officer123", "name": "Priya Mehta", "role": "Loan Officer"},
    "admin@sentinel.bank":   {"password": "admin123",   "name": "Rajesh Kumar", "role": "Admin"}
}

def authenticate(email, password):
    user = USERS.get(email)
    if user and user["password"] == password:
        return user
    return None

def score_color(s):
    if s is None: return "#4B5563"
    if s >= 75:   return "#34D399"
    elif s >= 50: return "#FBB824"
    elif s >= 25: return "#F87171"
    else:         return "#EF4444"

def risk_color(r):
    return {"low": "#34D399", "medium": "#FBB824", "high": "#F87171", "reject": "#EF4444"}.get(r, "#9CA3AF")

def status_color(s):
    if "Flagged" in s or "Senior" in s: return "#F59E0B"
    return {"Approved": "#34D399", "Rejected": "#EF4444", "Pending": "#9CA3AF", "Under Review": "#FBB824"}.get(s, "#9CA3AF")

# ==========================================
# SESSION STATE INIT
# ==========================================

defaults = {
    "authenticated": False,
    "user": None,
    "page": "dashboard",
    "selected_app": None,
    "new_app_step": 1,
    "new_app_data": {},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ==========================================
# DUMMY DATA (shared across pages)
# ==========================================

random.seed(42)

def generate_applications(n=30):
    names = [
        "Rahul Sharma","Priya Patel","Amit Verma","Sneha Iyer","Vikram Singh",
        "Ananya Das","Rohan Gupta","Pooja Nair","Karan Mehta","Divya Rao",
        "Suresh Kumar","Neha Joshi","Arjun Reddy","Meera Pillai","Rajesh Tiwari",
        "Kavya Shah","Manish Dubey","Sunita Yadav","Deepak Mishra","Ritu Agarwal",
        "Arun Sharma","Geeta Nair","Nikhil Jain","Swati Kulkarni","Aditya Bose",
        "Rekha Singh","Farhan Qureshi","Lalita Devi","Yash Kapoor","Nisha Menon"
    ]
    risk_tiers = ["low","medium","high","reject","low","low","medium"]
    statuses   = ["Pending","Approved","Rejected","Pending","Under Review"]
    amounts    = [2,5,8,10,15,25,50]
    apps = []
    for i in range(n):
        risk   = random.choice(risk_tiers)
        status = random.choice(statuses)
        score  = {"low": random.randint(76,95),"medium": random.randint(50,74),
                  "high": random.randint(25,49),"reject": random.randint(5,24)}[risk]
        apps.append({
            "app_id": f"APP{1000+i}", "applicant": names[i],
            "loan_type": random.choice(["Personal","MSME"]),
            "amount": random.choice(amounts),
            "date": (datetime.now() - timedelta(days=random.randint(0,30))).strftime("%d %b %Y"),
            "trust_score": score, "risk_tier": risk, "status": status,
            "flags": random.randint(0,8)
        })
    return apps

if "applications" not in st.session_state:
    st.session_state.applications = generate_applications(30)

# ==========================================
# NAVIGATION HELPER
# ==========================================

def go(page):
    st.session_state.page = page
    st.rerun()

# ==========================================
# SIDEBAR (shared for all authenticated pages)
# ==========================================

def render_sidebar():
    user = st.session_state.user
    page = st.session_state.page

    def nav_style(p):
        if p == page:
            return "padding:10px 12px;border-radius:8px;margin-bottom:4px;font-size:13px;font-weight:600;color:#3B82F6;background:rgba(59,130,246,0.15);cursor:pointer;"
        return "padding:10px 12px;border-radius:8px;margin-bottom:4px;font-size:13px;font-weight:500;color:#9CA3AF;cursor:pointer;"

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:28px;">🛡️</div>
            <div class="brand">SENTINEL</div>
            <div class="tagline">Real-time layered fraud intelligence for banking</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="sidebar-user">
            <div class="name">{user['name']}</div>
            <div class="role">{user['role']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation buttons
        if st.button("Dashboard",       key="nav_dashboard",    use_container_width=True):
            go("dashboard")
        if st.button("Applications",    key="nav_applications", use_container_width=True):
            go("applications")
        if st.button("New Application", key="nav_new_app",      use_container_width=True):
            st.session_state.new_app_step = 1
            st.session_state.new_app_data = {}
            go("new_application")
        if st.button("Analytics",       key="nav_analytics",    use_container_width=True):
            go("analytics")
        if st.button("Settings",        key="nav_settings",     use_container_width=True):
            go("settings")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("Sign Out", key="signout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "dashboard"
            st.rerun()

# ==========================================
# PAGE: LOGIN
# ==========================================

def page_login():
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        # Brand header
        st.markdown("""
        <div class="login-card">
            <div class="sentinel-logo">
                <span class="shield">🛡️</span>
                <div class="brand">SENTINEL</div>
                <div class="tagline">Real-time layered fraud intelligence for banking</div>
            </div>
            <hr class="divider">
        """, unsafe_allow_html=True)

        # Role selector tabs (rendered as styled HTML buttons via session state)
        if "login_role" not in st.session_state:
            st.session_state.login_role = "Loan Officer"

        role_col1, role_col2 = st.columns(2)
        with role_col1:
            officer_active = st.session_state.login_role == "Loan Officer"
            if st.button(
                "Loan Officer",
                key="tab_officer",
                use_container_width=True,
                type="primary" if officer_active else "secondary"
            ):
                st.session_state.login_role = "Loan Officer"
                st.rerun()
        with role_col2:
            admin_active = st.session_state.login_role == "Admin"
            if st.button(
                "Admin",
                key="tab_admin",
                use_container_width=True,
                type="primary" if admin_active else "secondary"
            ):
                st.session_state.login_role = "Admin"
                st.rerun()

        # Show hint credentials under the tabs
        role = st.session_state.login_role
        if role == "Loan Officer":
            hint_email = "officer@sentinel.bank"
            hint_label = "Loan Officer credentials"
            hint_color = "#3B82F6"
        else:
            hint_email = "admin@sentinel.bank"
            hint_label = "Admin credentials"
            hint_color = "#8B5CF6"

        st.markdown(f"""
        <div style="margin:16px 0 4px;padding:10px 14px;background:rgba(59,130,246,0.06);
             border:1px solid rgba(59,130,246,0.15);border-radius:8px;
             font-size:12px;color:#6B7280;line-height:1.7;">
            <span style="color:{hint_color};font-weight:600;">{hint_label}</span><br>
            Email: <span style="color:#D1D5DB;">{hint_email}</span>
        </div>
        """, unsafe_allow_html=True)

        # Form — keyed to role so fields reset when switching tabs
        with st.form(f"login_form_{role}"):
            email    = st.text_input("Email Address", placeholder=hint_email, value=hint_email)
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        # Close the card div
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.markdown('<div class="error-box" style="max-width:420px;margin:8px auto 0;">Please enter your email and password.</div>', unsafe_allow_html=True)
            else:
                user = authenticate(email.strip().lower(), password)
                if user:
                    # Validate role matches selected tab
                    if user["role"] != role:
                        st.markdown(f'<div class="error-box" style="max-width:420px;margin:8px auto 0;">These credentials belong to a <strong>{user["role"]}</strong>. Please select the correct login tab.</div>', unsafe_allow_html=True)
                    else:
                        st.session_state.authenticated = True
                        st.session_state.user = user
                        st.session_state.page = "dashboard"
                        st.rerun()
                else:
                    st.markdown('<div class="error-box" style="max-width:420px;margin:8px auto 0;">Invalid credentials. Please check your email and password.</div>', unsafe_allow_html=True)

        st.markdown("""
        <div class="footer-note">
            Access restricted to authorised bank personnel only.<br>
            Contact your administrator if you need access.
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: DASHBOARD
# ==========================================

def page_dashboard():
    user = st.session_state.user
    apps = st.session_state.applications

    st.markdown(f"""
    <div class="page-title">Good morning, {user['name'].split()[0]} </div>
    <div class="page-subtitle">{datetime.now().strftime("%A, %d %B %Y")} — Here's your fraud intelligence summary</div>
    """, unsafe_allow_html=True)

    # Stat cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="stat-card"><div class="label">Total Applications</div><div class="value">142</div><div class="delta up">↑ 12 this week</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card"><div class="label">Pending Review</div><div class="value">38</div><div class="delta">Awaiting analysis</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card"><div class="label">High Risk Flagged</div><div class="value">17</div><div class="delta down">↑ 5 since yesterday</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="stat-card"><div class="label">Approved This Week</div><div class="value">29</div><div class="delta up">↑ 8 vs last week</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

    col_main, col_alerts = st.columns([3, 1])

    with col_main:
        st.markdown('<div class="section-header">Recent Applications</div>', unsafe_allow_html=True)

        display_df = pd.DataFrame(apps[:10])[[
            "app_id","applicant","loan_type","amount","trust_score","risk_tier","status"
        ]].rename(columns={
            "app_id":"App ID","applicant":"Applicant","loan_type":"Type",
            "amount":"Amount (₹L)","trust_score":"Trust Score",
            "risk_tier":"Risk","status":"Status"
        })

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        if st.button("View All Applications →", key="dash_view_all"):
            go("applications")

    with col_alerts:
        st.markdown('<div class="section-header">Fraud Alerts</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="alert-card">
            <div class="alert-title">Fraud Ring Detected</div>
            <div class="alert-body">APP1003, APP1007, APP1015 share device ID DEV999. Possible coordinated fraud ring.</div>
        </div>
        <div class="alert-card">
            <div class="alert-title">Deepfake Suspected</div>
            <div class="alert-body">APP1012 — video KYC flagged with 84% deepfake confidence. Manual review required.</div>
        </div>
        <div class="alert-card">
            <div class="alert-title">Ghost Business</div>
            <div class="alert-body">APP1018 — MSME registered 3 months ago, applying for ₹25L. Director linked to 8 other companies.</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# PAGE: APPLICATIONS
# ==========================================

def page_applications():
    apps = st.session_state.applications

    st.markdown('<div class="page-title">Applications</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Review, approve, or reject loan applications based on SENTINEL analysis</div>', unsafe_allow_html=True)

    # Summary bar
    total    = len(apps)
    pending  = sum(1 for a in apps if a["status"] == "Pending")
    high_risk= sum(1 for a in apps if a["risk_tier"] in ["high","reject"])
    approved = sum(1 for a in apps if a["status"] == "Approved")

    st.markdown(f"""
    <div class="summary-bar">
        <div class="summary-item"><div class="s-label">Total</div><div class="s-value">{total}</div></div>
        <div class="summary-item"><div class="s-label">Pending</div><div class="s-value" style="color:#FBB824">{pending}</div></div>
        <div class="summary-item"><div class="s-label">High Risk</div><div class="s-value" style="color:#F87171">{high_risk}</div></div>
        <div class="summary-item"><div class="s-label">Approved</div><div class="s-value" style="color:#34D399">{approved}</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    f1, f2, f3, f4 = st.columns([2,1,1,1])
    with f1: search        = st.text_input("Search", placeholder="Search by name or App ID...")
    with f2: filter_type   = st.selectbox("Loan Type", ["All","Personal","MSME"])
    with f3: filter_risk   = st.selectbox("Risk Tier", ["All","low","medium","high","reject"])
    with f4: filter_status = st.selectbox("Status", ["All","Pending","Approved","Rejected","Under Review"])

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    filtered = apps.copy()
    if search:
        filtered = [a for a in filtered if search.lower() in a["applicant"].lower() or search.lower() in a["app_id"].lower()]
    if filter_type   != "All": filtered = [a for a in filtered if a["loan_type"] == filter_type]
    if filter_risk   != "All": filtered = [a for a in filtered if a["risk_tier"] == filter_risk]
    if filter_status != "All": filtered = [a for a in filtered if a["status"] == filter_status]

    st.markdown(f'<div class="section-header">Showing {len(filtered)} applications</div>', unsafe_allow_html=True)

    if not filtered:
        st.markdown('<div style="text-align:center;padding:60px 0;color:#4B5563;"><div style="font-size:32px;margin-bottom:12px;">🔍</div><div style="font-size:14px;">No applications match your filters.</div></div>', unsafe_allow_html=True)
        return

    # Table header
    h1,h2,h3,h4,h5,h6,h7,h8 = st.columns([1.2,2,1.2,1,1.2,1,1.2,2])
    hs = "color:#6B7280;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:0.5px;padding:4px 0;"
    h1.markdown(f"<div style='{hs}'>App ID</div>",      unsafe_allow_html=True)
    h2.markdown(f"<div style='{hs}'>Applicant</div>",   unsafe_allow_html=True)
    h3.markdown(f"<div style='{hs}'>Type</div>",        unsafe_allow_html=True)
    h4.markdown(f"<div style='{hs}'>Amount</div>",      unsafe_allow_html=True)
    h5.markdown(f"<div style='{hs}'>Trust Score</div>", unsafe_allow_html=True)
    h6.markdown(f"<div style='{hs}'>Risk</div>",        unsafe_allow_html=True)
    h7.markdown(f"<div style='{hs}'>Status</div>",      unsafe_allow_html=True)
    h8.markdown(f"<div style='{hs}'>Actions</div>",     unsafe_allow_html=True)
    st.markdown("<div style='border-bottom:1px solid #2A2D3E;margin-bottom:8px;'></div>", unsafe_allow_html=True)

    for i, app in enumerate(filtered):
        sc  = score_color(app["trust_score"])
        rc  = risk_color(app["risk_tier"])
        stc = status_color(app["status"])
        c1,c2,c3,c4,c5,c6,c7,c8 = st.columns([1.2,2,1.2,1,1.2,1,1.2,2])

        c1.markdown(f"<div style='color:#6B7280;font-size:12px;font-family:monospace;padding:8px 0'>{app['app_id']}</div>", unsafe_allow_html=True)
        c2.markdown(f"<div style='color:#FFFFFF;font-size:13px;font-weight:500;padding:8px 0'>{app['applicant']}</div>", unsafe_allow_html=True)
        c3.markdown(f"<div style='color:#9CA3AF;font-size:12px;padding:8px 0'>{app['loan_type']}</div>", unsafe_allow_html=True)
        c4.markdown(f"<div style='color:#9CA3AF;font-size:12px;padding:8px 0'>₹{app['amount']}L</div>", unsafe_allow_html=True)
        c5.markdown(f"<div style='padding:8px 0'><span style='color:{sc};font-weight:700;font-size:14px'>{app['trust_score']}</span><span style='color:#4B5563;font-size:11px'>/100</span></div>", unsafe_allow_html=True)
        c6.markdown(f"<div style='padding:8px 0'><span style='color:{rc};font-size:12px;font-weight:600;text-transform:uppercase'>{app['risk_tier']}</span></div>", unsafe_allow_html=True)
        c7.markdown(f"<div style='padding:8px 0'><span style='color:{stc};font-size:12px;font-weight:500'>{app['status']}</span></div>", unsafe_allow_html=True)

        with c8:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("👁", key=f"view_{i}", help="View Details"):
                    st.session_state.selected_app = app
                    go("application_detail")
            with b2:
                if st.button("✓", key=f"approve_{i}", help="Approve"):
                    idx = next(j for j,a in enumerate(st.session_state.applications) if a["app_id"]==app["app_id"])
                    st.session_state.applications[idx]["status"] = "Approved"
                    st.rerun()
            with b3:
                if st.button("✗", key=f"reject_{i}", help="Reject"):
                    idx = next(j for j,a in enumerate(st.session_state.applications) if a["app_id"]==app["app_id"])
                    st.session_state.applications[idx]["status"] = "Rejected"
                    st.rerun()

        st.markdown("<div style='border-bottom:1px solid #1E2130;'></div>", unsafe_allow_html=True)

# ==========================================
# PAGE: APPLICATION DETAIL
# ==========================================

def page_application_detail():
    app = st.session_state.get("selected_app") or st.session_state.applications[0]

    # Back button
    if st.button("← Back to Applications", key="back_to_apps"):
        go("applications")

    st.markdown(f"""
    <div class="page-title">{app['applicant']} — {app['app_id']}</div>
    <div class="page-subtitle">{app['loan_type']} Loan · ₹{app['amount']}L requested · Submitted {app['date']}</div>
    """, unsafe_allow_html=True)

    # Use real API results if available, otherwise fall back to dummy
    api_results = app.get("api_results")

    if api_results:
        kyc_result_stored = api_results.get("kyc_result")
        analysis = parse_api_results(api_results, app["loan_type"], kyc_result=kyc_result_stored)
        if analysis.get("trust_score") is not None:
            app = dict(app)
            app["trust_score"] = int(analysis["trust_score"])
        if analysis.get("risk_tier"):
            app = dict(app)
            app["risk_tier"] = analysis["risk_tier"]
    else:
        # Dummy analysis for pre-existing demo applications
        random.seed(int(app["app_id"].replace("APP","") or "0"))
        analysis = {
            "deepfake": {
                "score":  random.randint(10,30) if app["risk_tier"]=="reject" else random.randint(60,95),
                "result": "Deepfake Detected" if app["risk_tier"]=="reject" else "Genuine",
                "confidence": 0, "flags":
                ["Face edge artifacts detected","Unnatural blink rate"] if app["risk_tier"] in ["reject","high"] else []
            },
            "document": {
                "score": random.randint(5,25) if app["risk_tier"]=="reject" else random.randint(55,90),
                "flags": ["Salary slip income does not match ITR","Employer name mismatch"] if app["risk_tier"] in ["reject","high"] else []
            },
            "ghost": {
                "score": random.randint(5,20) if app["risk_tier"]=="reject" else random.randint(60,90),
                "flags": ["Irregular GST filing history","Suspicious registered address","Director linked to 9 other companies"] if app["risk_tier"] in ["reject","high"] else [],
                "applicable": app["loan_type"]=="MSME"
            },
            "graph": {
                "score":  random.randint(0,15) if app["risk_tier"]=="reject" else random.randint(65,95),
                "linked": random.randint(2,4) if app["risk_tier"] in ["reject","high"] else 0,
                "ring":   app["risk_tier"]=="reject",
                "flags":  ["Linked to 3 previously flagged applications","Shared phone number with known fraud application"] if app["risk_tier"] in ["reject","high"] else []
            }
        }

    all_flags = (
        [("identity", f) for f in analysis["deepfake"]["flags"]] +
        [("document", f) for f in analysis["document"]["flags"]] +
        [("business", f) for f in analysis["ghost"]["flags"]] +
        [("network",  f) for f in analysis["graph"]["flags"]]
    )

    # Trust score + applicant info
    top_left, top_right = st.columns([1,2])
    with top_left:
        tier   = app["risk_tier"]
        color  = risk_color(tier)
        bg     = {"low":"rgba(52,211,153,0.15)","medium":"rgba(251,191,36,0.15)","high":"rgba(248,113,113,0.15)","reject":"rgba(239,68,68,0.2)"}.get(tier,"rgba(107,114,128,0.2)")
        action = {"low":"Proceed with approval","medium":"Flag for manual review","high":"Reject — high fraud risk","reject":"Immediate rejection"}.get(tier,"")
        st.markdown(f"""
        <div class="card" style="text-align:center;">
            <div class="trust-label">SENTINEL Trust Score</div>
            <div class="trust-score-big" style="color:{color}">{app['trust_score']}</div>
            <div style="color:#4B5563;font-size:14px;margin-top:-4px;">/100</div>
            <div class="risk-tier-badge" style="background:{bg};color:{color}">{tier.upper()}</div>
            <div style="margin-top:14px;font-size:12px;color:#6B7280;padding:10px;background:#0F1117;border-radius:8px;">{action}</div>
        </div>
        """, unsafe_allow_html=True)

    with top_right:
        st.markdown('<div class="card"><div class="card-title">Applicant Information</div>', unsafe_allow_html=True)

        # Build a colour-coded status badge
        raw_status = app["status"]
        is_flagged = "Flagged" in raw_status or "Senior" in raw_status
        if is_flagged:
            status_html = (
                '<span style="color:#F59E0B;font-weight:600;">Pending</span>'
                '&nbsp;<span style="display:inline-block;font-size:11px;font-weight:600;'
                'color:#F59E0B;background:rgba(245,158,11,0.15);border:1px solid rgba(245,158,11,0.3);'
                'padding:2px 8px;border-radius:10px;">Flagged for Senior Review</span>'
            )
        else:
            sc = status_color(raw_status)
            status_html = f'<span style="color:{sc};font-weight:600;">{raw_status}</span>'

        for label, value in [
            ("Application ID",   app["app_id"]),
            ("Full Name",        app["applicant"]),
            ("Loan Type",        app["loan_type"]),
            ("Amount Requested", f"₹{app['amount']} Lakhs"),
            ("Submission Date",  app["date"]),
            ("Total Flags Raised", f"{len(all_flags)} flags"),
        ]:
            st.markdown(f'<div class="info-row"><span class="info-label">{label}</span><span class="info-value">{value}</span></div>', unsafe_allow_html=True)

        # Status row rendered separately with the badge
        st.markdown(f'<div class="info-row"><span class="info-label">Current Status</span><span class="info-value">{status_html}</span></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Module cards
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Module Analysis</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)

    def msc(s): return score_color(s)

    with m1:
        kyc_score = analysis["deepfake"]["score"]
        kyc_pred  = analysis["deepfake"].get("result", "—")
        kyc_conf  = analysis["deepfake"].get("confidence", 0)
        sc = score_color(kyc_score) if kyc_score is not None else "#4B5563"
        disp = str(kyc_score) if kyc_score is not None else "—"

        if kyc_score is None:
            sublabel = "Not yet analysed"
            fh = ""
        else:
            conf_str = f" · {kyc_conf:.1f}% deepfake conf" if kyc_conf else ""
            sublabel = f"Score /100 · {kyc_pred}{conf_str}"
            fh = "".join([f'<div class="module-flag">⚠ {f}</div>' for f in analysis["deepfake"]["flags"]]) or '<div style="font-size:11px;color:#34D399;">✓ No flags</div>'
            pred_col = {"REAL":"#34D399","Genuine":"#34D399","SUSPICIOUS":"#FBB824","Suspicious":"#FBB824","DEEPFAKE":"#EF4444","Deepfake Detected":"#EF4444"}.get(kyc_pred, "#9CA3AF")
            fh = f'<div style="margin-top:8px;display:inline-block;font-size:11px;font-weight:700;color:{pred_col};background:rgba(255,255,255,0.05);padding:3px 8px;border-radius:6px;border:1px solid {pred_col}40">{kyc_pred.upper()}</div>' + fh

        st.markdown(f'<div class="module-card"><div class="module-title">KYC Verification</div><div class="module-score" style="color:{sc}">{disp}</div><div class="module-label">{sublabel}</div>{fh}</div>', unsafe_allow_html=True)

    with m2:
        doc_score = analysis["document"]["score"]
        sc = msc(doc_score)
        disp = str(doc_score) if doc_score is not None else "—"
        sublabel = "Consistency Score /100" if doc_score is not None else "Not yet analysed"
        fh = "".join([f'<div class="module-flag">⚠ {f}</div>' for f in analysis["document"]["flags"]]) or '<div style="font-size:11px;color:#34D399;">✓ No flags</div>'
        st.markdown(f'<div class="module-card"><div class="module-title">Document Correlation</div><div class="module-score" style="color:{sc}">{disp}</div><div class="module-label">{sublabel}</div>{fh}</div>', unsafe_allow_html=True)

    with m3:
        sc = msc(analysis["ghost"]["score"])
        if analysis["ghost"]["applicable"]:
            fh = "".join([f'<div class="module-flag">⚠ {f}</div>' for f in analysis["ghost"]["flags"]]) or '<div style="font-size:11px;color:#34D399;">✓ No flags</div>'
            content = f'<div class="module-score" style="color:{sc}">{analysis["ghost"]["score"]}</div><div class="module-label">Ghost Score /100</div>{fh}'
        else:
            content = '<div style="font-size:12px;color:#4B5563;margin-top:16px;">Not applicable for Personal loans</div>'
        st.markdown(f'<div class="module-card"><div class="module-title">Ghost Borrower</div>{content}</div>', unsafe_allow_html=True)

    with m4:
        sc = msc(analysis["graph"]["score"])
        ring_html = '<div style="font-size:11px;color:#EF4444;margin-top:6px;">Fraud ring suspected</div>' if analysis["graph"]["ring"] else ""
        fh = "".join([f'<div class="module-flag">⚠ {f}</div>' for f in analysis["graph"]["flags"]]) or '<div style="font-size:11px;color:#34D399;">✓ No flags</div>'
        st.markdown(f'<div class="module-card"><div class="module-title">Fraud Graph</div><div class="module-score" style="color:{sc}">{analysis["graph"]["score"]}</div><div class="module-label">Graph Risk Score /100 · {analysis["graph"]["linked"]} linked apps</div>{ring_html}{fh}</div>', unsafe_allow_html=True)

    # All flags
    if all_flags:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-header">All Flags Raised</div>', unsafe_allow_html=True)
        flag_cols = st.columns(2)
        tag_map = {"identity":("Identity","flag-identity"),"document":("Document","flag-document"),"business":("Business","flag-business"),"network":("Network","flag-network")}
        for idx,(ft,text) in enumerate(all_flags):
            tag, css = tag_map.get(ft, ("Flag","flag-document"))
            with flag_cols[idx%2]:
                st.markdown(f'<div class="flag-item {css}"><span style="font-size:10px;font-weight:700;opacity:0.7;text-transform:uppercase;letter-spacing:0.5px">[{tag}]</span><br>{text}</div>', unsafe_allow_html=True)

    # Decision panel
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="section-header">Officer Decision</div>', unsafe_allow_html=True)
    notes = st.text_area("Officer Notes", placeholder="Add your assessment or reason for decision...", height=100)
    d1,d2,d3 = st.columns(3)
    with d1:
        if st.button("Approve Application", key="approve_final"):
            idx = next(j for j,a in enumerate(st.session_state.applications) if a["app_id"]==app["app_id"])
            st.session_state.applications[idx]["status"] = "Approved"
            st.session_state.selected_app = st.session_state.applications[idx]
            st.success(f"{app['app_id']} approved successfully.")
    with d2:
        if st.button("Flag for Senior Review", key="flag_final"):
            idx = next(j for j,a in enumerate(st.session_state.applications) if a["app_id"]==app["app_id"])
            st.session_state.applications[idx]["status"] = "Pending · Flagged for Senior Review"
            st.session_state.selected_app = st.session_state.applications[idx]
            st.warning(f"{app['app_id']} has been flagged for senior review. Status updated.")
    with d3:
        if st.button("Reject Application", key="reject_final"):
            idx = next(j for j,a in enumerate(st.session_state.applications) if a["app_id"]==app["app_id"])
            st.session_state.applications[idx]["status"] = "Rejected"
            st.session_state.selected_app = st.session_state.applications[idx]
            st.error(f"{app['app_id']} has been rejected.")

# ==========================================
# PAGE: NEW APPLICATION
# ==========================================

def page_new_application():
    step = st.session_state.new_app_step
    data = st.session_state.new_app_data

    st.markdown('<div class="page-title">New Application</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Create a new loan application and run SENTINEL fraud analysis</div>', unsafe_allow_html=True)

    # Step indicator
    def step_class(n):
        if n < step: return "step-done"
        elif n == step: return "step-active"
        return "step-inactive"
    def step_icon(n): return "✓" if n < step else str(n)
    def line_class(n): return "step-line-done" if n < step else ""

    st.markdown(f"""
    <div class="step-bar">
        <div class="step {step_class(1)}"><div class="step-circle">{step_icon(1)}</div><span class="step-label">Basic Details</span></div>
        <div class="step-line {line_class(1)}"></div>
        <div class="step {step_class(2)}"><div class="step-circle">{step_icon(2)}</div><span class="step-label">Documents</span></div>
        <div class="step-line {line_class(2)}"></div>
        <div class="step {step_class(3)}"><div class="step-circle">{step_icon(3)}</div><span class="step-label">KYC Video</span></div>
        <div class="step-line {line_class(3)}"></div>
        <div class="step {step_class(4)}"><div class="step-circle">{step_icon(4)}</div><span class="step-label">Run Analysis</span></div>
    </div>
    """, unsafe_allow_html=True)

    # --- STEP 1 ---
    if step == 1:
        st.markdown('<div class="card"><div class="card-title">Applicant Details</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            name    = st.text_input("Full Name *",        placeholder="e.g. Rahul Sharma")
            pan     = st.text_input("PAN Number *",       placeholder="e.g. ABCDE1234F")
            phone   = st.text_input("Mobile Number *",    placeholder="e.g. 9876543210")
        with c2:
            email   = st.text_input("Email Address *",    placeholder="e.g. rahul@email.com")
            dob     = st.text_input("Date of Birth *",    placeholder="DD-MM-YYYY")
            address = st.text_input("Residential Address *", placeholder="Full address with pincode")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card"><div class="card-title"> Loan Details</div>', unsafe_allow_html=True)
        l1,l2,l3 = st.columns(3)
        with l1: loan_type    = st.selectbox("Loan Type *", ["Personal","MSME"])
        with l2: loan_amount  = st.number_input("Loan Amount (₹ Lakhs) *", min_value=1, max_value=500, value=10)
        with l3: loan_purpose = st.selectbox("Loan Purpose *", ["Home Renovation","Medical Emergency","Education","Working Capital","Equipment Purchase","Business Expansion","Debt Consolidation","Other"])

        if loan_type == "MSME":
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            m1,m2 = st.columns(2)
            with m1: gst = st.text_input("GST Number *",  placeholder="e.g. 29ABCDE1234F1Z5")
            with m2: cin = st.text_input("CIN Number",    placeholder="e.g. U74999MH2020PTC123456")
        st.markdown("</div>", unsafe_allow_html=True)

        col_back, col_next = st.columns([4,1])
        with col_next:
            if st.button("Next →", key="step1_next"):
                if not name or not pan or not phone or not email:
                    st.error("Please fill all required fields.")
                else:
                    st.session_state.new_app_data.update({"name":name,"pan":pan,"phone":phone,"email":email,"loan_type":loan_type,"loan_amount":loan_amount,"loan_purpose":loan_purpose})
                    st.session_state.new_app_step = 2
                    st.rerun()

    # --- STEP 2 ---
    elif step == 2:
        loan_type = data.get("loan_type","Personal")
        st.markdown('<div class="card"><div class="card-title">Document Upload</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:12px;color:#6B7280;margin-bottom:20px;">Loan type: <strong style="color:#3B82F6">{loan_type}</strong></div>', unsafe_allow_html=True)

        u1,u2 = st.columns(2)
        with u1:
            st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">Salary Slip <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
            salary_slip = st.file_uploader("", type=["pdf"], key="salary_slip", label_visibility="collapsed")
            if salary_slip: st.markdown(f'<div class="upload-status-ok">✓ {salary_slip.name} uploaded</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">ITR Acknowledgement <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
            itr = st.file_uploader("", type=["pdf"], key="itr", label_visibility="collapsed")
            if itr: st.markdown(f'<div class="upload-status-ok">✓ {itr.name} uploaded</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">Aadhaar Card <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
            aadhaar = st.file_uploader("", type=["pdf","jpg","png"], key="aadhaar", label_visibility="collapsed")
            if aadhaar: st.markdown(f'<div class="upload-status-ok">✓ {aadhaar.name} uploaded</div>', unsafe_allow_html=True)

        with u2:
            st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">Bank Statement (6 months) <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
            bank_stmt = st.file_uploader("", type=["pdf"], key="bank_stmt", label_visibility="collapsed")
            if bank_stmt: st.markdown(f'<div class="upload-status-ok">✓ {bank_stmt.name} uploaded</div>', unsafe_allow_html=True)

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">PAN Card <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
            pan_doc = st.file_uploader("", type=["pdf","jpg","png"], key="pan_doc", label_visibility="collapsed")
            if pan_doc: st.markdown(f'<div class="upload-status-ok">✓ {pan_doc.name} uploaded</div>', unsafe_allow_html=True)

            if loan_type == "MSME":
                st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:4px;">GST Certificate <span class="required-badge">Required for MSME</span></div>', unsafe_allow_html=True)
                gst_cert = st.file_uploader("", type=["pdf"], key="gst_cert", label_visibility="collapsed")
                if gst_cert: st.markdown(f'<div class="upload-status-ok">✓ {gst_cert.name} uploaded</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        cb, cs, cn = st.columns([1,3,1])
        with cb:
            if st.button("← Back", key="step2_back"):
                st.session_state.new_app_step = 1; st.rerun()
        with cn:
            if st.button("Next →", key="step2_next"):
                if not salary_slip or not itr or not bank_stmt:
                    st.error("Please upload all required documents.")
                else:
                    st.session_state.new_app_data["documents"] = {"salary_slip": salary_slip.name, "itr": itr.name, "bank_statement": bank_stmt.name}
                    st.session_state.new_app_step = 3; st.rerun()

    # --- STEP 3 ---
    elif step == 3:
        st.markdown('<div class="card"><div class="card-title"> KYC Video Verification</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#0F1117;border-radius:10px;padding:20px;margin-bottom:20px;border:1px solid #2A2D3E;">
            <div style="font-size:13px;color:#9CA3AF;line-height:1.8;">
                <strong style="color:#FFFFFF;">Instructions for KYC Video:</strong><br>
                1. The applicant should record a 15-second face video in good lighting.<br>
                2. Face should be clearly visible — no glasses, masks, or hats.<br>
                3. The applicant should look directly at the camera and blink naturally.<br>
                4. Video should be recorded on the applicant's registered device.<br>
                5. Accepted formats: MP4, MOV, AVI (max 50MB)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="font-size:12px;color:#9CA3AF;font-weight:500;margin-bottom:8px;">Upload KYC Video <span class="required-badge">Required</span></div>', unsafe_allow_html=True)
        kyc_video = st.file_uploader("", type=["mp4","mov","avi"], key="kyc_video", label_visibility="collapsed")
        if kyc_video:
            st.markdown(f'<div class="upload-status-ok">✓ {kyc_video.name} uploaded successfully — ready for deepfake analysis</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="margin-top:12px;padding:30px;background:#0F1117;border:2px dashed #2A2D3E;border-radius:10px;text-align:center;"><div style="font-size:28px;margin-bottom:8px;">🎥</div><div style="font-size:13px;color:#4B5563;">Upload the applicant\'s KYC video here</div><div style="font-size:11px;color:#374151;margin-top:4px;">MP4, MOV, AVI · Max 50MB · Min 10 seconds</div></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        cb, cs, cn = st.columns([1,3,1])
        with cb:
            if st.button("← Back", key="step3_back"):
                st.session_state.new_app_step = 2; st.rerun()
        with cn:
            if st.button("Next →", key="step3_next"):
                # Store raw bytes so Step 4 can POST them directly to Module 1
                if kyc_video:
                    st.session_state.new_app_data["kyc_video_bytes"]    = kyc_video.read()
                    st.session_state.new_app_data["kyc_video_filename"] = kyc_video.name
                else:
                    st.session_state.new_app_data["kyc_video_bytes"]    = None
                    st.session_state.new_app_data["kyc_video_filename"] = None
                st.session_state.new_app_step = 4; st.rerun()

    # --- STEP 4 ---
    elif step == 4:
        st.markdown('<div class="card"><div class="card-title">Ready to Run SENTINEL Analysis</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
            <div style="background:#0F1117;border-radius:8px;padding:14px 16px;border:1px solid #2A2D3E;">
                <div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Applicant</div>
                <div style="font-size:14px;color:#FFFFFF;font-weight:600;">{data.get('name','—')}</div>
                <div style="font-size:12px;color:#6B7280;margin-top:2px;">PAN: {data.get('pan','—')}</div>
            </div>
            <div style="background:#0F1117;border-radius:8px;padding:14px 16px;border:1px solid #2A2D3E;">
                <div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:6px;">Loan Details</div>
                <div style="font-size:14px;color:#FFFFFF;font-weight:600;">₹{data.get('loan_amount','—')} Lakhs</div>
                <div style="font-size:12px;color:#6B7280;margin-top:2px;">{data.get('loan_type','—')} · {data.get('loan_purpose','—')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        modules = [
            ("KYC Verification","Analyzes KYC video for AI-generated or synthetic faces"),
            ("Document Correlation","Cross-checks all uploaded financial documents"),
            ("Ghost Borrower Detection", "Validates business existence and GST filing history" if data.get("loan_type")=="MSME" else "Skipped — not applicable for Personal loans"),
            ("Fraud Graph Intelligence","Checks for connections to known fraud entities"),
        ]
        for title,desc in modules:
            skipped = "Skipped" in desc
            st.markdown(f'<div style="font-size:13px;font-weight:500;color:{"#4B5563" if skipped else "#FFFFFF"};">{title}</div><div style="font-size:12px;color:{"#4B5563" if skipped else "#6B7280"};margin-top:2px;">{desc}</div></div></div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        cb, cs, cr = st.columns([1,2,1])
        with cb:
            if st.button("← Back", key="step4_back"):
                st.session_state.new_app_step = 3; st.rerun()
        with cr:
            if st.button("Run SENTINEL Analysis", key="run_analysis"):
                progress    = st.progress(0)
                status_text = st.empty()

                # ── STEP A: Module 1 — KYC deepfake (direct binary upload) ──
                status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">⏳ Uploading KYC video to deepfake detection module...</div>', unsafe_allow_html=True)
                progress.progress(10)

                kyc_bytes    = data.get("kyc_video_bytes")
                kyc_filename = data.get("kyc_video_filename") or "kyc_video.mp4"
                kyc_result   = None

                if kyc_bytes:
                    status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">Running KYC deepfake analysis (EfficientNet-B3)...</div>', unsafe_allow_html=True)
                    progress.progress(20)
                    kyc_result = call_kyc_module(kyc_bytes, kyc_filename)
                    if "error" in kyc_result:
                        st.warning(f"KYC module: {kyc_result['error']} — KYC score will show as unavailable.")
                    else:
                        kyc_pred = kyc_result.get("prediction", "?")
                        kyc_conf = kyc_result.get("confidence", 0)
                        st.info(f"KYC result: **{kyc_pred}** ({kyc_conf:.1f}% deepfake confidence)")
                else:
                    st.warning("No KYC video uploaded — KYC module skipped.")

                # ── STEP B: Orchestrator (modules 2 + 4 + scoring) ──
                status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">⏳ Correlating financial documents...</div>', unsafe_allow_html=True)
                progress.progress(40)

                status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">⏳ Checking ghost borrower signals...</div>', unsafe_allow_html=True)
                progress.progress(55)

                generated_id = f"APP{random.randint(1100,1999)}"
                payload = {
                    "application_id": generated_id,
                    "loan_type": data.get("loan_type", "Personal").lower(),
                    "loan_amount": float(data.get("loan_amount", 10)),
                    "phone": data.get("phone", ""),
                    "email": data.get("email", ""),
                    "pan": data.get("pan", ""),
                    "device_id": "DEV_NODE_UI_SECURE",
                    "address": data.get("address", "Not Specified"),
                    "is_flagged": False,
                    "business_type": "Proprietorship" if data.get("loan_type") == "MSME" else None,
                    "business_age_months": 24 if data.get("loan_type") == "MSME" else None,
                    "loan_purpose": data.get("loan_purpose", "working capital"),
                }

                # Forward Module 1 scores into orchestrator so scoring engine sees KYC
                if kyc_result and "error" not in kyc_result and kyc_result.get("result") != "No Face Detected":
                    payload["deepfake_score"]      = kyc_result.get("trust_score")
                    payload["deepfake_confidence"] = kyc_result.get("confidence", 0)
                    payload["deepfake_prediction"] = kyc_result.get("prediction", "")
                    payload["deepfake_flags"] = (
                        [f"{len(kyc_result.get('flagged_frames',[]))} frames flagged"]
                        if kyc_result.get("flagged_frames") else []
                    )

                api_resp = call_orchestrator(payload)
                progress.progress(75)

                status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">⏳ Building fraud graph...</div>', unsafe_allow_html=True)
                progress.progress(85)

                status_text.markdown('<div style="font-size:12px;color:#6B7280;margin-top:8px;">⏳ Generating trust score...</div>', unsafe_allow_html=True)
                progress.progress(95)

                progress.progress(100)
                status_text.empty()
                progress.empty()

                # ── STEP C: Parse results ──
                if "error" in api_resp:
                    st.error(f"Orchestrator error: {api_resp['error']}")
                    st.info("Falling back to demo mode.")
                    backend_score = random.randint(5, 95)
                    backend_tier  = ("low" if backend_score >= 75 else "medium" if backend_score >= 50 else "high" if backend_score >= 25 else "reject")
                    api_results   = None
                else:
                    trust_report  = api_resp.get("trust_report") or {}
                    backend_score = trust_report.get("trust_score") or random.randint(5, 95)
                    backend_tier  = (trust_report.get("risk_tier") or "").lower()
                    if backend_tier not in ("low","medium","high","reject"):
                        backend_tier = ("low" if backend_score >= 75 else "medium" if backend_score >= 50 else "high" if backend_score >= 25 else "reject")
                    api_resp["kyc_result"] = kyc_result   # attach so detail page can read it
                    api_results = api_resp
                    st.success(" SENTINEL analysis complete!")

                new_app = {
                    "app_id":      generated_id,
                    "applicant":   data.get("name","Unknown"),
                    "loan_type":   data.get("loan_type","Personal"),
                    "amount":      data.get("loan_amount",10),
                    "date":        datetime.now().strftime("%d %b %Y"),
                    "trust_score": int(backend_score),
                    "risk_tier":   backend_tier,
                    "status":      "Pending",
                    "flags":       0,
                    "api_results": api_results,
                }
                st.session_state.applications.insert(0, new_app)
                st.session_state.selected_app  = new_app
                st.session_state.new_app_step  = 1
                st.session_state.new_app_data  = {}
                time.sleep(0.8)
                go("application_detail")
# ==========================================
# PAGE: ANALYTICS
# ==========================================

def page_analytics():
    random.seed(99)
    dates         = [(datetime.now()-timedelta(days=i)).strftime("%d %b") for i in range(13,-1,-1)]
    daily_counts  = [random.randint(6,22) for _ in dates]
    daily_flagged = [random.randint(1,6)  for _ in dates]
    risk_data     = {"Low":58,"Medium":31,"High":17,"Reject":9}
    loan_data     = {"Personal":81,"MSME":61}
    module_flags  = {"Document Correlation":67,"Ghost Borrower Detection":43,"Fraud Graph Intelligence":38,"KYC Verification":21}
    top_flags     = [("Salary slip income does not match ITR",41,"#FBB824"),("Irregular GST filing history",29,"#F87171"),("Director linked to many companies",24,"#F87171"),("Address mismatch across documents",22,"#FBB824"),("Fraud ring connection detected",19,"#EF4444"),("Suspicious document metadata",16,"#FBB824"),("Deepfake face detected in KYC",14,"#8B5CF6"),("Bank credits inconsistent with salary",13,"#FBB824")]
    weeks         = ["Week 1","Week 2","Week 3","Week 4"]
    approved_weekly  = [18,23,19,29]
    rejected_weekly  = [7,11,9,14]

    st.markdown('<div class="page-title">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Fraud intelligence trends and system performance overview</div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown('<div class="stat-card"><div class="label">Fraud Detection Rate</div><div class="value">23.1%</div><div class="delta down">↑ 2.4% vs last month</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="stat-card"><div class="label">Avg Trust Score</div><div class="value">61.4</div><div class="delta up">↑ 3.2 vs last month</div></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="stat-card"><div class="label">Fraud Rings Detected</div><div class="value">4</div><div class="delta down">↑ 2 this month</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="stat-card"><div class="label">Avg Analysis Time</div><div class="value">43s</div><div class="delta up">↓ 8s faster this week</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    r1l, r1r = st.columns([2,1])
    with r1l:
        st.markdown('<div class="card"><div class="card-title">Daily Application Volume — Last 14 Days</div>', unsafe_allow_html=True)
        chart_df = pd.DataFrame({"Date":dates,"Total Applications":daily_counts,"Flagged":daily_flagged}).set_index("Date")
        st.bar_chart(chart_df, color=["#3B82F6","#EF4444"], height=220)
        st.markdown("</div>", unsafe_allow_html=True)
    with r1r:
        st.markdown('<div class="card"><div class="card-title">Risk Tier Distribution</div>', unsafe_allow_html=True)
        total_apps  = sum(risk_data.values())
        risk_colors = {"Low":"#34D399","Medium":"#FBB824","High":"#F87171","Reject":"#EF4444"}
        for tier,count in risk_data.items():
            pct = round(count/total_apps*100,1)
            color = risk_colors[tier]
            st.markdown(f'<div style="margin-bottom:12px;"><div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:12px;color:#9CA3AF;">{tier}</span><span style="font-size:12px;color:{color};font-weight:600;">{count} <span style="color:#4B5563;font-weight:400;">({pct}%)</span></span></div><div style="background:#2A2D3E;border-radius:4px;height:6px;overflow:hidden;"><div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div></div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    r2l, r2r = st.columns([1,1])
    max_flags     = max(module_flags.values())
    max_flag_count= top_flags[0][1]
    module_colors = {"Document Correlation":"#FBB824","Ghost Borrower Detection":"#F87171","Fraud Graph Intelligence":"#EF4444","KYC Verification":"#8B5CF6"}

    with r2l:
        st.markdown('<div class="card"><div class="card-title">Flags by Module</div>', unsafe_allow_html=True)
        for module,count in module_flags.items():
            pct   = round(count/max_flags*100)
            color = module_colors[module]
            st.markdown(f'<div class="flag-bar-item"><div class="flag-bar-label">{module}</div><div class="flag-bar-track"><div class="flag-bar-fill" style="width:{pct}%;background:{color};"></div></div><div class="flag-bar-count">{count}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2r:
        st.markdown('<div class="card"><div class="card-title">Most Common Fraud Flags</div>', unsafe_allow_html=True)
        for flag_text,count,color in top_flags:
            pct = round(count/max_flag_count*100)
            st.markdown(f'<div class="flag-bar-item"><div class="flag-bar-label">{flag_text}</div><div class="flag-bar-track"><div class="flag-bar-fill" style="width:{pct}%;background:{color};"></div></div><div class="flag-bar-count">{count}</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    r3l, r3r = st.columns([2,1])
    with r3l:
        st.markdown('<div class="card"><div class="card-title">Weekly Decision Trend</div>', unsafe_allow_html=True)
        trend_df = pd.DataFrame({"Week":weeks,"Approved":approved_weekly,"Rejected":rejected_weekly}).set_index("Week")
        st.bar_chart(trend_df, color=["#34D399","#EF4444"], height=200)
        st.markdown("</div>", unsafe_allow_html=True)
    with r3r:
        st.markdown('<div class="card"><div class="card-title">Loan Type Breakdown</div>', unsafe_allow_html=True)
        total_loans = sum(loan_data.values())
        loan_colors = {"Personal":"#3B82F6","MSME":"#8B5CF6"}
        for lt,count in loan_data.items():
            pct   = round(count/total_loans*100,1)
            color = loan_colors[lt]
            st.markdown(f'<div style="margin-bottom:16px;"><div style="display:flex;justify-content:space-between;margin-bottom:5px;"><span style="font-size:13px;color:#FFFFFF;font-weight:500;">{lt}</span><span style="font-size:13px;color:{color};font-weight:600;">{count} <span style="color:#4B5563;font-weight:400;">({pct}%)</span></span></div><div style="background:#2A2D3E;border-radius:4px;height:8px;overflow:hidden;"><div style="width:{pct}%;height:100%;background:{color};border-radius:4px;"></div></div></div>', unsafe_allow_html=True)
        st.markdown('<div style="margin-top:20px;padding-top:16px;border-top:1px solid #2A2D3E;"><div style="font-size:11px;color:#6B7280;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">MSME Fraud Rate</div><div style="font-size:24px;font-weight:700;color:#F87171;">31.1%</div><div style="font-size:11px;color:#6B7280;margin-top:2px;">vs 18.5% for Personal loans</div></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PAGE: SETTINGS
# ==========================================

def page_settings():
    user     = st.session_state.user
    is_admin = user["role"] == "Admin"

    st.markdown('<div class="page-title">System Settings</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">Logged in as <strong style="color:#3B82F6">{user["name"]}</strong> · <span style="color:{"#34D399" if is_admin else "#FBB824"}">{"Admin" if is_admin else "Loan Officer"}</span></div>', unsafe_allow_html=True)

    # Tab visibility: Loan Officers only see tabs 1 & 2 (read-only) and tab 4 (read-only)
    # Tab 3 (User Mgmt) is Admin-only entirely
    if is_admin:
        tab1, tab2, tab3, tab4 = st.tabs(["Module Configuration","Scoring Weights"," User Management","Application Settings"])
    else:
        tab1, tab2, tab4 = st.tabs(["Module Configuration"," Scoring Weights","Application Settings"])
        tab3 = None  # not shown to officer

    # ---- TAB 1: MODULE CONFIGURATION ----
    with tab1:
        if not is_admin:
            st.markdown('<div class="warning-banner">Module configuration is read-only for Loan Officers. Contact an Admin to make changes.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-banner">Disabling a module removes it from analysis and redistributes its weight to remaining active modules.</div>', unsafe_allow_html=True)

        modules = [
            ("KYC Verification","Analyzes KYC video for AI-generated or synthetic faces",True),
            ("Document Correlation","Cross-checks financial documents for inconsistencies and forgery",True),
            ("Ghost Borrower Detection","Validates MSME business existence via GST and MCA signals",True),
            ("Fraud Graph Intelligence","Detects hidden connections between applications and known fraud entities",True),
        ]
        for name,desc,default in modules:
            col_info,col_toggle = st.columns([4,1])
            with col_info:
                st.markdown(f'<div style="padding:4px 0"><div style="font-size:13px;font-weight:500;color:#FFFFFF;"> &nbsp;{name}</div><div style="font-size:12px;color:#6B7280;margin-top:3px;">{desc}</div></div>', unsafe_allow_html=True)
            with col_toggle:
                st.toggle("", value=default, key=f"toggle_{name}", disabled=not is_admin)
            st.markdown("<div style='border-bottom:1px solid #1E2130;margin:8px 0'></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Detection Thresholds</div>', unsafe_allow_html=True)
        t1,t2 = st.columns(2)
        with t1:
            st.number_input("Deepfake confidence threshold (%)", min_value=50, max_value=99, value=75, step=1, disabled=not is_admin)
            st.number_input("Income mismatch threshold (%)",     min_value=5,  max_value=50, value=20, step=5, disabled=not is_admin)
        with t2:
            st.number_input("Ghost borrower flag threshold (flags)", min_value=1, max_value=8, value=3, step=1, disabled=not is_admin)
            st.number_input("Fraud graph hop limit",                 min_value=1, max_value=5, value=2, step=1, disabled=not is_admin)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if is_admin:
            if st.button("Save Module Configuration", key="save_modules"):
                st.success("Module configuration saved successfully.")
        else:
            st.markdown('<div style="font-size:12px;color:#4B5563;font-style:italic;margin-top:8px;">Admin access required to save changes</div>', unsafe_allow_html=True)

    # ---- TAB 2: SCORING WEIGHTS ----
    with tab2:
        if not is_admin:
            st.markdown('<div class="warning-banner">Scoring weights are read-only for Loan Officers. Contact an Admin to make changes.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-banner">Weights must sum to 100% for each loan type. Adjust based on your bank\'s risk priorities.</div>', unsafe_allow_html=True)

        w1,w2 = st.columns(2)
        with w1:
            st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Personal Loan Weights</div>', unsafe_allow_html=True)
            p_kyc  = st.slider("KYC Verification",      0,100,35,key="p_kyc",   disabled=not is_admin)
            p_doc  = st.slider("Document Correlation",   0,100,40,key="p_doc",   disabled=not is_admin)
            p_graph= st.slider("Fraud Graph",            0,100,25,key="p_graph", disabled=not is_admin)
            p_total= p_kyc+p_doc+p_graph
            p_color= "#34D399" if p_total==100 else "#F87171"
            st.markdown(f'<div style="margin-top:12px;padding:12px 16px;background:#0F1117;border-radius:8px;border:1px solid {"rgba(52,211,153,0.3)" if p_total==100 else "rgba(248,113,113,0.3)"};display:flex;justify-content:space-between;align-items:center;"><span style="font-size:12px;color:#6B7280;">Total Weight</span><span style="font-size:16px;font-weight:700;color:{p_color};">{p_total}%</span></div>', unsafe_allow_html=True)
        with w2:
            st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">MSME Loan Weights</div>', unsafe_allow_html=True)
            m_kyc  = st.slider("KYC Verification",          0,100,20,key="m_kyc",   disabled=not is_admin)
            m_doc  = st.slider("Document Correlation",       0,100,25,key="m_doc",   disabled=not is_admin)
            m_ghost= st.slider("Ghost Borrower Detection",   0,100,30,key="m_ghost", disabled=not is_admin)
            m_graph= st.slider("Fraud Graph",                0,100,25,key="m_graph", disabled=not is_admin)
            m_total= m_kyc+m_doc+m_ghost+m_graph
            m_color= "#34D399" if m_total==100 else "#F87171"
            st.markdown(f'<div style="margin-top:12px;padding:12px 16px;background:#0F1117;border-radius:8px;border:1px solid {"rgba(52,211,153,0.3)" if m_total==100 else "rgba(248,113,113,0.3)"};display:flex;justify-content:space-between;align-items:center;"><span style="font-size:12px;color:#6B7280;">Total Weight</span><span style="font-size:16px;font-weight:700;color:{m_color};">{m_total}%</span></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Risk Tier Thresholds</div>', unsafe_allow_html=True)
        r1,r2,r3,r4 = st.columns(4)
        with r1:
            st.markdown('<div style="font-size:11px;color:#34D399;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">LOW RISK</div>', unsafe_allow_html=True)
            st.number_input("Min score",min_value=50,max_value=100,value=75,key="low_min",  disabled=not is_admin)
        with r2:
            st.markdown('<div style="font-size:11px;color:#FBB824;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">MEDIUM RISK</div>', unsafe_allow_html=True)
            st.number_input("Min score",min_value=25,max_value=74, value=50,key="med_min",  disabled=not is_admin)
        with r3:
            st.markdown('<div style="font-size:11px;color:#F87171;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">HIGH RISK</div>', unsafe_allow_html=True)
            st.number_input("Min score",min_value=10,max_value=49, value=25,key="high_min", disabled=not is_admin)
        with r4:
            st.markdown('<div style="font-size:11px;color:#EF4444;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;">REJECT</div>', unsafe_allow_html=True)
            st.number_input("Max score",min_value=0, max_value=24, value=24,key="reject_max",disabled=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if is_admin:
            if st.button("Save Scoring Configuration", key="save_weights"):
                if p_total==100 and m_total==100: st.success("Scoring weights saved successfully.")
                else: st.error("Please ensure all weights sum to 100% before saving.")
        else:
            st.markdown('<div style="font-size:12px;color:#4B5563;font-style:italic;margin-top:8px;">Admin access required to save changes</div>', unsafe_allow_html=True)

    # ---- TAB 3: USER MANAGEMENT (Admin only) ----
    if is_admin and tab3 is not None:
        with tab3:
            # Initialise managed user list in session state
            if "managed_users" not in st.session_state:
                st.session_state.managed_users = [
                    {"name":"Rajesh Kumar",  "role":"Admin",       "email":"rajesh@sentinel.bank",  "active":True},
                    {"name":"Priya Mehta",   "role":"Loan Officer","email":"priya@sentinel.bank",   "active":True},
                    {"name":"Amit Verma",    "role":"Loan Officer","email":"amit@sentinel.bank",    "active":True},
                    {"name":"Sneha Iyer",    "role":"Loan Officer","email":"sneha@sentinel.bank",   "active":False},
                ]

            st.markdown(f'<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;">Current Users <span style="font-size:12px;color:#6B7280;font-weight:400;">({len(st.session_state.managed_users)} total)</span></div>', unsafe_allow_html=True)

            for i, u in enumerate(st.session_state.managed_users):
                sc = "user-status-active" if u["active"] else "user-status-inactive"
                role_color = "#3B82F6" if u["role"]=="Admin" else "#9CA3AF"
                col_card, col_toggle_btn = st.columns([5, 1])
                with col_card:
                    st.markdown(f'<div class="user-row"><div class="user-avatar">👤</div><div><div class="user-name">{u["name"]} <span style="font-size:11px;color:{role_color};background:rgba(59,130,246,0.1);padding:2px 7px;border-radius:8px;margin-left:6px;">{u["role"]}</span></div><div class="user-role">{u["email"]}</div></div><div class="{sc}">{"Active" if u["active"] else "Inactive"}</div></div>', unsafe_allow_html=True)
                with col_toggle_btn:
                    btn_label = "Deactivate" if u["active"] else "Activate"
                    if st.button(btn_label, key=f"toggle_user_{i}"):
                        st.session_state.managed_users[i]["active"] = not u["active"]
                        st.rerun()

            st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
            st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Add New User</div>', unsafe_allow_html=True)

            n1,n2 = st.columns(2)
            with n1:
                new_name  = st.text_input("Full Name",      placeholder="e.g. Rahul Sharma",        key="new_user_name")
                new_email = st.text_input("Email Address",  placeholder="e.g. rahul@sentinel.bank", key="new_user_email")
            with n2:
                new_role  = st.selectbox("Role", ["Loan Officer","Admin"], key="new_user_role")
                new_pass  = st.text_input("Temporary Password", type="password", placeholder="Min 8 characters", key="new_user_pass")

            if st.button("Add User", key="add_user"):
                if new_name and new_email and new_pass:
                    # Check for duplicate email
                    existing_emails = [u["email"] for u in st.session_state.managed_users]
                    if new_email in existing_emails:
                        st.error(f"A user with email {new_email} already exists.")
                    elif len(new_pass) < 8:
                        st.error("Password must be at least 8 characters.")
                    else:
                        st.session_state.managed_users.append({
                            "name": new_name, "role": new_role,
                            "email": new_email, "active": True
                        })
                        st.success(f"{new_name} added as {new_role}. They can now log in with the temporary password.")
                        st.rerun()
                else:
                    st.error("Please fill all fields.")

    # ---- TAB 4: APPLICATION SETTINGS ----
    with tab4:
        if not is_admin:
            st.markdown('<div class="warning-banner">Application settings are read-only for Loan Officers. Contact an Admin to make changes.</div>', unsafe_allow_html=True)

        st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Loan Configuration</div>', unsafe_allow_html=True)
        a1,a2 = st.columns(2)
        with a1:
            st.number_input("Minimum Loan Amount (₹ Lakhs)",   min_value=1,  max_value=10,  value=1,   key="min_loan",    disabled=not is_admin)
            st.number_input("Maximum Personal Loan (₹ Lakhs)", min_value=10, max_value=100, value=50,  key="max_personal", disabled=not is_admin)
            st.number_input("Maximum MSME Loan (₹ Lakhs)",     min_value=10, max_value=500, value=200, key="max_msme",     disabled=not is_admin)
        with a2:
            st.number_input("KYC Video Max Duration (seconds)", min_value=10, max_value=60,  value=30,  key="kyc_duration", disabled=not is_admin)
            st.number_input("KYC Video Max File Size (MB)",      min_value=10, max_value=100, value=50,  key="kyc_size",     disabled=not is_admin)
            st.number_input("Application Expiry (days)",         min_value=7,  max_value=90,  value=30,  key="app_expiry",   disabled=not is_admin)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown('<div style="font-size:13px;font-weight:600;color:#FFFFFF;margin-bottom:16px;padding-bottom:10px;border-bottom:1px solid #2A2D3E;">Required Documents</div>', unsafe_allow_html=True)
        d1,d2 = st.columns(2)
        with d1:
            st.markdown('<div style="font-size:12px;color:#3B82F6;font-weight:600;margin-bottom:10px;">Personal Loan</div>', unsafe_allow_html=True)
            st.toggle("Salary Slip",               value=True,  key="doc_salary_personal", disabled=not is_admin)
            st.toggle("ITR Acknowledgement",        value=True,  key="doc_itr_personal",    disabled=not is_admin)
            st.toggle("Bank Statement (6 months)", value=True,  key="doc_bank_personal",   disabled=not is_admin)
            st.toggle("Aadhaar Card",              value=True,  key="doc_aadhaar_personal", disabled=not is_admin)
            st.toggle("PAN Card",                  value=True,  key="doc_pan_personal",    disabled=not is_admin)
        with d2:
            st.markdown('<div style="font-size:12px;color:#8B5CF6;font-weight:600;margin-bottom:10px;">MSME Loan</div>', unsafe_allow_html=True)
            st.toggle("GST Certificate",           value=True,  key="doc_gst_msme",     disabled=not is_admin)
            st.toggle("Business Registration",     value=True,  key="doc_reg_msme",     disabled=not is_admin)
            st.toggle("ITR (Business)",            value=True,  key="doc_itr_msme",     disabled=not is_admin)
            st.toggle("Bank Statement (6 months)", value=True,  key="doc_bank_msme",    disabled=not is_admin)
            st.toggle("Property Papers",           value=False, key="doc_property_msme",disabled=not is_admin)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if is_admin:
            if st.button("Save Application Settings", key="save_app_settings"):
                st.success("Application settings saved successfully.")
        else:
            st.markdown('<div style="font-size:12px;color:#4B5563;font-style:italic;margin-top:8px;">Admin access required to save changes</div>', unsafe_allow_html=True)

# ==========================================
# ROUTER
# ==========================================

if not st.session_state.authenticated:
    page_login()
else:
    render_sidebar()
    page = st.session_state.page

    if page == "dashboard":
        page_dashboard()
    elif page == "applications":
        page_applications()
    elif page == "application_detail":
        page_application_detail()
    elif page == "new_application":
        page_new_application()
    elif page == "analytics":
        page_analytics()
    elif page == "settings":
        page_settings()
    else:
        page_dashboard()
