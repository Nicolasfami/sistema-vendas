# operax_theme.py
# Tema visual OPERAX SALES — Dark Neon Blue
# Importe este arquivo no seu app principal com:
#   from operax_theme import aplicar_tema, mostrar_cabecalho_completo

import streamlit as st
from pathlib import Path


# ══════════════════════════════════════════════════════════════════════
#  LOGO SVG (inline — sem precisar de arquivo externo)
# ══════════════════════════════════════════════════════════════════════

LOGO_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" width="72" height="72">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#000918"/>
      <stop offset="100%" stop-color="#001a3a"/>
    </radialGradient>
    <radialGradient id="ring1" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#00d5ff" stop-opacity="0"/>
      <stop offset="60%"  stop-color="#00aaff" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#0055ff" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="ring2" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#5ee7ff" stop-opacity="0"/>
      <stop offset="65%"  stop-color="#00c8ff" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="#003eff" stop-opacity="0"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glow2">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>

  <!-- Fundo arredondado -->
  <rect width="120" height="120" rx="28" fill="url(#bg)"/>

  <!-- Anel externo inclinado -->
  <ellipse cx="60" cy="60" rx="46" ry="14"
    fill="none" stroke="url(#ring1)" stroke-width="3.5"
    transform="rotate(-28 60 60)" filter="url(#glow2)" opacity="0.85"/>

  <!-- Anel médio -->
  <ellipse cx="60" cy="60" rx="34" ry="10"
    fill="none" stroke="url(#ring2)" stroke-width="2.5"
    transform="rotate(-28 60 60)" filter="url(#glow)" opacity="0.75"/>

  <!-- Anel interno -->
  <ellipse cx="60" cy="60" rx="20" ry="6"
    fill="none" stroke="#00eaff" stroke-width="1.8"
    transform="rotate(-28 60 60)" filter="url(#glow)" opacity="0.6"/>

  <!-- Núcleo central brilhante -->
  <circle cx="60" cy="60" r="7" fill="#000" />
  <circle cx="60" cy="60" r="5" fill="#00d5ff" opacity="0.9" filter="url(#glow2)"/>
  <circle cx="60" cy="60" r="2.5" fill="#ffffff"/>

  <!-- Reflexo sutil -->
  <ellipse cx="60" cy="60" rx="52" ry="16"
    fill="none" stroke="#0088ff" stroke-width="0.8"
    stroke-dasharray="6 4"
    transform="rotate(-28 60 60)" opacity="0.30"/>
</svg>
"""


# ══════════════════════════════════════════════════════════════════════
#  ÍCONES SVG PARA O MENU LATERAL
# ══════════════════════════════════════════════════════════════════════

ICONES = {
    "admin": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 2a4 4 0 1 0 0 8 4 4 0 0 0 0-8z"/><path d="M6 20v-1a6 6 0 0 1 12 0v1"/>
        <path d="M18 8l2 2-2 2"/><path d="M22 10h-4"/></svg>""",

    "nova_venda": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="16" rx="3"/>
        <path d="M9 8h6M9 12h6M9 16h4"/>
        <path d="M16 2v4M8 2v4"/></svg>""",

    "painel": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="9" rx="2"/>
        <rect x="14" y="3" width="7" height="5" rx="2"/>
        <rect x="14" y="12" width="7" height="9" rx="2"/>
        <rect x="3" y="16" width="7" height="5" rx="2"/></svg>""",

    "usuarios": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="9" cy="7" r="4"/><path d="M3 20v-1a6 6 0 0 1 12 0v1"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        <path d="M21 20v-1a4 4 0 0 0-3-3.85"/></svg>""",

    "comissoes": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="9"/>
        <path d="M9 9h.01M15 15h.01"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <circle cx="9" cy="9" r="1" fill="currentColor"/>
        <circle cx="15" cy="15" r="1" fill="currentColor"/></svg>""",

    "sair": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
        <polyline points="16 17 21 12 16 7"/>
        <line x1="21" y1="12" x2="9" y2="12"/></svg>""",

    "chat": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>""",

    "bolt": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",

    "refresh": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="23 4 23 10 17 10"/>
        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>""",

    "usuario_ctrl": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="8" r="4"/><path d="M6 20v-1a6 6 0 0 1 12 0v1"/>
        <circle cx="19" cy="5" r="3" fill="#00c8ff" stroke="none"/></svg>""",

    "banco": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="22" x2="21" y2="22"/>
        <line x1="6" y1="18" x2="6" y2="11"/>
        <line x1="10" y1="18" x2="10" y2="11"/>
        <line x1="14" y1="18" x2="14" y2="11"/>
        <line x1="18" y1="18" x2="18" y2="11"/>
        <polygon points="12 2 20 7 4 7"/></svg>""",

    "cifrao": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="12" y1="1" x2="12" y2="23"/>
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>""",
}


# ══════════════════════════════════════════════════════════════════════
#  CSS COMPLETO — DARK NEON BLUE
# ══════════════════════════════════════════════════════════════════════

CSS_DARK_NEON = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── BASE ────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at 82% 12%, rgba(0, 174, 255, 0.22), transparent 24%),
        radial-gradient(circle at 92% 85%, rgba(0, 102, 255, 0.26), transparent 20%),
        radial-gradient(circle at 10% 90%, rgba(0, 60, 200, 0.18), transparent 22%),
        linear-gradient(135deg, #020617 0%, #06152f 42%, #020617 100%) !important;
    color: #eaf6ff !important;
}

.block-container {
    max-width: 1240px !important;
    padding-top: 1.3rem !important;
    padding-bottom: 3rem !important;
}

/* ── SIDEBAR ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(0, 195, 255, .32), transparent 32%),
        linear-gradient(180deg, #020e28 0%, #020617 100%) !important;
    border-right: 1px solid rgba(0, 183, 255, .55) !important;
    box-shadow: 4px 0 40px rgba(0, 183, 255, .20) !important;
    min-width: 260px !important;
    max-width: 260px !important;
}

section[data-testid="stSidebar"] > div {
    padding: 18px 18px 18px 18px !important;
}

[data-testid="stSidebar"] * { color: #ffffff !important; }

[data-testid="collapsedControl"] { background: transparent !important; }

/* ── LOGO SIDEBAR ────────────────────────────────────────── */
.sidebar-logo-wrap {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 4px 0 22px 0;
}
.sidebar-logo-icon {
    width: 64px;
    height: 64px;
    border-radius: 20px;
    background: radial-gradient(circle at 50% 50%, #000918 0%, #001a3a 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 24px rgba(0, 183, 255, .90),
        0 0 56px rgba(0, 102, 255, .50),
        inset 0 0 0 1px rgba(255,255,255,.18);
    flex-shrink: 0;
}
.sidebar-logo-text {
    display: flex;
    flex-direction: column;
    line-height: 1.1;
}
.sidebar-logo-text .name {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 26px;
    font-weight: 700;
    color: #ffffff !important;
    letter-spacing: .10em;
    text-shadow: 0 0 16px rgba(0,183,255,.55);
}
.sidebar-logo-text .sub {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .32em;
    color: #00c8ff !important;
    text-transform: uppercase;
    margin-top: 1px;
}

/* ── USUÁRIO LOGADO ──────────────────────────────────────── */
.sidebar-user {
    background: rgba(2, 12, 35, .65);
    border: 1px solid rgba(0, 183, 255, .40);
    border-radius: 18px;
    padding: 14px 16px;
    margin: 0 0 22px 0;
    box-shadow: 0 0 22px rgba(0, 183, 255, .15);
    display: flex;
    align-items: center;
    gap: 10px;
}
.sidebar-user .avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #005bff, #00c8ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.sidebar-user .uname {
    font-size: 14px;
    font-weight: 700;
    color: #fff !important;
}
.sidebar-user .ustatus {
    font-size: 11px;
    color: #00ff9d !important;
    display: flex;
    align-items: center;
    gap: 5px;
}
.sidebar-user .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #00ff9d;
    box-shadow: 0 0 6px #00ff9d;
    display: inline-block;
}

/* ── MENU LABELS ─────────────────────────────────────────── */
.menu-label {
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .16em;
    color: #00c8ff !important;
    margin: 18px 0 8px 4px;
}

/* ── MENU ATIVO ──────────────────────────────────────────── */
.menu-item-ativo {
    background: linear-gradient(90deg, rgba(0, 84, 255, .95), rgba(0, 200, 255, .95));
    color: #ffffff !important;
    border-radius: 16px;
    padding: 13px 14px;
    margin: 5px 0;
    font-weight: 800;
    font-size: 15px;
    box-shadow:
        0 0 20px rgba(0, 200, 255, .70),
        0 0 44px rgba(0, 102, 255, .30),
        inset 0 0 0 1px rgba(255,255,255,.18);
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;
    transition: all .2s;
}
.menu-item-ativo svg {
    width: 20px; height: 20px;
    stroke: #fff;
    flex-shrink: 0;
}

/* ── MENU INATIVO ────────────────────────────────────────── */
[data-testid="stSidebar"] .stButton button {
    color: #cceeff !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: .65rem .75rem !important;
    width: 100% !important;
    transition: all .18s !important;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(0, 183, 255, .14) !important;
    transform: translateX(3px) !important;
    color: #ffffff !important;
}

/* ── HEADER / HERO ───────────────────────────────────────── */
.operax-hero {
    background:
        radial-gradient(circle at 78% 20%, rgba(0, 183, 255, .20), transparent 30%),
        radial-gradient(circle at 5% 80%, rgba(0,60,255,.18), transparent 26%),
        linear-gradient(135deg, rgba(2, 6, 23, .94), rgba(3, 14, 40, .90));
    border: 1px solid rgba(0, 183, 255, .45);
    border-radius: 28px;
    box-shadow:
        0 0 38px rgba(0, 183, 255, .18),
        0 24px 70px rgba(0,0,0,.32);
    padding: 22px 30px;
    margin-bottom: 26px;
    position: relative;
    overflow: hidden;
}
.operax-hero::before {
    content: '';
    position: absolute;
    top: -40%;
    right: -8%;
    width: 340px;
    height: 340px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,183,255,.08), transparent 65%);
    pointer-events: none;
}
.operax-hero-inner {
    display: flex;
    align-items: center;
    gap: 22px;
}
.operax-hero-logo {
    width: 80px;
    height: 80px;
    border-radius: 24px;
    background: radial-gradient(circle, #000918, #001a3a);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow:
        0 0 28px rgba(0,183,255,.85),
        0 0 60px rgba(0,100,255,.45);
    flex-shrink: 0;
}
.operax-hero-text h1 {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 52px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    letter-spacing: .06em !important;
    margin: 0 !important;
    line-height: 1 !important;
    text-shadow: 0 0 28px rgba(0,183,255,.40) !important;
}
.operax-hero-text h1 span {
    color: #00c8ff !important;
    text-shadow: 0 0 22px rgba(0,200,255,.55) !important;
}
.operax-hero-text p {
    color: #cceeff !important;
    font-size: 16px !important;
    margin: 8px 0 0 0 !important;
    font-weight: 500 !important;
}
.operax-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 14px;
}
.operax-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(2, 12, 35, .72);
    border: 1px solid rgba(0, 183, 255, .55);
    color: #eaf6ff !important;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 0 18px rgba(0, 183, 255, .18);
}
.operax-pill svg {
    width: 15px; height: 15px; stroke: #00c8ff;
}

/* ── TOPBAR ÍCONES ───────────────────────────────────────── */
.operax-topbar {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 10px;
    padding: 0 4px 0 0;
    margin-bottom: 6px;
}
.topbar-icon {
    width: 38px; height: 38px;
    border-radius: 12px;
    background: rgba(2, 12, 35, .70);
    border: 1px solid rgba(0, 183, 255, .35);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    transition: all .18s;
    position: relative;
}
.topbar-icon:hover {
    border-color: rgba(0, 200, 255, .75);
    box-shadow: 0 0 18px rgba(0,183,255,.35);
}
.topbar-icon svg { width: 18px; height: 18px; stroke: #00c8ff; }
.topbar-badge {
    position: absolute;
    top: -5px; right: -5px;
    width: 18px; height: 18px;
    border-radius: 50%;
    background: linear-gradient(135deg, #005bff, #00c8ff);
    color: #fff !important;
    font-size: 10px;
    font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 10px rgba(0,183,255,.6);
}
.topbar-chat-btn {
    display: inline-flex; align-items: center; gap: 8px;
    padding: 9px 18px;
    border-radius: 14px;
    background: linear-gradient(135deg, #005bff, #00c8ff);
    color: #fff !important;
    font-weight: 800;
    font-size: 14px;
    cursor: pointer;
    box-shadow: 0 0 22px rgba(0,183,255,.40);
    border: 1px solid rgba(0,200,255,.45);
    transition: all .18s;
}
.topbar-chat-btn:hover { box-shadow: 0 0 36px rgba(0,183,255,.65); }
.topbar-chat-btn svg { width: 17px; height: 17px; stroke: #fff; }

/* ── FORMULÁRIOS ─────────────────────────────────────────── */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    border-radius: 14px !important;
    border: 1px solid rgba(0, 183, 255, .45) !important;
    background: rgba(2, 12, 35, .65) !important;
    color: #ffffff !important;
    box-shadow: 0 0 14px rgba(0, 183, 255, .10) !important;
    font-size: 15px !important;
}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: rgba(207, 236, 255, .60) !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(0, 220, 255, .90) !important;
    box-shadow: 0 0 0 3px rgba(0,183,255,.16), 0 0 22px rgba(0,183,255,.18) !important;
}
div[data-baseweb="select"] {
    border-radius: 14px !important;
    border: 1px solid rgba(0, 183, 255, .45) !important;
    background: rgba(2, 12, 35, .65) !important;
    color: #ffffff !important;
}

/* ── BOTÕES ──────────────────────────────────────────────── */
.stButton button {
    background: linear-gradient(135deg, #005bff, #00c8ff) !important;
    border: 1px solid rgba(0, 183, 255, .45) !important;
    border-radius: 14px !important;
    color: white !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    box-shadow: 0 0 22px rgba(0, 183, 255, .35) !important;
    transition: all .18s !important;
}
.stButton button:hover {
    box-shadow: 0 0 38px rgba(0, 183, 255, .60) !important;
    transform: translateY(-1px) !important;
}

/* ── CARDS / MÉTRICAS ────────────────────────────────────── */
div[data-testid="stMetric"] {
    background: rgba(2, 12, 35, .72) !important;
    border: 1px solid rgba(0, 183, 255, .38) !important;
    border-radius: 22px !important;
    padding: 18px 20px !important;
    box-shadow: 0 0 24px rgba(0, 183, 255, .14) !important;
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { color: #00ff9d !important; }

/* ── TABELA ──────────────────────────────────────────────── */
.stDataFrame {
    border-radius: 18px !important;
    overflow: hidden !important;
    border: 1px solid rgba(0, 183, 255, .22) !important;
    box-shadow: 0 0 24px rgba(0, 183, 255, .10) !important;
}

/* ── TÍTULOS ─────────────────────────────────────────────── */
h1, h2, h3, h4 {
    color: #ffffff !important;
    text-shadow: 0 0 18px rgba(0, 183, 255, .22) !important;
}

/* ── DIVIDER ─────────────────────────────────────────────── */
hr { border-color: rgba(0, 183, 255, .20) !important; }

/* ── ALERTAS ─────────────────────────────────────────────── */
div[data-testid="stAlert"] { border-radius: 16px !important; }

/* ── CHAT FLUTUANTE ──────────────────────────────────────── */
.chat-float {
    position: fixed;
    bottom: 28px; right: 28px;
    width: 56px; height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #005bff, #00c8ff);
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
    box-shadow:
        0 0 28px rgba(0, 183, 255, .75),
        0 0 56px rgba(0, 102, 255, .40);
    border: 2px solid rgba(255,255,255,.25);
    z-index: 9999;
    transition: all .2s;
}
.chat-float:hover { transform: scale(1.08); box-shadow: 0 0 40px rgba(0,183,255,.90); }
.chat-float svg { width: 26px; height: 26px; stroke: #fff; }
.chat-float-badge {
    position: absolute; top: -4px; right: -4px;
    width: 20px; height: 20px; border-radius: 50%;
    background: linear-gradient(135deg, #0040ff, #00c8ff);
    color: #fff !important; font-size: 11px; font-weight: 800;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 12px rgba(0,183,255,.6);
}

/* ── FORMULÁRIO CARD (cadastro de venda) ─────────────────── */
.form-card {
    background: rgba(2, 8, 28, .80);
    border: 1px solid rgba(0, 183, 255, .35);
    border-radius: 24px;
    padding: 28px 32px;
    box-shadow:
        0 0 32px rgba(0, 183, 255, .12),
        0 22px 60px rgba(0,0,0,.30);
    margin-bottom: 24px;
}
.form-card-title {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px;
    font-size: 22px;
    font-weight: 800;
    color: #ffffff !important;
}
.form-card-title svg {
    width: 32px; height: 32px;
    stroke: #00c8ff;
    background: rgba(0,183,255,.12);
    padding: 6px;
    border-radius: 10px;
    border: 1px solid rgba(0,183,255,.35);
    box-sizing: content-box;
}
.field-label {
    font-size: 13px;
    font-weight: 700;
    color: #cceeff !important;
    letter-spacing: .04em;
    margin-bottom: 4px;
}
</style>
"""


# ══════════════════════════════════════════════════════════════════════
#  FUNÇÕES PÚBLICAS
# ══════════════════════════════════════════════════════════════════════

def aplicar_tema():
    """Aplica todo o CSS dark neon. Chame logo após st.set_page_config."""
    st.markdown(CSS_DARK_NEON, unsafe_allow_html=True)


def logo_svg(size: int = 64) -> str:
    """Retorna o logo SVG como string HTML com tamanho customizável."""
    return LOGO_SVG.replace('width="72"', f'width="{size}"').replace('height="72"', f'height="{size}"')


def icone(nome: str, size: int = 22, cor: str = "#00c8ff") -> str:
    """Retorna ícone SVG como string HTML."""
    svg = ICONES.get(nome, ICONES["nova_venda"])
    return f'<span style="display:inline-flex;align-items:center;color:{cor};width:{size}px;height:{size}px">{svg}</span>'


def mostrar_topbar(notificacoes: int = 0):
    """Renderiza a barra superior direita com ícones e botão Chat."""
    ico_star = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>'
    ico_pen  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>'
    ico_gear = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    ico_bell = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>'
    ico_chat = ICONES["chat"]

    badge_html = f'<div class="topbar-badge">{notificacoes}</div>' if notificacoes > 0 else ""

    st.markdown(f"""
    <div class="operax-topbar">
        <div class="topbar-icon">{ico_star}</div>
        <div class="topbar-icon">{ico_pen}</div>
        <div class="topbar-icon">{ico_gear}</div>
        <div class="topbar-icon" style="position:relative">
            {ico_bell}
            {badge_html}
        </div>
        <div class="topbar-chat-btn">
            {ico_chat}&nbsp;Chat
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:14px;height:14px"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_cabecalho(subtitulo: str = "Sistema inteligente de vendas e operações financeiras"):
    """Renderiza o hero header com logo SVG, título e pills."""
    bolt_svg  = ICONES["bolt"]
    ref_svg   = ICONES["refresh"]
    ctrl_svg  = ICONES["usuario_ctrl"]

    st.markdown(f"""
    <div class="operax-hero">
        <div class="operax-hero-inner">
            <div class="operax-hero-logo">{logo_svg(62)}</div>
            <div class="operax-hero-text">
                <h1>OPERAX <span>SALES</span></h1>
                <p>{subtitulo}</p>
                <div class="operax-pills">
                    <div class="operax-pill">{bolt_svg} Painel inteligente</div>
                    <div class="operax-pill">{ref_svg} Atualização por ação</div>
                    <div class="operax-pill">{ctrl_svg} Controle por vendedor</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_sidebar_logo():
    """Renderiza o logo e nome OPERAX SALES no topo da sidebar."""
    st.markdown(f"""
    <div class="sidebar-logo-wrap">
        <div class="sidebar-logo-icon">{logo_svg(46)}</div>
        <div class="sidebar-logo-text">
            <span class="name">OPERAX</span>
            <span class="sub">— SALES —</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_usuario_sidebar(nome: str = "Administrador", online: bool = True):
    """Renderiza o card do usuário logado na sidebar."""
    status_dot = '<span class="dot"></span>' if online else ""
    status_txt = "Online" if online else "Offline"
    st.markdown(f"""
    <div class="sidebar-user">
        <div class="avatar">👤</div>
        <div>
            <div class="uname">{nome}</div>
            <div class="ustatus">{status_dot} {status_txt}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def mostrar_menu_label(label: str):
    """Renderiza o label de seção do menu (ex: OPERAÇÃO, GESTÃO)."""
    st.markdown(f'<div class="menu-label">{label}</div>', unsafe_allow_html=True)


def mostrar_menu_ativo(label: str, icone_nome: str = "nova_venda"):
    """Renderiza o item de menu ativo (selecionado)."""
    svg = ICONES.get(icone_nome, ICONES["nova_venda"])
    st.markdown(f"""
    <div class="menu-item-ativo">
        {svg}
        <span>{label}</span>
    </div>
    """, unsafe_allow_html=True)


def mostrar_chat_float(badge: int = 2):
    """Renderiza o botão flutuante de chat no canto inferior direito."""
    badge_html = f'<div class="chat-float-badge">{badge}</div>' if badge > 0 else ""
    st.markdown(f"""
    <div class="chat-float">
        {ICONES['chat']}
        {badge_html}
    </div>
    """, unsafe_allow_html=True)


def form_card_inicio(titulo: str, icone_nome: str = "nova_venda"):
    """Abre o container visual de um formulário/card."""
    svg = ICONES.get(icone_nome, ICONES["nova_venda"])
    st.markdown(f"""
    <div class="form-card">
        <div class="form-card-title">{svg} {titulo}</div>
    """, unsafe_allow_html=True)


def form_card_fim():
    """Fecha o container visual de um formulário/card."""
    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════
#  EXEMPLO DE USO RÁPIDO
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    st.set_page_config(page_title="OPERAX SALES", layout="wide", page_icon="💠")
    aplicar_tema()

    with st.sidebar:
        mostrar_sidebar_logo()
        mostrar_usuario_sidebar("Administrador")
        mostrar_menu_label("OPERAÇÃO")
        mostrar_menu_ativo("Nova Venda", "nova_venda")
        st.button("📊 Painel")
        mostrar_menu_label("GESTÃO")
        st.button("👥 Usuários")
        st.button("💰 Comissões")
        st.button("🚪 Sair")

    mostrar_topbar(notificacoes=2)
    mostrar_cabecalho()
    form_card_inicio("Cadastro de Venda", "nova_venda")
    st.text_input("Cliente", placeholder="Digite o nome do cliente...")
    st.text_input("CPF / CNPJ", placeholder="Ex: 999.999.999-99")
    st.text_input("Telefone", placeholder="Ex: (11) 99976-7867")
    form_card_fim()
    mostrar_chat_float(2)
