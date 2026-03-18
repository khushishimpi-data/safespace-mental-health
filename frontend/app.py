"""
SafeSpace - AI Mental Health Support Platform
Professional UI Redesign v2.0
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import time
from datetime import datetime

st.set_page_config(
    page_title="SafeSpace — Mental Health Support",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed"
)

BACKEND_URL = "http://localhost:8000"

# ── DESIGN TOKENS ──────────────────────────────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,700;1,500&family=Inter:wght@300;400;500;600&display=swap');

:root {
  --bg:        #F7F5F0;
  --surface:   #FFFFFF;
  --border:    #E8E4DC;
  --green:     #2E6B4F;
  --green-lt:  #EAF2EE;
  --green-mid: #4A8C68;
  --text:      #1C1C1C;
  --text-2:    #5A5A5A;
  --text-3:    #9A9A9A;
  --red:       #C0392B;
  --red-lt:    #FDECEA;
  --amber:     #D4860A;
  --amber-lt:  #FEF3DC;
  --radius:    14px;
  --radius-sm: 8px;
  --shadow:    0 1px 3px rgba(0,0,0,.06), 0 4px 16px rgba(0,0,0,.06);
  --shadow-lg: 0 8px 32px rgba(0,0,0,.10);
}

/* ── RESET ── */
* { box-sizing: border-box; }
#MainMenu, footer, header, .stDeployButton,
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] { display:none !important; }
section[data-testid="stSidebar"] { display:none !important; }
.block-container {
  padding: 0 !important;
  max-width: 760px !important;
  margin: 0 auto !important;
}

/* ── APP BG ── */
.stApp { background: var(--bg); font-family: 'Inter', sans-serif; color: var(--text); }

/* ── STREAMLIT TEXT OVERRIDES ── */
.stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p { color: var(--text) !important; }

/* ── NAVBAR ── */
.ss-nav {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 40px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 999;
}
.ss-nav-brand {
  display: flex; align-items: center; gap: 10px;
  font-size: 17px; font-weight: 600; color: var(--text);
  letter-spacing: -.3px;
}
.ss-nav-logo { color: var(--green); font-size: 20px; }
.ss-nav-right { display: flex; align-items: center; gap: 16px; }
.ss-nav-user { text-align: right; }
.ss-nav-name { font-size: 14px; font-weight: 600; color: var(--text); }
.ss-nav-wid  { font-size: 11px; color: var(--text-3); font-family: monospace; }

/* ── PAGE CONTAINER ── */
.ss-page {
  max-width: 100%;
  margin: 0 auto;
  padding: 32px 0 80px;
}
.ss-page-wide {
  max-width: 100%;
  margin: 0 auto;
  padding: 32px 0 80px;
}

/* ── TYPOGRAPHY ── */
.ss-h1 {
  font-family: 'Playfair Display', serif;
  font-size: 38px; font-weight: 700;
  line-height: 1.15; color: var(--text);
  margin-bottom: 10px;
}
.ss-h1 em { color: var(--green); font-style: italic; }
.ss-h2 {
  font-family: 'Playfair Display', serif;
  font-size: 26px; font-weight: 500;
  color: var(--text); margin-bottom: 6px;
  text-align: center;
}
.ss-lead { font-size: 16px; color: var(--text-2); line-height: 1.65; margin-bottom: 32px; text-align: center; }
.ss-sub  { font-size: 14px; color: var(--text-3); margin-bottom: 24px; text-align: center; }
.ss-label {
  font-size: 10px; font-weight: 700; letter-spacing: 1.4px;
  text-transform: uppercase; color: var(--text-3);
}

/* ── CARDS ── */
.ss-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 18px 22px;
  margin-bottom: 10px;
  box-shadow: var(--shadow);
  transition: box-shadow .2s, transform .15s;
}
.ss-card:hover {
  box-shadow: 0 4px 20px rgba(0,0,0,.09);
  transform: translateY(-1px);
}
.ss-card-row {
  display: flex; align-items: center;
  justify-content: space-between; gap: 16px;
}
.ss-icon-box {
  width: 38px; height: 38px;
  background: var(--green-lt);
  border-radius: 8px;
  display: flex; align-items: center;
  justify-content: center; font-size: 18px;
  flex-shrink: 0; margin-bottom: 10px;
}
.ss-card-title {
  font-family: 'Playfair Display', serif;
  font-size: 17px; font-weight: 500;
  color: var(--text); margin-bottom: 4px;
}
.ss-card-desc { font-size: 13px; color: var(--text-2); line-height: 1.5; }

/* ── FEATURE CARD (landing) ── */
.ss-feat {
  background: rgba(255,255,255,.8);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px 24px; text-align: center;
  margin-bottom: 12px;
}
.ss-feat-icon { font-size: 28px; margin-bottom: 10px; }
.ss-feat-title { font-size: 16px; font-weight: 600; color: var(--text); margin-bottom: 6px; }
.ss-feat-desc  { font-size: 13px; color: var(--text-2); line-height: 1.5; }

/* ── AUTH CARD ── */
.ss-auth {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 48px 44px;
  max-width: 440px;
  margin: 48px auto;
  box-shadow: var(--shadow-lg);
  text-align: center;
}
.ss-auth h2 {
  font-family: 'Playfair Display', serif;
  font-size: 30px; color: var(--text); margin-bottom: 6px;
}
.ss-auth p { font-size: 14px; color: var(--text-3); margin-bottom: 28px; }
.ss-divider {
  display: flex; align-items: center; gap: 12px;
  margin: 20px 0; color: var(--text-3); font-size: 13px;
}
.ss-divider::before, .ss-divider::after {
  content: ''; flex: 1; height: 1px; background: var(--border);
}
.ss-link { color: var(--green); font-weight: 500; cursor: pointer; }

/* ── PILLS / BADGES ── */
.ss-pill {
  display: inline-block;
  padding: 4px 12px; border-radius: 50px;
  font-size: 12px; font-weight: 600;
}
.ss-pill-green { background: var(--green-lt); color: var(--green); }
.ss-pill-red   { background: var(--red-lt); color: var(--red); }
.ss-pill-amber { background: var(--amber-lt); color: var(--amber); }

/* ── STATS ROW ── */
.ss-stats {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 10px; margin-bottom: 16px;
}
.ss-stat {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 14px 16px;
  text-align: center;
}
.ss-stat-num { font-size: 24px; font-weight: 700; color: var(--green); line-height: 1; }
.ss-stat-lbl { font-size: 11px; color: var(--text-3); margin-top: 3px; letter-spacing:.3px; }

/* ── CHAT BUBBLES ── */
.ss-bubble-wrap-user { display: flex; justify-content: flex-end; margin: 6px 0; }
.ss-bubble-wrap-ai   { display: flex; justify-content: flex-start; margin: 6px 0; }
.ss-bubble-user {
  background: var(--green); color: #fff;
  border-radius: 18px 18px 4px 18px;
  padding: 11px 16px; font-size: 14px; line-height: 1.55;
  max-width: 82%; box-shadow: 0 2px 8px rgba(46,107,79,.25);
}
.ss-bubble-ai {
  background: var(--surface); color: var(--text);
  border-radius: 18px 18px 18px 4px;
  padding: 11px 16px; font-size: 14px; line-height: 1.55;
  max-width: 82%; border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

/* ── PROGRESS ── */
.ss-progress-wrap { background: var(--border); border-radius: 6px; height: 5px; margin-bottom: 24px; overflow: hidden; }
.ss-progress-fill { background: var(--green); height: 100%; border-radius: 6px; transition: width .4s; }

/* ── CATEGORY BADGE ── */
.ss-cat-badge {
  display: inline-block;
  background: var(--green-lt); color: var(--green);
  font-size: 11px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; padding: 4px 12px;
  border-radius: 50px; margin-bottom: 14px;
}

/* ── QUIZ OPTION ── */
.ss-quiz-opt {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 13px 16px;
  margin-bottom: 8px; font-size: 14px; color: var(--text);
  cursor: pointer; transition: border-color .15s;
}

/* ── USER ROW ── */
.ss-user-row {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 0; border-bottom: 1px solid var(--border);
}
.ss-avatar {
  width: 38px; height: 38px;
  background: var(--green-lt); border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; flex-shrink: 0;
}
.ss-user-name { font-weight: 600; font-size: 14px; color: var(--text); }
.ss-user-wid  { font-size: 11px; color: var(--text-3); font-family: monospace; }
.ss-user-role { font-size: 13px; color: var(--text-2); }
.ss-user-date { font-size: 11px; color: var(--text-3); }

/* ── PRIVACY CARD ── */
.ss-privacy {
  background: var(--green-lt);
  border: 1px solid #C3DDD0;
  border-radius: var(--radius);
  padding: 18px 22px;
  display: flex; gap: 14px; align-items: flex-start;
  margin-top: 8px;
}
.ss-privacy-body .title { font-weight: 600; font-size: 14px; color: var(--green); margin-bottom: 4px; }
.ss-privacy-body .body  { font-size: 13px; color: #3A6B53; line-height: 1.55; }

/* ── MOOD ENTRY ── */
.ss-mood-entry {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.ss-mood-time { font-size: 12px; color: var(--text-3); margin-left: auto; }

/* ── CAT SCORE ROW ── */
.ss-cat-row {
  display: flex; align-items: center; gap: 12px;
  padding: 10px 0; border-bottom: 1px solid var(--border);
}
.ss-cat-name { font-size: 14px; font-weight: 500; min-width: 110px; }
.ss-bar-wrap { flex: 1; background: var(--border); border-radius: 6px; height: 7px; overflow: hidden; }
.ss-bar-fill { height: 100%; border-radius: 6px; }
.ss-cat-score { font-size: 14px; font-weight: 600; min-width: 36px; text-align: right; }

/* ── BUTTON OVERRIDES ── */
.stButton > button {
  font-family: 'Inter', sans-serif !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  transition: all .15s !important;
  border: none !important;
  width: auto !important;
}
.stButton > button[kind="primary"] {
  background: var(--green) !important;
  color: white !important;
}
.stButton > button[kind="primary"]:hover {
  background: #245840 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 3px 10px rgba(46,107,79,.25) !important;
}
.stButton > button[kind="secondary"] {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
}
.stButton > button[kind="secondary"]:hover { border-color: var(--green) !important; }
/* Use container width only when explicitly set */
[data-testid="stButton"] > button { min-width: 0; }

/* ── INPUT OVERRIDES ── */
.stTextInput > div > div > input,
.stTextArea > div > textarea {
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  padding: 11px 14px !important;
  font-size: 14px !important;
  font-family: 'Inter', sans-serif !important;
  background: var(--surface) !important;
  color: var(--text) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > textarea:focus {
  border-color: var(--green) !important;
  box-shadow: 0 0 0 3px rgba(46,107,79,.12) !important;
}
.stSelectbox > div > div {
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface) !important;
}
.stSelectbox label, .stTextInput label, .stTextArea label,
.stSelectbox > label { color: var(--text-2) !important; font-size: 13px !important; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg) !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important; font-weight: 500 !important;
  color: var(--text-2) !important;
  padding: 12px 20px !important;
  border-radius: 0 !important;
  border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color: var(--green) !important;
  border-bottom: 2px solid var(--green) !important;
  background: transparent !important;
}

/* ── RADIO ── */
.stRadio > div { gap: 8px !important; }
.stRadio > div > label {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  color: var(--text) !important;
  cursor: pointer !important;
  transition: border-color .15s !important;
}
.stRadio > div > label:hover { border-color: var(--green) !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-size: 14px !important;
  font-weight: 500 !important;
  color: var(--text) !important;
}
.streamlit-expanderContent {
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
  background: var(--surface) !important;
}

/* ── ALERT OVERRIDES ── */
div[data-testid="stAlert"] {
  border-radius: 8px !important;
  font-size: 14px !important;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--green) !important; }

/* ── GRID FOR HOME CARDS ── */
.ss-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 12px; }
.ss-grid-3 { display: grid; grid-template-columns: repeat(3,1fr); gap: 12px; }

/* ── LANDING HERO ── */
.ss-hero {
  text-align: center;
  padding: 72px 20px 52px;
  max-width: 600px; margin: 0 auto;
}
.ss-hero .tag {
  display: inline-block;
  background: var(--green-lt); color: var(--green);
  font-size: 12px; font-weight: 600; letter-spacing: .5px;
  padding: 5px 14px; border-radius: 50px; margin-bottom: 20px;
}

/* ── DIVIDER ── */
.ss-hr { height: 1px; background: var(--border); margin: 24px 0; }

/* ── CHAT AREA ── */
.ss-chat-area {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  min-height: 300px;
  max-height: 480px;
  overflow-y: auto;
  margin-bottom: 16px;
}

/* ── VOICE ORB ── */
@keyframes orb-pulse {
  0%   { box-shadow: 0 0 0 0 rgba(46,107,79,.4); }
  70%  { box-shadow: 0 0 0 14px rgba(46,107,79,0); }
  100% { box-shadow: 0 0 0 0 rgba(46,107,79,0); }
}
@keyframes orb-listen {
  0%,100% { transform: scale(1); }
  50%      { transform: scale(1.08); }
}

/* ── BACK LINK ── */
.ss-back { font-size: 13px; color: var(--text-3); cursor: pointer; }
.ss-back:hover { color: var(--green); }

/* ── CRISIS PREDICTOR WARNING ── */
.ss-predictor-low {
  background: #EAF2EE; border: 1px solid #C3DDD0;
  border-radius: 10px; padding: 12px 16px; margin: 8px 0;
  display: flex; align-items: flex-start; gap: 10px;
}
.ss-predictor-moderate {
  background: #FEF3DC; border: 1px solid #F0D090;
  border-radius: 10px; padding: 12px 16px; margin: 8px 0;
  display: flex; align-items: flex-start; gap: 10px;
}
.ss-predictor-high {
  background: #FDECEA; border: 1px solid #EFC7C4;
  border-radius: 10px; padding: 12px 16px; margin: 8px 0;
  display: flex; align-items: flex-start; gap: 10px;
}
.ss-predictor-text { font-size: 13px; line-height: 1.5; }
.ss-predictor-label { font-weight: 700; font-size: 11px; letter-spacing: .5px; text-transform: uppercase; margin-bottom: 3px; }

/* ── EMOTION TAG ── */
.ss-emotion-tag {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 3px 10px; border-radius: 50px;
  font-size: 11px; font-weight: 600;
  margin-top: 5px; letter-spacing: .3px;
}
.ss-emotion-positive { background: #EAF2EE; color: #2E6B4F; }
.ss-emotion-negative  { background: #FDECEA; color: #C0392B; }
.ss-emotion-neutral   { background: #F5F3EE; color: #9A9A9A; }

/* ── EMOTION TIMELINE ── */
.ss-timeline {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 20px 24px; margin-bottom: 12px;
}
.ss-timeline-row {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 0; border-bottom: 1px solid var(--border);
}
.ss-timeline-row:last-child { border-bottom: none; }
.ss-timeline-emoji { font-size: 20px; flex-shrink: 0; width: 28px; text-align: center; }
.ss-timeline-info { flex: 1; }
.ss-timeline-emotion { font-weight: 600; font-size: 13px; color: var(--text); }
.ss-timeline-insight { font-size: 12px; color: var(--text-3); margin-top: 1px; }
.ss-timeline-time { font-size: 11px; color: var(--text-3); }
.ss-intensity-high   { color: #C0392B; font-size: 11px; font-weight: 700; }
.ss-intensity-medium { color: #D4860A; font-size: 11px; font-weight: 700; }
.ss-intensity-low    { color: #2E6B4F; font-size: 11px; font-weight: 700; }

/* ── CRISIS OVERLAY ── */
.ss-crisis-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,.65);
  z-index: 9999;
  display: flex; align-items: center; justify-content: center;
  padding: 20px;
}
.ss-crisis-modal {
  background: white; border-radius: 20px;
  padding: 36px 32px; max-width: 480px; width: 100%;
  box-shadow: 0 20px 60px rgba(0,0,0,.3);
  text-align: center;
}
.ss-crisis-modal .icon { font-size: 48px; margin-bottom: 14px; }
.ss-crisis-modal h3 {
  font-family: 'Playfair Display', serif;
  font-size: 22px; color: #C0392B; margin-bottom: 10px;
}
.ss-crisis-modal .msg {
  font-size: 15px; color: #5A5A5A; line-height: 1.6; margin-bottom: 20px;
}
.ss-crisis-helpline {
  background: #FDECEA; border: 1px solid #EFC7C4;
  border-radius: 12px; padding: 16px 18px; margin-bottom: 12px; text-align: left;
}
.ss-crisis-helpline .hl-label {
  font-size: 11px; font-weight: 700; letter-spacing: .8px;
  text-transform: uppercase; color: #C0392B; margin-bottom: 4px;
}
.ss-crisis-helpline .hl-name  { font-weight: 600; font-size: 15px; color: #1C1C1C; }
.ss-crisis-helpline .hl-num   { font-size: 18px; font-weight: 700; color: #C0392B; margin: 2px 0; }
.ss-crisis-helpline .hl-hours { font-size: 12px; color: #9A9A9A; }

/* ── RESPONSIVE ── */
@media (max-width: 640px) {
  .ss-grid { grid-template-columns: 1fr !important; }
  .ss-stats { grid-template-columns: repeat(3,1fr) !important; }
  .ss-h1 { font-size: 28px !important; }
  .ss-h2 { font-size: 22px !important; }
  .ss-nav { padding: 0 16px !important; }
  .block-container { padding: 0 8px !important; }
}

/* ── SMOOTH SCROLL ── */
html { scroll-behavior: smooth; }

/* ── HIDE STREAMLIT COLUMN GAPS ── */
[data-testid="column"] { padding: 0 4px !important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── FEATURE CARD ROW COMPACT ── */
.ss-card-compact { padding: 12px 16px !important; }


/* ── AI REPORT ── */
.ss-report {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 28px 32px;
  margin-bottom: 12px;
  line-height: 1.75;
}
.ss-report h2 {
  font-family: 'Playfair Display', serif !important;
  font-size: 18px !important;
  color: var(--green) !important;
  margin: 20px 0 8px !important;
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.ss-report h2:first-child { margin-top: 0 !important; }
.ss-report p { font-size: 14px; color: var(--text-2); margin-bottom: 10px; }
.ss-report ul { padding-left: 18px; margin-bottom: 10px; }
.ss-report li { font-size: 14px; color: var(--text-2); margin-bottom: 6px; }
.ss-report-header {
  display: flex; align-items: center; gap: 14px;
  background: var(--green-lt); border-radius: 10px;
  padding: 14px 18px; margin-bottom: 20px;
}
.ss-report-header .icon { font-size: 28px; }
.ss-report-header .title { font-weight: 600; font-size: 15px; color: var(--green); }
.ss-report-header .sub   { font-size: 12px; color: #4A8C68; margin-top: 2px; }

/* ── CRISIS CARD ── */
.ss-crisis {
  background: var(--red-lt);
  border: 1px solid #EFC7C4;
  border-radius: var(--radius);
  padding: 20px 24px; margin-bottom: 12px;
}
.ss-crisis .title { font-weight: 700; font-size: 15px; color: var(--red); margin-bottom: 8px; }
.ss-crisis .body  { font-size: 14px; color: #7B2020; line-height: 1.7; }

/* ── BADGE CARD ── */
.ss-badge-card {
  display: flex; align-items: center; gap: 16px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px; margin-bottom: 10px;
}
.ss-badge-card.earned { border-color: var(--green); background: var(--green-lt); }
.ss-badge-icon { font-size: 28px; flex-shrink: 0; }
.ss-badge-name { font-weight: 600; font-size: 15px; color: var(--text); }
.ss-badge-desc { font-size: 13px; color: var(--text-3); }
.ss-badge-check { margin-left: auto; color: var(--green); font-size: 18px; }

</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

# ── SESSION ────────────────────────────────────────────────────────────────────
def init():
    for k,v in {
        "page":"landing","user_id":None,"username":None,"wellness_id":None,
        "is_admin":False,"conversation_id":None,"messages":[],
        "screening_active":False,"current_screening":None,"screening_results":None,
        "mood_log":[],"quiz_state":None,"badges":[],"total_points":0,"ai_report":None,"report_loading":False,"has_memory":False,"memory_summary":"","predictor_warning":None,"predictor_trajectory":"stable",
        "mindfulness_step":0,"show_crisis_alert":False,"emotion_timeline":[],
    }.items():
        if k not in st.session_state: st.session_state[k] = v
init()
def nav(p): st.session_state.page = p; st.rerun()

# ── API ────────────────────────────────────────────────────────────────────────
def api(method, path, **kw):
    try:
        r = getattr(requests,method)(f"{BACKEND_URL}{path}", timeout=10, **kw)
        if r.status_code == 200: return r.json()
    except: pass
    return None

def api_register():    return api("post","/api/auth/register",json={"preferred_language":"en","enable_voice_input":True})
def api_create_conv(): return api("post","/api/conversations",params={"user_id":st.session_state.user_id})
def api_send_msg(t):
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/conversations/{st.session_state.conversation_id}/messages",
            params={"user_id": st.session_state.user_id},
            json={"content": t, "message_type": "text"},
            timeout=30
        )
        if r.status_code == 200: return r.json()
    except: pass
    return None

def check_crisis_in_message(text: str) -> bool:
    """Client-side crisis keyword check as backup"""
    keywords = [
        "suicide","kill myself","end my life","want to die","no reason to live",
        "self-harm","hurt myself","cutting","overdose","worthless","nobody cares",
        "better off dead","can't go on","give up on life"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)
def api_start_screening(): return api("post","/api/screening/start",params={"user_id":st.session_state.user_id})
def api_answer(qid,v):     return api("post","/api/screening/answer",params={"user_id":st.session_state.user_id,"question_id":qid,"response":v})

def api_generate_report(screening_data: dict):
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/screening/generate-report",
            params={"user_id": st.session_state.user_id},
            json=screening_data,
            timeout=60
        )
        if r.status_code == 200: return r.json()
    except: pass
    return None

def api_summarize_conversation():
    """Save conversation summary to memory"""
    if not st.session_state.conversation_id: return None
    try:
        r = requests.post(
            f"{BACKEND_URL}/api/conversations/{st.session_state.conversation_id}/summarize",
            params={"user_id": st.session_state.user_id},
            timeout=30
        )
        if r.status_code == 200: return r.json()
    except: pass
    return None

def api_get_memory():
    """Get user past session memory"""
    try:
        r = requests.get(
            f"{BACKEND_URL}/api/user/{st.session_state.user_id}/memory",
            timeout=5
        )
        if r.status_code == 200: return r.json()
    except: pass
    return {"memory": "", "has_memory": False}

# ── NAVBAR ─────────────────────────────────────────────────────────────────────
def navbar():
    if st.session_state.username:
        name = st.session_state.username
        wid  = st.session_state.wellness_id or ""
        st.markdown(f"""
        <div class="ss-nav">
          <div class="ss-nav-brand">
            <span class="ss-nav-logo">🌿</span> SafeSpace
          </div>
          <div class="ss-nav-right">
            <div class="ss-nav-user">
              <div class="ss-nav-name">{name}</div>
              <div class="ss-nav-wid">{wid}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
        col1, col2 = st.columns([8,1])
        with col2:
            if st.button("Sign out", key="__nav_out__", help="Sign out"):
                for k in list(st.session_state.keys()): del st.session_state[k]
                init(); nav("landing")
    else:
        st.markdown("""
        <div class="ss-nav">
          <div class="ss-nav-brand"><span class="ss-nav-logo">🌿</span> SafeSpace</div>
          <div class="ss-nav-right">
            <span style="font-size:14px;color:#5A5A5A;font-weight:500">Sign in</span>
          </div>
        </div>""", unsafe_allow_html=True)

# ── CRISIS ALERT ──────────────────────────────────────────────────────────────
def render_crisis_alert():
    """Show full-screen crisis overlay if triggered"""
    if not st.session_state.get("show_crisis_alert", False):
        return
    st.markdown("""
    <div class="ss-crisis-overlay" id="crisis-overlay">
      <div class="ss-crisis-modal">
        <div class="icon">🆘</div>
        <h3>You Are Not Alone</h3>
        <p class="msg">
          It seems like you might be going through something really difficult right now.
          You matter, and help is available — please reach out immediately.
        </p>
        <div class="ss-crisis-helpline">
          <div class="hl-label">India — 24/7</div>
          <div class="hl-name">Vandrevala Foundation</div>
          <div class="hl-num">📞 1860-2662-345</div>
          <div class="hl-hours">Available 24 hours, 7 days a week</div>
        </div>
        <div class="ss-crisis-helpline">
          <div class="hl-label">India — iCall</div>
          <div class="hl-name">iCall Psychosocial Helpline</div>
          <div class="hl-num">📞 9152987821</div>
          <div class="hl-hours">Monday to Saturday, 8am – 10pm</div>
        </div>
        <div class="ss-crisis-helpline">
          <div class="hl-label">Global — Text</div>
          <div class="hl-name">Crisis Text Line</div>
          <div class="hl-num">💬 Text HOME to 741741</div>
          <div class="hl-hours">Available 24/7 worldwide</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ I am safe — Continue", use_container_width=True, type="primary", key="crisis_safe"):
            st.session_state.show_crisis_alert = False
            st.rerun()
    with col2:
        if st.button("📞 Call Helpline Now", use_container_width=True, key="crisis_call"):
            st.markdown('<script>window.open("tel:18602662345");</script>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  LANDING
# ══════════════════════════════════════════════════════════════════════════════
def page_landing():
    navbar()
    st.markdown("""
    <div class="ss-hero">
      <div class="tag">🌿 Anonymous &amp; Confidential</div>
      <div class="ss-h1">Your Mental Wellness,<br><em>Completely Private</em></div>
      <p class="ss-lead">A safe space for students to access mental health support without fear of judgment or exposure.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    _,c1,c2,_ = st.columns([1,1,1,1])
    with c1:
        if st.button("Get Started →", use_container_width=True, type="primary"): nav("register")
    with c2:
        if st.button("Admin Portal", use_container_width=True): nav("admin_login")

# ══════════════════════════════════════════════════════════════════════════════
#  REGISTER
# ══════════════════════════════════════════════════════════════════════════════
def api_signin(wellness_id: str):
    return api("post", "/api/auth/signin", params={"wellness_id": wellness_id})

def page_register():
    navbar()
    st.markdown("""
    <div class="ss-auth">
      <h2>Welcome</h2>
      <p>Create a new account or sign in with your Wellness ID</p>
    </div>""", unsafe_allow_html=True)

    _,c,_ = st.columns([1,3,1])
    with c:
        tab_new, tab_return = st.tabs(["New Student", "Returning Student"])

        with tab_new:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            lang = st.selectbox("Preferred language",
                ["English","हिन्दी (Hindi)","தமிழ் (Tamil)","বাংলা (Bengali)","తెలుగు (Telugu)"],
                key="reg_lang")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("Join as Student", use_container_width=True, type="primary", key="reg_new"):
                with st.spinner("Creating your anonymous identity…"):
                    data = api_register()
                if data:
                    st.session_state.user_id     = data["id"]
                    st.session_state.username    = data["username"]
                    st.session_state.wellness_id = data["wellness_id"]
                    st.session_state.is_admin    = False
                    st.success(f"✅ Welcome, {data['username']}! Your Wellness ID: **{data['wellness_id']}** — save it to sign in later.")
                    time.sleep(2)
                    nav("home")
                else:
                    st.error("Backend not reachable. Make sure the backend server is running.")
            st.markdown("""
            <p style="text-align:center;font-size:12px;color:#9A9A9A;margin:10px 0">
              A unique username and Wellness ID will be auto-generated — no personal info needed.
            </p>""", unsafe_allow_html=True)

        with tab_return:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="ss-card" style="padding:14px 18px;margin-bottom:14px;background:#EAF2EE;border-color:#C3DDD0">
              <p style="font-size:13px;color:#2E6B4F;margin:0">
                🔐 Enter your <strong>Wellness ID</strong> (e.g. WL123456) to pick up where you left off.
                Your chat history, points and badges will be restored.
              </p>
            </div>""", unsafe_allow_html=True)
            wid_input = st.text_input("Your Wellness ID", placeholder="e.g. WL123456", key="signin_wid")
            if st.button("Sign In →", use_container_width=True, type="primary", key="reg_return"):
                if wid_input.strip():
                    with st.spinner("Looking up your account…"):
                        data = api_signin(wid_input.strip())
                    if data:
                        st.session_state.user_id     = data["id"]
                        st.session_state.username    = data["username"]
                        st.session_state.wellness_id = data["wellness_id"]
                        st.session_state.is_admin    = False
                        st.success(f"✅ Welcome back, {data['username']}!")
                        time.sleep(1)
                        nav("home")
                    else:
                        st.error("Wellness ID not found. Please check and try again, or create a new account.")
                else:
                    st.warning("Please enter your Wellness ID.")

        st.markdown('<div class="ss-divider">or</div>', unsafe_allow_html=True)
        if st.button("← Back to home", use_container_width=True): nav("landing")

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def page_admin_login():
    navbar()
    st.markdown("""
    <div class="ss-auth">
      <h2>Admin Portal</h2>
      <p>Sign in with your Admin Wellness ID</p>
    </div>""", unsafe_allow_html=True)

    _,c,_ = st.columns([1,3,1])
    with c:
        aid = st.text_input("Admin Wellness ID", placeholder="e.g. WL123456")
        if st.button("Access Admin Portal", use_container_width=True, type="primary"):
            if aid.strip():
                st.session_state.user_id     = "admin_" + aid
                st.session_state.username    = "Admin Dashboard"
                st.session_state.wellness_id = aid.upper()
                st.session_state.is_admin    = True
                nav("admin_dashboard")
            else:
                st.warning("Please enter your Admin Wellness ID.")
        st.markdown('<div class="ss-divider">or</div>', unsafe_allow_html=True)
        if st.button("Create Admin Account", use_container_width=True):
            data = api_register()
            if data:
                st.session_state.user_id     = data["id"]
                st.session_state.username    = "Admin Dashboard"
                st.session_state.wellness_id = data["wellness_id"]
                st.session_state.is_admin    = True
                nav("admin_dashboard")
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("← Back to home", use_container_width=True): nav("landing")

# ══════════════════════════════════════════════════════════════════════════════
#  HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)

    pts    = st.session_state.total_points
    badges = len(st.session_state.badges)
    badge_str = "  ".join(["🏅"]*min(badges,5)) if badges else "—"

    st.markdown(f"""
    <div class="ss-h2" style="margin-bottom:4px">Welcome to Your Sanctuary</div>
    <p class="ss-sub">A safe, anonymous space for your mental wellness journey</p>
    <div class="ss-stats">
      <div class="ss-stat">
        <div class="ss-stat-num">{pts}</div>
        <div class="ss-stat-lbl">Points</div>
      </div>
      <div class="ss-stat">
        <div class="ss-stat-num">{badges}</div>
        <div class="ss-stat-lbl">Badges</div>
      </div>
      <div class="ss-stat">
        <div class="ss-stat-num" style="font-size:20px">{badge_str if badges else "—"}</div>
        <div class="ss-stat-lbl">Recent</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Mood quick log
    st.markdown("""
    <div class="ss-card" style="margin-bottom:10px;display:flex;align-items:center;gap:16px;padding:14px 18px">
      <div style="font-size:22px">🌤️</div>
      <div>
        <div style="font-weight:600;font-size:14px;color:#1C1C1C;margin-bottom:2px">How are you feeling today?</div>
        <div style="font-size:12px;color:#9A9A9A">Log your mood to earn +10 points</div>
      </div>
    </div>""", unsafe_allow_html=True)

    m_cols = st.columns(5)
    for i,(emoji,lbl) in enumerate([("😄","Great"),("🙂","Good"),("😐","Okay"),("😔","Low"),("😢","Sad")]):
        with m_cols[i]:
            if st.button(f"{emoji} {lbl}", key=f"hm_{i}", use_container_width=True):
                st.session_state.mood_log.append({"emoji":emoji,"label":lbl,"time":datetime.now().strftime("%H:%M")})
                st.session_state.total_points += 10
                if "Mood Logger" not in st.session_state.badges:
                    st.session_state.badges.append("Mood Logger")
                st.toast(f"Logged {emoji} {lbl} · +10 pts")
                time.sleep(0.6); st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Emotion Timeline (shown if user has chatted)
    if st.session_state.emotion_timeline:
        recent = st.session_state.emotion_timeline[-5:]
        traj = st.session_state.get("predictor_trajectory", "stable")
        traj_html = {"declining": "📉 Declining", "stable": "📊 Stable", "improving": "📈 Improving"}.get(traj, "📊 Stable")
        traj_color = {"declining": "#C0392B", "stable": "#9A9A9A", "improving": "#2E6B4F"}.get(traj, "#9A9A9A")
        st.markdown(f"""
        <div class="ss-timeline">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">
            <div class="ss-card-title" style="font-size:17px;margin:0">🧠 Emotion Timeline</div>
            <span style="font-size:12px;font-weight:600;color:{traj_color}">{traj_html}</span>
          </div>""", unsafe_allow_html=True)
        for entry in reversed(recent):
            sent = entry.get("sentiment","neutral")
            cls = "ss-intensity-low" if sent=="positive" else "ss-intensity-high" if sent=="negative" else "ss-timeline-time"
            st.markdown(f"""
            <div class="ss-timeline-row">
              <div class="ss-timeline-emoji">{entry['emoji']}</div>
              <div class="ss-timeline-info">
                <div class="ss-timeline-emotion">{entry['emotion']}</div>
                <div class="ss-timeline-insight">{entry.get('insight','')}</div>
              </div>
              <div style="text-align:right">
                <div class="{cls} ss-timeline-time">{entry.get('intensity','').upper()}</div>
                <div class="ss-timeline-time">{entry.get('time','')}</div>
              </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("💬 Continue Chat", use_container_width=True, type="primary", key="home_chat_emotion"):
            nav("chat")

    # Feature grid (2 columns)
    features = [
        ("💬","AI SUPPORT","Chat with AI","Confidential conversation with our AI therapist","chat","Start Chat"),
        ("📋","ASSESSMENT","Self-Screening","Know your wellness across mood, sleep, stress & behaviour","screening","Begin Screening"),
        ("🎮","ACTIVITIES","Wellness Games","Quizzes, mindfulness and resilience challenges","activities","Explore"),
        ("📚","RESOURCES","Resources & Help","Helplines, articles and professional support","resources","View Resources"),
        ("🗺️","LOCATION","Find Nearby Help","Locate mental health clinics near you","map","Open Map"),
    ]
    for i in range(0, len(features), 2):
        row = features[i:i+2]
        cols = st.columns(len(row))
        for col, (icon,lbl,title,desc,pg,btn) in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="ss-card" style="display:flex;align-items:center;gap:14px;padding:14px 16px;cursor:pointer">
                  <div class="ss-icon-box" style="margin-bottom:0;flex-shrink:0">{icon}</div>
                  <div style="flex:1;min-width:0">
                    <div class="ss-label" style="margin-bottom:2px">{lbl}</div>
                    <div class="ss-card-title" style="font-size:15px;margin-bottom:2px">{title}</div>
                    <div class="ss-card-desc" style="font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{desc}</div>
                  </div>
                  <div style="color:var(--green);font-size:16px;flex-shrink:0">›</div>
                </div>""", unsafe_allow_html=True)
                if st.button(btn, key=f"hf_{pg}", use_container_width=True, type="primary"):
                    nav(pg)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CHAT
# ══════════════════════════════════════════════════════════════════════════════
VOICE_LANGS = {
    "English":"en-US","हिन्दी":"hi-IN","தமிழ்":"ta-IN",
    "বাংলা":"bn-IN","తెలుగు":"te-IN","ಕನ್ನಡ":"kn-IN","മലയാളം":"ml-IN"
}

def page_chat():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)
    st.markdown('<div class="ss-h2">AI Support Chat</div>', unsafe_allow_html=True)
    st.markdown('<p class="ss-sub">A confidential space to express yourself freely</p>', unsafe_allow_html=True)

    if not st.session_state.conversation_id:
        d = api_create_conv()
        if d:
            st.session_state.conversation_id = d["id"]
            # Check for past memory
            mem = api_get_memory()
            st.session_state.has_memory = mem.get("has_memory", False)
            st.session_state.memory_summary = mem.get("memory", "")

    # Show memory banner if returning user
    if st.session_state.has_memory and st.session_state.memory_summary:
        st.markdown(f"""
        <div class="ss-card" style="background:#EAF2EE;border-color:#C3DDD0;padding:14px 18px;margin-bottom:12px">
          <div style="display:flex;align-items:flex-start;gap:10px">
            <div style="font-size:20px">🧠</div>
            <div>
              <div style="font-weight:600;font-size:13px;color:#2E6B4F;margin-bottom:3px">I remember you from our last session</div>
              <div style="font-size:13px;color:#3A6B53;line-height:1.5">{st.session_state.memory_summary.split(chr(10))[0][:200]}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    # Voice expander
    with st.expander("🎙️ Voice Input — click to speak"):
        v_lang = st.selectbox("Language", list(VOICE_LANGS.keys()), key="vlang")
        lc = VOICE_LANGS[v_lang]
        st.components.v1.html(f"""
        <div style="font-family:Inter,sans-serif;padding:6px 0;text-align:center">
          <div id="orb" onclick="toggle()" style="
            width:64px;height:64px;background:#2E6B4F;border-radius:50%;
            display:inline-flex;align-items:center;justify-content:center;
            font-size:26px;cursor:pointer;margin:0 auto 10px;
            animation:orb-pulse 2s infinite;transition:background .2s">🎙️</div>
          <div id="st" style="font-size:13px;color:#5A5A5A;margin-bottom:6px">Click mic to speak</div>
          <div id="tbox" style="background:#F7F5F0;border:1px solid #E8E4DC;border-radius:8px;
            padding:10px 12px;min-height:44px;font-size:14px;color:#1C1C1C;
            margin:8px 0;display:none;text-align:left"></div>
          <div id="cbtn" style="display:none;margin-top:8px">
            <button onclick="copyT()" style="background:#2E6B4F;color:white;border:none;
              border-radius:8px;padding:8px 20px;font-size:13px;font-weight:600;
              cursor:pointer;font-family:Inter,sans-serif">Copy to Chat ↑</button>
          </div>
          <div style="font-size:11px;color:#9A9A9A;margin-top:8px">
            Paste copied text in the chat box below · Chrome only
          </div>
        </div>
        <style>
          @keyframes orb-pulse{{0%{{box-shadow:0 0 0 0 rgba(46,107,79,.4)}}70%{{box-shadow:0 0 0 14px rgba(46,107,79,0)}}100%{{box-shadow:0 0 0 0 rgba(46,107,79,0)}}}}
          @keyframes orb-listen{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}}
        </style>
        <script>
          let rec=null,listen=false,final_t="";
          function toggle(){{listen?stop():start();}}
          function start(){{
            if(!('webkitSpeechRecognition' in window||'SpeechRecognition' in window)){{
              document.getElementById('st').textContent='⚠️ Use Chrome for voice input';return;}}
            const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
            rec=new SR();rec.lang='{lc}';rec.interimResults=true;rec.continuous=false;
            rec.onstart=()=>{{listen=true;final_t='';
              document.getElementById('orb').style.cssText='width:64px;height:64px;background:#C0392B;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:26px;cursor:pointer;margin:0 auto 10px;animation:orb-listen .8s infinite';
              document.getElementById('orb').textContent='⏹️';
              document.getElementById('st').textContent='🔴 Listening…';
              document.getElementById('st').style.color='#C0392B';
              document.getElementById('tbox').style.display='block';
              document.getElementById('tbox').textContent='…';
              document.getElementById('cbtn').style.display='none';
            }};
            rec.onresult=(e)=>{{let interim='';
              for(let i=e.resultIndex;i<e.results.length;i++)
                e.results[i].isFinal?final_t+=e.results[i][0].transcript:interim+=e.results[i][0].transcript;
              document.getElementById('tbox').textContent=final_t||interim||'…';
            }};
            rec.onend=()=>{{listen=false;
              document.getElementById('orb').style.cssText='width:64px;height:64px;background:#2E6B4F;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:26px;cursor:pointer;margin:0 auto 10px;animation:orb-pulse 2s infinite';
              document.getElementById('orb').textContent='🎙️';
              if(final_t){{document.getElementById('st').textContent='✅ Done — copy and paste below';
                document.getElementById('st').style.color='#2E6B4F';
                document.getElementById('cbtn').style.display='block';}}
              else{{document.getElementById('st').textContent='No speech detected. Try again.';
                document.getElementById('st').style.color='#5A5A5A';}}
            }};
            rec.onerror=(e)=>{{listen=false;
              document.getElementById('orb').style.background='#2E6B4F';
              document.getElementById('orb').textContent='🎙️';
              document.getElementById('st').textContent=e.error==='not-allowed'?'⚠️ Allow mic in browser':'Error: '+e.error;
              document.getElementById('st').style.color='#C0392B';
            }};
            rec.start();
          }}
          function stop(){{if(rec)rec.stop();}}
          function copyT(){{navigator.clipboard.writeText(final_t).then(()=>{{
            document.getElementById('st').textContent='✅ Copied! Paste in chat box ↓';
          }});}}
        </script>""", height=230)

        vt = st.text_input("Or paste text and send:", key="vpaste", placeholder="Paste transcribed text…")
        if st.button("Send Voice Message", use_container_width=True, type="primary") and vt:
            st.session_state.messages.append({"role":"user","content":f"🎙️ {vt}"})
            with st.spinner("Thinking…"):
                r = api_send_msg(vt)
            if r: st.session_state.messages.append({"role":"assistant","content":r["content"]})
            st.rerun()

    # Chat area
    st.markdown('<div class="ss-chat-area">', unsafe_allow_html=True)
    if not st.session_state.messages:
        st.markdown("""
        <div class="ss-bubble-wrap-ai">
          <div class="ss-bubble-ai">Hello! I'm your SafeSpace therapist. I'm here to listen — no judgment. How are you feeling today? 🌿</div>
        </div>""", unsafe_allow_html=True)
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f'<div class="ss-bubble-wrap-user"><div class="ss-bubble-user">{m["content"]}</div></div>', unsafe_allow_html=True)
        else:
            emotion = m.get("ai_emotion", {})
            emotion_tag = ""
            if emotion and emotion.get("primary_emotion"):
                sent = emotion.get("sentiment","neutral")
                cls = "ss-emotion-positive" if sent=="positive" else "ss-emotion-negative" if sent=="negative" else "ss-emotion-neutral"
                emoji = emotion.get("emoji","")
                name  = emotion.get("primary_emotion","").capitalize()
                intensity = emotion.get("intensity","")
                intensity_cls = f"ss-intensity-{intensity}"
                emotion_tag = f'<div style="margin-top:5px"><span class="ss-emotion-tag {cls}">{emoji} {name}</span> <span class="{intensity_cls}">{intensity.upper()}</span></div>'
            st.markdown(f'<div class="ss-bubble-wrap-ai"><div class="ss-bubble-ai">{m["content"]}{emotion_tag}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Show AI Crisis Predictor warning if detected
    pw = st.session_state.get("predictor_warning")
    if pw:
        level = pw.get("level", "moderate")
        msg   = pw.get("message") or "I notice some patterns in our conversation that I want to check in about."
        traj  = pw.get("trajectory", "stable")
        rec   = pw.get("recommendation", "none")
        patterns = pw.get("patterns", [])
        
        cls_map = {"moderate": "ss-predictor-moderate", "high": "ss-predictor-high"}
        icon_map = {"moderate": "⚠️", "high": "🔴"}
        label_map = {"moderate": "Wellness Check-in", "high": "Important Notice"}
        color_map = {"moderate": "#D4860A", "high": "#C0392B"}
        
        cls   = cls_map.get(level, "ss-predictor-moderate")
        icon  = icon_map.get(level, "⚠️")
        label = label_map.get(level, "Notice")
        color = color_map.get(level, "#D4860A")

        traj_indicator = "📉 Declining pattern" if traj == "declining" else "📊 Stable" if traj == "stable" else "📈 Improving"

        st.markdown(f"""
        <div class="{cls}">
          <div style="font-size:22px;flex-shrink:0">{icon}</div>
          <div class="ss-predictor-text">
            <div class="ss-predictor-label" style="color:{color}">{label} · {traj_indicator}</div>
            <div style="color:#1C1C1C;margin-bottom:6px">{msg}</div>
            {"<div style='font-size:12px;color:#9A9A9A'>Patterns noticed: " + ", ".join(patterns[:3]) + "</div>" if patterns else ""}
          </div>
        </div>""", unsafe_allow_html=True)

        # Show resource suggestion based on recommendation
        if rec == "suggest_resources":
            c1, c2 = st.columns(2)
            with c1:
                if st.button("📚 View Resources", key="pred_res", use_container_width=True):
                    nav("resources")
            with c2:
                if st.button("✓ I'm okay, continue", key="pred_ok", use_container_width=True):
                    st.session_state.predictor_warning = None
                    st.rerun()
        elif rec in ["suggest_professional", "immediate_support"]:
            st.session_state.show_crisis_alert = True
            if st.button("✓ I'm okay, continue", key="pred_ok2", use_container_width=True):
                st.session_state.predictor_warning = None
                st.rerun()

    ui = st.chat_input("Share what's on your mind…")
    if ui:
        st.session_state.messages.append({"role":"user","content":ui})

        # Client-side crisis check (instant)
        if check_crisis_in_message(ui):
            st.session_state.show_crisis_alert = True

        with st.spinner("Analysing your message…"):
            r = api_send_msg(ui)
        if r:
            ai_emotion = r.get("ai_emotion", {})
            ai_crisis  = r.get("ai_crisis", {})
            st.session_state.messages.append({
                "role": "assistant",
                "content": r["content"],
                "ai_emotion": ai_emotion,
            })
            # Store in emotion timeline
            if ai_emotion:
                st.session_state.emotion_timeline.append({
                    "emoji":   ai_emotion.get("emoji", "😐"),
                    "emotion": ai_emotion.get("primary_emotion", "neutral").capitalize(),
                    "insight": ai_emotion.get("insight", ""),
                    "intensity": ai_emotion.get("intensity", "low"),
                    "sentiment": ai_emotion.get("sentiment", "neutral"),
                    "time": datetime.now().strftime("%H:%M"),
                    "message_preview": ui[:40] + "…" if len(ui) > 40 else ui,
                })
            # Process AI crisis prediction
            if ai_crisis:
                risk_lvl = ai_crisis.get("risk_level", "low")
                trajectory = ai_crisis.get("trajectory", "stable")
                warning = ai_crisis.get("warning_message")
                st.session_state.predictor_trajectory = trajectory
                if risk_lvl in ["moderate", "high"]:
                    st.session_state.predictor_warning = {
                        "level": risk_lvl,
                        "message": warning,
                        "patterns": ai_crisis.get("patterns_detected", []),
                        "recommendation": ai_crisis.get("recommendation", "none"),
                        "trajectory": trajectory,
                    }
                else:
                    st.session_state.predictor_warning = None
            st.session_state.total_points += 5
            if r.get("crisis_detected"):
                st.session_state.show_crisis_alert = True
            if len(st.session_state.messages)>=6 and "Conversationalist" not in st.session_state.badges:
                st.session_state.badges.append("Conversationalist")
        else:
            st.session_state.messages.append({"role":"assistant","content":"I'm having a temporary issue. Please try again. 💚"})
        st.rerun()

    # Show crisis alert overlay if triggered
    render_crisis_alert()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Back to Home", key="chat_back", use_container_width=True):
            # Save conversation summary to memory before leaving
            if st.session_state.messages and len(st.session_state.messages) >= 4:
                with st.spinner("💾 Saving session to memory…"):
                    api_summarize_conversation()
                st.session_state.conversation_id = None
            nav("home")
    with col2:
        if st.button("💾 Save & End Session", key="chat_save", use_container_width=True, type="primary"):
            if st.session_state.messages and len(st.session_state.messages) >= 2:
                with st.spinner("🧠 Summarising session…"):
                    result = api_summarize_conversation()
                if result and result.get("summary"):
                    st.success("✅ Session saved to memory! I'll remember this next time.")
                    if "Memory Keeper" not in st.session_state.badges:
                        st.session_state.badges.append("Memory Keeper")
                        st.session_state.total_points += 20
                    time.sleep(1.5)
                st.session_state.conversation_id = None
            nav("home")

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SCREENING
# ══════════════════════════════════════════════════════════════════════════════
def page_screening():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)

    if not st.session_state.screening_active and not st.session_state.screening_results:
        st.markdown('<div class="ss-h2">Wellness Self-Screening</div>', unsafe_allow_html=True)
        st.markdown('<p class="ss-sub">Know your mental health across 4 key dimensions</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="ss-card">
          <div class="ss-icon-box">🧠</div>
          <div class="ss-card-title">Mental Wellness Assessment</div>
          <div class="ss-card-desc" style="margin-top:6px">
            16 guided questions across:<br><br>
            <strong>😊 Mood</strong> — Emotional patterns and outlook<br>
            <strong>😴 Sleep</strong> — Quality and sleep habits<br>
            <strong>😤 Stress</strong> — Stress levels and coping strategies<br>
            <strong>🏃 Behaviour</strong> — Lifestyle and social patterns<br><br>
            <span style="font-style:italic;color:#9A9A9A">Not a medical diagnosis — a wellness guide.</span>
          </div>
        </div>""", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("← Back", use_container_width=True): nav("home")
        with c2:
            if st.button("Begin Screening →", use_container_width=True, type="primary"):
                d = api_start_screening()
                if d:
                    st.session_state.screening_active = True
                    st.session_state.current_screening = d
                    st.rerun()
                else:
                    st.error("Could not start. Ensure backend is running.")

    elif st.session_state.screening_active and st.session_state.current_screening:
        s  = st.session_state.current_screening
        qid = s.get("question_id","")
        cat = qid.split("_")[0] if "_" in qid else "mood"
        q_num = int(qid.split("_")[1]) if "_" in qid else 1
        total = 16
        cat_labels = {"mood":"😊 Mood","sleep":"😴 Sleep","stress":"😤 Stress","behavior":"🏃 Behaviour"}

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#9A9A9A;margin-bottom:6px">
          <span>Question {q_num} of {total}</span><span>{int((q_num/total)*100)}% complete</span>
        </div>
        <div class="ss-progress-wrap"><div class="ss-progress-fill" style="width:{min((q_num/total)*100,100)}%"></div></div>
        <div><span class="ss-cat-badge">{cat_labels.get(cat, cat.capitalize())}</span></div>
        <div class="ss-card"><p style="font-family:'Playfair Display',serif;font-size:20px;color:#1C1C1C;line-height:1.4;margin:0">{s['question']}</p></div>
        """, unsafe_allow_html=True)

        opts = list(s.get("options",{}).values())
        if opts:
            choice = st.radio("", opts, label_visibility="collapsed", key=f"sq_{qid}")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.screening_active = False; nav("home")
            with c2:
                if st.button("Next →", use_container_width=True, type="primary"):
                    for k,v in s["options"].items():
                        if v == choice:
                            res = api_answer(s["question_id"], int(k))
                            if res:
                                if res.get("status") == "completed":
                                    st.session_state.screening_active = False
                                    st.session_state.screening_results = res.get("results", res)
                                    st.session_state.total_points += 50
                                    if "Wellness Seeker" not in st.session_state.badges:
                                        st.session_state.badges.append("Wellness Seeker")
                                else:
                                    st.session_state.current_screening = res
                                st.rerun()
                            break

    elif st.session_state.screening_results:
        r        = st.session_state.screening_results
        overall  = r.get("overall_score", 0)
        risk     = r.get("risk_level","low")
        cat_sc   = r.get("category_scores", {})
        recs     = r.get("recommendations", {})

        pill_map = {"low":("ss-pill-green","✅ Low Risk"),"moderate":("ss-pill-amber","⚠️ Moderate Risk"),"high":("ss-pill-red","🔴 High Risk")}
        pill_cls, pill_lbl = pill_map.get(risk, ("ss-pill-green","Low Risk"))

        st.markdown(f"""
        <div class="ss-h2" style="margin-bottom:4px">Your Results</div>
        <p class="ss-sub">Wellness assessment completed</p>
        <div class="ss-card" style="text-align:center;padding:32px">
          <div style="font-size:64px;font-weight:700;color:#1C1C1C;line-height:1">{int(overall)}</div>
          <div style="font-size:13px;color:#9A9A9A;margin:6px 0 14px">Risk Score (0 = best, 100 = most concern)</div>
          <span class="ss-pill {pill_cls}">{pill_lbl}</span>
        </div>""", unsafe_allow_html=True)

        # Category breakdown
        cat_labels = {"mood":"😊 Mood","sleep":"😴 Sleep","stress":"😤 Stress","behavior":"🏃 Behaviour"}
        st.markdown('<div class="ss-card"><div class="ss-card-title" style="margin-bottom:14px">Category Breakdown</div>', unsafe_allow_html=True)
        for cat, score in cat_sc.items():
            bar_color = "#C0392B" if score>=60 else "#D4860A" if score>=40 else "#2E6B4F"
            st.markdown(f"""
            <div class="ss-cat-row">
              <div class="ss-cat-name">{cat_labels.get(cat,cat)}</div>
              <div class="ss-bar-wrap"><div class="ss-bar-fill" style="width:{min(score,100)}%;background:{bar_color}"></div></div>
              <div class="ss-cat-score" style="color:{bar_color}">{int(score)}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        interp = recs.get("overall_assessment",{}).get("interpretation","")
        if interp:
            st.markdown(f'<div class="ss-card"><div class="ss-icon-box">💡</div><div class="ss-card-title">Interpretation</div><p class="ss-card-desc" style="margin-top:6px">{interp}</p></div>', unsafe_allow_html=True)

        steps = recs.get("next_steps",[])
        if steps:
            rows = "".join([f"<div style='padding:8px 0;border-bottom:1px solid var(--border);font-size:14px;color:#5A5A5A'><span style='color:#2E6B4F;font-weight:600'>→</span> {s}</div>" for s in steps])
            st.markdown(f'<div class="ss-card"><div class="ss-card-title" style="margin-bottom:12px">Recommended Next Steps</div>{rows}</div>', unsafe_allow_html=True)

        if risk == "high":
            st.session_state.show_crisis_alert = True
            st.markdown("""
            <div class="ss-crisis">
              <div class="title">🆘 Immediate Support Available</div>
              <div class="body">
                <strong>iCall (India):</strong> 9152987821<br>
                <strong>Vandrevala Foundation:</strong> 1860-2662-345 (24/7)<br>
                <strong>Crisis Text Line:</strong> Text HOME to 741741
              </div>
            </div>""", unsafe_allow_html=True)
            render_crisis_alert()

        c1,c2 = st.columns(2)
        with c1:
            if st.button("Retake Screening", use_container_width=True):
                st.session_state.screening_results = None
                st.session_state.current_screening = None
                st.session_state.ai_report = None
                st.rerun()
        with c2:
            if st.button("← Back to Home", use_container_width=True, type="primary"): nav("home")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # AI Report Section
        st.markdown("""
        <div class="ss-card" style="background:var(--green-lt);border-color:#C3DDD0;padding:18px 22px">
          <div style="display:flex;align-items:center;gap:12px">
            <div style="font-size:28px">🤖</div>
            <div>
              <div style="font-weight:600;font-size:15px;color:#2E6B4F">AI Personalised Report</div>
              <div style="font-size:13px;color:#4A8C68;margin-top:2px">
                Get a detailed AI-written report explaining your results with tailored advice
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

        if st.session_state.ai_report is None:
            if st.button("✨ Generate My AI Report", use_container_width=True, type="primary", key="gen_report"):
                with st.spinner("🤖 AI is analysing your results and writing your personalised report… (this takes 15-20 seconds)"):
                    report_data = api_generate_report({
                        "overall_score": overall,
                        "risk_level": risk,
                        "category_scores": cat_sc,
                        "responses": r.get("responses", {}),
                    })
                if report_data:
                    st.session_state.ai_report = report_data.get("report", "")
                    if "Report Writer" not in st.session_state.badges:
                        st.session_state.badges.append("Report Writer")
                        st.session_state.total_points += 30
                    st.rerun()
                else:
                    st.error("Could not generate report. Please ensure the backend is running.")

        else:
            # Display the generated report
            report_text = st.session_state.ai_report
            generated_at = datetime.now().strftime("%B %d, %Y at %H:%M")

            st.markdown(f"""
            <div class="ss-report">
              <div class="ss-report-header">
                <div class="icon">📋</div>
                <div>
                  <div class="title">Your Personalised Wellness Report</div>
                  <div class="sub">Generated by AI on {generated_at} · Wellness ID: {st.session_state.wellness_id}</div>
                </div>
              </div>""", unsafe_allow_html=True)

            # Render report sections
            import re
            sections = re.split(r'(## .+)', report_text)
            report_html = ""
            for section in sections:
                if section.startswith("## "):
                    report_html += f"<h2>{section[3:]}</h2>"
                else:
                    lines = section.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        if line.startswith("- ") or line.startswith("* "):
                            report_html += f"<ul><li>{line[2:]}</li></ul>"
                        elif re.match(r'^\d+\.', line):
                            report_html += f"<ul><li>{re.sub(r'^\d+\.\s*', '', line)}</li></ul>"
                        else:
                            report_html += f"<p>{line}</p>"

            st.markdown(report_html + "</div>", unsafe_allow_html=True)

            # Download as text
            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    "⬇️ Download Report",
                    data=f"SAFESPACE WELLNESS REPORT\n{'='*40}\nGenerated: {generated_at}\nWellness ID: {st.session_state.wellness_id}\nRisk Level: {risk.upper()}\nOverall Score: {int(overall)}/100\n{'='*40}\n\n{report_text}",
                    file_name=f"safespace_report_{st.session_state.wellness_id}.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with c2:
                if st.button("🔄 Regenerate Report", use_container_width=True):
                    st.session_state.ai_report = None
                    st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ACTIVITIES
# ══════════════════════════════════════════════════════════════════════════════
QS = [
    {"q":"Which is a healthy stress-management strategy?","opts":["Ignore it","Deep breathing","More caffeine","Work longer"],"ans":1,"exp":"Deep breathing activates the parasympathetic nervous system, reducing cortisol."},
    {"q":"How many hours of sleep do adults need per night?","opts":["4–5 hrs","5–6 hrs","7–9 hrs","10–12 hrs"],"ans":2,"exp":"7–9 hours supports optimal physical and mental health for adults."},
    {"q":"Which is NOT recommended for mental wellness?","opts":["Exercise","Social isolation","Journaling","Meditation"],"ans":1,"exp":"Social isolation worsens mental health. Human connection is essential."},
    {"q":"What does mindfulness mean?","opts":["Planning the future","Present-moment awareness","Avoiding stress","Hours of meditation"],"ans":1,"exp":"Mindfulness means paying attention to the present moment without judgment."},
    {"q":"Which is a key sign of burnout?","opts":["High energy","Better sleep","Emotional exhaustion","Improved focus"],"ans":2,"exp":"Emotional exhaustion, cynicism, and reduced performance define burnout."},
]
BREATH = [
    {"icon":"🌬️","title":"Inhale","desc":"Breathe in slowly and deeply through your nose","secs":4},
    {"icon":"⏸️","title":"Hold","desc":"Gently hold your breath","secs":4},
    {"icon":"💨","title":"Exhale","desc":"Release slowly through your mouth","secs":6},
    {"icon":"⏸️","title":"Rest","desc":"Pause before the next breath","secs":2},
]

def page_activities():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)
    st.markdown('<div class="ss-h2">Wellness Activities</div>', unsafe_allow_html=True)
    st.markdown('<p class="ss-sub">Earn points and unlock badges through interactive challenges</p>', unsafe_allow_html=True)

    pts = st.session_state.total_points
    bgs = len(st.session_state.badges)
    st.markdown(f"""
    <div class="ss-card" style="background:var(--green-lt);border-color:#C3DDD0;padding:14px 20px;display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div style="font-size:14px;color:var(--green);font-weight:600">🏆 {pts} Points</div>
      <div style="font-size:13px;color:#4A8C68">🏅 {bgs} Badge{"s" if bgs!=1 else ""} earned</div>
    </div>""", unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["🧠 Stress Quiz","😊 Mood Tracker","🧘 Mindfulness","🏅 Badges"])

    with tab1:
        qs = st.session_state.quiz_state
        if qs is None:
            st.markdown("""
            <div class="ss-card">
              <div class="ss-icon-box">🧠</div>
              <div class="ss-card-title">Stress Awareness Quiz</div>
              <p class="ss-card-desc" style="margin-top:6px">5 questions on stress, sleep, and mental wellness strategies. Earn up to 50 points!</p>
            </div>""", unsafe_allow_html=True)
            if st.button("Start Quiz →", use_container_width=True, type="primary"):
                st.session_state.quiz_state = {"index":0,"score":0,"answered":False,"selected":None}
                st.rerun()
        else:
            idx = qs["index"]
            if idx < len(QS):
                q = QS[idx]
                pct = int((idx/len(QS))*100)
                st.markdown(f"""
                <div style="display:flex;justify-content:space-between;font-size:12px;color:#9A9A9A;margin-bottom:6px">
                  <span>Question {idx+1} of {len(QS)}</span><span>{pct}% done</span>
                </div>
                <div class="ss-progress-wrap"><div class="ss-progress-fill" style="width:{pct}%"></div></div>
                <div class="ss-card"><p style="font-family:'Playfair Display',serif;font-size:18px;line-height:1.45;margin:0">{q['q']}</p></div>
                """, unsafe_allow_html=True)
                if not qs["answered"]:
                    for i,opt in enumerate(q["opts"]):
                        if st.button(opt, key=f"qo_{idx}_{i}", use_container_width=True):
                            qs["selected"] = i; qs["answered"] = True
                            if i == q["ans"]: qs["score"]+=10; st.session_state.total_points+=10
                            st.rerun()
                else:
                    sel = qs["selected"]
                    for i,opt in enumerate(q["opts"]):
                        if i == q["ans"]:    st.success(f"✅ {opt}")
                        elif i == sel:       st.error(f"❌ {opt}")
                        else:                st.markdown(f'<div style="padding:10px 14px;background:#F7F5F0;border-radius:8px;margin-bottom:6px;font-size:14px;color:#9A9A9A">{opt}</div>', unsafe_allow_html=True)
                    st.info(f"💡 {q['exp']}")
                    if st.button("Next Question →", use_container_width=True, type="primary"):
                        qs["index"]+=1; qs["answered"]=False; qs["selected"]=None; st.rerun()
            else:
                sc = qs["score"]; pct = int((sc/50)*100)
                st.markdown(f"""
                <div class="ss-card" style="text-align:center;padding:36px 24px">
                  <div style="font-size:56px;font-weight:700;color:#2E6B4F">{sc}</div>
                  <div style="font-size:13px;color:#9A9A9A;margin:6px 0 14px">Points earned · {pct}% correct</div>
                  <div style="font-size:16px">{'🏆 Excellent!' if pct>=80 else '👍 Good effort!' if pct>=60 else '📚 Keep practising!'}</div>
                </div>""", unsafe_allow_html=True)
                if pct>=80 and "Quiz Master" not in st.session_state.badges:
                    st.session_state.badges.append("Quiz Master"); st.balloons()
                if st.button("Retake Quiz", use_container_width=True, type="primary"):
                    st.session_state.quiz_state = None; st.rerun()

    with tab2:
        st.markdown('<div class="ss-card-title" style="margin-bottom:6px">Daily Mood Log</div>', unsafe_allow_html=True)
        st.markdown('<p class="ss-card-desc" style="margin-bottom:18px">Log your mood daily to track patterns and earn points.</p>', unsafe_allow_html=True)
        mc = st.columns(5)
        for i,(e,l,v) in enumerate([("😄","Great",5),("🙂","Good",4),("😐","Okay",3),("😔","Low",2),("😢","Sad",1)]):
            with mc[i]:
                if st.button(f"{e} {l}", key=f"mt_{i}", use_container_width=True):
                    st.session_state.mood_log.append({"emoji":e,"label":l,"val":v,"time":datetime.now().strftime("%I:%M %p")})
                    st.session_state.total_points+=10
                    if len(st.session_state.mood_log)>=5 and "Mood Tracker" not in st.session_state.badges:
                        st.session_state.badges.append("Mood Tracker")
                    st.rerun()
        if st.session_state.mood_log:
            st.markdown('<div class="ss-card" style="margin-top:14px"><div class="ss-card-title" style="margin-bottom:12px;font-size:16px">Recent Entries</div>', unsafe_allow_html=True)
            for entry in reversed(st.session_state.mood_log[-8:]):
                st.markdown(f"""
                <div class="ss-mood-entry">
                  <div style="font-size:22px">{entry['emoji']}</div>
                  <div style="font-weight:500;font-size:14px">{entry['label']}</div>
                  <div class="ss-mood-time">{entry.get('time','')}</div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="ss-card" style="text-align:center;padding:28px;color:#9A9A9A">Log your first mood above to get started!</div>', unsafe_allow_html=True)

    with tab3:
        step = st.session_state.mindfulness_step
        s    = BREATH[step]
        st.markdown(f"""
        <div class="ss-card" style="text-align:center;padding:36px 24px">
          <div style="font-size:52px;margin-bottom:12px">{s['icon']}</div>
          <div style="font-family:'Playfair Display',serif;font-size:26px;margin-bottom:8px">{s['title']}</div>
          <p style="font-size:15px;color:#5A5A5A;margin-bottom:16px">{s['desc']}</p>
          <div style="font-size:44px;font-weight:700;color:#2E6B4F">{s['secs']}</div>
          <div style="font-size:12px;color:#9A9A9A;margin-top:4px">seconds</div>
        </div>""", unsafe_allow_html=True)
        prog = int((step/len(BREATH))*100)
        st.markdown(f'<div class="ss-progress-wrap"><div class="ss-progress-fill" style="width:{prog}%"></div></div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.mindfulness_step = max(0,step-1); st.rerun()
        with c2:
            if step < len(BREATH)-1:
                if st.button("Next →", use_container_width=True, type="primary"):
                    st.session_state.mindfulness_step += 1; st.rerun()
            else:
                if st.button("✅ Complete Session", use_container_width=True, type="primary"):
                    st.session_state.mindfulness_step = 0
                    st.session_state.total_points += 20
                    if "Mindful Soul" not in st.session_state.badges:
                        st.session_state.badges.append("Mindful Soul")
                    st.balloons()
                    st.toast("Session complete! +20 pts 🧘")
        st.markdown("""
        <div class="ss-card" style="margin-top:12px">
          <div class="ss-card-title" style="font-size:15px;margin-bottom:6px">Why Box Breathing?</div>
          <p class="ss-card-desc">The 4-4-6-2 pattern activates the body's relaxation response, lowers cortisol, and reduces anxiety. Practise for 5 minutes daily for best results.</p>
        </div>""", unsafe_allow_html=True)

    with tab4:
        ALL_BADGES = [
            ("🌱","Mood Logger","Log your first mood"),
            ("📊","Mood Tracker","Log 5 moods"),
            ("💬","Conversationalist","Complete 3 chat exchanges"),
            ("🔍","Wellness Seeker","Complete the self-screening"),
            ("🏆","Quiz Master","Score 80%+ on the stress quiz"),
            ("🧘","Mindful Soul","Complete a mindfulness session"),
        ]
        earned = st.session_state.badges
        st.markdown(f'<div class="ss-card-title" style="margin-bottom:4px">Your Badges</div><p class="ss-sub">{len(earned)} of {len(ALL_BADGES)} earned</p>', unsafe_allow_html=True)
        for icon,name,desc in ALL_BADGES:
            cls = "earned" if name in earned else ""
            chk = '<div class="ss-badge-check">✓</div>' if name in earned else ""
            st.markdown(f"""
            <div class="ss-badge-card {cls}">
              <div class="ss-badge-icon">{icon}</div>
              <div>
                <div class="ss-badge-name" style="{'color:#2E6B4F' if name in earned else ''}">{name}</div>
                <div class="ss-badge-desc">{desc}</div>
              </div>
              {chk}
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Home", key="act_back"): nav("home")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  RESOURCES
# ══════════════════════════════════════════════════════════════════════════════
def page_resources():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)
    st.markdown('<div class="ss-h2">Mental Health Resources</div>', unsafe_allow_html=True)
    st.markdown('<p class="ss-sub">Curated helplines, guides and professional support</p>', unsafe_allow_html=True)

    resources = [
        ("📞","CRISIS — INDIA","iCall","9152987821 · Mon–Sat 8am–10pm","","#FDECEA","#C0392B"),
        ("📞","CRISIS — INDIA","Vandrevala Foundation","1860-2662-345 · Available 24 / 7","","#FDECEA","#C0392B"),
        ("💬","GLOBAL","Crisis Text Line","Text HOME to 741741 for immediate support","","#FEF3DC","#D4860A"),
        ("📖","SELF-HELP","Mind.org.uk","Mental health information and guidance","https://www.mind.org.uk","#FFFFFF","#1C1C1C"),
        ("🏥","ORGANISATION","NAMI","National Alliance on Mental Illness","https://www.nami.org","#FFFFFF","#1C1C1C"),
        ("🧘","APP","Headspace","Guided meditation and mindfulness","https://www.headspace.com","#FFFFFF","#1C1C1C"),
        ("🎵","APP","Calm","Sleep stories and relaxation","https://www.calm.com","#FFFFFF","#1C1C1C"),
    ]
    for icon,lbl,title,desc,url,bg,tc in resources:
        link = f' <a href="{url}" target="_blank" style="color:#2E6B4F;font-size:12px;font-weight:600;text-decoration:none">Visit →</a>' if url else ""
        st.markdown(f"""
        <div class="ss-card" style="background:{bg}">
          <div style="display:flex;align-items:flex-start;gap:14px">
            <div class="ss-icon-box" style="flex-shrink:0">{icon}</div>
            <div style="flex:1">
              <div class="ss-label" style="margin-bottom:4px">{lbl}</div>
              <div class="ss-card-title" style="color:{tc};font-size:17px">{title}</div>
              <div class="ss-card-desc">{desc}{link}</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)

    if st.button("← Back to Home", key="res_back"): nav("home")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  MAP
# ══════════════════════════════════════════════════════════════════════════════
def page_map():
    navbar()
    st.markdown('<div class="ss-page">', unsafe_allow_html=True)
    st.markdown('<div class="ss-h2">Find Nearby Help</div>', unsafe_allow_html=True)
    st.markdown('<p class="ss-sub">Locate mental health clinics and therapists near you</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="ss-card" style="padding:14px 20px;margin-bottom:14px">
      <p style="font-size:13px;color:#5A5A5A;margin:0">
        🔍 Searches for <strong>mental health clinics, hospitals, psychotherapists and counsellors</strong>
        using OpenStreetMap. Enter any city or use your GPS location.
      </p>
    </div>""", unsafe_allow_html=True)

    c1,c2 = st.columns([4,1])
    with c1:
        loc = st.text_input("Search location", placeholder="e.g. Mumbai, Pune, Delhi…", label_visibility="collapsed")
    with c2:
        search = st.button("Search", use_container_width=True, type="primary")

    search_q = loc.strip() if loc.strip() else "Pune, India"

    st.components.v1.html(f"""
    <!DOCTYPE html><html><head><meta charset="utf-8"/>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <style>
      body{{margin:0;padding:0;font-family:Inter,sans-serif}}
      #map{{width:100%;height:440px;border-radius:12px;border:1px solid #E8E4DC}}
      .ctrl{{display:flex;gap:8px;margin-bottom:10px}}
      .ctrl input{{flex:1;padding:9px 14px;border-radius:8px;border:1px solid #E8E4DC;font-size:13px;outline:none}}
      .ctrl input:focus{{border-color:#2E6B4F}}
      .btn{{background:#2E6B4F;color:white;border:none;border-radius:8px;padding:9px 16px;font-size:13px;font-weight:600;cursor:pointer}}
      .btn:hover{{background:#245840}}
      .btn-o{{background:white;color:#2E6B4F;border:1px solid #2E6B4F;border-radius:8px;padding:9px 14px;font-size:13px;font-weight:600;cursor:pointer}}
      #status{{font-size:13px;color:#9A9A9A;padding:8px 0;text-align:center}}
      #results{{margin-top:10px;max-height:260px;overflow-y:auto}}
      .pcard{{background:white;border:1px solid #E8E4DC;border-radius:10px;padding:12px 14px;margin-bottom:8px;cursor:pointer;border-left:3px solid #2E6B4F}}
      .pcard:hover{{border-color:#2E6B4F;box-shadow:0 2px 8px rgba(0,0,0,.08)}}
      .pname{{font-weight:600;font-size:14px;color:#1C1C1C;margin-bottom:3px}}
      .ptype{{font-size:11px;font-weight:700;color:#2E6B4F;text-transform:uppercase;letter-spacing:.5px;margin-bottom:3px}}
      .paddr{{font-size:12px;color:#9A9A9A}}
    </style></head><body>
    <div class="ctrl">
      <input type="text" id="li" placeholder="Enter city or area…" value="{search_q}"/>
      <button class="btn" onclick="search()">Search</button>
      <button class="btn-o" onclick="myLoc()">📍 Me</button>
    </div>
    <div id="map"></div>
    <div id="status">Enter a location and click Search</div>
    <div id="results"></div>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      var map=L.map('map').setView([18.52,73.86],13);
      L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',{{attribution:'© OpenStreetMap',maxZoom:19}}).addTo(map);
      var markers=[],gIcon=L.divIcon({{html:'<div style="background:#2E6B4F;width:26px;height:26px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid white;box-shadow:0 2px 6px rgba(0,0,0,.3)"></div>',iconSize:[26,26],iconAnchor:[13,26],popupAnchor:[0,-26],className:''}});
      function clr(){{markers.forEach(m=>map.removeLayer(m));markers=[];}}
      function search(){{
        var q=document.getElementById('li').value.trim();if(!q)return;
        document.getElementById('status').textContent='Searching…';document.getElementById('results').innerHTML='';
        fetch('https://nominatim.openstreetmap.org/search?format=json&q='+encodeURIComponent(q)+'&limit=1')
        .then(r=>r.json()).then(d=>{{if(!d.length){{document.getElementById('status').textContent='Location not found.';return;}}
        map.setView([+d[0].lat,+d[0].lon],14);nearby(+d[0].lat,+d[0].lon);}}).catch(()=>document.getElementById('status').textContent='Search failed.');
      }}
      function myLoc(){{if(!navigator.geolocation)return;document.getElementById('status').textContent='Getting location…';
        navigator.geolocation.getCurrentPosition(p=>{{map.setView([p.coords.latitude,p.coords.longitude],14);nearby(p.coords.latitude,p.coords.longitude);}},
        ()=>document.getElementById('status').textContent='Location access denied.');
      }}
      function nearby(lat,lng){{
        clr();document.getElementById('status').textContent='Finding nearby mental health services…';
        L.marker([lat,lng],{{icon:L.divIcon({{html:'<div style="background:#1565c0;width:12px;height:12px;border-radius:50%;border:2px solid white;box-shadow:0 2px 5px rgba(0,0,0,.4)"></div>',iconSize:[12,12],iconAnchor:[6,6],className:''}})}}).addTo(map).bindPopup('<b>Your Location</b>');
        var q=`[out:json][timeout:25];(node["amenity"="clinic"](around:5000,${{lat}},${{lng}});node["amenity"="hospital"](around:5000,${{lat}},${{lng}});node["healthcare"="psychotherapist"](around:5000,${{lat}},${{lng}});node["healthcare"="counsellor"](around:5000,${{lat}},${{lng}});node["healthcare"="centre"](around:5000,${{lat}},${{lng}});way["amenity"="clinic"](around:5000,${{lat}},${{lng}});way["amenity"="hospital"](around:5000,${{lat}},${{lng}}););out center 30;`;
        fetch('https://overpass-api.de/api/interpreter',{{method:'POST',body:q}}).then(r=>r.json()).then(data=>{{
          var els=data.elements||[],res=document.getElementById('results');res.innerHTML='';
          if(!els.length){{document.getElementById('status').textContent='No clinics found. Try a different location.';return;}}
          document.getElementById('status').textContent=`Found ${{els.length}} services nearby`;
          els.slice(0,20).forEach(el=>{{
            var lt=el.lat||el.center?.lat,ln=el.lon||el.center?.lon;if(!lt||!ln)return;
            var nm=el.tags?.name||el.tags?.['name:en']||'Health Centre',
                ad=el.tags?.['addr:street']||el.tags?.['addr:full']||'',
                tp=el.tags?.healthcare||el.tags?.amenity||'clinic',
                ph=el.tags?.phone||el.tags?.['contact:phone']||'',
                tl=tp==='psychotherapist'?'Psychotherapist':tp==='counsellor'?'Counsellor':tp==='hospital'?'Hospital':'Clinic';
            var mk=L.marker([lt,ln],{{icon:gIcon}}).addTo(map).bindPopup(`<div style="font-family:Inter,sans-serif;min-width:180px"><b style="font-size:14px">${{nm}}</b><div style="font-size:11px;color:#2E6B4F;font-weight:700;text-transform:uppercase;margin:4px 0">${{tl}}</div>${{ad?'<div style="font-size:12px;color:#9A9A9A">'+ad+'</div>':''}}${{ph?'<div style="font-size:12px;color:#5A5A5A;margin-top:3px">📞 '+ph+'</div>':''}}</div>`);
            markers.push(mk);
            res.innerHTML+=`<div class="pcard" onclick="map.setView([${{lt}},${{ln}}],17)"><div class="ptype">${{tl}}</div><div class="pname">${{nm}}</div>${{ad?'<div class="paddr">📍 '+ad+'</div>':''}}${{ph?'<div class="paddr">📞 '+ph+'</div>':''}}</div>`;
          }});
        }}).catch(()=>document.getElementById('status').textContent='Could not fetch results.');
      }}
      search();
    </script></body></html>""", height=800, scrolling=True)

    if st.button("← Back to Home", key="map_back"): nav("home")
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def page_admin():
    navbar()
    st.markdown('<div class="ss-page-wide">', unsafe_allow_html=True)
    st.markdown('<div class="ss-h2">Platform Analytics</div>', unsafe_allow_html=True)
    st.markdown('<p class="ss-sub">Live data from the database</p>', unsafe_allow_html=True)

    # Fetch real stats from backend
    with st.spinner("Loading live data…"):
        stats_data = api("get", "/api/admin/stats") or {}

    total_users      = stats_data.get("total_users", 0)
    total_messages   = stats_data.get("total_messages", 0)
    total_screenings = stats_data.get("total_screenings", 0)
    high_risk        = stats_data.get("high_risk", 0)
    moderate_risk    = stats_data.get("moderate_risk", 0)
    low_risk         = stats_data.get("low_risk", 0)
    recent_users     = stats_data.get("recent_users", [])
    engagement       = min(round((total_messages / max(total_users,1)) * 10), 100) if total_users > 0 else 0

    # Stats grid
    stats = [
        ("👥","Total Users", str(total_users), "#2E6B4F"),
        ("📋","Screenings Done", str(total_screenings), "#2E6B4F"),
        ("💬","Chat Messages", str(total_messages), "#2E6B4F"),
        ("🔴","High Risk", str(high_risk), "#C0392B"),
        ("⚠️","Moderate Risk", str(moderate_risk), "#D4860A"),
        ("✅","Low Risk", str(low_risk), "#2E6B4F"),
    ]
    cols = st.columns(3)
    for i,(icon,lbl,val,color) in enumerate(stats):
        with cols[i%3]:
            st.markdown(f"""
            <div class="ss-card" style="text-align:center;padding:20px">
              <div style="font-size:24px;margin-bottom:8px">{icon}</div>
              <div class="ss-stat-num" style="color:{color}">{val}</div>
              <div class="ss-stat-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Engagement banner
    st.markdown(f"""
    <div class="ss-card" style="display:flex;align-items:center;gap:16px;padding:18px 24px">
      <div style="font-size:28px">📊</div>
      <div style="flex:1">
        <div style="font-weight:600;font-size:15px;margin-bottom:3px">Engagement Score</div>
        <div style="font-size:13px;color:#9A9A9A">Based on avg messages per student</div>
      </div>
      <div style="background:var(--green-lt);color:var(--green);font-weight:700;font-size:18px;padding:6px 18px;border-radius:50px">{engagement}%</div>
    </div>""", unsafe_allow_html=True)

    # Risk overview
    st.markdown(f"""
    <div class="ss-card">
      <div class="ss-card-title" style="margin-bottom:14px">Screening Risk Overview</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap">
        <span class="ss-pill ss-pill-green">✅ Low Risk: {low_risk}</span>
        <span class="ss-pill ss-pill-amber">⚠️ Moderate: {moderate_risk}</span>
        <span class="ss-pill ss-pill-red">🔴 High Risk: {high_risk}</span>
      </div>
    </div>""", unsafe_allow_html=True)

    # Recent users from DB
    st.markdown('<div class="ss-card"><div class="ss-card-title" style="margin-bottom:14px">Recent Anonymous Users</div>', unsafe_allow_html=True)
    if recent_users:
        for u in recent_users:
            name = u.get("username","—")
            wid  = u.get("wellness_id","—")
            role = u.get("role","Student")
            date = u.get("created_at","—")
            rc   = "#2E6B4F" if role == "Admin" else "#9A9A9A"
            st.markdown(f"""
            <div class="ss-user-row">
              <div class="ss-avatar">👤</div>
              <div style="flex:1">
                <div class="ss-user-name">{name}</div>
                <div class="ss-user-wid">{wid}</div>
              </div>
              <div style="text-align:right">
                <div class="ss-user-role" style="color:{rc};font-weight:500">{role}</div>
                <div class="ss-user-date">{date}</div>
              </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<p style="padding:16px 0;text-align:center;color:#9A9A9A;font-size:14px">No users registered yet.</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔄 Refresh Stats", use_container_width=True):
        st.rerun()

    # Privacy notice
    st.markdown("""
    <div class="ss-privacy">
      <div style="font-size:22px;flex-shrink:0;margin-top:2px">🔒</div>
      <div class="ss-privacy-body">
        <div class="title">Privacy First</div>
        <div class="body">All user interactions are completely anonymous. Usernames and Wellness IDs cannot be traced back to real identities, ensuring a safe space for mental wellness support.</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
p = st.session_state.page
if   p == "landing":          page_landing()
elif p == "register":         page_register()
elif p == "admin_login":      page_admin_login()
elif p == "home":             page_home()
elif p == "chat":             page_chat()
elif p == "screening":        page_screening()
elif p == "activities":       page_activities()
elif p == "resources":        page_resources()
elif p == "map":              page_map()
elif p == "admin_dashboard":  page_admin()
else:                         page_landing()
