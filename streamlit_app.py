import streamlit as st
import tempfile
import pandas as pd
import hashlib
from main import run_pipeline
from tools.analytics_tool import plot_correlation_heatmap

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Analyst AI Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

DEMO_USER = "admin"
DEMO_PASS = hash_password("1234")

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">

<style>

/* ── Tokens ── */
:root {
  --bg:      #0a0f1e;
  --bg2:     #0f1629;
  --bg3:     #131d35;
  --surface: rgba(255,255,255,0.05);
  --border:  rgba(255,255,255,0.09);
  --border2: rgba(255,255,255,0.16);
  --blue:    #3b82f6;
  --green:   #10b981;
  --purple:  #8b5cf6;
  --orange:  #f59e0b;
  --text:    #f1f5f9;
  --text2:   #cbd5e1;
  --text3:   #94a3b8;
  --text4:   #64748b;
  --font:    'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --mono:    'JetBrains Mono', monospace;
}

/* ── Reset Streamlit shell ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stSidebar"]    { display: none !important; }
#MainMenu, footer            { visibility: hidden !important; }
[data-testid="stAppViewContainer"] > .main > .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar             { width: 5px; }
::-webkit-scrollbar-track       { background: var(--bg); }
::-webkit-scrollbar-thumb       { background: rgba(59,130,246,0.4); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue); }

/* ── Pulsing live dot ── */
@keyframes blink {
  0%,100% { opacity:1; box-shadow:0 0 0 0 rgba(16,185,129,0.5); }
  50%     { opacity:0.6; box-shadow:0 0 0 5px rgba(16,185,129,0); }
}

/* ══════════════════════════════
   NAVBAR
══════════════════════════════ */
.da-nav {
  position: sticky; top: 0; z-index: 500;
  height: 64px; padding: 0 40px;
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(10,15,30,0.94);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border);
}
.da-logo {
  display: flex; align-items: center; gap: 10px;
  font-size: 16px; font-weight: 700; color: var(--text);
  letter-spacing: -0.3px;
}
.da-logo-box {
  width: 30px; height: 30px;
  background: linear-gradient(135deg, var(--blue), var(--purple));
  border-radius: 7px;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; line-height: 1;
}
.da-live-dot {
  width: 7px; height: 7px;
  background: var(--green);
  border-radius: 50%;
  animation: blink 2s ease-in-out infinite;
  flex-shrink: 0;
}
.da-nav-pill {
  font-size: 11px; font-weight: 600; padding: 4px 12px;
  border-radius: 20px; background: rgba(59,130,246,0.10);
  color: #93c5fd; border: 1px solid rgba(59,130,246,0.22);
  letter-spacing: 0.4px; white-space: nowrap;
}

/* Nav login button */
.nav-login-btn .stButton > button {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  color: #fff !important; font-family: var(--font) !important;
  font-weight: 600 !important; font-size: 14px !important;
  border: none !important; border-radius: 8px !important;
  padding: 0 20px !important; height: 36px !important;
  width: auto !important; cursor: pointer !important;
  transition: all 0.2s !important; letter-spacing: -0.2px !important;
}
.nav-login-btn .stButton > button:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 20px rgba(59,130,246,0.38) !important;
}

/* ══════════════════════════════
   HERO
══════════════════════════════ */
.da-hero {
  padding: 96px 48px 72px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.da-hero::before {
  content: '';
  position: absolute; top: -180px; left: 50%;
  transform: translateX(-50%);
  width: 900px; height: 600px;
  background: radial-gradient(ellipse, rgba(59,130,246,0.09) 0%, rgba(139,92,246,0.05) 45%, transparent 70%);
  pointer-events: none; z-index: 0;
}
.da-hero > * { position: relative; z-index: 1; }

.da-chip {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 16px; border-radius: 20px;
  background: rgba(16,185,129,0.09);
  border: 1px solid rgba(16,185,129,0.22);
  font-size: 11px; font-weight: 700; color: #34d399;
  letter-spacing: 1px; text-transform: uppercase;
  margin-bottom: 28px;
}
.da-h1 {
  font-size: clamp(38px, 5.5vw, 68px);
  font-weight: 800; line-height: 1.06;
  letter-spacing: -2.5px; color: var(--text);
  margin-bottom: 10px;
}
.da-h1 .grad {
  background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.da-hero-sub {
  font-size: 17px; font-weight: 400; color: var(--text3);
  line-height: 1.75; max-width: 560px;
  margin: 0 auto 44px;
  text-align: center;
}

/* CTA buttons */
.cta-primary .stButton > button {
  background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
  color: #fff !important; font-family: var(--font) !important;
  font-weight: 700 !important; font-size: 15px !important;
  border: none !important; border-radius: 10px !important;
  height: 50px !important; padding: 0 34px !important;
  width: auto !important; cursor: pointer !important;
  transition: all 0.2s !important; letter-spacing: -0.3px !important;
}
.cta-primary .stButton > button:hover {
  background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 14px 36px rgba(59,130,246,0.42) !important;
}
.cta-secondary .stButton > button {
  background: transparent !important; color: var(--text3) !important;
  font-family: var(--font) !important; font-weight: 500 !important;
  font-size: 15px !important; border: 1px solid var(--border2) !important;
  border-radius: 10px !important; height: 50px !important;
  padding: 0 28px !important; width: auto !important;
  cursor: pointer !important; transition: all 0.2s !important;
}
.cta-secondary .stButton > button:hover {
  border-color: rgba(255,255,255,0.28) !important;
  color: var(--text) !important;
  transform: translateY(-2px) !important;
}

/* ══════════════════════════════
   STATS BAR
══════════════════════════════ */
.da-stats-bar {
  display: flex; justify-content: center;
  margin: 0 48px;
  border: 1px solid var(--border);
  border-radius: 14px; overflow: hidden;
  background: var(--bg2);
}
.da-stat-item {
  flex: 1; padding: 26px 24px; text-align: center;
  border-right: 1px solid var(--border);
  transition: background 0.2s;
}
.da-stat-item:last-child { border-right: none; }
.da-stat-item:hover      { background: rgba(255,255,255,0.04); }
.da-stat-num {
  font-size: 28px; font-weight: 800; line-height: 1;
  margin-bottom: 5px; letter-spacing: -0.8px;
}
.blue-text   { color: #60a5fa; }
.green-text  { color: #34d399; }
.purple-text { color: #a78bfa; }
.orange-text { color: #fbbf24; }
.da-stat-label {
  font-size: 11px; font-weight: 600;
  color: var(--text4); text-transform: uppercase; letter-spacing: 0.7px;
}

/* ══════════════════════════════
   DIVIDER
══════════════════════════════ */
.da-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--border), transparent);
  margin: 0 48px;
}

/* ══════════════════════════════
   SECTION WRAPPER
══════════════════════════════ */
.sec { padding: 72px 48px 56px; max-width: 1160px; margin: 0 auto; }
.sec-eye   { font-size:11px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:var(--blue); margin-bottom:12px; }
.sec-title { font-size:clamp(24px,3.5vw,38px); font-weight:800; color:var(--text); letter-spacing:-1.3px; line-height:1.15; margin-bottom:44px; max-width:520px; }
.sec-title-center { max-width:none; text-align:center; }

/* ══════════════════════════════
   FEATURE CARDS
══════════════════════════════ */
.feat-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:14px; }
.feat-card {
  background: var(--bg2); border:1px solid var(--border); border-radius:14px;
  padding:30px; position:relative; overflow:hidden;
  transition: border-color 0.2s, transform 0.2s;
}
.feat-card:hover { border-color:var(--border2); transform:translateY(-2px); }
.feat-card-num {
  position:absolute; top:20px; right:24px;
  font-size:48px; font-weight:800; color:rgba(255,255,255,0.025);
  font-family:var(--mono); line-height:1; user-select:none;
}
.feat-icon {
  width:42px; height:42px; border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  font-size:19px; margin-bottom:16px;
}
.feat-icon.b { background:rgba(59,130,246,0.12); }
.feat-icon.p { background:rgba(139,92,246,0.12); }
.feat-icon.g { background:rgba(16,185,129,0.12); }
.feat-icon.o { background:rgba(245,158,11,0.12); }
.feat-title { font-size:16px; font-weight:700; color:var(--text); margin-bottom:9px; letter-spacing:-0.3px; }
.feat-desc  { font-size:14px; font-weight:400; color:var(--text3); line-height:1.72; }

/* ══════════════════════════════
   AGENT CREW CARDS
══════════════════════════════ */
.crew-grid { display:flex; gap:14px; }
.crew-card {
  flex:1; background:var(--bg2); border:1px solid var(--border);
  border-radius:14px; padding:26px;
  transition:border-color 0.2s, transform 0.2s;
}
.crew-card:hover { border-color:var(--border2); transform:translateY(-2px); }
.crew-emoji { font-size:28px; margin-bottom:12px; }
.crew-tag   { font-size:11px; font-weight:700; color:var(--blue); text-transform:uppercase; letter-spacing:0.6px; margin-bottom:5px; }
.crew-name  { font-size:16px; font-weight:700; color:var(--text); margin-bottom:9px; letter-spacing:-0.3px; }
.crew-desc  { font-size:13px; color:var(--text3); line-height:1.68; }

/* ══════════════════════════════
   WORKFLOW STEPS
══════════════════════════════ */
.steps-wrap { padding:0 48px 72px; max-width:1160px; margin:0 auto; }
.steps-row  { display:flex; position:relative; }
.steps-row::before {
  content:''; position:absolute; top:23px; left:40px; right:40px; height:1px;
  background:linear-gradient(90deg,var(--blue),var(--purple),var(--green)); z-index:0;
}
.step { flex:1; display:flex; flex-direction:column; align-items:center; text-align:center; gap:12px; position:relative; z-index:1; }
.step-circle {
  width:46px; height:46px; border-radius:50%; background:var(--bg);
  border:2px solid var(--blue);
  display:flex; align-items:center; justify-content:center;
  font-size:14px; font-weight:700; color:var(--blue);
}
.step:nth-child(2) .step-circle { border-color:var(--purple); color:var(--purple); }
.step:nth-child(3) .step-circle { border-color:var(--green);  color:var(--green); }
.step:nth-child(4) .step-circle { border-color:var(--orange); color:var(--orange); }
.step-title { font-size:14px; font-weight:700; color:var(--text); }
.step-desc  { font-size:12px; color:var(--text3); line-height:1.65; max-width:130px; }

/* ══════════════════════════════
   TECH BADGES
══════════════════════════════ */
.badges { display:flex; flex-wrap:wrap; gap:10px; justify-content:center; padding:0 48px 72px; }
.badge {
  padding:8px 18px; border-radius:8px; font-size:13px; font-weight:600;
  color:var(--text2); background:var(--bg2); border:1px solid var(--border);
  transition:all 0.18s;
}
.badge:hover { border-color:var(--blue); color:var(--text); background:rgba(59,130,246,0.07); }

/* ══════════════════════════════
   FOOTER
══════════════════════════════ */
.da-footer {
  padding:26px 48px; border-top:1px solid var(--border);
  display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-top:32px;
}
.foot-text { font-size:13px; color:var(--text4); }

/* ══════════════════════════════
   LOGIN PAGE
══════════════════════════════ */
.login-wrap { min-height:100vh; display:flex; align-items:center; justify-content:center; padding:24px; }
.login-card {
  width:100%; max-width:410px;
  background:var(--bg2); border:1px solid var(--border2);
  border-radius:18px; padding:42px 38px; position:relative; overflow:hidden;
}
.login-card::before {
  content:''; position:absolute; top:0; left:20%; right:20%; height:1px;
  background:linear-gradient(90deg,transparent,var(--blue),transparent);
}
.login-emoji { font-size:32px; margin-bottom:14px; }
.login-title { font-size:22px; font-weight:800; color:var(--text); letter-spacing:-0.7px; margin-bottom:6px; }
.login-sub   { font-size:13px; color:var(--text3); margin-bottom:28px; line-height:1.55; }
.login-hint  { text-align:center; font-size:12px; color:var(--text4); margin-top:14px; }
.login-hint b{ color:#60a5fa; font-weight:600; }

/* Input styles inside login */
.login-card [data-testid="stTextInput"] input {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 9px !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
  font-size: 14px !important;
  transition: border-color 0.2s, box-shadow 0.2s !important;
}
.login-card [data-testid="stTextInput"] input:focus {
  border-color: rgba(59,130,246,0.6) !important;
  box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
}
.login-card [data-testid="stTextInput"] input::placeholder { color: var(--text4) !important; }
.login-card label {
  color: var(--text3) !important; font-size: 11px !important;
  font-weight: 700 !important; letter-spacing: 0.7px !important; text-transform: uppercase !important;
}

.submit-btn .stButton > button {
  width:100% !important; height:48px !important;
  background:linear-gradient(135deg,#3b82f6,#2563eb) !important;
  color:#fff !important; font-family:var(--font) !important;
  font-weight:700 !important; font-size:15px !important;
  border:none !important; border-radius:9px !important;
  cursor:pointer !important; transition:all 0.2s !important; letter-spacing:-0.2px !important;
}
.submit-btn .stButton > button:hover {
  transform:translateY(-1px) !important;
  box-shadow:0 10px 28px rgba(59,130,246,0.38) !important;
}
.back-btn .stButton > button {
  width:100% !important; height:38px !important;
  background:transparent !important; color:var(--text3) !important;
  border:1px solid var(--border) !important; border-radius:8px !important;
  font-size:13px !important; font-weight:500 !important; font-family:var(--font) !important;
  cursor:pointer !important; transition:all 0.2s !important;
}
.back-btn .stButton > button:hover { border-color:var(--border2) !important; color:var(--text) !important; }

/* Alert */
[data-testid="stAlert"] { border-radius:10px !important; font-family:var(--font) !important; font-size:14px !important; }

/* ══════════════════════════════
   DASHBOARD
══════════════════════════════ */
.dash-nav {
  position:sticky; top:0; z-index:500; height:60px; padding:0 36px;
  display:flex; align-items:center; justify-content:space-between;
  background:rgba(10,15,30,0.95); backdrop-filter:blur(20px);
  border-bottom:1px solid var(--border);
}
.dash-title { font-size:15px; font-weight:700; color:var(--text); letter-spacing:-0.3px; display:flex; align-items:center; gap:8px; }
.dash-sub   { font-size:12px; color:var(--text4); margin-top:1px; }

.logout-btn .stButton > button {
  width:auto !important; height:34px !important; padding:0 16px !important;
  background:transparent !important; color:var(--text3) !important;
  border:1px solid var(--border) !important; border-radius:7px !important;
  font-size:13px !important; font-weight:500 !important; font-family:var(--font) !important;
  cursor:pointer !important; transition:all 0.2s !important;
}
.logout-btn .stButton > button:hover { border-color:rgba(239,68,68,0.4) !important; color:#f87171 !important; }

/* Metrics */
[data-testid="stMetric"] {
  background:var(--bg2) !important; border:1px solid var(--border) !important;
  border-radius:12px !important; padding:20px 22px !important;
  transition:border-color 0.2s !important;
}
[data-testid="stMetric"]:hover { border-color:var(--border2) !important; }
[data-testid="stMetricValue"] {
  font-family:var(--font) !important; font-size:26px !important;
  font-weight:800 !important; color:var(--text) !important; letter-spacing:-0.7px !important;
}
[data-testid="stMetricLabel"] {
  font-family:var(--font) !important; font-size:11px !important;
  font-weight:600 !important; color:var(--text4) !important;
  text-transform:uppercase !important; letter-spacing:0.6px !important;
}

/* File uploader */
[data-testid="stFileUploader"] > div {
  background:rgba(59,130,246,0.04) !important;
  border:2px dashed rgba(59,130,246,0.26) !important;
  border-radius:12px !important; transition:all 0.2s !important;
}
[data-testid="stFileUploader"] > div:hover {
  border-color:rgba(59,130,246,0.52) !important;
  background:rgba(59,130,246,0.07) !important;
}
[data-testid="stFileUploader"] label { color:var(--text3) !important; font-family:var(--font) !important; }

/* Dashboard section heading */
.dash-sec {
  font-size:15px; font-weight:700; color:var(--text); letter-spacing:-0.3px;
  padding-bottom:14px; margin-bottom:18px; border-bottom:1px solid var(--border);
  display:flex; align-items:center; gap:8px;
}

/* Result card */
.res-card {
  background:var(--bg2); border:1px solid var(--border); border-radius:13px;
  padding:22px 26px; margin-bottom:14px; transition:border-color 0.2s;
}
.res-card:hover { border-color:var(--border2); }
.res-label {
  font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.7px;
  color:var(--text4); margin-bottom:13px; display:flex; align-items:center; gap:7px;
}

/* Make markdown output readable */
.res-card p, .res-card li { color:var(--text2) !important; font-size:14px !important; line-height:1.75 !important; }
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li  { color:var(--text2) !important; font-size:14px !important; line-height:1.75 !important; }
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3  { color:var(--text) !important; font-family:var(--font) !important; letter-spacing:-0.5px !important; }
[data-testid="stMarkdownContainer"] strong { color:var(--text) !important; }
[data-testid="stMarkdownContainer"] code  { background:rgba(255,255,255,0.07) !important; color:#93c5fd !important; font-family:var(--mono) !important; border-radius:4px !important; padding:1px 6px !important; }

/* Spinner */
.stSpinner > div { border-top-color:var(--blue) !important; }

/* Download button */
.dl-btn .stDownloadButton > button {
  background:transparent !important; color:#60a5fa !important;
  border:1px solid rgba(59,130,246,0.35) !important; border-radius:9px !important;
  font-family:var(--font) !important; font-weight:600 !important; font-size:14px !important;
  height:42px !important; padding:0 24px !important; cursor:pointer !important; transition:all 0.2s !important;
}
.dl-btn .stDownloadButton > button:hover {
  background:rgba(59,130,246,0.09) !important; border-color:var(--blue) !important;
}

/* Images */
[data-testid="stImage"] img { border-radius:12px !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius:11px !important; overflow:hidden; }

/* Empty state */
.empty-state {
  text-align:center; padding:64px 32px;
  border:2px dashed rgba(59,130,246,0.18); border-radius:14px;
  background:rgba(59,130,246,0.02); max-width:500px; margin:28px auto;
}
.empty-icon  { font-size:44px; margin-bottom:16px; opacity:0.55; }
.empty-title { font-size:19px; font-weight:700; color:var(--text); margin-bottom:9px; letter-spacing:-0.3px; }
.empty-sub   { font-size:14px; color:var(--text3); line-height:1.7; }

/* Responsive */
@media (max-width:768px) {
  .da-nav, .dash-nav      { padding:0 18px; }
  .da-hero                { padding:60px 18px 48px; }
  .da-h1                  { letter-spacing:-1.5px; }
  .feat-grid              { grid-template-columns:1fr; }
  .steps-row::before      { display:none; }
  .steps-row              { flex-direction:column; align-items:center; gap:24px; }
  .crew-grid              { flex-direction:column; }
  .sec, .steps-wrap, .badges { padding-left:18px; padding-right:18px; }
  .da-stats-bar           { flex-direction:column; margin:0 18px; border-radius:12px; }
  .da-stat-item           { border-right:none !important; border-bottom:1px solid var(--border); }
  .da-stat-item:last-child{ border-bottom:none; }
  .da-divider, .da-footer { margin-left:18px; margin-right:18px; }
}
</style>
"""

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def inject():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def html(code):
    st.markdown(code, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════
def page_landing():
    inject()

    # ── Navbar ──
    nav_l, nav_r = st.columns([5, 1])
    with nav_l:
        html("""
        <div class="da-nav">
          <div class="da-logo">
            <div class="da-logo-box">📊</div>
            Data Analyst AI Agent
            <div class="da-live-dot"></div>
          </div>
          <div class="da-nav-pill">Powered by CrewAI</div>
        </div>
        """)
    with nav_r:
        html('<div class="da-nav" style="justify-content:flex-end;padding-right:28px;">')
        html('<div class="nav-login-btn">')
        if st.button("Login →", key="nav_login"):
            st.session_state.page = "login"
            st.rerun()
        html('</div></div>')

    # ── Hero ──
    html("""
    <div class="da-hero">
      <div class="da-chip">
        <div class="da-live-dot"></div>
        Multi-Agent AI · Built with CrewAI · Automated EDA
      </div>
      <div class="da-h1">
        Automated Data Analysis<br/>
        <span class="grad">Powered by AI Agents</span>
      </div>
      <p class="da-hero-sub" style="text-align:center;margin-left:auto;margin-right:auto;">
        Upload any CSV and a specialized crew of AI agents will automatically
        compute statistics, generate smart analytical questions, create visualizations,
        and produce business-ready summaries — end to end.
      </p>
    </div>
    """)

    _, c1, g, c2, _ = st.columns([2.6, 1.0, 0.18, 1.1, 2.6])
    with c1:
        html('<div class="cta-primary">')
        if st.button("🚀  Start Analyzing", key="hero_cta"):
            st.session_state.page = "login"
            st.rerun()
        html('</div>')
    with c2:
        html('<div class="cta-secondary">')
        if st.button("Learn More ↓", key="hero_learn"):
            pass
        html('</div>')

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Stats bar ──
    html("""
    <div class="da-stats-bar">
      <div class="da-stat-item">
        <div class="da-stat-num blue-text">3</div>
        <div class="da-stat-label">Specialized AI Agents</div>
      </div>
      <div class="da-stat-item">
        <div class="da-stat-num green-text">&lt;60s</div>
        <div class="da-stat-label">Full EDA Runtime</div>
      </div>
      <div class="da-stat-item">
        <div class="da-stat-num purple-text">Auto</div>
        <div class="da-stat-label">Chart Generation</div>
      </div>
      <div class="da-stat-item">
        <div class="da-stat-num orange-text">0</div>
        <div class="da-stat-label">Code Required</div>
      </div>
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    html('<div class="da-divider"></div>')

    # ── Capabilities ──
    html("""
    <div class="sec">
      <div class="sec-eye">Core Capabilities</div>
      <div class="sec-title">What the Agent Does For You</div>
      <div class="feat-grid">
        <div class="feat-card">
          <div class="feat-card-num">01</div>
          <div class="feat-icon b">📊</div>
          <div class="feat-title">Descriptive Statistics</div>
          <div class="feat-desc">Automatically reads your dataset and computes shape, data types, missing values, distributions, and statistical summaries — without writing a single line of code.</div>
        </div>
        <div class="feat-card">
          <div class="feat-card-num">02</div>
          <div class="feat-icon p">🤔</div>
          <div class="feat-title">AI-Generated Questions</div>
          <div class="feat-desc">Based on column metadata, the agent generates smart EDA questions — guiding the analysis the same way an experienced data scientist would approach a new dataset.</div>
        </div>
        <div class="feat-card">
          <div class="feat-card-num">03</div>
          <div class="feat-icon g">📈</div>
          <div class="feat-title">Automated Visualizations</div>
          <div class="feat-desc">Generates contextual plots — histograms, scatter plots, correlation heatmaps, and trend charts — for each analytical question, surfacing hidden patterns visually.</div>
        </div>
        <div class="feat-card">
          <div class="feat-card-num">04</div>
          <div class="feat-icon o">📄</div>
          <div class="feat-title">Business-Level Summary</div>
          <div class="feat-desc">Produces plain-language summaries and actionable insights from your data — ready to share directly with stakeholders who don't work with data daily.</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="da-divider"></div>')

    # ── Agent Crew ──
    html("""
    <div class="sec" style="padding-bottom:28px;">
      <div class="sec-eye">The Agent Crew</div>
      <div class="sec-title">Three Agents, One Unified Workflow</div>
    </div>
    <div style="padding:0 48px 64px;max-width:1160px;margin:0 auto;">
      <div class="crew-grid">
        <div class="crew-card">
          <div class="crew-emoji">🔬</div>
          <div class="crew-tag">EDA Crew</div>
          <div class="crew-name">Data Scientist Agent</div>
          <div class="crew-desc">Reads the raw CSV, computes descriptive statistics, detects data types, identifies missing values, and extracts structural metadata to lay the analysis foundation.</div>
        </div>
        <div class="crew-card">
          <div class="crew-emoji">🧠</div>
          <div class="crew-tag">Quest Crew</div>
          <div class="crew-name">Business Consultant Agent</div>
          <div class="crew-desc">Analyzes dataset metadata to generate targeted, high-value analytical questions. Frames EDA in terms of business objectives and helps translate data into decisions.</div>
        </div>
        <div class="crew-card">
          <div class="crew-emoji">📉</div>
          <div class="crew-tag">Junior DA Crew</div>
          <div class="crew-name">Junior Data Analyst Agent</div>
          <div class="crew-desc">Takes the generated questions and produces relevant plots and visual insights — identifying trends, outliers, correlations, and distributions across your dataset.</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="da-divider"></div>')

    # ── How it works ──
    html("""
    <div class="sec" style="padding-bottom:28px;">
      <div class="sec-eye">How It Works</div>
      <div class="sec-title sec-title-center">Four steps from raw data to ready insights</div>
    </div>
    <div class="steps-wrap">
      <div class="steps-row">
        <div class="step">
          <div class="step-circle">1</div>
          <div class="step-title">Upload CSV</div>
          <div class="step-desc">Drop any structured dataset</div>
        </div>
        <div class="step">
          <div class="step-circle">2</div>
          <div class="step-title">Agents Activate</div>
          <div class="step-desc">EDA, Quest & DA crews run in sequence</div>
        </div>
        <div class="step">
          <div class="step-circle">3</div>
          <div class="step-title">Insights Surface</div>
          <div class="step-desc">Stats, questions & charts auto-generated</div>
        </div>
        <div class="step">
          <div class="step-circle">4</div>
          <div class="step-title">Export Report</div>
          <div class="step-desc">Download full AI report as .txt</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="da-divider"></div>')

    # ── Tech stack ──
    html("""
    <div class="sec" style="padding-bottom:28px;text-align:center;">
      <div class="sec-eye">Built With</div>
      <div class="sec-title sec-title-center">Open-source technologies under the hood</div>
    </div>
    """)
    html("""
    <div class="badges">
      <span class="badge">🤖 CrewAI</span>
      <span class="badge">🦜 LangChain</span>
      <span class="badge">🐍 Python</span>
      <span class="badge">🎈 Streamlit</span>
      <span class="badge">🐼 Pandas</span>
      <span class="badge">📊 Matplotlib</span>
      <span class="badge">🔥 Seaborn</span>
      <span class="badge">🧩 GPT-4 / LLM</span>
    </div>
    """)

    # ── Footer ──
    html("""
    <div class="da-footer">
      <div class="da-logo" style="font-size:14px;">
        <div class="da-logo-box" style="width:26px;height:26px;font-size:13px;">📊</div>
        Data Analyst AI Agent
      </div>
      <span class="foot-text">Built with CrewAI · Multi-Agent Automated EDA</span>
      <span class="foot-text">© 2026 · Open Source</span>
    </div>
    """)


# ══════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ══════════════════════════════════════════════════════════════
def page_login():
    inject()

    html("""
    <div class="da-nav">
      <div class="da-logo">
        <div class="da-logo-box">📊</div>
        Data Analyst AI Agent
      </div>
    </div>
    """)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    _, col, _ = st.columns([1.6, 2, 1.6])
    with col:
        html("""
        <div class="login-card">
          <div class="login-emoji">🔐</div>
          <div class="login-title">Welcome back</div>
          <div class="login-sub">Sign in to access the Data Analyst AI Agent and start exploring your datasets with AI.</div>
        """)

        username = st.text_input("USERNAME", placeholder="Enter your username", key="u")
        password = st.text_input("PASSWORD", type="password", placeholder="Enter your password", key="p")

        st.markdown("<br>", unsafe_allow_html=True)
        html('<div class="submit-btn">')
        clicked = st.button("Sign In  →", key="login_btn")
        html('</div>')

        if clicked:
            if username == DEMO_USER and hash_password(password) == DEMO_PASS:
                st.session_state.authenticated = True
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

        html('<div class="login-hint">Demo: <b>admin</b> / <b>1234</b></div>')
        st.markdown("<br>", unsafe_allow_html=True)

        html('<div class="back-btn">')
        if st.button("← Back to Home", key="back"):
            st.session_state.page = "landing"
            st.rerun()
        html('</div></div>')


# ══════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    inject()

    # ── Navbar ──
    nav_l, nav_r = st.columns([5, 1])
    with nav_l:
        html("""
        <div class="dash-nav">
          <div>
            <div class="dash-title">
              <span>📊</span> Data Analyst AI Agent
              <div class="da-live-dot"></div>
            </div>
            <div class="dash-sub">Multi-Agent EDA Platform · CrewAI</div>
          </div>
        </div>
        """)
    with nav_r:
        html('<div class="dash-nav" style="justify-content:flex-end;padding-right:22px;">')
        html('<div class="logout-btn">')
        if st.button("⎋  Logout", key="logout"):
            st.session_state.authenticated = False
            st.session_state.page = "landing"
            st.rerun()
        html('</div></div>')

    st.markdown("<br>", unsafe_allow_html=True)

    _, main, _ = st.columns([0.4, 11.2, 0.4])
    with main:

        # ── Upload ──
        html('<div class="dash-sec">📂 Upload Dataset</div>')
        uploaded_file = st.file_uploader(
            "Drag & drop a CSV file here, or click to browse",
            type=["csv"],
            help="Any structured CSV — the AI agent crew will handle the rest"
        )

        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
                tmp_file.write(uploaded_file.read())
                temp_path = tmp_file.name

            df = pd.read_csv(temp_path)
            numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
            null_pct = round(
                df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 1
            )

            # ── Metrics ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dash-sec">📊 Dataset Overview</div>')
            m1, m2, m3, m4 = st.columns(4)
            with m1: st.metric("Total Rows",      f"{df.shape[0]:,}")
            with m2: st.metric("Total Columns",   df.shape[1])
            with m3: st.metric("Numeric Columns", len(numeric_cols))
            with m4: st.metric("Missing Data",    f"{null_pct}%")

            # ── Preview — direct dataframe, no extra wrapper divs ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dash-sec">🔍 Data Preview</div>')
            st.dataframe(df.head(10), use_container_width=True)

            # ── AI Analysis ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dash-sec">🤖 AI Agent Analysis</div>')

            with st.spinner("🧠 AI Agents are analyzing your dataset — this may take a moment..."):
                output = run_pipeline(temp_path)

            # Summary
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="res-label" style="padding:0 0 10px;">📋 Summary</div>')
            html('<div class="res-card">')
            st.markdown(output["summary"])
            html('</div>')

            st.markdown("<br>", unsafe_allow_html=True)

            # Key Questions + Visualization Suggestions side by side
            q_col, v_col = st.columns(2)
            with q_col:
                html('<div class="res-label" style="padding:0 0 10px;">❓ Key Questions</div>')
                html('<div class="res-card">')
                st.markdown(output["questions"])
                html('</div>')
            with v_col:
                html('<div class="res-label" style="padding:0 0 10px;">📈 Visualization Suggestions</div>')
                html('<div class="res-card">')
                st.markdown(output["visuals"])
                html('</div>')

            # ── Generated Plots — each in its own column block, no deprecated param ──
            if output.get("plots"):
                st.markdown("<br>", unsafe_allow_html=True)
                html('<div class="dash-sec">📊 Generated Plots</div>')
                for plot_path in output["plots"]:
                    p_l, p_m, p_r = st.columns([0.5, 9, 0.5])
                    with p_m:
                        st.image(plot_path, width=820)

            # ── Heatmap ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dash-sec">🔥 Correlation Heatmap</div>')
            heatmap_fig = plot_correlation_heatmap(df)
            if heatmap_fig:
                heatmap_fig.set_size_inches(10, 6)
                h_l, h_m, h_r = st.columns([0.5, 9, 0.5])
                with h_m:
                    st.pyplot(heatmap_fig)
            else:
                html('<div class="res-card"><p style="color:var(--text3);font-size:14px;">Not enough numeric columns to compute correlations.</p></div>')

            # ── Download ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dl-btn">')
            st.download_button(
                label="⬇  Download AI Report (.txt)",
                data=(
                    "DATA ANALYST AI AGENT — ANALYSIS REPORT\n"
                    + "=" * 50 + "\n\n"
                    + f"SUMMARY:\n{output['summary']}\n\n"
                    + f"KEY QUESTIONS:\n{output['questions']}\n\n"
                    + f"VISUAL SUGGESTIONS:\n{output['visuals']}\n"
                ),
                file_name="data_analyst_agent_report.txt",
                mime="text/plain"
            )
            html('</div>')

        else:
            html("""
            <div class="empty-state">
              <div class="empty-icon">📂</div>
              <div class="empty-title">No dataset uploaded yet</div>
              <div class="empty-sub">
                Upload a CSV file above. The EDA Agent, Quest Agent, and
                Junior DA Agent will immediately begin analyzing your data
                and generating insights automatically.
              </div>
            </div>
            """)

    # ── Footer ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    html("""
    <div class="da-footer">
      <div class="da-logo" style="font-size:14px;">
        <div class="da-logo-box" style="width:26px;height:26px;font-size:13px;">📊</div>
        Data Analyst AI Agent
      </div>
      <span class="foot-text">Multi-Agent EDA · Powered by CrewAI</span>
      <span class="foot-text">© 2026 · Open Source</span>
    </div>
    """)


# ══════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    page_landing()

elif st.session_state.page == "login":
    page_login()

elif st.session_state.page == "dashboard":
    if st.session_state.authenticated:
        page_dashboard()
    else:
        st.session_state.page = "login"
        st.rerun()