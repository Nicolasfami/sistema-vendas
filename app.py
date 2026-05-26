
import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib
import re
from pathlib import Path

# =========================
# CONFIGURAÇÕES
# =========================

st.set_page_config(page_title="OPERAX SALES", layout="wide")

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# DESIGN FUTURISTA / LOGO
# =========================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(34, 197, 94, 0.13), transparent 28%),
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.14), transparent 30%),
            linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #f8fafc 100%);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(241,245,249,0.96) 100%);
        border-right: 1px solid rgba(15,23,42,0.06);
        min-width: 220px;
        max-width: 220px;
        backdrop-filter: blur(10px);
    }

    section[data-testid="stSidebar"] > div {
        padding-left: 4px;
        padding-right: 4px;
    }

    [data-testid="stSidebar"] * {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: rgba(255,255,255,0.08);
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.18);
        border-radius: 14px;
    }

    [data-testid="stSidebar"] .stRadio label {
        font-size: 16px;
        font-weight: 600;
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(15,23,42,0.06);
        border-radius: 14px;
        padding: 7px 8px;
        margin: 5px 0;
        box-shadow: 0 8px 20px rgba(15,23,42,0.04);
    }

    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(220,252,231,0.88);
        border-color: rgba(34,197,94,0.20);
    }


    h1, h2, h3 {
        color: #111827;
        letter-spacing: -0.04em;
    }

    .crm-hero {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.86), rgba(240,253,250,0.72)),
            linear-gradient(135deg, rgba(34,197,94,0.10), rgba(59,130,246,0.10));
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 28px;
        padding: 24px 28px;
        margin-bottom: 28px;
        box-shadow: 0 22px 70px rgba(15, 23, 42, 0.11);
        backdrop-filter: blur(14px);
    }

    .crm-header {
        display: flex;
        align-items: center;
        gap: 22px;
    }

    .crm-logo-fallback {
        width: 104px;
        height: 104px;
        border-radius: 28px;
        background: linear-gradient(135deg, #0f766e, #22c55e, #38bdf8);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        box-shadow: 0 20px 45px rgba(34, 197, 94, 0.30);
    }

    .crm-title {
        font-size: 48px;
        line-height: 1.02;
        font-weight: 900;
        color: #0f172a;
        margin: 0;
    }

    .crm-subtitle {
        margin: 10px 0 0 0;
        color: #64748b;
        font-size: 16px;
        font-weight: 500;
    }

    .crm-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        margin-top: 12px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(15,118,110,0.10);
        color: #0f766e;
        border: 1px solid rgba(15,118,110,0.16);
        font-weight: 700;
        font-size: 13px;
    }

    .crm-card {
        background: rgba(255, 255, 255, 0.86);
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 18px 55px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(14px);
        margin-bottom: 22px;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.92), rgba(240,253,250,0.72));
        border: 1px solid rgba(15, 23, 42, 0.08);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.08);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: 1px solid rgba(15, 23, 42, 0.08) !important;
        background: rgba(255,255,255,0.86) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
    }

    .stButton button {
        border-radius: 14px;
        padding: 0.62rem 1.1rem;
        font-weight: 800;
        border: 1px solid rgba(15, 118, 110, 0.2);
        background: linear-gradient(135deg, #0f766e, #22c55e);
        color: white;
        box-shadow: 0 12px 26px rgba(34, 197, 94, 0.24);
    }

    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 16px 34px rgba(34, 197, 94, 0.32);
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(15, 23, 42, 0.08);
        box-shadow: 0 14px 38px rgba(15, 23, 42, 0.06);
    }

    hr {
        border-color: rgba(15, 23, 42, 0.08);
    }

    /* =========================================================
       OPERAX SALES — TEMA NEON AZUL / DASHBOARD PREMIUM
       ========================================================= */

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(37,99,235,0.16), transparent 32%),
            linear-gradient(135deg, #eff6ff 0%, #f8fafc 42%, #ffffff 100%) !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
        border-right: 1px solid rgba(56,189,248,0.28) !important;
        min-width: 250px !important;
        max-width: 250px !important;
        box-shadow: 18px 0 45px rgba(14,165,233,0.18) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-top: 18px !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .sidebar-logo-v8 {
        display:flex;
        align-items:center;
        gap:12px;
        padding: 8px 4px 20px 4px;
        color:white;
        font-size:22px;
        font-weight:900;
        letter-spacing: .02em;
    }

    .sidebar-logo-icon-v8 {
        width:48px;
        height:48px;
        border-radius:16px;
        background:
            radial-gradient(circle at 35% 30%, #7dd3fc 0%, #0ea5e9 35%, #1d4ed8 72%, #0f172a 100%);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:24px;
        font-weight:900;
        color:#ffffff;
        box-shadow:
            0 0 28px rgba(56,189,248,0.50),
            inset 0 0 0 1px rgba(255,255,255,0.24);
    }

    .sidebar-user-v8 {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(56,189,248,0.26);
        border-radius: 18px;
        padding: 15px 14px;
        margin: 8px 0 20px 0;
        color: white !important;
        font-weight: 900;
        box-shadow: 0 16px 34px rgba(14,165,233,0.15);
    }

    .menu-label-v8 {
        color: rgba(125,211,252,0.88) !important;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 18px 0 8px 6px;
    }

    .menu-ativo-v8 {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.94), rgba(14,165,233,0.96));
        color: #ffffff !important;
        border-radius: 16px;
        padding: 13px 14px;
        margin: 7px 0;
        font-weight: 900;
        box-shadow:
            0 0 22px rgba(56,189,248,0.42),
            inset 0 0 0 1px rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .menu-ativo-v8 span {
        color:#ffffff !important;
        font-size: 16px;
    }

    .menu-ativo-v8 svg,
    .menu-svg-v8 svg {
        width: 21px;
        height: 21px;
        stroke-width: 2.25;
        flex-shrink: 0;
        stroke: #ffffff;
    }

    .menu-svg-v8 {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        color: #7dd3fc !important;
        opacity: 0.95;
    }

    [data-testid="stSidebar"] .stButton button {
        color: #ffffff !important;
        background: transparent !important;
        border: 0 !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 760 !important;
        padding: 0.65rem 0.75rem !important;
        transition: all .18s ease-in-out;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(56,189,248,0.13) !important;
        transform: translateX(2px);
    }

    .crm-hero {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.96), rgba(239,246,255,0.86)),
            linear-gradient(135deg, rgba(14,165,233,0.10), rgba(37,99,235,0.08)) !important;
        border: 1px solid rgba(14,165,233,0.13) !important;
        border-radius: 30px !important;
        box-shadow: 0 24px 70px rgba(15,23,42,0.08), 0 0 38px rgba(56,189,248,0.10) !important;
        padding: 26px 30px !important;
        margin-bottom: 28px !important;
    }

    .crm-title {
        font-size: 50px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        color: #0f172a !important;
        margin: 0 !important;
        letter-spacing: -0.05em !important;
    }

    .crm-subtitle {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 560 !important;
        margin-top: 10px !important;
    }

    .crm-pill {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.94), rgba(14,165,233,0.95)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 999px !important;
        box-shadow: 0 12px 30px rgba(14,165,233,0.22) !important;
    }

    h1, h2, h3 {
        color: #0f172a !important;
        letter-spacing: -0.04em !important;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.95), rgba(239,246,255,0.80)) !important;
        border: 1px solid rgba(14,165,233,0.14) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        box-shadow: 0 18px 45px rgba(15,23,42,0.07) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: 1px solid rgba(14,165,233,0.20) !important;
        background: rgba(255,255,255,0.94) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.8) !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(14,165,233,0.60) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.14) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        border: 1px solid rgba(14,165,233,0.28) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 850 !important;
        box-shadow: 0 14px 30px rgba(37,99,235,0.23) !important;
    }

    .stButton button:hover {
        box-shadow: 0 18px 42px rgba(14,165,233,0.32) !important;
        transform: translateY(-1px);
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(14,165,233,0.13);
        box-shadow: 0 16px 42px rgba(15,23,42,0.06);
    }

    /* Remove bug de quadrado branco antigo */
    .menu-ativo-v8 div,
    .menu-ativo-v8 span {
        background: transparent !important;
    }


    /* =========================================================
       OPERAX SALES — LAYOUT FINAL
       Sidebar azul neon + área direita branca limpa
       ========================================================= */

    .stApp {
        background:
            linear-gradient(90deg, #020617 0px, #020617 250px, #ffffff 250px, #ffffff 100%) !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top left, rgba(14,165,233,0.35), transparent 26%),
            linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
        border-right: 1px solid rgba(56,189,248,0.38) !important;
        min-width: 250px !important;
        max-width: 250px !important;
        box-shadow: 18px 0 45px rgba(14,165,233,0.22) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-top: 18px !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stButton button {
        color: #ffffff !important;
        background: transparent !important;
        border: 0 !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 760 !important;
        padding: 0.65rem 0.75rem !important;
        transition: all .18s ease-in-out;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(56,189,248,0.14) !important;
        transform: translateX(2px);
    }

    .sidebar-logo-v8 {
        display:flex;
        align-items:center;
        gap:12px;
        padding: 8px 4px 22px 4px;
        color:white;
        font-size:22px;
        font-weight:900;
        letter-spacing: .02em;
    }

    .sidebar-logo-icon-v8 {
        width:52px;
        height:52px;
        border-radius:18px;
        background:
            radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:25px;
        font-weight:900;
        color:#ffffff;
        box-shadow:
            0 0 34px rgba(56,189,248,0.58),
            inset 0 0 0 1px rgba(255,255,255,0.22);
    }

    .sidebar-user-v8 {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(56,189,248,0.30);
        border-radius: 18px;
        padding: 15px 14px;
        margin: 8px 0 20px 0;
        color: white !important;
        font-weight: 900;
        box-shadow: 0 16px 34px rgba(14,165,233,0.18);
    }

    .menu-label-v8 {
        color: rgba(56,189,248,0.94) !important;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 18px 0 8px 6px;
    }

    .menu-ativo-v8 {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.96), rgba(14,165,233,0.96));
        color: #ffffff !important;
        border-radius: 16px;
        padding: 13px 14px;
        margin: 7px 0;
        font-weight: 900;
        box-shadow:
            0 0 26px rgba(56,189,248,0.52),
            inset 0 0 0 1px rgba(255,255,255,0.22);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .menu-ativo-v8 span {
        color:#ffffff !important;
        font-size: 16px;
        background: transparent !important;
    }

    .menu-ativo-v8 svg,
    .menu-svg-v8 svg {
        width: 21px;
        height: 21px;
        stroke-width: 2.25;
        flex-shrink: 0;
        stroke: #ffffff;
        background: transparent !important;
    }

    .menu-svg-v8 {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        color: #7dd3fc !important;
        opacity: 0.95;
    }

    .crm-hero {
        background: #ffffff !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 14px 0 12px 0 !important;
        margin-bottom: 24px !important;
    }

    .crm-title {
        font-size: 50px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        color: #0f172a !important;
        margin: 0 !important;
        letter-spacing: -0.05em !important;
    }

    .crm-subtitle {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 560 !important;
        margin-top: 10px !important;
    }

    .crm-pill {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.96), rgba(14,165,233,0.96)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 999px !important;
        box-shadow: 0 12px 30px rgba(14,165,233,0.22) !important;
    }

    h1, h2, h3 {
        color: #0f172a !important;
        letter-spacing: -0.04em !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid rgba(14,165,233,0.15) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        box-shadow: 0 18px 45px rgba(15,23,42,0.07) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: 1px solid rgba(14,165,233,0.24) !important;
        background: #ffffff !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.8) !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(14,165,233,0.70) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.14) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        border: 1px solid rgba(14,165,233,0.28) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 850 !important;
        box-shadow: 0 14px 30px rgba(37,99,235,0.23) !important;
    }

    .stButton button:hover {
        box-shadow: 0 18px 42px rgba(14,165,233,0.32) !important;
        transform: translateY(-1px);
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(14,165,233,0.13);
        box-shadow: 0 16px 42px rgba(15,23,42,0.06);
    }

    /* Remove qualquer quadrado branco bugado no item ativo */
    .menu-ativo-v8 div,
    .menu-ativo-v8 span,
    .menu-ativo-v8 p {
        background: transparent !important;
    }


/* PATCH FINAL OPERAX */
.stApp {
    background: linear-gradient(90deg, #020617 0px, #020617 250px, #ffffff 250px, #ffffff 100%) !important;
}
[data-testid="stSidebar"] {
    background: radial-gradient(circle at top left, rgba(14,165,233,0.35), transparent 26%),
                linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
    border-right: 1px solid rgba(56,189,248,0.38) !important;
    min-width: 250px !important;
    max-width: 250px !important;
    box-shadow: 18px 0 45px rgba(14,165,233,0.22) !important;
}
section[data-testid="stSidebar"] > div {
    padding-left: 16px !important;
    padding-right: 16px !important;
    padding-top: 18px !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
.sidebar-logo-v8 {display:flex;align-items:center;gap:12px;padding:8px 4px 22px 4px;color:white;font-size:22px;font-weight:900;}
.sidebar-logo-icon-v8 {width:52px;height:52px;border-radius:18px;background:radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:900;color:#fff;box-shadow:0 0 34px rgba(56,189,248,.58), inset 0 0 0 1px rgba(255,255,255,.22);}
.sidebar-user-v8 {background:rgba(255,255,255,.075);border:1px solid rgba(56,189,248,.30);border-radius:18px;padding:15px 14px;margin:8px 0 20px 0;color:white!important;font-weight:900;box-shadow:0 16px 34px rgba(14,165,233,.18);}
.menu-label-v8 {color:rgba(56,189,248,.94)!important;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;margin:18px 0 8px 6px;}
.menu-ativo-v8 {background:linear-gradient(90deg, rgba(37,99,235,.96), rgba(14,165,233,.96));color:#fff!important;border-radius:16px;padding:13px 14px;margin:7px 0;font-weight:900;box-shadow:0 0 26px rgba(56,189,248,.52), inset 0 0 0 1px rgba(255,255,255,.22);display:flex;align-items:center;gap:12px;}
.menu-ativo-v8 span {color:#fff!important;font-size:16px;background:transparent!important;}
.menu-ativo-v8 svg,.menu-svg-v8 svg {width:21px;height:21px;stroke-width:2.25;flex-shrink:0;stroke:#fff;background:transparent!important;}
.menu-svg-v8 {display:flex;align-items:center;justify-content:center;min-height:42px;color:#7dd3fc!important;opacity:.95;}
[data-testid="stSidebar"] .stButton button {color:#fff!important;background:transparent!important;border:0!important;border-radius:14px!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-weight:760!important;padding:.65rem .75rem!important;}
[data-testid="stSidebar"] .stButton button:hover {background:rgba(56,189,248,.14)!important;transform:translateX(2px);}
.crm-hero {background:#fff!important;border:0!important;border-radius:0!important;box-shadow:none!important;padding:14px 0 12px 0!important;margin-bottom:24px!important;}
.crm-title {font-size:50px!important;line-height:1.02!important;font-weight:950!important;color:#0f172a!important;margin:0!important;letter-spacing:-.05em!important;}
.crm-subtitle {color:#475569!important;font-size:16px!important;font-weight:560!important;margin-top:10px!important;}
.crm-pill {background:linear-gradient(90deg, rgba(37,99,235,.96), rgba(14,165,233,.96))!important;color:#fff!important;border:1px solid rgba(56,189,248,.28)!important;border-radius:999px!important;box-shadow:0 12px 30px rgba(14,165,233,.22)!important;}
h1,h2,h3 {color:#0f172a!important;letter-spacing:-.04em!important;}
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea, div[data-baseweb="select"] {border-radius:15px!important;border:1px solid rgba(14,165,233,.24)!important;background:#fff!important;}
.stButton button {background:linear-gradient(135deg,#2563eb,#0ea5e9)!important;border:1px solid rgba(14,165,233,.28)!important;border-radius:15px!important;color:white!important;font-weight:850!important;box-shadow:0 14px 30px rgba(37,99,235,.23)!important;}
.menu-ativo-v8 div,.menu-ativo-v8 span,.menu-ativo-v8 p {background:transparent!important;}

</style>
""", unsafe_allow_html=True)


def mostrar_cabecalho():
    logo_path = Path("logo.png")

    st.markdown('<div class="crm-hero">', unsafe_allow_html=True)
    col_logo, col_titulo = st.columns([1.25, 7])

    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=155)
        else:
            st.markdown('<div class="crm-logo-fallback">💰</div>', unsafe_allow_html=True)

    with col_titulo:
        st.markdown(
            """
            <div>
                <h1 class="crm-title">OPERAX SALES</h1>
                <p class="crm-subtitle">Sistema inteligente de vendas e operações financeiras</p>
                <div class="crm-pill">⚡ Painel inteligente • Atualização por ação • Controle por vendedor</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)



# =========================
# FUNÇÕES
# =========================

def hash_senha(senha):
    return hashlib.sha256(str(senha).encode()).hexdigest()


def dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def limpar_documento(valor):
    return re.sub(r"\D", "", str(valor or ""))

def validar_cpf(cpf):
    cpf_limpo = limpar_documento(cpf)

    if len(cpf_limpo) != 11:
        return False

    if cpf_limpo == cpf_limpo[0] * 11:
        return False

    soma = sum(int(cpf_limpo[i]) * (10 - i) for i in range(9))
    digito1 = (soma * 10) % 11
    if digito1 == 10:
        digito1 = 0

    soma = sum(int(cpf_limpo[i]) * (11 - i) for i in range(10))
    digito2 = (soma * 10) % 11
    if digito2 == 10:
        digito2 = 0

    return digito1 == int(cpf_limpo[9]) and digito2 == int(cpf_limpo[10])


def validar_telefone(telefone):
    telefone_limpo = limpar_documento(telefone)

    if len(telefone_limpo) not in [10, 11]:
        return False

    ddd = telefone_limpo[:2]
    numero = telefone_limpo[2:]

    if ddd == "00":
        return False

    if len(telefone_limpo) == 11 and not numero.startswith("9"):
        return False

    return True


def converter_valor_brasileiro(valor):
    texto = str(valor or "").strip()

    if not texto:
        return 0.0

    texto = texto.replace("R$", "").replace(" ", "")

    # Se vier no formato brasileiro: 1.758,71
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        # Se vier como 1758.71, mantém o ponto decimal
        texto = texto

    try:
        return float(texto)
    except Exception:
        return 0.0


def formatar_valor_para_tela(valor):
    numero = converter_valor_brasileiro(valor)
    if numero == 0:
        return ""
    return f"{numero:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def login(usuario, senha):
    usuario = str(usuario).strip().lower()
    senha_hash = hash_senha(str(senha).strip())

    res = (
        supabase.table("usuarios")
        .select("*")
        .eq("usuario", usuario)
        .eq("ativo", True)
        .execute()
    )

    if not res.data:
        return None

    user = res.data[0]

    if user.get("senha_hash") == senha_hash:
        return user

    return None


def carregar_tabelas():
    res = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("ativo", True)
        .execute()
    )

    tabelas = sorted(list(set([
        r.get("produto")
        for r in res.data
        if r.get("produto")
    ])))

    if not tabelas:
        tabelas = ["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]

    return tabelas


def calcular_comissao_montante(df_filtrado):
    total_empresa = 0

    if df_filtrado.empty:
        return 0

    if "status" not in df_filtrado.columns or "tabela_banco" not in df_filtrado.columns:
        return 0

    df_pagas = df_filtrado[df_filtrado["status"] == "Pago"].copy()

    if df_pagas.empty:
        return 0

    for tabela in df_pagas["tabela_banco"].dropna().unique():
        total_tabela = (
            df_pagas[df_pagas["tabela_banco"] == tabela]["valor"]
            .fillna(0)
            .sum()
        )

        regras = (
            supabase.table("regras_comissao")
            .select("*")
            .eq("produto", tabela)
            .eq("ativo", True)
            .order("valor_minimo", desc=True)
            .execute()
        )

        percentual = 0

        for regra in regras.data:
            valor_minimo = float(regra.get("valor_minimo") or 0)

            if float(total_tabela) >= valor_minimo:
                percentual = float(regra.get("percentual_empresa") or 0)
                break

        total_empresa += float(total_tabela) * (percentual / 100)

    return total_empresa


def calcular_percentual_empresa_venda(tabela_banco, valor):
    regras = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("produto", tabela_banco)
        .eq("ativo", True)
        .order("valor_minimo", desc=True)
        .execute()
    )

    percentual = 0

    for regra in regras.data:
        valor_minimo = float(regra.get("valor_minimo") or 0)

        if float(valor) >= valor_minimo:
            percentual = float(regra.get("percentual_empresa") or 0)
            break

    return percentual


def preparar_dataframe_vendas():
    vendas = (
        supabase.table("vendas")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    df = pd.DataFrame(vendas.data)

    if df.empty:
        return df

    if "data" not in df.columns:
        df["data"] = None

    if "vendedor_id" not in df.columns:
        df["vendedor_id"] = None

    if "tabela_banco" not in df.columns:
        if "produto" in df.columns:
            df["tabela_banco"] = df["produto"]
        else:
            df["tabela_banco"] = ""

    if "valor" not in df.columns:
        df["valor"] = 0

    if "status" not in df.columns:
        df["status"] = "Pendente"

    if "conferido" not in df.columns:
        df["conferido"] = False

    if "alterado_vendedor" not in df.columns:
        df["alterado_vendedor"] = False

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["mes_num"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year

    return df


def destacar_linhas_pendentes(row, tipo_usuario):
    """
    Destaca propostas pendentes:
    - Pendente recente: amarelo
    - Pendente com mais de 1 hora: vermelho somente para admin
    """
    try:
        status = str(row.get("status", "")).strip().lower()
        data_venda = row.get("data", None)

        if status != "pendente":
            return [""] * len(row)

        agora = pd.Timestamp.now()

        if pd.notna(data_venda):
            data_venda = pd.to_datetime(data_venda, errors="coerce")
            horas_pendente = (agora - data_venda).total_seconds() / 3600
        else:
            horas_pendente = 0

        if tipo_usuario == "admin" and horas_pendente >= 1:
            return ["background-color: #ffb3b3"] * len(row)

        return ["background-color: #fff3b0"] * len(row)

    except Exception:
        return [""] * len(row)




def carregar_usuarios_chat():
    try:
        res = (
            supabase.table("usuarios")
            .select("id,nome,usuario,tipo,ativo")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )

        usuarios = res.data or []

        return [
            u for u in usuarios
            if int(u.get("id")) != int(st.session_state.user_id)
        ]

    except Exception:
        return []


def carregar_mensagens_chat(destinatario_id, limite=80):
    try:
        meu_id = int(st.session_state.user_id)
        outro_id = int(destinatario_id)

        res = (
            supabase.table("chat_interno")
            .select("*")
            .order("criado_em", desc=True)
            .limit(300)
            .execute()
        )

        todas = res.data or []

        mensagens = []

        for msg in todas:
            origem = msg.get("usuario_id")
            destino = msg.get("destinatario_id")

            try:
                origem = int(origem) if origem is not None else None
                destino = int(destino) if destino is not None else None
            except Exception:
                origem = None
                destino = None

            # Mensagens privadas entre eu e o usuário escolhido.
            if (
                (origem == meu_id and destino == outro_id)
                or
                (origem == outro_id and destino == meu_id)
            ):
                mensagens.append(msg)

        mensagens = mensagens[-limite:]
        mensagens.reverse()

        return mensagens

    except Exception:
        return []


def enviar_mensagem_chat(usuario_id, destinatario_id, nome, tipo, mensagem):
    supabase.table("chat_interno").insert({
        "usuario_id": usuario_id,
        "destinatario_id": destinatario_id,
        "nome": nome,
        "tipo": tipo,
        "mensagem": mensagem,
        "criado_em": str(datetime.now())
    }).execute()



def contar_mensagens_nao_lidas():
    try:
        if "chat_lido_em" not in st.session_state:
            st.session_state.chat_lido_em = str(datetime.now())

        res = (
            supabase.table("chat_interno")
            .select("*")
            .eq("destinatario_id", st.session_state.user_id)
            .execute()
        )

        mensagens = res.data or []
        ultima_leitura = pd.to_datetime(st.session_state.chat_lido_em, errors="coerce")

        total = 0

        for msg in mensagens:
            data_msg = pd.to_datetime(msg.get("criado_em"), errors="coerce")

            if pd.notna(data_msg) and pd.notna(ultima_leitura):
                if data_msg > ultima_leitura:
                    total += 1

        return total

    except Exception:
        return 0


def mostrar_chat_popup():
    nao_lidas = contar_mensagens_nao_lidas()

    if nao_lidas > 0:
        st.markdown("""
        <style>
            @keyframes piscarChat {
                0% { opacity: 1; transform: scale(1); }
                50% { opacity: 0.35; transform: scale(1.18); }
                100% { opacity: 1; transform: scale(1); }
            }

            .chat-alerta {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #dcfce7;
                border: 1px solid #86efac;
                color: #166534;
                padding: 8px 12px;
                border-radius: 999px;
                font-weight: 800;
                box-shadow: 0 12px 28px rgba(34,197,94,0.22);
            }

            .bolinha-verde {
                width: 11px;
                height: 11px;
                background: #22c55e;
                border-radius: 999px;
                animation: piscarChat 1s infinite;
            }
        
    /* =========================================================
       OPERAX SALES — TEMA NEON AZUL / DASHBOARD PREMIUM
       ========================================================= */

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(56,189,248,0.18), transparent 28%),
            radial-gradient(circle at bottom right, rgba(37,99,235,0.16), transparent 32%),
            linear-gradient(135deg, #eff6ff 0%, #f8fafc 42%, #ffffff 100%) !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 1.8rem !important;
        padding-bottom: 3rem !important;
    }

    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
        border-right: 1px solid rgba(56,189,248,0.28) !important;
        min-width: 250px !important;
        max-width: 250px !important;
        box-shadow: 18px 0 45px rgba(14,165,233,0.18) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-top: 18px !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .sidebar-logo-v8 {
        display:flex;
        align-items:center;
        gap:12px;
        padding: 8px 4px 20px 4px;
        color:white;
        font-size:22px;
        font-weight:900;
        letter-spacing: .02em;
    }

    .sidebar-logo-icon-v8 {
        width:48px;
        height:48px;
        border-radius:16px;
        background:
            radial-gradient(circle at 35% 30%, #7dd3fc 0%, #0ea5e9 35%, #1d4ed8 72%, #0f172a 100%);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:24px;
        font-weight:900;
        color:#ffffff;
        box-shadow:
            0 0 28px rgba(56,189,248,0.50),
            inset 0 0 0 1px rgba(255,255,255,0.24);
    }

    .sidebar-user-v8 {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(56,189,248,0.26);
        border-radius: 18px;
        padding: 15px 14px;
        margin: 8px 0 20px 0;
        color: white !important;
        font-weight: 900;
        box-shadow: 0 16px 34px rgba(14,165,233,0.15);
    }

    .menu-label-v8 {
        color: rgba(125,211,252,0.88) !important;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 18px 0 8px 6px;
    }

    .menu-ativo-v8 {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.94), rgba(14,165,233,0.96));
        color: #ffffff !important;
        border-radius: 16px;
        padding: 13px 14px;
        margin: 7px 0;
        font-weight: 900;
        box-shadow:
            0 0 22px rgba(56,189,248,0.42),
            inset 0 0 0 1px rgba(255,255,255,0.18);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .menu-ativo-v8 span {
        color:#ffffff !important;
        font-size: 16px;
    }

    .menu-ativo-v8 svg,
    .menu-svg-v8 svg {
        width: 21px;
        height: 21px;
        stroke-width: 2.25;
        flex-shrink: 0;
        stroke: #ffffff;
    }

    .menu-svg-v8 {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        color: #7dd3fc !important;
        opacity: 0.95;
    }

    [data-testid="stSidebar"] .stButton button {
        color: #ffffff !important;
        background: transparent !important;
        border: 0 !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 760 !important;
        padding: 0.65rem 0.75rem !important;
        transition: all .18s ease-in-out;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(56,189,248,0.13) !important;
        transform: translateX(2px);
    }

    .crm-hero {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.96), rgba(239,246,255,0.86)),
            linear-gradient(135deg, rgba(14,165,233,0.10), rgba(37,99,235,0.08)) !important;
        border: 1px solid rgba(14,165,233,0.13) !important;
        border-radius: 30px !important;
        box-shadow: 0 24px 70px rgba(15,23,42,0.08), 0 0 38px rgba(56,189,248,0.10) !important;
        padding: 26px 30px !important;
        margin-bottom: 28px !important;
    }

    .crm-title {
        font-size: 50px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        color: #0f172a !important;
        margin: 0 !important;
        letter-spacing: -0.05em !important;
    }

    .crm-subtitle {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 560 !important;
        margin-top: 10px !important;
    }

    .crm-pill {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.94), rgba(14,165,233,0.95)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 999px !important;
        box-shadow: 0 12px 30px rgba(14,165,233,0.22) !important;
    }

    h1, h2, h3 {
        color: #0f172a !important;
        letter-spacing: -0.04em !important;
    }

    div[data-testid="stMetric"] {
        background:
            linear-gradient(135deg, rgba(255,255,255,0.95), rgba(239,246,255,0.80)) !important;
        border: 1px solid rgba(14,165,233,0.14) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        box-shadow: 0 18px 45px rgba(15,23,42,0.07) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: 1px solid rgba(14,165,233,0.20) !important;
        background: rgba(255,255,255,0.94) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.8) !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(14,165,233,0.60) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.14) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        border: 1px solid rgba(14,165,233,0.28) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 850 !important;
        box-shadow: 0 14px 30px rgba(37,99,235,0.23) !important;
    }

    .stButton button:hover {
        box-shadow: 0 18px 42px rgba(14,165,233,0.32) !important;
        transform: translateY(-1px);
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(14,165,233,0.13);
        box-shadow: 0 16px 42px rgba(15,23,42,0.06);
    }

    /* Remove bug de quadrado branco antigo */
    .menu-ativo-v8 div,
    .menu-ativo-v8 span {
        background: transparent !important;
    }


    /* =========================================================
       OPERAX SALES — LAYOUT FINAL
       Sidebar azul neon + área direita branca limpa
       ========================================================= */

    .stApp {
        background:
            linear-gradient(90deg, #020617 0px, #020617 250px, #ffffff 250px, #ffffff 100%) !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top left, rgba(14,165,233,0.35), transparent 26%),
            linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
        border-right: 1px solid rgba(56,189,248,0.38) !important;
        min-width: 250px !important;
        max-width: 250px !important;
        box-shadow: 18px 0 45px rgba(14,165,233,0.22) !important;
    }

    section[data-testid="stSidebar"] > div {
        padding-left: 16px !important;
        padding-right: 16px !important;
        padding-top: 18px !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] .stButton button {
        color: #ffffff !important;
        background: transparent !important;
        border: 0 !important;
        border-radius: 14px !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 760 !important;
        padding: 0.65rem 0.75rem !important;
        transition: all .18s ease-in-out;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        background: rgba(56,189,248,0.14) !important;
        transform: translateX(2px);
    }

    .sidebar-logo-v8 {
        display:flex;
        align-items:center;
        gap:12px;
        padding: 8px 4px 22px 4px;
        color:white;
        font-size:22px;
        font-weight:900;
        letter-spacing: .02em;
    }

    .sidebar-logo-icon-v8 {
        width:52px;
        height:52px;
        border-radius:18px;
        background:
            radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:25px;
        font-weight:900;
        color:#ffffff;
        box-shadow:
            0 0 34px rgba(56,189,248,0.58),
            inset 0 0 0 1px rgba(255,255,255,0.22);
    }

    .sidebar-user-v8 {
        background: rgba(255,255,255,0.075);
        border: 1px solid rgba(56,189,248,0.30);
        border-radius: 18px;
        padding: 15px 14px;
        margin: 8px 0 20px 0;
        color: white !important;
        font-weight: 900;
        box-shadow: 0 16px 34px rgba(14,165,233,0.18);
    }

    .menu-label-v8 {
        color: rgba(56,189,248,0.94) !important;
        font-size: 12px;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .08em;
        margin: 18px 0 8px 6px;
    }

    .menu-ativo-v8 {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.96), rgba(14,165,233,0.96));
        color: #ffffff !important;
        border-radius: 16px;
        padding: 13px 14px;
        margin: 7px 0;
        font-weight: 900;
        box-shadow:
            0 0 26px rgba(56,189,248,0.52),
            inset 0 0 0 1px rgba(255,255,255,0.22);
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .menu-ativo-v8 span {
        color:#ffffff !important;
        font-size: 16px;
        background: transparent !important;
    }

    .menu-ativo-v8 svg,
    .menu-svg-v8 svg {
        width: 21px;
        height: 21px;
        stroke-width: 2.25;
        flex-shrink: 0;
        stroke: #ffffff;
        background: transparent !important;
    }

    .menu-svg-v8 {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        color: #7dd3fc !important;
        opacity: 0.95;
    }

    .crm-hero {
        background: #ffffff !important;
        border: 0 !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 14px 0 12px 0 !important;
        margin-bottom: 24px !important;
    }

    .crm-title {
        font-size: 50px !important;
        line-height: 1.02 !important;
        font-weight: 950 !important;
        color: #0f172a !important;
        margin: 0 !important;
        letter-spacing: -0.05em !important;
    }

    .crm-subtitle {
        color: #475569 !important;
        font-size: 16px !important;
        font-weight: 560 !important;
        margin-top: 10px !important;
    }

    .crm-pill {
        background:
            linear-gradient(90deg, rgba(37,99,235,0.96), rgba(14,165,233,0.96)) !important;
        color: #ffffff !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 999px !important;
        box-shadow: 0 12px 30px rgba(14,165,233,0.22) !important;
    }

    h1, h2, h3 {
        color: #0f172a !important;
        letter-spacing: -0.04em !important;
    }

    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid rgba(14,165,233,0.15) !important;
        border-radius: 22px !important;
        padding: 18px 20px !important;
        box-shadow: 0 18px 45px rgba(15,23,42,0.07) !important;
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-baseweb="select"] {
        border-radius: 15px !important;
        border: 1px solid rgba(14,165,233,0.24) !important;
        background: #ffffff !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.8) !important;
    }

    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: rgba(14,165,233,0.70) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.14) !important;
    }

    .stButton button {
        background: linear-gradient(135deg, #2563eb, #0ea5e9) !important;
        border: 1px solid rgba(14,165,233,0.28) !important;
        border-radius: 15px !important;
        color: white !important;
        font-weight: 850 !important;
        box-shadow: 0 14px 30px rgba(37,99,235,0.23) !important;
    }

    .stButton button:hover {
        box-shadow: 0 18px 42px rgba(14,165,233,0.32) !important;
        transform: translateY(-1px);
    }

    .stDataFrame {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(14,165,233,0.13);
        box-shadow: 0 16px 42px rgba(15,23,42,0.06);
    }

    /* Remove qualquer quadrado branco bugado no item ativo */
    .menu-ativo-v8 div,
    .menu-ativo-v8 span,
    .menu-ativo-v8 p {
        background: transparent !important;
    }


/* PATCH FINAL OPERAX */
.stApp {
    background: linear-gradient(90deg, #020617 0px, #020617 250px, #ffffff 250px, #ffffff 100%) !important;
}
[data-testid="stSidebar"] {
    background: radial-gradient(circle at top left, rgba(14,165,233,0.35), transparent 26%),
                linear-gradient(180deg, #020617 0%, #061a3d 48%, #0f172a 100%) !important;
    border-right: 1px solid rgba(56,189,248,0.38) !important;
    min-width: 250px !important;
    max-width: 250px !important;
    box-shadow: 18px 0 45px rgba(14,165,233,0.22) !important;
}
section[data-testid="stSidebar"] > div {
    padding-left: 16px !important;
    padding-right: 16px !important;
    padding-top: 18px !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; }
.sidebar-logo-v8 {display:flex;align-items:center;gap:12px;padding:8px 4px 22px 4px;color:white;font-size:22px;font-weight:900;}
.sidebar-logo-icon-v8 {width:52px;height:52px;border-radius:18px;background:radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);display:flex;align-items:center;justify-content:center;font-size:25px;font-weight:900;color:#fff;box-shadow:0 0 34px rgba(56,189,248,.58), inset 0 0 0 1px rgba(255,255,255,.22);}
.sidebar-user-v8 {background:rgba(255,255,255,.075);border:1px solid rgba(56,189,248,.30);border-radius:18px;padding:15px 14px;margin:8px 0 20px 0;color:white!important;font-weight:900;box-shadow:0 16px 34px rgba(14,165,233,.18);}
.menu-label-v8 {color:rgba(56,189,248,.94)!important;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;margin:18px 0 8px 6px;}
.menu-ativo-v8 {background:linear-gradient(90deg, rgba(37,99,235,.96), rgba(14,165,233,.96));color:#fff!important;border-radius:16px;padding:13px 14px;margin:7px 0;font-weight:900;box-shadow:0 0 26px rgba(56,189,248,.52), inset 0 0 0 1px rgba(255,255,255,.22);display:flex;align-items:center;gap:12px;}
.menu-ativo-v8 span {color:#fff!important;font-size:16px;background:transparent!important;}
.menu-ativo-v8 svg,.menu-svg-v8 svg {width:21px;height:21px;stroke-width:2.25;flex-shrink:0;stroke:#fff;background:transparent!important;}
.menu-svg-v8 {display:flex;align-items:center;justify-content:center;min-height:42px;color:#7dd3fc!important;opacity:.95;}
[data-testid="stSidebar"] .stButton button {color:#fff!important;background:transparent!important;border:0!important;border-radius:14px!important;box-shadow:none!important;text-align:left!important;justify-content:flex-start!important;font-weight:760!important;padding:.65rem .75rem!important;}
[data-testid="stSidebar"] .stButton button:hover {background:rgba(56,189,248,.14)!important;transform:translateX(2px);}
.crm-hero {background:#fff!important;border:0!important;border-radius:0!important;box-shadow:none!important;padding:14px 0 12px 0!important;margin-bottom:24px!important;}
.crm-title {font-size:50px!important;line-height:1.02!important;font-weight:950!important;color:#0f172a!important;margin:0!important;letter-spacing:-.05em!important;}
.crm-subtitle {color:#475569!important;font-size:16px!important;font-weight:560!important;margin-top:10px!important;}
.crm-pill {background:linear-gradient(90deg, rgba(37,99,235,.96), rgba(14,165,233,.96))!important;color:#fff!important;border:1px solid rgba(56,189,248,.28)!important;border-radius:999px!important;box-shadow:0 12px 30px rgba(14,165,233,.22)!important;}
h1,h2,h3 {color:#0f172a!important;letter-spacing:-.04em!important;}
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea, div[data-baseweb="select"] {border-radius:15px!important;border:1px solid rgba(14,165,233,.24)!important;background:#fff!important;}
.stButton button {background:linear-gradient(135deg,#2563eb,#0ea5e9)!important;border:1px solid rgba(14,165,233,.28)!important;border-radius:15px!important;color:white!important;font-weight:850!important;box-shadow:0 14px 30px rgba(37,99,235,.23)!important;}
.menu-ativo-v8 div,.menu-ativo-v8 span,.menu-ativo-v8 p {background:transparent!important;}

</style>
        """, unsafe_allow_html=True)

    col_spacer, col_chat = st.columns([8, 1.8])

    with col_chat:
        label_chat = f"🟢 💬 Chat ({nao_lidas})" if nao_lidas > 0 else "💬 Chat"

        try:
            chat_context = st.popover(label_chat, use_container_width=True)
        except Exception:
            chat_context = st.expander(label_chat, expanded=False)

    with chat_context:
        st.session_state.chat_lido_em = str(datetime.now())
        st.markdown("### Chat interno")

        usuarios_chat = carregar_usuarios_chat()

        if not usuarios_chat:
            st.info("Nenhum outro usuário ativo encontrado.")
            return

        opcoes = {
            f"{u.get('nome', u.get('usuario'))} ({u.get('tipo', '')})": u
            for u in usuarios_chat
        }

        escolhido_label = st.selectbox(
            "Enviar mensagem para",
            list(opcoes.keys())
        )

        usuario_destino = opcoes[escolhido_label]
        destinatario_id = int(usuario_destino["id"])

        mensagens = carregar_mensagens_chat(destinatario_id, 80)

        chat_area = st.container(height=360)

        with chat_area:
            if not mensagens:
                st.info("Nenhuma mensagem nessa conversa ainda.")
            else:
                for msg in mensagens:
                    nome_msg = msg.get("nome", "Usuário")
                    texto_msg = msg.get("mensagem", "")
                    data_msg = str(msg.get("criado_em", ""))[:16]

                    if int(msg.get("usuario_id")) == int(st.session_state.user_id):
                        st.markdown(
                            f"""
                            <div style="
                                background:linear-gradient(135deg,#dcfce7,#bbf7d0);
                                border:1px solid #86efac;
                                border-radius:16px;
                                padding:10px 12px;
                                margin:8px 0 8px auto;
                                max-width:88%;
                                text-align:right;
                                box-shadow:0 8px 20px rgba(34,197,94,0.10);
                            ">
                                <div style="font-size:12px;color:#166534;font-weight:700;">Você • {data_msg}</div>
                                <div style="font-size:15px;color:#111827;">{texto_msg}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div style="
                                background:#ffffff;
                                border:1px solid #e5e7eb;
                                border-radius:16px;
                                padding:10px 12px;
                                margin:8px auto 8px 0;
                                max-width:88%;
                                box-shadow:0 8px 20px rgba(15,23,42,0.06);
                            ">
                                <div style="font-size:12px;color:#64748b;font-weight:700;">{nome_msg} • {data_msg}</div>
                                <div style="font-size:15px;color:#111827;">{texto_msg}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

        with st.form("form_chat_popup", clear_on_submit=True):
            mensagem = st.text_input(
                "Mensagem",
                placeholder=f"Digite uma mensagem para {usuario_destino.get('nome', 'usuário')}..."
            )

            enviar = st.form_submit_button("Enviar")

            if enviar:
                if not mensagem.strip():
                    st.error("Digite uma mensagem antes de enviar.")
                else:
                    enviar_mensagem_chat(
                        st.session_state.user_id,
                        destinatario_id,
                        st.session_state.nome,
                        st.session_state.tipo,
                        mensagem.strip()
                    )
                    st.rerun()



def icone_svg(nome):
    icones = {
        "nova": """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M7 3h7l4 4v14H7V3Z"/>
            <path d="M14 3v5h5"/>
            <path d="M9 14h6"/>
            <path d="M12 11v6"/>
        </svg>
        """,
        "painel": """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M4 19V5"/>
            <path d="M4 19h16"/>
            <path d="M8 16v-5"/>
            <path d="M12 16V8"/>
            <path d="M16 16v-7"/>
            <path d="M20 16v-3"/>
        </svg>
        """,
        "usuarios": """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/>
            <circle cx="9.5" cy="7" r="4"/>
            <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
        """,
        "comissoes": """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 2v20"/>
            <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/>
            <path d="M19 9l2-2-2-2"/>
            <path d="M5 15l-2 2 2 2"/>
        </svg>
        """
    }
    return icones.get(nome, "")


def menu_lateral_v8():
    if "menu_atual" not in st.session_state:
        st.session_state.menu_atual = "📋 Nova Venda"

    if st.session_state.tipo == "admin":
        opcoes = [
            ("📋 Nova Venda", "nova", "Operação"),
            ("📊 Painel", "painel", "Operação"),
            ("👥 Usuários", "usuarios", "Gestão"),
            ("💰 Comissões", "comissoes", "Gestão"),
        ]
    else:
        opcoes = [
            ("📋 Nova Venda", "nova", "Operação"),
            ("📊 Painel", "painel", "Operação"),
        ]

    st.sidebar.markdown(
        """
        <div class="sidebar-logo-v8">
            <div class="sidebar-logo-icon-v8">O</div>
            <div>OPERAX</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        f"""
        <div class="sidebar-user-v8">
            {st.session_state.nome}
        </div>
        """,
        unsafe_allow_html=True
    )

    grupo_atual = None

    for nome, icone_nome, grupo in opcoes:
        nome_limpo = (
            nome.replace("📋 ", "")
            .replace("📊 ", "")
            .replace("👥 ", "")
            .replace("💰 ", "")
        )

        if grupo != grupo_atual:
            st.sidebar.markdown(
                f'<div class="menu-label-v8">{grupo}</div>',
                unsafe_allow_html=True
            )
            grupo_atual = grupo

        svg = icone_svg(icone_nome)

        if st.session_state.menu_atual == nome:
            st.sidebar.markdown(
                f"""
                <div class="menu-ativo-v8">
                    {svg}
                    <span>{nome_limpo}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            col_icon, col_btn = st.sidebar.columns([0.23, 0.77])

            with col_icon:
                st.markdown(
                    f'<div class="menu-svg-v8">{svg}</div>',
                    unsafe_allow_html=True
                )

            with col_btn:
                if st.button(
                    nome_limpo,
                    key=f"menu_{nome}",
                    use_container_width=True
                ):
                    st.session_state.menu_atual = nome
                    st.rerun()

    st.sidebar.markdown("---")

    if st.sidebar.button("Sair  ↪", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    return st.session_state.menu_atual


# =========================
# LOGIN
# =========================

mostrar_cabecalho()

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user = login(usuario, senha)

        if user:
            st.session_state.logado = True
            st.session_state.user_id = user["id"]
            st.session_state.usuario = user["usuario"]
            st.session_state.nome = user["nome"]
            st.session_state.tipo = user["tipo"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

else:
    menu = menu_lateral_v8()

    mostrar_chat_popup()

    if "mostrar_comissao_empresa" not in st.session_state:
        st.session_state.mostrar_comissao_empresa = True

    if "venda_sucesso_msg" not in st.session_state:
        st.session_state.venda_sucesso_msg = ""

    # =========================
    # NOVA VENDA
    # =========================

    if menu == "📋 Nova Venda":
        st.header("📋 Cadastro de Venda")

        if st.session_state.venda_sucesso_msg:
            st.success(st.session_state.venda_sucesso_msg)
            st.session_state.venda_sucesso_msg = ""
        tabelas = carregar_tabelas()

        cliente = st.text_input("Cliente", key="novo_cliente")

        cpf_digitado = st.text_input(
            "CPF",
            placeholder="Ex: 999.999.999-99",
            key="novo_cpf"
        )
        cpf = limpar_documento(cpf_digitado)

        if cpf_digitado:
            if len(cpf) < 11:
                st.error(f"CPF incompleto: faltam {11 - len(cpf)} número(s).")
            elif len(cpf) > 11:
                st.error(f"CPF com números a mais: remova {len(cpf) - 11} número(s).")
            elif validar_cpf(cpf):
                st.success(f"CPF válido: {cpf}")
            else:
                st.error("CPF inválido. Confira os números digitados.")

        telefone_digitado = st.text_input(
            "Telefone",
            placeholder="Ex: (11) 99976-7867",
            key="novo_telefone"
        )
        telefone = limpar_documento(telefone_digitado)

        if telefone_digitado:
            if len(telefone) < 10:
                st.error("Telefone incompleto. Informe DDD + número.")
            elif len(telefone) > 11:
                st.error(f"Telefone com números a mais: remova {len(telefone) - 11} número(s).")
            elif validar_telefone(telefone):
                st.success(f"Telefone válido: {telefone}")
            else:
                st.error("Telefone inválido. Use DDD + número. Exemplo: 11910721110.")

        tabela_banco = st.selectbox("Tabela/Banco", tabelas)

        valor_digitado = st.text_input(
            "Valor vendido",
            placeholder="Ex: R$ 1.758,71",
            key="novo_valor"
        )
        valor = converter_valor_brasileiro(valor_digitado)

        if valor_digitado:
            if valor > 0:
                st.success(f"Valor válido: {dinheiro(valor)}")
            else:
                st.error("Valor inválido. Exemplo correto: R$ 1.758,71")

        status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])

        observacao = st.text_area("Observação", key="nova_observacao")

        if st.button("Salvar venda"):
            cpf_ok = validar_cpf(cpf)
            telefone_ok = validar_telefone(telefone)
            valor_ok = valor > 0

            if not cpf_ok:
                st.error("Corrija o CPF antes de salvar. Ele precisa ser válido e ter 11 números.")
            elif not telefone_ok:
                st.error("Corrija o telefone antes de salvar. Informe DDD + número.")
            elif not valor_ok:
                st.error("Corrija o valor antes de salvar.")
            else:
                perc_empresa = calcular_percentual_empresa_venda(tabela_banco, valor)
                valor_empresa = float(valor) * (perc_empresa / 100)

                dados = {
                    "data": str(datetime.now()),
                    "vendedor_id": st.session_state.user_id,
                    "vendedor": st.session_state.usuario,
                    "cliente": cliente,
                    "cpf": cpf,
                    "telefone": telefone,
                    "produto": tabela_banco,
                    "tabela_banco": tabela_banco,
                    "valor": valor,
                    "status": status,
                    "percentual_comissao": 0,
                    "valor_comissao": 0,
                    "comissao_empresa": perc_empresa,
                    "valor_comissao_empresa": valor_empresa,
                    "conferido": False,
                    "alterado_vendedor": False,
                    "observacao": observacao
                }

                supabase.table("vendas").insert(dados).execute()

                st.session_state.venda_sucesso_msg = "Proposta cadastrada com sucesso!"

                for campo in ["novo_cliente", "novo_cpf", "novo_telefone", "novo_valor", "nova_observacao"]:
                    if campo in st.session_state:
                        st.session_state[campo] = ""

                st.rerun()

    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":
        st.header("📊 Painel de Vendas")
        df = preparar_dataframe_vendas()

        if df.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            meses = {
                1: "Janeiro",
                2: "Fevereiro",
                3: "Março",
                4: "Abril",
                5: "Maio",
                6: "Junho",
                7: "Julho",
                8: "Agosto",
                9: "Setembro",
                10: "Outubro",
                11: "Novembro",
                12: "Dezembro"
            }

            st.subheader("🔎 Filtros")

            col_f1, col_f2, col_f3, col_f4 = st.columns(4)

            mes_nome = col_f1.selectbox(
                "Mês",
                list(meses.values()),
                index=datetime.now().month - 1
            )

            anos = sorted(
                df["ano"].dropna().unique().astype(int).tolist(),
                reverse=True
            )

            if not anos:
                anos = [datetime.now().year]

            ano_filtro = col_f2.selectbox("Ano", anos)

            dias = ["Todos"] + list(range(1, 32))

            dia_filtro = col_f3.selectbox(
                "Dia",
                dias
            )

            status_filtro = col_f4.selectbox(
                "Status",
                ["Todos", "Pago", "Pendente", "Cancelado"]
            )

            tabelas = carregar_tabelas()

            tabela_filtro = st.selectbox(
                "Tabela/Banco",
                ["Todas"] + tabelas
            )

            mes_num = [k for k, v in meses.items() if v == mes_nome][0]

            df = df[(df["mes_num"] == mes_num) & (df["ano"] == ano_filtro)]

            if dia_filtro != "Todos":
                df = df[df["data"].dt.day == int(dia_filtro)]

            # VENDEDOR VÊ SOMENTE AS PRÓPRIAS VENDAS PELO ID
            if st.session_state.tipo != "admin":
                df = df[df["vendedor_id"] == st.session_state.user_id]

            if status_filtro != "Todos":
                df = df[df["status"] == status_filtro]

            if tabela_filtro != "Todas":
                df = df[df["tabela_banco"] == tabela_filtro]

            if st.session_state.tipo == "admin":
                vendedores = sorted(df["vendedor"].dropna().unique().tolist())

                vendedor_filtro = st.selectbox(
                    "Vendedor",
                    ["Todos"] + vendedores
                )

                if vendedor_filtro != "Todos":
                    df = df[df["vendedor"] == vendedor_filtro]

            total_vendido = df["valor"].fillna(0).sum()
            qtd = len(df)

            col1, col2, col3 = st.columns(3)

            col1.metric("💵 Total vendido", dinheiro(total_vendido))
            col2.metric("📋 Quantidade", qtd)
            col3.metric("🗓️ Mês", mes_nome)

            if st.session_state.tipo == "admin":
                total_empresa = calcular_comissao_montante(df)

                col_comissao_label, col_comissao_btn = st.columns([4, 1])

                with col_comissao_btn:
                    if st.button("👁️" if st.session_state.mostrar_comissao_empresa else "🙈", key="btn_ocultar_comissao"):
                        st.session_state.mostrar_comissao_empresa = not st.session_state.mostrar_comissao_empresa
                        st.rerun()

                valor_comissao_tela = (
                    dinheiro(total_empresa)
                    if st.session_state.mostrar_comissao_empresa
                    else "R$ •••••"
                )

                st.metric("🏦 Comissão empresa", valor_comissao_tela)

                alteradas = df[df["alterado_vendedor"] == True]

                if not alteradas.empty:
                    st.warning(
                        f"⚠️ Existem {len(alteradas)} proposta(s) alterada(s) pelo vendedor aguardando conferência."
                    )

            st.divider()
            st.subheader("📄 Propostas")
            st.caption("🟨 Pendente | 🟥 Pendente há mais de 1 hora no painel do admin")

            if df.empty:
                st.info("Nenhuma proposta encontrada.")
            else:
                if st.session_state.tipo == "admin":
                    colunas = [
                        "id",
                        "data",
                        "vendedor",
                        "cliente",
                        "cpf",
                        "telefone",
                        "tabela_banco",
                        "valor",
                        "status",
                        "conferido",
                        "alterado_vendedor",
                        "observacao",
                        "observacao_admin",
                        "observacao_alteracao"
                    ]
                else:
                    colunas = [
                        "id",
                        "data",
                        "cliente",
                        "telefone",
                        "tabela_banco",
                        "valor",
                        "status",
                        "conferido",
                        "observacao"
                    ]

                colunas = [c for c in colunas if c in df.columns]

                df_visao = df[colunas].copy()

                if "valor" in df_visao.columns:
                    df_visao["valor"] = df_visao["valor"].apply(dinheiro)

                if "valor_comissao_empresa" in df_visao.columns:
                    df_visao["valor_comissao_empresa"] = (
                        df_visao["valor_comissao_empresa"].apply(dinheiro)
                    )

                st.dataframe(
                    df_visao.style.apply(
                        destacar_linhas_pendentes,
                        tipo_usuario=st.session_state.tipo,
                        axis=1
                    ),
                    use_container_width=True
                )

                # =========================
                # AÇÕES RÁPIDAS ADMIN
                # =========================

                if st.session_state.tipo == "admin":
                    st.divider()
                    st.subheader("⚙️ Ações rápidas")

                    acoes_df = df[["id", "cliente", "valor", "status", "conferido", "alterado_vendedor"]].copy()
                    acoes_df["excluir"] = False

                    editado = st.data_editor(
                        acoes_df,
                        use_container_width=True,
                        disabled=["id", "cliente", "valor", "status", "alterado_vendedor"],
                        hide_index=True
                    )

                    col_a, col_b = st.columns(2)

                    with col_a:
                        if st.button("✅ Salvar conferências"):
                            for _, row in editado.iterrows():
                                update = {"conferido": bool(row["conferido"])}

                                if bool(row["conferido"]):
                                    update["alterado_vendedor"] = False

                                supabase.table("vendas").update(update).eq("id", int(row["id"])).execute()

                            st.success("Conferências salvas!")
                            st.rerun()

                    with col_b:
                        confirmar_exclusao = st.checkbox("Confirmo que quero excluir as propostas marcadas")

                        if st.button("🗑️ Excluir propostas marcadas"):
                            if not confirmar_exclusao:
                                st.error("Marque a confirmação antes de excluir.")
                            else:
                                ids_excluir = editado[editado["excluir"] == True]["id"].tolist()

                                if not ids_excluir:
                                    st.warning("Nenhuma proposta marcada para excluir.")
                                else:
                                    for venda_id in ids_excluir:
                                        supabase.table("vendas").delete().eq("id", int(venda_id)).execute()

                                    st.success(f"{len(ids_excluir)} proposta(s) excluída(s)!")
                                    st.rerun()

                # =========================
                # EDITAR PROPOSTA
                # =========================

                st.divider()
                st.subheader("✏️ Editar proposta")

                proposta_id = st.selectbox("Escolha a proposta", df["id"].tolist())

                proposta = df[df["id"] == proposta_id].iloc[0]

                bloqueada = (
                    st.session_state.tipo != "admin"
                    and bool(proposta.get("conferido", False)) is True
                )

                if bloqueada:
                    st.warning("🔒 Esta proposta já foi conferida pelo admin. O vendedor não pode mais editar.")
                else:
                    with st.form("editar_proposta"):
                        cliente_edit = st.text_input("Cliente", value=str(proposta.get("cliente", "") or ""))
                        cpf_edit = st.text_input("CPF", value=str(proposta.get("cpf", "") or ""))
                        cpf_edit_preview = limpar_documento(cpf_edit)

                        if cpf_edit:
                            if len(cpf_edit_preview) < 11:
                                st.error(f"CPF incompleto: faltam {11 - len(cpf_edit_preview)} número(s).")
                            elif len(cpf_edit_preview) > 11:
                                st.error(f"CPF com números a mais: remova {len(cpf_edit_preview) - 11} número(s).")
                            elif validar_cpf(cpf_edit_preview):
                                st.success(f"CPF válido: {cpf_edit_preview}")
                            else:
                                st.error("CPF inválido. Confira os números digitados.")

                        telefone_edit = st.text_input("Telefone", value=str(proposta.get("telefone", "") or ""))
                        telefone_edit_preview = limpar_documento(telefone_edit)

                        if telefone_edit:
                            if len(telefone_edit_preview) < 10:
                                st.error("Telefone incompleto. Informe DDD + número.")
                            elif len(telefone_edit_preview) > 11:
                                st.error(f"Telefone com números a mais: remova {len(telefone_edit_preview) - 11} número(s).")
                            elif validar_telefone(telefone_edit_preview):
                                st.success(f"Telefone válido: {telefone_edit_preview}")
                            else:
                                st.error("Telefone inválido. Use DDD + número. Exemplo: 11910721110.")

                        tabelas_edit = carregar_tabelas()
                        tabela_atual = str(proposta.get("tabela_banco", "") or proposta.get("produto", "") or "")
                        tabela_index = tabelas_edit.index(tabela_atual) if tabela_atual in tabelas_edit else 0

                        tabela_edit = st.selectbox("Tabela/Banco", tabelas_edit, index=tabela_index)

                        valor_edit_texto = st.text_input(
                            "Valor",
                            value=dinheiro(proposta.get("valor") or 0).replace("R$ ", ""),
                            placeholder="Ex: R$ 1.758,71"
                        )

                        valor_edit = converter_valor_brasileiro(valor_edit_texto)

                        if valor_edit_texto:
                            st.caption(f"Valor identificado: {dinheiro(valor_edit)}")

                        status_lista = ["Pendente", "Pago", "Cancelado"]
                        status_atual = str(proposta.get("status", "Pendente") or "Pendente")
                        status_index = status_lista.index(status_atual) if status_atual in status_lista else 0

                        status_edit = st.selectbox("Status", status_lista, index=status_index)

                        observacao_edit = st.text_area(
                            "Observação",
                            value=str(proposta.get("observacao", "") or "")
                        )

                        if st.session_state.tipo == "admin":
                            conferido_edit = st.checkbox(
                                "✅ Conferido",
                                value=bool(proposta.get("conferido", False))
                            )

                            observacao_admin_edit = st.text_area(
                                "Observação admin",
                                value=str(proposta.get("observacao_admin", "") or "")
                            )
                        else:
                            observacao_alteracao_edit = st.text_area(
                                "Motivo da alteração",
                                placeholder="Ex: corrigi valor, telefone ou status..."
                            )

                        salvar_edit = st.form_submit_button("Salvar alterações")

                        if salvar_edit:
                            cpf_edit_limpo = limpar_documento(cpf_edit)
                            telefone_edit_limpo = limpar_documento(telefone_edit)

                            if not validar_cpf(cpf_edit_limpo):
                                st.error("Corrija o CPF antes de salvar. Ele precisa ser válido e ter 11 números.")
                            elif not validar_telefone(telefone_edit_limpo):
                                st.error("Corrija o telefone antes de salvar. Informe DDD + número.")
                            elif valor_edit <= 0:
                                st.error("Corrija o valor antes de salvar.")
                            else:
                                perc_empresa = calcular_percentual_empresa_venda(tabela_edit, valor_edit)
                                valor_empresa = float(valor_edit) * (perc_empresa / 100)

                                dados_update = {
                                "cliente": cliente_edit,
                                "cpf": limpar_documento(cpf_edit),
                                "telefone": limpar_documento(telefone_edit),
                                "produto": tabela_edit,
                                "tabela_banco": tabela_edit,
                                "valor": valor_edit,
                                "status": status_edit,
                                "observacao": observacao_edit,
                                "comissao_empresa": perc_empresa,
                                "valor_comissao_empresa": valor_empresa
                            }

                                if st.session_state.tipo == "admin":
                                    dados_update["conferido"] = conferido_edit
                                    dados_update["alterado_vendedor"] = False
                                    dados_update["observacao_admin"] = observacao_admin_edit
                                else:
                                    dados_update["alterado_vendedor"] = True
                                    dados_update["data_alteracao_vendedor"] = str(datetime.now())
                                    dados_update["observacao_alteracao"] = observacao_alteracao_edit
                                    dados_update["conferido"] = False

                                supabase.table("vendas").update(dados_update).eq("id", int(proposta_id)).execute()

                                st.success("Proposta atualizada!")
                                st.rerun()


    # =========================
    # USUÁRIOS
    # =========================

    elif menu == "👥 Usuários":
        st.header("👥 Usuários")
        st.subheader("➕ Criar usuário")

        with st.form("novo_usuario"):
            nome = st.text_input("Nome")
            usuario = st.text_input("Usuário")
            senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo", ["vendedor", "admin"])

            criar = st.form_submit_button("Criar usuário")

            if criar:
                if not nome or not usuario or not senha:
                    st.error("Preencha nome, usuário e senha.")
                else:
                    dados = {
                        "nome": nome.strip(),
                        "usuario": usuario.strip().lower(),
                        "senha_hash": hash_senha(senha),
                        "tipo": tipo,
                        "ativo": True
                    }

                    supabase.table("usuarios").insert(dados).execute()
                    st.success("Usuário criado!")
                    st.rerun()

        usuarios = supabase.table("usuarios").select("*").order("id").execute()
        df_users = pd.DataFrame(usuarios.data)

        if not df_users.empty:
            st.subheader("📋 Usuários cadastrados")
            st.dataframe(df_users[["id", "nome", "usuario", "tipo", "ativo"]], use_container_width=True)

            st.divider()
            st.subheader("✏️ Editar usuário")

            user_id = st.selectbox("ID do usuário", df_users["id"].tolist())
            user = df_users[df_users["id"] == user_id].iloc[0]

            novo_nome = st.text_input("Nome", value=str(user.get("nome", "") or ""))
            novo_login = st.text_input("Usuário/Login", value=str(user.get("usuario", "") or ""))

            tipo_atual = str(user.get("tipo", "vendedor") or "vendedor")
            tipo_index = 0 if tipo_atual == "vendedor" else 1

            novo_tipo = st.selectbox("Tipo", ["vendedor", "admin"], index=tipo_index)

            if st.button("Salvar usuário"):
                supabase.table("usuarios").update({
                    "nome": novo_nome.strip(),
                    "usuario": novo_login.strip().lower(),
                    "tipo": novo_tipo
                }).eq("id", int(user_id)).execute()

                st.success("Usuário atualizado!")
                st.rerun()

            st.divider()
            st.subheader("🔑 Alterar senha")

            nova_senha = st.text_input("Nova senha", type="password")

            if st.button("Alterar senha"):
                if nova_senha:
                    supabase.table("usuarios").update({
                        "senha_hash": hash_senha(nova_senha)
                    }).eq("id", int(user_id)).execute()

                    st.success("Senha alterada!")
                    st.rerun()
                else:
                    st.error("Digite uma nova senha.")

            st.divider()
            st.subheader("✅ Ativar / Desativar")

            if st.button("Alterar status"):
                if str(user.get("usuario", "")).lower() == "admin":
                    st.error("Não é permitido desativar o admin principal.")
                else:
                    supabase.table("usuarios").update({
                        "ativo": not bool(user.get("ativo", True))
                    }).eq("id", int(user_id)).execute()

                    st.success("Status alterado!")
                    st.rerun()

            st.divider()
            st.subheader("🗑️ Excluir usuário")

            if st.button("Excluir usuário"):
                if str(user.get("usuario", "")).lower() == "admin":
                    st.error("Não é permitido excluir o admin principal.")
                else:
                    supabase.table("usuarios").delete().eq("id", int(user_id)).execute()
                    st.success("Usuário excluído!")
                    st.rerun()

    # =========================
    # COMISSÕES
    # =========================

    elif menu == "💰 Comissões":
        st.header("💰 Regras de Comissão")
        st.subheader("➕ Criar nova regra")

        with st.form("nova_regra"):
            produto = st.text_input("Tabela/Banco")
            valor_minimo = st.number_input("Valor mínimo", min_value=0.0, step=1000.0)
            percentual_empresa = st.number_input("% empresa", min_value=0.0, step=0.01)

            salvar = st.form_submit_button("Salvar regra")

            if salvar:
                if not produto:
                    st.error("Preencha o nome da tabela/banco.")
                else:
                    supabase.table("regras_comissao").insert({
                        "produto": produto.strip().upper(),
                        "valor_minimo": valor_minimo,
                        "percentual_empresa": percentual_empresa,
                        "percentual_vendedor": 0,
                        "ativo": True
                    }).execute()

                    st.success("Regra criada!")
                    st.rerun()

        regras = (
            supabase.table("regras_comissao")
            .select("*")
            .order("produto")
            .order("valor_minimo")
            .execute()
        )

        df_regras = pd.DataFrame(regras.data)

        if df_regras.empty:
            st.warning("Nenhuma regra cadastrada.")
        else:
            st.subheader("📋 Regras cadastradas")
            st.dataframe(df_regras, use_container_width=True)

            st.divider()
            st.subheader("✏️ Editar regra")

            regra_id = st.selectbox("ID da regra", df_regras["id"].tolist())
            regra = df_regras[df_regras["id"] == regra_id].iloc[0]

            with st.form("editar_regra"):
                produto_edit = st.text_input("Tabela/Banco", value=str(regra.get("produto", "") or ""))
                valor_minimo_edit = st.number_input(
                    "Valor mínimo",
                    min_value=0.0,
                    step=1000.0,
                    value=float(regra.get("valor_minimo") or 0)
                )
                percentual_empresa_edit = st.number_input(
                    "% empresa",
                    min_value=0.0,
                    step=0.01,
                    value=float(regra.get("percentual_empresa") or 0)
                )
                ativo_edit = st.checkbox("Ativo", value=bool(regra.get("ativo", True)))

                salvar_regra = st.form_submit_button("Salvar alterações")

                if salvar_regra:
                    supabase.table("regras_comissao").update({
                        "produto": produto_edit.strip().upper(),
                        "valor_minimo": valor_minimo_edit,
                        "percentual_empresa": percentual_empresa_edit,
                        "percentual_vendedor": 0,
                        "ativo": ativo_edit
                    }).eq("id", int(regra_id)).execute()

                    st.success("Regra atualizada!")
                    st.rerun()

            st.divider()
            st.subheader("🗑️ Excluir regra")

            confirmar = st.checkbox("Confirmo que quero excluir esta regra")

            if st.button("Excluir regra"):
                if not confirmar:
                    st.error("Marque a confirmação.")
                else:
                    supabase.table("regras_comissao").delete().eq("id", int(regra_id)).execute()
                    st.success("Regra excluída!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
