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

# ─────────────────────────────────────────────────────────────
# GLOBAL CSS  — Obsidian Luxury Dark
# Fonts: Syne (display) + DM Sans (body) + DM Mono (code/labels)
# Palette: Deep obsidian bg · Amber gold accent · Teal secondary
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
/* ══════════════════════════════════════════════
   TOKENS
══════════════════════════════════════════════ */
:root {
  /* Backgrounds */
  --bg0: #06080f;
  --bg1: #090d18;
  --bg2: #0d1220;
  --bg3: #111828;
  --bg4: #161f33;

  /* Borders */
  --b1: rgba(255,255,255,0.06);
  --b2: rgba(255,255,255,0.10);
  --b3: rgba(255,255,255,0.18);

  /* Accent — amber gold */
  --gold:    #f5a623;
  --gold-d:  #d4861a;
  --gold-l:  #fbbf5c;
  --gold-glow: rgba(245,166,35,0.18);

  /* Secondary — cool teal */
  --teal:    #14b8a6;
  --teal-d:  #0d9488;
  --teal-l:  #5eead4;

  /* Tertiary — soft violet */
  --violet:  #818cf8;
  --rose:    #fb7185;

  /* Text */
  --t1: #f0f4ff;
  --t2: #c8d0e8;
  --t3: #8892b0;
  --t4: #4e5a78;

  /* Typography */
  --ff-display: 'Syne', system-ui, sans-serif;
  --ff-body:    'DM Sans', system-ui, sans-serif;
  --ff-mono:    'DM Mono', monospace;

  /* Radii */
  --r-xs: 6px;
  --r-sm: 10px;
  --r-md: 16px;
  --r-lg: 22px;
  --r-xl: 32px;
}

/* ══════════════════════════════════════════════
   STREAMLIT SHELL RESET
══════════════════════════════════════════════ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: var(--bg0) !important;
  color: var(--t1) !important;
  font-family: var(--ff-body) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stSidebar"]      { display: none !important; }
#MainMenu, footer              { visibility: hidden !important; }
[data-testid="stAppViewContainer"] > .main > .block-container {
  padding: 0 !important;
  max-width: 100% !important;
}
.main .block-container { padding-top: 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar              { width: 3px; }
::-webkit-scrollbar-track        { background: var(--bg0); }
::-webkit-scrollbar-thumb        { background: var(--gold-d); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover  { background: var(--gold); }

/* ══════════════════════════════════════════════
   KEYFRAMES
══════════════════════════════════════════════ */
@keyframes pulse-live {
  0%,100% { box-shadow: 0 0 0 0 rgba(20,184,166,0.6); opacity: 1; }
  50%     { box-shadow: 0 0 0 5px rgba(20,184,166,0); opacity: 0.7; }
}
@keyframes gold-shimmer {
  0%   { background-position: 200% center; }
  100% { background-position: -200% center; }
}
@keyframes fade-rise {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes glow-pulse {
  0%,100% { box-shadow: 0 0 20px rgba(245,166,35,0.12); }
  50%     { box-shadow: 0 0 36px rgba(245,166,35,0.28); }
}

/* ══════════════════════════════════════════════
   TOPBAR / NAVBAR
══════════════════════════════════════════════ */
.topbar {
  position: sticky; top: 0; z-index: 999;
  height: 62px; padding: 0 40px;
  display: flex; align-items: center; justify-content: space-between;
  background: rgba(6,8,15,0.92);
  backdrop-filter: blur(28px) saturate(180%);
  -webkit-backdrop-filter: blur(28px) saturate(180%);
  border-bottom: 1px solid var(--b2);
}
.topbar-brand {
  display: flex; align-items: center; gap: 11px;
  font-family: var(--ff-display);
  font-size: 15px; font-weight: 700;
  color: var(--t1); letter-spacing: -0.2px;
}
.topbar-logo {
  width: 33px; height: 33px; border-radius: var(--r-xs);
  background: linear-gradient(135deg, var(--gold), #e67c0a);
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; flex-shrink: 0;
  box-shadow: 0 0 18px rgba(245,166,35,0.30);
}
.topbar-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--teal);
  animation: pulse-live 2s ease-in-out infinite;
  flex-shrink: 0;
}
.topbar-pill {
  font-family: var(--ff-mono);
  font-size: 10.5px; font-weight: 500;
  padding: 4px 13px; border-radius: 100px;
  background: rgba(245,166,35,0.08);
  color: var(--gold-l);
  border: 1px solid rgba(245,166,35,0.20);
  letter-spacing: 0.3px;
}

/* ══════════════════════════════════════════════
   HERO SECTION
══════════════════════════════════════════════ */
.hero-wrap {
  padding: 88px 40px 72px;
  text-align: center;
  position: relative;
  overflow: hidden;
}
/* Atmospheric mesh glow */
.hero-wrap::before {
  content: '';
  position: absolute; top: -80px; left: 50%;
  transform: translateX(-50%);
  width: 100%; max-width: 900px; height: 520px;
  background:
    radial-gradient(ellipse 55% 55% at 40% 45%, rgba(245,166,35,0.07) 0%, transparent 65%),
    radial-gradient(ellipse 45% 45% at 65% 55%, rgba(20,184,166,0.06) 0%, transparent 65%);
  pointer-events: none; z-index: 0;
}
/* Grain texture overlay */
.hero-wrap::after {
  content: '';
  position: absolute; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
  pointer-events: none; z-index: 0;
}
.hero-wrap > * { position: relative; z-index: 1; }

.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 5px 15px; border-radius: 100px;
  background: rgba(20,184,166,0.07);
  border: 1px solid rgba(20,184,166,0.20);
  font-family: var(--ff-mono);
  font-size: 10px; font-weight: 500;
  color: var(--teal-l); letter-spacing: 1.5px;
  text-transform: uppercase; margin-bottom: 28px;
  animation: fade-rise 0.7s ease both;
}
.hero-eyebrow-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--teal); flex-shrink: 0;
  animation: pulse-live 2s infinite;
}

.hero-h1 {
  font-family: var(--ff-display);
  font-size: clamp(40px, 6.5vw, 76px);
  font-weight: 800; line-height: 1.02;
  letter-spacing: -3px; color: var(--t1);
  margin-bottom: 6px;
  animation: fade-rise 0.7s 0.08s ease both;
}
.hero-h1 .gold-text {
  background: linear-gradient(90deg, var(--gold-l), var(--gold), #d4861a, var(--gold), var(--gold-l));
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gold-shimmer 5s linear infinite;
}
.hero-sub {
  font-family: var(--ff-body);
  font-size: clamp(15px, 1.8vw, 17px);
  font-weight: 300; color: var(--t3);
  line-height: 1.8; max-width: 520px;
  margin: 16px auto 44px;
  text-align: center;
  animation: fade-rise 0.7s 0.16s ease both;
}

/* Primary CTA */
.cta-btn .stButton > button {
  background: linear-gradient(135deg, var(--gold), var(--gold-d)) !important;
  color: #06080f !important;
  font-family: var(--ff-display) !important;
  font-weight: 700 !important; font-size: 14px !important;
  border: none !important; border-radius: var(--r-sm) !important;
  height: 48px !important; padding: 0 32px !important;
  width: auto !important;
  letter-spacing: -0.2px !important;
  transition: all 0.22s ease !important;
  box-shadow: 0 0 28px rgba(245,166,35,0.25) !important;
  animation: glow-pulse 3s ease-in-out infinite !important;
}
.cta-btn .stButton > button:hover {
  background: linear-gradient(135deg, var(--gold-l), var(--gold)) !important;
  transform: translateY(-2px) scale(1.01) !important;
  box-shadow: 0 10px 40px rgba(245,166,35,0.40) !important;
}

/* ══════════════════════════════════════════════
   STATS STRIP
══════════════════════════════════════════════ */
.stats-strip {
  display: flex;
  margin: 0 40px;
  border: 1px solid var(--b2);
  border-radius: var(--r-md);
  background: var(--bg2);
  overflow: hidden;
  position: relative;
}
.stats-strip::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(245,166,35,0.4), transparent);
}
.stat-block {
  flex: 1; padding: 24px 20px; text-align: center;
  border-right: 1px solid var(--b1);
  transition: background 0.22s;
  cursor: default;
}
.stat-block:last-child { border-right: none; }
.stat-block:hover      { background: rgba(245,166,35,0.04); }
.stat-num {
  font-family: var(--ff-display);
  font-size: 28px; font-weight: 800;
  line-height: 1; margin-bottom: 5px; letter-spacing: -1px;
}
.s-gold   { color: var(--gold); }
.s-teal   { color: var(--teal-l); }
.s-violet { color: var(--violet); }
.s-rose   { color: var(--rose); }
.stat-lbl {
  font-family: var(--ff-mono);
  font-size: 10px; font-weight: 500;
  color: var(--t4); text-transform: uppercase; letter-spacing: 1px;
}

/* ══════════════════════════════════════════════
   SECTION LAYOUT
══════════════════════════════════════════════ */
.section {
  padding: 72px 40px 56px;
  max-width: 1180px; margin: 0 auto;
}
.section.tight-b { padding-bottom: 24px; }
.section.no-t    { padding-top: 0; }

.divider-line {
  height: 1px; margin: 0 40px;
  background: linear-gradient(90deg, transparent, var(--b2), transparent);
}
.sec-label {
  font-family: var(--ff-mono);
  font-size: 10px; font-weight: 500;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: var(--gold); margin-bottom: 10px;
}
.sec-heading {
  font-family: var(--ff-display);
  font-size: clamp(22px, 3.2vw, 36px);
  font-weight: 800; color: var(--t1);
  letter-spacing: -1.2px; line-height: 1.12;
  margin-bottom: 40px; max-width: 460px;
}
.sec-heading.wide   { max-width: none; }
.sec-heading.center { max-width: none; text-align: center; }

/* ══════════════════════════════════════════════
   CAPABILITY CARDS — 2×2 grid
══════════════════════════════════════════════ */
.cap-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.cap-card {
  background: var(--bg2);
  border: 1px solid var(--b2); border-radius: var(--r-md);
  padding: 28px 26px; position: relative; overflow: hidden;
  transition: border-color 0.22s, transform 0.22s;
}
.cap-card::before {
  content: '';
  position: absolute; inset: 0; border-radius: var(--r-md);
  background: linear-gradient(135deg, rgba(245,166,35,0.04) 0%, transparent 60%);
  opacity: 0; transition: opacity 0.22s;
}
.cap-card:hover { border-color: rgba(245,166,35,0.28); transform: translateY(-3px); }
.cap-card:hover::before { opacity: 1; }
.cap-num {
  position: absolute; top: 16px; right: 20px;
  font-family: var(--ff-display); font-size: 42px; font-weight: 800;
  color: rgba(255,255,255,0.025); line-height: 1; user-select: none;
}
.cap-ico {
  width: 40px; height: 40px; border-radius: var(--r-xs);
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; margin-bottom: 14px;
}
.ico-g { background: rgba(245,166,35,0.10); }
.ico-t { background: rgba(20,184,166,0.10); }
.ico-v { background: rgba(129,140,248,0.10); }
.ico-r { background: rgba(251,113,133,0.10); }
.cap-title {
  font-family: var(--ff-display);
  font-size: 15px; font-weight: 700; color: var(--t1);
  margin-bottom: 8px; letter-spacing: -0.2px;
}
.cap-desc {
  font-family: var(--ff-body);
  font-size: 13px; font-weight: 300; color: var(--t3); line-height: 1.75;
}

/* ══════════════════════════════════════════════
   AGENT CREW CARDS — 3 columns
══════════════════════════════════════════════ */
.crew-row  { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }
.crew-card {
  background: var(--bg2); border: 1px solid var(--b2); border-radius: var(--r-md);
  padding: 24px; position: relative; overflow: hidden;
  transition: border-color 0.22s, transform 0.22s;
}
.crew-card:hover { border-color: rgba(20,184,166,0.30); transform: translateY(-3px); }
.crew-card-bar {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--gold), var(--teal));
  transform: scaleX(0); transform-origin: left;
  transition: transform 0.35s ease;
}
.crew-card:hover .crew-card-bar { transform: scaleX(1); }
.crew-emo  { font-size: 26px; margin-bottom: 10px; }
.crew-tag  {
  font-family: var(--ff-mono); font-size: 10px; font-weight: 500;
  color: var(--teal-l); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;
}
.crew-name {
  font-family: var(--ff-display);
  font-size: 15px; font-weight: 700; color: var(--t1);
  margin-bottom: 8px; letter-spacing: -0.2px;
}
.crew-desc { font-family: var(--ff-body); font-size: 12.5px; color: var(--t3); line-height: 1.7; }

/* ══════════════════════════════════════════════
   HOW IT WORKS — horizontal steps
══════════════════════════════════════════════ */
.steps-row {
  display: grid; grid-template-columns: repeat(4,1fr);
  position: relative;
}
.steps-row::before {
  content: '';
  position: absolute; top: 21px;
  left: calc(12.5%); right: calc(12.5%); height: 1px;
  background: linear-gradient(90deg, var(--gold), var(--teal), var(--violet), var(--rose));
  z-index: 0;
}
.step {
  display: flex; flex-direction: column; align-items: center;
  text-align: center; gap: 12px; position: relative; z-index: 1; padding: 0 10px;
}
.step-n {
  width: 42px; height: 42px; border-radius: 50%;
  background: var(--bg1); border: 1.5px solid var(--gold);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--ff-mono); font-size: 13px; font-weight: 500; color: var(--gold);
}
.step:nth-child(2) .step-n { border-color: var(--teal); color: var(--teal); }
.step:nth-child(3) .step-n { border-color: var(--violet); color: var(--violet); }
.step:nth-child(4) .step-n { border-color: var(--rose); color: var(--rose); }
.step-title { font-family: var(--ff-display); font-size: 13px; font-weight: 700; color: var(--t1); }
.step-desc  { font-family: var(--ff-body); font-size: 12px; color: var(--t3); line-height: 1.6; max-width: 120px; }

/* ══════════════════════════════════════════════
   TECH BADGES
══════════════════════════════════════════════ */
.badge-row  { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.tech-badge {
  padding: 7px 16px; border-radius: var(--r-xs);
  font-family: var(--ff-mono); font-size: 11.5px; font-weight: 500;
  color: var(--t3); background: var(--bg2); border: 1px solid var(--b2);
  transition: all 0.18s;
}
.tech-badge:hover { border-color: rgba(245,166,35,0.35); color: var(--t1); background: rgba(245,166,35,0.05); }

/* ══════════════════════════════════════════════
   PAGE FOOTER
══════════════════════════════════════════════ */
.pg-footer {
  padding: 24px 40px; margin-top: 24px;
  border-top: 1px solid var(--b1);
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;
}
.pg-footer-brand {
  display: flex; align-items: center; gap: 9px;
  font-family: var(--ff-display); font-size: 13px; font-weight: 700; color: var(--t2);
}
.pg-footer-logo {
  width: 24px; height: 24px; border-radius: 5px;
  background: linear-gradient(135deg, var(--gold), var(--gold-d));
  display: flex; align-items: center; justify-content: center; font-size: 12px;
}
.pg-footer-txt { font-family: var(--ff-mono); font-size: 11px; color: var(--t4); }

/* ══════════════════════════════════════════════
   DASHBOARD — specific styles
══════════════════════════════════════════════ */

/* Dashboard section heading */
.d-sec {
  font-family: var(--ff-display);
  font-size: 14px; font-weight: 700; color: var(--t1);
  letter-spacing: -0.1px;
  padding-bottom: 13px; margin-bottom: 16px;
  border-bottom: 1px solid var(--b1);
  display: flex; align-items: center; gap: 8px;
}

/* Metric cards */
[data-testid="stMetric"] {
  background: var(--bg2) !important;
  border: 1px solid var(--b2) !important;
  border-radius: var(--r-md) !important;
  padding: 18px 20px !important;
  position: relative !important; overflow: hidden !important;
  transition: border-color 0.2s !important;
}
[data-testid="stMetric"]::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--gold), var(--teal));
}
[data-testid="stMetric"]:hover { border-color: rgba(245,166,35,0.28) !important; }
[data-testid="stMetricValue"] {
  font-family: var(--ff-display) !important;
  font-size: 26px !important; font-weight: 800 !important;
  color: var(--t1) !important; letter-spacing: -0.8px !important;
}
[data-testid="stMetricLabel"] {
  font-family: var(--ff-mono) !important;
  font-size: 10px !important; font-weight: 500 !important;
  color: var(--t4) !important; text-transform: uppercase !important;
  letter-spacing: 0.9px !important;
}
[data-testid="stMetricDelta"] { display: none !important; }

/* File uploader */
[data-testid="stFileUploader"] > div {
  background: rgba(245,166,35,0.03) !important;
  border: 2px dashed rgba(245,166,35,0.20) !important;
  border-radius: var(--r-md) !important; transition: all 0.22s !important;
}
[data-testid="stFileUploader"] > div:hover {
  border-color: rgba(245,166,35,0.45) !important;
  background: rgba(245,166,35,0.06) !important;
}
[data-testid="stFileUploader"] label {
  color: var(--t3) !important; font-family: var(--ff-body) !important; font-size: 14px !important;
}
[data-testid="stFileUploader"] button {
  background: var(--bg3) !important; border: 1px solid var(--b2) !important;
  color: var(--t2) !important; border-radius: var(--r-xs) !important;
  font-family: var(--ff-body) !important;
}

/* Result card */
.r-card {
  background: var(--bg2); border: 1px solid var(--b2);
  border-radius: var(--r-md); padding: 20px 24px;
  transition: border-color 0.22s;
}
.r-card:hover { border-color: rgba(245,166,35,0.20); }

/* Result card label */
.r-lbl {
  font-family: var(--ff-mono);
  font-size: 10px; font-weight: 500; text-transform: uppercase;
  letter-spacing: 1.2px; color: var(--gold);
  margin-bottom: 14px; display: flex; align-items: center; gap: 7px;
}

/* Markdown output — readable on dark */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
  color: var(--t2) !important;
  font-family: var(--ff-body) !important;
  font-size: 14px !important; line-height: 1.80 !important;
  font-weight: 300 !important;
}
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3 {
  color: var(--t1) !important;
  font-family: var(--ff-display) !important;
  letter-spacing: -0.5px !important; font-weight: 700 !important;
}
[data-testid="stMarkdownContainer"] strong { color: var(--t1) !important; font-weight: 600 !important; }
[data-testid="stMarkdownContainer"] ul,
[data-testid="stMarkdownContainer"] ol    { padding-left: 18px !important; }
[data-testid="stMarkdownContainer"] code {
  background: rgba(245,166,35,0.10) !important;
  color: var(--gold-l) !important;
  font-family: var(--ff-mono) !important;
  border-radius: 4px !important; padding: 1px 7px !important; font-size: 12.5px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: var(--r-md) !important; overflow: hidden !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--gold) !important; }

/* Images */
[data-testid="stImage"] img { border-radius: var(--r-md) !important; }

/* Download button */
.dl-wrap .stDownloadButton > button {
  background: transparent !important;
  color: var(--gold-l) !important;
  border: 1px solid rgba(245,166,35,0.30) !important;
  border-radius: var(--r-sm) !important;
  font-family: var(--ff-body) !important;
  font-weight: 600 !important; font-size: 13px !important;
  height: 42px !important; padding: 0 24px !important;
  transition: all 0.2s !important;
}
.dl-wrap .stDownloadButton > button:hover {
  background: rgba(245,166,35,0.08) !important;
  border-color: var(--gold) !important;
  box-shadow: 0 0 16px rgba(245,166,35,0.18) !important;
}

/* Home button in dash nav */
.home-btn .stButton > button {
  width: auto !important; height: 32px !important; padding: 0 14px !important;
  background: transparent !important; color: var(--t3) !important;
  border: 1px solid var(--b2) !important; border-radius: var(--r-xs) !important;
  font-family: var(--ff-body) !important; font-size: 12px !important;
  font-weight: 500 !important; transition: all 0.2s !important;
}
.home-btn .stButton > button:hover {
  border-color: rgba(245,166,35,0.35) !important;
  color: var(--gold-l) !important;
}

/* Alert */
[data-testid="stAlert"] {
  border-radius: var(--r-sm) !important;
  font-family: var(--ff-body) !important; font-size: 14px !important;
}

/* Empty upload state */
.empty-box {
  text-align: center; padding: 60px 28px;
  border: 1.5px dashed rgba(245,166,35,0.15);
  border-radius: var(--r-lg);
  background: rgba(245,166,35,0.02);
  max-width: 480px; margin: 24px auto;
}
.e-icon  { font-size: 40px; margin-bottom: 14px; opacity: 0.45; }
.e-title {
  font-family: var(--ff-display);
  font-size: 18px; font-weight: 700; color: var(--t1); margin-bottom: 8px; letter-spacing: -0.3px;
}
.e-sub {
  font-family: var(--ff-body);
  font-size: 13.5px; font-weight: 300; color: var(--t3); line-height: 1.72;
}

/* ══════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════ */
@media (max-width: 768px) {
  .topbar                { padding: 0 16px; }
  .hero-wrap             { padding: 56px 16px 48px; }
  .hero-h1               { letter-spacing: -2px; }
  .stats-strip           { flex-direction: column; margin: 0 16px; border-radius: var(--r-md); }
  .stat-block            { border-right: none !important; border-bottom: 1px solid var(--b1); }
  .stat-block:last-child { border-bottom: none; }
  .cap-grid              { grid-template-columns: 1fr; }
  .crew-row              { grid-template-columns: 1fr; }
  .steps-row             { grid-template-columns: repeat(2,1fr); gap: 20px; }
  .steps-row::before     { display: none; }
  .section               { padding: 52px 16px 40px; }
  .divider-line          { margin: 0 16px; }
  .badge-row             { padding: 0 16px; }
  .pg-footer             { padding: 20px 16px; flex-direction: column; align-items: flex-start; }
}
@media (max-width: 480px) {
  .steps-row  { grid-template-columns: 1fr; }
  .hero-h1    { font-size: 34px; letter-spacing: -1.5px; }
  .topbar     { height: 54px; }
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

    # ── Top bar ──
    html("""
    <div class="topbar">
      <div class="topbar-brand">
        <div class="topbar-logo">📊</div>
        Data Analyst AI Agent
        <div class="topbar-dot"></div>
      </div>
      <span class="topbar-pill">CrewAI · Multi-Agent EDA</span>
    </div>
    """)

    # ── Hero ──
    html("""
    <div class="hero-wrap">
      <div class="hero-eyebrow">
        <span class="hero-eyebrow-dot"></span>
        Automated EDA · Zero Code Required · Instant Insights
      </div>
      <div class="hero-h1">
        Your Data, Decoded<br>
        <span class="gold-text">by AI Agents</span>
      </div>
      <p class="da-hero-sub" style="text-align:center; margin-left:auto; margin-right:auto;">
        Upload any CSV and a specialized crew of AI agents will automatically
        compute statistics, generate analytical questions, create visualizations,
        and produce business-ready summaries — end to end.
      </p>
     <p>(NOTE :- This demo works best with datasets under 1000 rows for optimal performance and responsiveness.)
    </p>
    </div>
    """)

    # CTA centered
    _, mid, _ = st.columns([2.4, 1.2, 2.4])
    with mid:
        html('<div class="cta-btn">')
        if st.button("🚀  Analyze My Data", key="hero_cta"):
            st.session_state.page = "dashboard"
            st.rerun()
        html('</div>')

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ── Stats strip ──
    html("""
    <div class="stats-strip">
      <div class="stat-block">
        <div class="stat-num s-gold">3</div>
        <div class="stat-lbl">AI Agents</div>
      </div>
      <div class="stat-block">
        <div class="stat-num s-teal">&lt;60s</div>
        <div class="stat-lbl">Full EDA</div>
      </div>
      <div class="stat-block">
        <div class="stat-num s-violet">Auto</div>
        <div class="stat-lbl">Charts</div>
      </div>
      <div class="stat-block">
        <div class="stat-num s-rose">0</div>
        <div class="stat-lbl">Code Needed</div>
      </div>
    </div>
    """)

    st.markdown("<br>", unsafe_allow_html=True)
    html('<div class="divider-line"></div>')

    # ── Capabilities ──
    html("""
    <div class="section">
      <div class="sec-label">Core Capabilities</div>
      <div class="sec-heading">What the Agent Does For You</div>
      <div class="cap-grid">
        <div class="cap-card">
          <div class="cap-num">01</div>
          <div class="cap-ico ico-g">📊</div>
          <div class="cap-title">Descriptive Statistics</div>
          <div class="cap-desc">Reads your dataset and automatically computes shape, data types, missing values, distributions, and summaries — without writing a single line of code.</div>
        </div>
        <div class="cap-card">
          <div class="cap-num">02</div>
          <div class="cap-ico ico-t">🤔</div>
          <div class="cap-title">AI-Generated Questions</div>
          <div class="cap-desc">From column metadata alone, the agent generates smart EDA questions that guide analysis exactly the way a senior data scientist would approach a new dataset.</div>
        </div>
        <div class="cap-card">
          <div class="cap-num">03</div>
          <div class="cap-ico ico-v">📈</div>
          <div class="cap-title">Automated Visualizations</div>
          <div class="cap-desc">Produces contextual plots — histograms, scatter plots, heatmaps, trend charts — for each analytical question, surfacing hidden patterns visually.</div>
        </div>
        <div class="cap-card">
          <div class="cap-num">04</div>
          <div class="cap-ico ico-r">📄</div>
          <div class="cap-title">Business-Level Summary</div>
          <div class="cap-desc">Delivers plain-language summaries and actionable insights ready to share directly with stakeholders who don't work with data daily.</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="divider-line"></div>')

    # ── Agent Crew ──
    html("""
    <div class="section tight-b">
      <div class="sec-label">The Agent Crew</div>
      <div class="sec-heading">Three Agents, One Unified Workflow</div>
    </div>
    <div style="padding: 0 40px 60px; max-width: 1180px; margin: 0 auto;">
      <div class="crew-row">
        <div class="crew-card">
          <div class="crew-card-bar"></div>
          <div class="crew-emo">🔬</div>
          <div class="crew-tag">EDA Crew</div>
          <div class="crew-name">Data Scientist Agent</div>
          <div class="crew-desc">Reads the raw CSV, computes descriptive statistics, detects data types, identifies missing values, and extracts structural metadata to lay the analysis foundation.</div>
        </div>
        <div class="crew-card">
          <div class="crew-card-bar"></div>
          <div class="crew-emo">🧠</div>
          <div class="crew-tag">Quest Crew</div>
          <div class="crew-name">Business Consultant Agent</div>
          <div class="crew-desc">Analyzes dataset metadata to generate targeted, high-value questions. Frames EDA in terms of business objectives and translates patterns into decisions.</div>
        </div>
        <div class="crew-card">
          <div class="crew-card-bar"></div>
          <div class="crew-emo">📉</div>
          <div class="crew-tag">Junior DA Crew</div>
          <div class="crew-name">Junior Data Analyst Agent</div>
          <div class="crew-desc">Takes generated questions and produces relevant plots and visual insights — identifying trends, outliers, correlations, and distributions across your dataset.</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="divider-line"></div>')

    # ── How it works ──
    html("""
    <div class="section tight-b">
      <div class="sec-label">How It Works</div>
      <div class="sec-heading center">Four steps. Full EDA. Zero effort.</div>
    </div>
    <div style="padding: 0 40px 64px; max-width: 1180px; margin: 0 auto;">
      <div class="steps-row">
        <div class="step">
          <div class="step-n">01</div>
          <div class="step-title">Upload CSV</div>
          <div class="step-desc">Drop any structured dataset</div>
        </div>
        <div class="step">
          <div class="step-n">02</div>
          <div class="step-title">Agents Activate</div>
          <div class="step-desc">EDA, Quest & DA crews run in sequence</div>
        </div>
        <div class="step">
          <div class="step-n">03</div>
          <div class="step-title">Insights Surface</div>
          <div class="step-desc">Stats, questions & charts generated</div>
        </div>
        <div class="step">
          <div class="step-n">04</div>
          <div class="step-title">Export Report</div>
          <div class="step-desc">Download full AI report as .txt</div>
        </div>
      </div>
    </div>
    """)

    html('<div class="divider-line"></div>')

    # ── Tech stack ──
    html("""
    <div class="section tight-b" style="text-align:center;">
      <div class="sec-label" style="text-align:center;">Built With</div>
      <div class="sec-heading center">Open-source technologies under the hood</div>
    </div>
    <div style="padding: 0 40px 64px;">
      <div class="badge-row">
        <span class="tech-badge">🤖 CrewAI</span>
        <span class="tech-badge">🦜 LangChain</span>
        <span class="tech-badge">🐍 Python</span>
        <span class="tech-badge">🎈 Streamlit</span>
        <span class="tech-badge">🐼 Pandas</span>
        <span class="tech-badge">📊 Matplotlib</span>
        <span class="tech-badge">🔥 Seaborn</span>
        <span class="tech-badge">🧩 GPT-4 / LLM</span>
      </div>
    </div>
    """)

    # ── Footer ──
    html("""
    <div class="pg-footer">
      <div class="pg-footer-brand">
        <div class="pg-footer-logo">📊</div>
        Data Analyst AI Agent
      </div>
      <span class="pg-footer-txt">Built with CrewAI · Multi-Agent Automated EDA</span>
      <span class="pg-footer-txt">© 2026 · Open Source</span>
    </div>
    """)


# ══════════════════════════════════════════════════════════════
#  DASHBOARD — direct access, no login required
# ══════════════════════════════════════════════════════════════
def page_dashboard():
    inject()

    # ── Top bar ──
    tl, tr = st.columns([5, 1])
    with tl:
        html("""
        <div class="topbar">
          <div class="topbar-brand">
            <div class="topbar-logo">📊</div>
            Data Analyst AI Agent
            <div class="topbar-dot"></div>
          </div>
          <span class="topbar-pill" style="display:none"></span>
        </div>
        """)
    with tr:
        html('<div class="topbar" style="justify-content:flex-end;padding-right:16px;">')
        html('<div class="home-btn">')
        if st.button("← Home", key="go_home"):
            st.session_state.page = "landing"
            st.rerun()
        html('</div></div>')

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Body ──
    _, body, _ = st.columns([0.3, 11.4, 0.3])
    with body:

        # Upload
        html('<div class="d-sec">📂  Upload Dataset</div>')
        uploaded_file = st.file_uploader(
            "Drag & drop a CSV file here, or click to browse",
            type=["csv"],
            help="Any structured CSV — the AI agent crew will handle the rest"
        )

        if uploaded_file is not None:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            df       = pd.read_csv(temp_path)
            num_cols = df.select_dtypes(include=["int64","float64"]).columns
            null_pct = round(
                df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100, 1
            )

            # ── Dataset Overview ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="d-sec">📊  Dataset Overview</div>')
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Rows",      f"{df.shape[0]:,}")
            with c2: st.metric("Total Columns",   df.shape[1])
            with c3: st.metric("Numeric Columns", len(num_cols))
            with c4: st.metric("Missing Data",    f"{null_pct}%")

            # ── Data Preview ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="d-sec">🔍  Data Preview</div>')
            st.dataframe(df.head(10), use_container_width=True)

            # ── AI Analysis ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="d-sec">🤖  AI Agent Analysis</div>')

            with st.spinner("🧠  AI Agents analyzing your dataset — please wait..."):
                output = run_pipeline(temp_path)

            # Summary
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="r-card"><div class="r-lbl">📋 &nbsp;Summary</div>')
            st.markdown(output["summary"])
            html('</div>')

            # Key Questions + Visualization Suggestions
            st.markdown("<br>", unsafe_allow_html=True)
            col_q, col_v = st.columns(2)
            with col_q:
                html('<div class="r-card" style="height:100%">')
                html('<div class="r-lbl">❓ &nbsp;Key Questions</div>')
                st.markdown(output["questions"])
                html('</div>')
            with col_v:
                html('<div class="r-card" style="height:100%">')
                html('<div class="r-lbl">📈 &nbsp;Visualization Suggestions</div>')
                st.markdown(output["visuals"])
                html('</div>')

            # ── Generated Plots ──
            if output.get("plots"):
                st.markdown("<br>", unsafe_allow_html=True)
                html('<div class="d-sec">📊  Generated Plots</div>')
                for plot_path in output["plots"]:
                    _, pm, _ = st.columns([0.5, 9, 0.5])
                    with pm:
                        st.image(plot_path, width=820)
                    st.markdown("<br>", unsafe_allow_html=True)

            # ── Correlation Heatmap ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="d-sec">🔥  Correlation Heatmap</div>')
            heatmap_fig = plot_correlation_heatmap(df)
            if heatmap_fig:
                heatmap_fig.set_size_inches(10, 5)
                _, hm, _ = st.columns([0.5, 9, 0.5])
                with hm:
                    st.pyplot(heatmap_fig)
            else:
                html('<div class="r-card"><p style="color:var(--t3);font-size:13px;font-family:var(--ff-body);margin:0;">Not enough numeric columns to compute correlations.</p></div>')

            # ── Download ──
            st.markdown("<br>", unsafe_allow_html=True)
            html('<div class="dl-wrap">')
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
            <div class="empty-box">
              <div class="e-icon">📂</div>
              <div class="e-title">No dataset uploaded yet</div>
              <div class="e-sub">
                Upload a CSV above. The EDA Agent, Quest Agent, and Junior DA Agent
                will immediately begin analyzing your data and generating insights automatically.
              </div>
            </div>
            """)

    # ── Footer ──
    st.markdown("<br><br>", unsafe_allow_html=True)
    html("""
    <div class="pg-footer">
      <div class="pg-footer-brand">
        <div class="pg-footer-logo">📊</div>
        Data Analyst AI Agent
      </div>
      <span class="pg-footer-txt">Multi-Agent EDA · CrewAI</span>
      <span class="pg-footer-txt">© 2026 · Open Source</span>
    </div>
    """)


# ══════════════════════════════════════════════════════════════
#  ROUTER — no login, direct access
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "landing":
    page_landing()
else:
    page_dashboard()