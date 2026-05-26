import { useState, useEffect, useCallback, useRef } from "react";

// ===================== SUPABASE CONFIG =====================
const SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co";
const SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt";

async function sb(path, options = {}) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${path}`, {
    headers: {
      apikey: SUPABASE_KEY,
      Authorization: `Bearer ${SUPABASE_KEY}`,
      "Content-Type": "application/json",
      Prefer: options.prefer || "return=representation",
      ...options.headers,
    },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  const text = await res.text();
  return text ? JSON.parse(text) : [];
}

async function hashSenha(senha) {
  const buf = new TextEncoder().encode(String(senha));
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

function limparDoc(v) {
  return String(v || "").replace(/\D/g, "");
}

function dinheiro(v) {
  try {
    return new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(
      parseFloat(v) || 0
    );
  } catch {
    return "R$ 0,00";
  }
}

function validarCPF(cpf) {
  const c = limparDoc(cpf);
  if (c.length !== 11) return false;
  if (c === c[0].repeat(11)) return false;
  let soma = Array.from({ length: 9 }, (_, i) => parseInt(c[i]) * (10 - i)).reduce((a, b) => a + b, 0);
  let d1 = (soma * 10) % 11;
  if (d1 === 10) d1 = 0;
  soma = Array.from({ length: 10 }, (_, i) => parseInt(c[i]) * (11 - i)).reduce((a, b) => a + b, 0);
  let d2 = (soma * 10) % 11;
  if (d2 === 10) d2 = 0;
  return d1 === parseInt(c[9]) && d2 === parseInt(c[10]);
}

function validarCNPJ(cnpj) {
  const c = limparDoc(cnpj);
  if (c.length !== 14) return false;
  if (c === c[0].repeat(14)) return false;
  return true;
}

function validarTelefone(tel) {
  const t = limparDoc(tel);
  if (![10, 11].includes(t.length)) return false;
  if (t.slice(0, 2) === "00") return false;
  if (t.length === 11 && t[2] !== "9") return false;
  return true;
}

// ===================== STYLES =====================
const CSS = `
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Exo+2:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg: #03091a;
  --bg2: #060e24;
  --bg3: #071228;
  --sidebar: linear-gradient(180deg, #070f22 0%, #060d1f 50%, #050b1a 100%);
  --card: rgba(8,18,45,0.85);
  --border: rgba(30,120,255,0.18);
  --border2: rgba(30,120,255,0.32);
  --blue: #1e78ff;
  --blue2: #38a3ff;
  --blue3: #0affef;
  --text: #e8f0ff;
  --text2: #8baad4;
  --text3: #4a6fa5;
  --success: #00e5a0;
  --warn: #ffa820;
  --danger: #ff4560;
  --font: 'Exo 2', sans-serif;
  --font2: 'Rajdhani', sans-serif;
  --glow: 0 0 24px rgba(30,120,255,0.22);
  --glow2: 0 0 40px rgba(30,120,255,0.30);
  --radius: 12px;
  --radius2: 18px;
}

body, #root { min-height: 100vh; background: var(--bg); font-family: var(--font); color: var(--text); }

/* ---- LAYOUT ---- */
.layout { display: flex; min-height: 100vh; }

/* ---- SIDEBAR ---- */
.sidebar {
  width: 240px; min-width: 240px; background: var(--sidebar);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  box-shadow: 4px 0 32px rgba(0,0,0,0.5);
  position: relative; overflow: hidden;
}
.sidebar::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(30,120,255,0.10) 0%, transparent 65%);
  pointer-events: none;
}
.sidebar-logo {
  padding: 22px 20px 16px;
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; gap: 12px;
}
.logo-icon {
  width: 40px; height: 40px; border-radius: 10px;
  background: linear-gradient(135deg, #0a2a6e, #1e78ff);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; box-shadow: 0 0 16px rgba(30,120,255,0.4);
  flex-shrink: 0;
}
.logo-text { font-family: var(--font2); font-size: 18px; font-weight: 700; color: #fff; letter-spacing: 0.05em; line-height: 1.1; }
.logo-sub { font-size: 11px; font-weight: 500; color: var(--blue2); letter-spacing: 0.12em; text-transform: uppercase; }

.sidebar-user {
  margin: 14px 12px; padding: 12px 14px;
  background: rgba(30,120,255,0.08); border: 1px solid var(--border);
  border-radius: var(--radius); display: flex; align-items: center; gap: 10px;
}
.user-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, #1e78ff, #38a3ff);
  display: flex; align-items: center; justify-content: center;
  font-size: 15px; font-weight: 700; color: #fff; flex-shrink: 0;
}
.user-name { font-size: 13px; font-weight: 600; color: var(--text); line-height: 1.2; }
.user-role { font-size: 11px; color: var(--blue2); text-transform: uppercase; letter-spacing: 0.07em; }
.user-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--success); box-shadow: 0 0 6px var(--success); margin-left: auto; }

.menu-section { padding: 10px 12px 4px; font-size: 10px; font-weight: 700; color: var(--text3); letter-spacing: 0.12em; text-transform: uppercase; }

.menu-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; margin: 2px 8px; border-radius: 10px;
  cursor: pointer; transition: all 0.18s; color: var(--text2);
  font-size: 14px; font-weight: 500; border: 1px solid transparent;
}
.menu-item:hover { background: rgba(30,120,255,0.10); color: var(--text); border-color: var(--border); }
.menu-item.active {
  background: rgba(30,120,255,0.16); color: var(--blue2);
  border-color: var(--border2); box-shadow: var(--glow);
  font-weight: 600;
}
.menu-item svg { width: 18px; height: 18px; flex-shrink: 0; stroke: currentColor; fill: none; stroke-width: 2; }

.sidebar-logout {
  margin-top: auto; padding: 14px 12px;
  border-top: 1px solid var(--border);
}

/* ---- MAIN ---- */
.main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

.topbar {
  padding: 0 28px; height: 64px; display: flex; align-items: center;
  background: rgba(3,9,26,0.92); border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px); gap: 16px;
}
.topbar-logo { display: flex; align-items: center; gap: 14px; }
.topbar-logo img { height: 46px; }
.topbar-title { font-family: var(--font2); font-size: 26px; font-weight: 700; letter-spacing: 0.06em; color: #fff; }
.topbar-title span { color: var(--blue2); }
.topbar-sub { font-size: 12px; color: var(--text3); margin-top: 2px; }

.topbar-pills { display: flex; gap: 2px; margin-left: auto; }
.topbar-pill {
  display: flex; align-items: center; gap: 6px; padding: 7px 14px;
  border-radius: 8px; font-size: 13px; font-weight: 500; color: var(--text2);
  border: 1px solid var(--border); cursor: pointer; transition: all 0.15s;
}
.topbar-pill:hover { background: rgba(30,120,255,0.10); color: var(--text); }
.topbar-pill svg { width: 15px; height: 15px; stroke: currentColor; fill: none; stroke-width: 2; }

.topbar-chat {
  display: flex; align-items: center; gap: 8px; padding: 8px 18px;
  background: rgba(30,120,255,0.15); border: 1px solid var(--border2);
  border-radius: 10px; font-size: 14px; font-weight: 600; color: var(--blue2);
  cursor: pointer; margin-left: 12px; transition: all 0.15s; position: relative;
}
.topbar-chat:hover { background: rgba(30,120,255,0.25); box-shadow: var(--glow); }
.chat-badge {
  position: absolute; top: -6px; right: -6px; background: var(--blue);
  color: #fff; font-size: 10px; font-weight: 700; width: 18px; height: 18px;
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  box-shadow: 0 0 8px var(--blue);
}

.content { flex: 1; overflow-y: auto; padding: 28px; background: var(--bg); }
.content::-webkit-scrollbar { width: 6px; }
.content::-webkit-scrollbar-track { background: var(--bg2); }
.content::-webkit-scrollbar-thumb { background: rgba(30,120,255,0.3); border-radius: 3px; }

/* ---- CARDS ---- */
.card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius2); padding: 24px; margin-bottom: 20px;
  backdrop-filter: blur(10px);
}
.card-header { display: flex; align-items: center; gap: 12px; margin-bottom: 22px; }
.card-icon {
  width: 42px; height: 42px; border-radius: 10px;
  background: rgba(30,120,255,0.15); border: 1px solid var(--border2);
  display: flex; align-items: center; justify-content: center;
}
.card-icon svg { width: 22px; height: 22px; stroke: var(--blue2); fill: none; stroke-width: 2; }
.card-title { font-family: var(--font2); font-size: 22px; font-weight: 700; color: var(--text); letter-spacing: 0.02em; }

/* ---- METRICS ---- */
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin-bottom: 22px; }
.metric {
  background: rgba(8,18,45,0.9); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 16px 20px;
  position: relative; overflow: hidden;
}
.metric::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, var(--blue), var(--blue3));
}
.metric-label { font-size: 11px; font-weight: 600; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px; }
.metric-value { font-family: var(--font2); font-size: 22px; font-weight: 700; color: var(--text); line-height: 1; }
.metric-value.success { color: var(--success); }
.metric-value.warn { color: var(--warn); }
.metric-value.danger { color: var(--danger); }

/* ---- FORM ---- */
.form-group { margin-bottom: 18px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-label {
  display: block; font-size: 13px; font-weight: 600; color: var(--text2);
  margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.06em;
}
.form-input, .form-select, .form-textarea {
  width: 100%; padding: 11px 14px;
  background: rgba(3,9,26,0.8); border: 1px solid var(--border);
  border-radius: 10px; color: var(--text); font-family: var(--font); font-size: 14px;
  transition: all 0.18s; outline: none; appearance: none;
}
.form-input:focus, .form-select:focus, .form-textarea:focus {
  border-color: var(--blue); box-shadow: 0 0 0 3px rgba(30,120,255,0.15);
}
.form-input::placeholder { color: var(--text3); }
.form-select { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%238baad4' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; padding-right: 36px; }
.form-select option { background: #060e24; color: var(--text); }
.form-textarea { resize: vertical; min-height: 90px; }
.form-error { font-size: 12px; color: var(--danger); margin-top: 4px; }

.prefix-input { display: flex; align-items: center; }
.prefix { padding: 11px 12px; background: rgba(30,120,255,0.08); border: 1px solid var(--border); border-right: none; border-radius: 10px 0 0 10px; font-size: 14px; font-weight: 600; color: var(--text2); white-space: nowrap; }
.prefix-input .form-input { border-radius: 0 10px 10px 0; }

/* ---- BUTTONS ---- */
.btn {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 10px 20px; border-radius: 10px; font-family: var(--font);
  font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.18s;
  border: 1px solid transparent; white-space: nowrap;
}
.btn-primary {
  background: linear-gradient(135deg, #1248c8, #1e78ff);
  color: #fff; border-color: rgba(30,120,255,0.4);
  box-shadow: 0 6px 20px rgba(30,120,255,0.25);
}
.btn-primary:hover { box-shadow: 0 8px 28px rgba(30,120,255,0.4); transform: translateY(-1px); }
.btn-secondary { background: rgba(30,120,255,0.10); color: var(--blue2); border-color: var(--border2); }
.btn-secondary:hover { background: rgba(30,120,255,0.20); }
.btn-danger { background: rgba(255,69,96,0.12); color: var(--danger); border-color: rgba(255,69,96,0.3); }
.btn-danger:hover { background: rgba(255,69,96,0.22); }
.btn-success { background: rgba(0,229,160,0.12); color: var(--success); border-color: rgba(0,229,160,0.3); }
.btn-success:hover { background: rgba(0,229,160,0.22); }
.btn svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 2; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

/* ---- TABLE ---- */
.table-wrap { overflow-x: auto; border-radius: var(--radius); border: 1px solid var(--border); }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th { background: rgba(30,120,255,0.08); color: var(--text3); font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 10px 14px; border-bottom: 1px solid var(--border); text-align: left; white-space: nowrap; }
td { padding: 11px 14px; border-bottom: 1px solid rgba(30,120,255,0.06); color: var(--text2); vertical-align: middle; }
tr:last-child td { border-bottom: none; }
tr:hover td { background: rgba(30,120,255,0.04); }
.td-primary { color: var(--text); font-weight: 500; }

/* ---- BADGES ---- */
.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; }
.badge-pago { background: rgba(0,229,160,0.12); color: var(--success); border: 1px solid rgba(0,229,160,0.25); }
.badge-pendente { background: rgba(255,168,32,0.12); color: var(--warn); border: 1px solid rgba(255,168,32,0.25); }
.badge-cancelado { background: rgba(255,69,96,0.12); color: var(--danger); border: 1px solid rgba(255,69,96,0.25); }
.badge-aguardando { background: rgba(30,120,255,0.12); color: var(--blue2); border: 1px solid rgba(30,120,255,0.25); }
.badge-admin { background: rgba(56,163,255,0.12); color: var(--blue2); border: 1px solid rgba(30,120,255,0.25); }
.badge-vendedor { background: rgba(0,229,160,0.10); color: var(--success); border: 1px solid rgba(0,229,160,0.25); }

/* ---- LOGIN ---- */
.login-wrap {
  min-height: 100vh; display: flex; align-items: center; justify-content: center;
  background: radial-gradient(ellipse at 50% 0%, rgba(30,120,255,0.15) 0%, transparent 55%),
    radial-gradient(ellipse at 80% 100%, rgba(10,255,239,0.07) 0%, transparent 50%),
    var(--bg);
}
.login-card {
  background: rgba(6,14,36,0.95); border: 1px solid var(--border2);
  border-radius: 24px; padding: 40px; width: 400px; max-width: 95vw;
  box-shadow: 0 24px 80px rgba(0,0,0,0.5), var(--glow2);
}
.login-logo { text-align: center; margin-bottom: 32px; }
.login-logo-icon {
  width: 72px; height: 72px; border-radius: 20px; margin: 0 auto 14px;
  background: linear-gradient(135deg, #071848, #1e78ff);
  display: flex; align-items: center; justify-content: center; font-size: 36px;
  box-shadow: 0 0 32px rgba(30,120,255,0.5);
}
.login-brand { font-family: var(--font2); font-size: 32px; font-weight: 700; color: #fff; letter-spacing: 0.06em; }
.login-brand span { color: var(--blue2); }
.login-tagline { font-size: 13px; color: var(--text3); margin-top: 4px; }

/* ---- ALERTS ---- */
.alert { padding: 12px 16px; border-radius: 10px; font-size: 13px; font-weight: 500; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
.alert-success { background: rgba(0,229,160,0.10); border: 1px solid rgba(0,229,160,0.3); color: var(--success); }
.alert-error { background: rgba(255,69,96,0.10); border: 1px solid rgba(255,69,96,0.3); color: var(--danger); }
.alert-info { background: rgba(30,120,255,0.10); border: 1px solid var(--border2); color: var(--blue2); }
.alert svg { width: 16px; height: 16px; stroke: currentColor; fill: none; stroke-width: 2; flex-shrink: 0; }

/* ---- DIVIDER ---- */
.divider { border: none; border-top: 1px solid var(--border); margin: 22px 0; }

/* ---- CHAT ---- */
.chat-panel { display: flex; flex-direction: column; height: calc(100vh - 64px); }
.chat-list { width: 240px; border-right: 1px solid var(--border); overflow-y: auto; padding: 12px; }
.chat-user-item { padding: 10px 12px; border-radius: 10px; cursor: pointer; transition: all 0.15s; display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.chat-user-item:hover { background: rgba(30,120,255,0.10); }
.chat-user-item.active { background: rgba(30,120,255,0.15); border: 1px solid var(--border2); }
.chat-main { flex: 1; display: flex; flex-direction: column; }
.chat-messages { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 10px; }
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-thumb { background: rgba(30,120,255,0.3); border-radius: 2px; }
.chat-msg { max-width: 68%; padding: 10px 14px; border-radius: 14px; font-size: 14px; line-height: 1.5; }
.chat-msg.mine { background: rgba(30,120,255,0.18); border: 1px solid var(--border2); color: var(--text); align-self: flex-end; border-bottom-right-radius: 4px; }
.chat-msg.theirs { background: rgba(8,18,45,0.9); border: 1px solid var(--border); color: var(--text2); align-self: flex-start; border-bottom-left-radius: 4px; }
.chat-msg-name { font-size: 11px; font-weight: 700; color: var(--blue2); margin-bottom: 3px; }
.chat-input-row { padding: 14px 20px; border-top: 1px solid var(--border); display: flex; gap: 10px; }

/* ---- LOADING ---- */
.spinner { width: 36px; height: 36px; border: 3px solid rgba(30,120,255,0.2); border-top-color: var(--blue); border-radius: 50%; animation: spin 0.8s linear infinite; margin: 40px auto; display: block; }
@keyframes spin { to { transform: rotate(360deg); } }

.page-loading { display: flex; align-items: center; justify-content: center; height: 200px; }

.empty-state { text-align: center; padding: 48px 20px; color: var(--text3); }
.empty-state svg { width: 48px; height: 48px; stroke: var(--text3); fill: none; stroke-width: 1.5; margin: 0 auto 16px; display: block; }

/* ---- CHECKBOX ---- */
.form-check { display: flex; align-items: center; gap: 8px; cursor: pointer; }
.form-check input { width: 16px; height: 16px; accent-color: var(--blue); cursor: pointer; }
.form-check span { font-size: 14px; color: var(--text2); }

/* ---- FILTER ROW ---- */
.filter-row { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; margin-bottom: 16px; }
.filter-row .form-group { margin-bottom: 0; flex: 1; min-width: 130px; }

/* ---- SECTION TITLE ---- */
.section-title { font-family: var(--font2); font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.section-title::before { content: ''; display: block; width: 3px; height: 18px; background: var(--blue); border-radius: 2px; }

/* ---- PAGINA PAINEL ---- */
.painel-date { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }

/* ---- MODAL ---- */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; z-index: 100; padding: 20px;
}
.modal-box {
  background: #060e24; border: 1px solid var(--border2); border-radius: 20px;
  padding: 28px; width: 100%; max-width: 560px; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 24px 80px rgba(0,0,0,0.6), var(--glow2);
}
.modal-box::-webkit-scrollbar { width: 5px; }
.modal-box::-webkit-scrollbar-thumb { background: rgba(30,120,255,0.3); border-radius: 3px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 22px; }
.modal-close { background: rgba(255,69,96,0.10); border: 1px solid rgba(255,69,96,0.25); border-radius: 8px; color: var(--danger); padding: 6px 10px; cursor: pointer; font-size: 18px; line-height: 1; transition: all 0.15s; }
.modal-close:hover { background: rgba(255,69,96,0.22); }
`;

// ===================== ICONS =====================
const Icons = {
  sale: <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>,
  panel: <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  users: <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  commission: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M9 9h4.5a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3H15"/></svg>,
  logout: <svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  chat: <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  bolt: <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  refresh: <svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>,
  person: <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  send: <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  check: <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
  x: <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  edit: <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  trash: <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
  plus: <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  key: <svg viewBox="0 0 24 24"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>,
  warn: <svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>,
  info: <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  bank: <svg viewBox="0 0 24 24"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>,
};

// ===================== ALERT COMPONENT =====================
function Alert({ type = "info", children }) {
  const map = { success: "alert-success", error: "alert-error", info: "alert-info" };
  const icon = type === "success" ? Icons.check : type === "error" ? Icons.x : Icons.info;
  return <div className={`alert ${map[type]}`}>{icon}{children}</div>;
}

// ===================== LOGIN =====================
function Login({ onLogin }) {
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [loading, setLoading] = useState(false);
  const [erro, setErro] = useState("");

  async function handleLogin() {
    if (!usuario || !senha) { setErro("Preencha usuário e senha."); return; }
    setLoading(true); setErro("");
    try {
      const usuarioLimpo = usuario.trim().toLowerCase();
      const data = await sb(
        `usuarios?select=*&usuario=eq.${encodeURIComponent(usuarioLimpo)}&ativo=eq.true`
      );
      if (!data.length) {
        setErro("Usuário não encontrado ou inativo."); setLoading(false); return;
      }
      const u = data[0];
      // testa com trim e sem trim, igual ao Python (str(senha).encode())
      const hash1 = await hashSenha(senha.trim());
      const hash2 = await hashSenha(senha);
      if (u.senha_hash !== hash1 && u.senha_hash !== hash2) {
        setErro("Senha incorreta."); setLoading(false); return;
      }
      onLogin(u);
    } catch (e) {
      setErro("Erro ao conectar: " + e.message); setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-logo">
          <div className="login-logo-icon">🌀</div>
          <div className="login-brand">OPERAX <span>SALES</span></div>
          <div className="login-tagline">Sistema inteligente de vendas e operações financeiras</div>
        </div>
        {erro && <Alert type="error">{erro}</Alert>}
        <div className="form-group">
          <label className="form-label">Usuário</label>
          <input className="form-input" placeholder="Seu login" value={usuario}
            onChange={e => setUsuario(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleLogin()} />
        </div>
        <div className="form-group">
          <label className="form-label">Senha</label>
          <input className="form-input" type="password" placeholder="Sua senha" value={senha}
            onChange={e => setSenha(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleLogin()} />
        </div>
        <button className="btn btn-primary" style={{ width: "100%", justifyContent: "center", marginTop: 8 }}
          onClick={handleLogin} disabled={loading}>
          {loading ? "Entrando..." : "Entrar"}
        </button>
      </div>
    </div>
  );
}

// ===================== NOVA VENDA =====================
function NovaVenda({ user }) {
  const [tabelas, setTabelas] = useState([]);
  const [cliente, setCliente] = useState("");
  const [cpf, setCpf] = useState("");
  const [telefone, setTelefone] = useState("");
  const [tabela, setTabela] = useState("");
  const [valorStr, setValorStr] = useState("");
  const [obs, setObs] = useState("");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState(null);
  const [erros, setErros] = useState({});

  useEffect(() => {
    sb("regras_comissao?select=produto&ativo=eq.true").then(d => {
      const unique = [...new Set(d.map(r => r.produto).filter(Boolean))].sort();
      setTabelas(unique.length ? unique : ["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]);
      if (unique.length) setTabela(unique[0]);
    }).catch(() => {
      setTabelas(["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]);
    });
  }, []);

  function validar() {
    const e = {};
    if (!cliente.trim()) e.cliente = "Informe o nome do cliente.";
    const doc = limparDoc(cpf);
    if (doc.length === 11 && !validarCPF(cpf)) e.cpf = "CPF inválido.";
    if (doc.length === 14 && !validarCNPJ(cpf)) e.cpf = "CNPJ inválido.";
    if (cpf && doc.length !== 11 && doc.length !== 14) e.cpf = "CPF/CNPJ com dígitos incorretos.";
    if (telefone && !validarTelefone(telefone)) e.telefone = "Telefone inválido.";
    if (!tabela) e.tabela = "Selecione uma tabela.";
    const val = parseFloat(String(valorStr).replace(/\./g, "").replace(",", ".").replace("R$", "").trim());
    if (!val || isNaN(val) || val <= 0) e.valor = "Informe um valor válido.";
    return e;
  }

  async function getPercentual(tab, valor) {
    try {
      const regras = await sb(
        `regras_comissao?produto=eq.${encodeURIComponent(tab)}&ativo=eq.true&order=valor_minimo.desc`
      );
      for (const r of regras) {
        if (parseFloat(valor) >= parseFloat(r.valor_minimo || 0)) {
          return parseFloat(r.percentual_empresa || 0);
        }
      }
    } catch {}
    return 0;
  }

  async function salvar() {
    const e = validar();
    setErros(e);
    if (Object.keys(e).length) return;
    setLoading(true); setMsg(null);
    try {
      const valor = parseFloat(String(valorStr).replace(/\./g, "").replace(",", ".").replace("R$", "").trim());
      const perc = await getPercentual(tabela, valor);
      const valor_empresa = valor * (perc / 100);
      await sb("vendas", {
        method: "POST",
        prefer: "return=minimal",
        body: JSON.stringify({
          cliente: cliente.trim(),
          cpf: limparDoc(cpf),
          telefone: limparDoc(telefone),
          produto: tabela,
          tabela_banco: tabela,
          valor,
          status: "Pendente",
          observacao: obs.trim(),
          vendedor_id: user.id,
          vendedor_nome: user.nome,
          data: new Date().toISOString(),
          comissao_empresa: perc,
          valor_comissao_empresa: valor_empresa,
          conferido: false,
          alterado_vendedor: false,
        }),
      });
      setMsg({ type: "success", text: "Venda cadastrada com sucesso!" });
      setCliente(""); setCpf(""); setTelefone(""); setValorStr(""); setObs("");
    } catch (err) {
      setMsg({ type: "error", text: "Erro ao salvar venda." });
    }
    setLoading(false);
  }

  return (
    <div>
      {msg && <Alert type={msg.type}>{msg.text}</Alert>}
      <div className="card">
        <div className="card-header">
          <div className="card-icon">{Icons.sale}</div>
          <div className="card-title">Cadastro de Venda</div>
        </div>

        <div className="form-group">
          <label className="form-label">Cliente</label>
          <input className="form-input" placeholder="Digite o nome do cliente..." value={cliente} onChange={e => setCliente(e.target.value)} />
          {erros.cliente && <div className="form-error">{erros.cliente}</div>}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">CPF / CNPJ</label>
            <input className="form-input" placeholder="Ex: 999.999.999-99" value={cpf} onChange={e => setCpf(e.target.value)} />
            {erros.cpf && <div className="form-error">{erros.cpf}</div>}
          </div>
          <div className="form-group">
            <label className="form-label">Telefone</label>
            <input className="form-input" placeholder="Ex: (11) 99976-7867" value={telefone} onChange={e => setTelefone(e.target.value)} />
            {erros.telefone && <div className="form-error">{erros.telefone}</div>}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Tabela / Banco</label>
          <select className="form-select" value={tabela} onChange={e => setTabela(e.target.value)}>
            {tabelas.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
          {erros.tabela && <div className="form-error">{erros.tabela}</div>}
        </div>

        <div className="form-group">
          <label className="form-label">Valor Vendido</label>
          <div className="prefix-input">
            <span className="prefix">R$</span>
            <input className="form-input" placeholder="0,00" value={valorStr} onChange={e => setValorStr(e.target.value)} />
          </div>
          {erros.valor && <div className="form-error">{erros.valor}</div>}
        </div>

        <div className="form-group">
          <label className="form-label">Observação</label>
          <textarea className="form-textarea" placeholder="Observações adicionais..." value={obs} onChange={e => setObs(e.target.value)} />
        </div>

        <button className="btn btn-primary" onClick={salvar} disabled={loading}>
          {Icons.plus}{loading ? "Salvando..." : "Registrar Venda"}
        </button>
      </div>
    </div>
  );
}

// ===================== PAINEL =====================
function Painel({ user }) {
  const [vendas, setVendas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mesSel, setMesSel] = useState(new Date().getMonth() + 1);
  const [anoSel, setAnoSel] = useState(new Date().getFullYear());
  const [editId, setEditId] = useState(null);
  const [editData, setEditData] = useState({});
  const [tabelas, setTabelas] = useState([]);
  const [msg, setMsg] = useState(null);

  async function carregar() {
    setLoading(true);
    try {
      let url = "vendas?select=*&order=id.desc";
      if (user.tipo !== "admin") url += `&vendedor_id=eq.${user.id}`;
      const data = await sb(url);
      setVendas(data);
    } catch {}
    setLoading(false);
  }

  useEffect(() => { carregar(); }, []);

  useEffect(() => {
    sb("regras_comissao?select=produto&ativo=eq.true").then(d => {
      const u = [...new Set(d.map(r => r.produto).filter(Boolean))].sort();
      setTabelas(u.length ? u : ["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]);
    }).catch(() => setTabelas(["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]));
  }, []);

  const meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

  const vendasFiltradas = vendas.filter(v => {
    const d = new Date(v.data);
    return d.getMonth() + 1 === mesSel && d.getFullYear() === anoSel;
  });

  const totalVendas = vendasFiltradas.reduce((s, v) => s + parseFloat(v.valor || 0), 0);
  const totalPago = vendasFiltradas.filter(v => v.status === "Pago").reduce((s, v) => s + parseFloat(v.valor || 0), 0);
  const totalPendente = vendasFiltradas.filter(v => v.status === "Pendente").reduce((s, v) => s + parseFloat(v.valor || 0), 0);
  const comissaoEmpresa = vendasFiltradas.reduce((s, v) => s + parseFloat(v.valor_comissao_empresa || 0), 0);

  function statusBadge(s) {
    const m = { "Pago": "badge-pago", "Pendente": "badge-pendente", "Cancelado": "badge-cancelado", "Aguardando": "badge-aguardando" };
    return <span className={`badge ${m[s] || "badge-aguardando"}`}>{s}</span>;
  }

  function abrirEdit(v) {
    setEditId(v.id);
    setEditData({ ...v, tabela_banco: v.tabela_banco || v.produto || "" });
  }

  async function salvarEdit() {
    try {
      const valor = parseFloat(String(editData.valor || 0).replace(/\./g, "").replace(",", ".").replace("R$", "").trim());
      let update = {
        cliente: editData.cliente, cpf: limparDoc(editData.cpf),
        telefone: limparDoc(editData.telefone), produto: editData.tabela_banco,
        tabela_banco: editData.tabela_banco, valor,
        status: editData.status, observacao: editData.observacao,
      };
      if (user.tipo === "admin") {
        update.conferido = editData.conferido;
        update.alterado_vendedor = false;
        update.observacao_admin = editData.observacao_admin;
      } else {
        update.alterado_vendedor = true;
        update.data_alteracao_vendedor = new Date().toISOString();
        update.conferido = false;
      }
      await sb(`vendas?id=eq.${editId}`, { method: "PATCH", prefer: "return=minimal", body: JSON.stringify(update) });
      setMsg({ type: "success", text: "Proposta atualizada!" });
      setEditId(null);
      carregar();
    } catch {
      setMsg({ type: "error", text: "Erro ao atualizar." });
    }
  }

  return (
    <div>
      {msg && <Alert type={msg.type}>{msg.text}</Alert>}

      <div className="metrics">
        <div className="metric">
          <div className="metric-label">Total Vendas</div>
          <div className="metric-value">{dinheiro(totalVendas)}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Pago</div>
          <div className="metric-value success">{dinheiro(totalPago)}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Pendente</div>
          <div className="metric-value warn">{dinheiro(totalPendente)}</div>
        </div>
        {user.tipo === "admin" && (
          <div className="metric">
            <div className="metric-label">Comissão Empresa</div>
            <div className="metric-value" style={{ color: "var(--blue2)" }}>{dinheiro(comissaoEmpresa)}</div>
          </div>
        )}
        <div className="metric">
          <div className="metric-label">Qtd Vendas</div>
          <div className="metric-value">{vendasFiltradas.length}</div>
        </div>
      </div>

      <div className="painel-date">
        <select className="form-select" style={{ width: 140 }} value={mesSel} onChange={e => setMesSel(parseInt(e.target.value))}>
          {meses.map((m, i) => <option key={i} value={i + 1}>{m}</option>)}
        </select>
        <select className="form-select" style={{ width: 100 }} value={anoSel} onChange={e => setAnoSel(parseInt(e.target.value))}>
          {[2024, 2025, 2026].map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <button className="btn btn-secondary" onClick={carregar}>{Icons.refresh} Atualizar</button>
      </div>

      {loading ? <div className="page-loading"><div className="spinner" /></div> : (
        <div className="card">
          {vendasFiltradas.length === 0 ? (
            <div className="empty-state">{Icons.sale}<p>Nenhuma venda encontrada neste período.</p></div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th><th>Cliente</th><th>CPF/CNPJ</th><th>Tabela/Banco</th>
                    <th>Valor</th><th>Status</th><th>Data</th>
                    {user.tipo === "admin" && <th>Vendedor</th>}
                    {user.tipo === "admin" && <th>Conf.</th>}
                    <th>Ações</th>
                  </tr>
                </thead>
                <tbody>
                  {vendasFiltradas.map(v => {
                    const isPendOld = v.status === "Pendente" && new Date() - new Date(v.data) > 3600000;
                    return (
                      <tr key={v.id} style={isPendOld && user.tipo === "admin" ? { background: "rgba(255,69,96,0.06)" } : v.status === "Pendente" ? { background: "rgba(255,168,32,0.04)" } : {}}>
                        <td className="td-primary">#{v.id}</td>
                        <td className="td-primary">{v.cliente}</td>
                        <td>{v.cpf || "—"}</td>
                        <td>{v.tabela_banco || v.produto || "—"}</td>
                        <td className="td-primary">{dinheiro(v.valor)}</td>
                        <td>{statusBadge(v.status)}</td>
                        <td>{v.data ? new Date(v.data).toLocaleDateString("pt-BR") : "—"}</td>
                        {user.tipo === "admin" && <td>{v.vendedor_nome || "—"}</td>}
                        {user.tipo === "admin" && <td>{v.conferido ? <span className="badge badge-pago">✓</span> : <span className="badge badge-pendente">—</span>}</td>}
                        <td>
                          <button className="btn btn-secondary" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => abrirEdit(v)}>
                            {Icons.edit}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {editId && (
        <div className="modal-overlay" onClick={() => setEditId(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title">Editar Proposta #{editId}</div>
              <button className="modal-close" onClick={() => setEditId(null)}>×</button>
            </div>

            <div className="form-group">
              <label className="form-label">Cliente</label>
              <input className="form-input" value={editData.cliente || ""} onChange={e => setEditData(p => ({ ...p, cliente: e.target.value }))} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">CPF / CNPJ</label>
                <input className="form-input" value={editData.cpf || ""} onChange={e => setEditData(p => ({ ...p, cpf: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Telefone</label>
                <input className="form-input" value={editData.telefone || ""} onChange={e => setEditData(p => ({ ...p, telefone: e.target.value }))} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Tabela / Banco</label>
              <select className="form-select" value={editData.tabela_banco || ""} onChange={e => setEditData(p => ({ ...p, tabela_banco: e.target.value }))}>
                {tabelas.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Valor</label>
                <input className="form-input" value={editData.valor || ""} onChange={e => setEditData(p => ({ ...p, valor: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Status</label>
                <select className="form-select" value={editData.status || "Pendente"} onChange={e => setEditData(p => ({ ...p, status: e.target.value }))}>
                  {["Pendente", "Aguardando", "Pago", "Cancelado"].map(s => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Observação</label>
              <textarea className="form-textarea" value={editData.observacao || ""} onChange={e => setEditData(p => ({ ...p, observacao: e.target.value }))} />
            </div>
            {user.tipo === "admin" && (
              <>
                <div className="form-group">
                  <label className="form-label">Obs. Admin</label>
                  <textarea className="form-textarea" value={editData.observacao_admin || ""} onChange={e => setEditData(p => ({ ...p, observacao_admin: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-check">
                    <input type="checkbox" checked={!!editData.conferido} onChange={e => setEditData(p => ({ ...p, conferido: e.target.checked }))} />
                    <span>Conferido</span>
                  </label>
                </div>
              </>
            )}
            <div style={{ display: "flex", gap: 10, marginTop: 8 }}>
              <button className="btn btn-primary" onClick={salvarEdit}>{Icons.check} Salvar</button>
              <button className="btn btn-secondary" onClick={() => setEditId(null)}>{Icons.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ===================== USUÁRIOS =====================
function Usuarios() {
  const [lista, setLista] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ nome: "", usuario: "", senha: "", tipo: "vendedor" });
  const [msg, setMsg] = useState(null);
  const [editId, setEditId] = useState(null);
  const [editData, setEditData] = useState({});
  const [novaSenha, setNovaSenha] = useState("");

  async function carregar() {
    setLoading(true);
    try { const d = await sb("usuarios?select=*&order=id"); setLista(d); }
    catch {}
    setLoading(false);
  }

  useEffect(() => { carregar(); }, []);

  async function criar() {
    if (!form.nome || !form.usuario || !form.senha) { setMsg({ type: "error", text: "Preencha nome, usuário e senha." }); return; }
    try {
      const hash = await hashSenha(form.senha);
      await sb("usuarios", { method: "POST", prefer: "return=minimal", body: JSON.stringify({ nome: form.nome.trim(), usuario: form.usuario.trim().toLowerCase(), senha_hash: hash, tipo: form.tipo, ativo: true }) });
      setMsg({ type: "success", text: "Usuário criado!" });
      setForm({ nome: "", usuario: "", senha: "", tipo: "vendedor" });
      carregar();
    } catch { setMsg({ type: "error", text: "Erro ao criar usuário." }); }
  }

  async function salvarEdit() {
    try {
      await sb(`usuarios?id=eq.${editId}`, { method: "PATCH", prefer: "return=minimal", body: JSON.stringify({ nome: editData.nome?.trim(), usuario: editData.usuario?.trim().toLowerCase(), tipo: editData.tipo }) });
      if (novaSenha) {
        const hash = await hashSenha(novaSenha);
        await sb(`usuarios?id=eq.${editId}`, { method: "PATCH", prefer: "return=minimal", body: JSON.stringify({ senha_hash: hash }) });
      }
      setMsg({ type: "success", text: "Usuário atualizado!" });
      setEditId(null); setNovaSenha(""); carregar();
    } catch { setMsg({ type: "error", text: "Erro ao atualizar." }); }
  }

  async function toggleAtivo(u) {
    if (u.usuario === "admin") { setMsg({ type: "error", text: "Não é permitido desativar o admin principal." }); return; }
    await sb(`usuarios?id=eq.${u.id}`, { method: "PATCH", prefer: "return=minimal", body: JSON.stringify({ ativo: !u.ativo }) });
    carregar();
  }

  async function excluir(u) {
    if (u.usuario === "admin") { setMsg({ type: "error", text: "Não é permitido excluir o admin principal." }); return; }
    if (!confirm(`Excluir usuário ${u.nome}?`)) return;
    await sb(`usuarios?id=eq.${u.id}`, { method: "DELETE", prefer: "return=minimal" });
    carregar();
  }

  return (
    <div>
      {msg && <Alert type={msg.type}>{msg.text}</Alert>}
      <div className="card">
        <div className="card-header"><div className="card-icon">{Icons.plus}</div><div className="card-title">Criar Usuário</div></div>
        <div className="form-row">
          <div className="form-group"><label className="form-label">Nome</label><input className="form-input" value={form.nome} onChange={e => setForm(p => ({ ...p, nome: e.target.value }))} /></div>
          <div className="form-group"><label className="form-label">Login</label><input className="form-input" value={form.usuario} onChange={e => setForm(p => ({ ...p, usuario: e.target.value }))} /></div>
        </div>
        <div className="form-row">
          <div className="form-group"><label className="form-label">Senha</label><input className="form-input" type="password" value={form.senha} onChange={e => setForm(p => ({ ...p, senha: e.target.value }))} /></div>
          <div className="form-group"><label className="form-label">Tipo</label>
            <select className="form-select" value={form.tipo} onChange={e => setForm(p => ({ ...p, tipo: e.target.value }))}>
              <option value="vendedor">Vendedor</option><option value="admin">Admin</option>
            </select>
          </div>
        </div>
        <button className="btn btn-primary" onClick={criar}>{Icons.plus} Criar Usuário</button>
      </div>

      {loading ? <div className="page-loading"><div className="spinner" /></div> : (
        <div className="card">
          <div className="card-header"><div className="card-icon">{Icons.users}</div><div className="card-title">Usuários Cadastrados</div></div>
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Nome</th><th>Login</th><th>Tipo</th><th>Ativo</th><th>Ações</th></tr></thead>
              <tbody>
                {lista.map(u => (
                  <tr key={u.id}>
                    <td>#{u.id}</td>
                    <td className="td-primary">{u.nome}</td>
                    <td>{u.usuario}</td>
                    <td><span className={`badge ${u.tipo === "admin" ? "badge-admin" : "badge-vendedor"}`}>{u.tipo}</span></td>
                    <td>{u.ativo ? <span className="badge badge-pago">Ativo</span> : <span className="badge badge-cancelado">Inativo</span>}</td>
                    <td style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-secondary" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => { setEditId(u.id); setEditData({ ...u }); setNovaSenha(""); }}>{Icons.edit}</button>
                      <button className="btn btn-secondary" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => toggleAtivo(u)}>{u.ativo ? Icons.x : Icons.check}</button>
                      <button className="btn btn-danger" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => excluir(u)}>{Icons.trash}</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {editId && (
        <div className="modal-overlay" onClick={() => setEditId(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title">Editar Usuário</div>
              <button className="modal-close" onClick={() => setEditId(null)}>×</button>
            </div>
            <div className="form-group"><label className="form-label">Nome</label><input className="form-input" value={editData.nome || ""} onChange={e => setEditData(p => ({ ...p, nome: e.target.value }))} /></div>
            <div className="form-group"><label className="form-label">Login</label><input className="form-input" value={editData.usuario || ""} onChange={e => setEditData(p => ({ ...p, usuario: e.target.value }))} /></div>
            <div className="form-group"><label className="form-label">Tipo</label>
              <select className="form-select" value={editData.tipo || "vendedor"} onChange={e => setEditData(p => ({ ...p, tipo: e.target.value }))}>
                <option value="vendedor">Vendedor</option><option value="admin">Admin</option>
              </select>
            </div>
            <div className="form-group"><label className="form-label">Nova Senha (opcional)</label><input className="form-input" type="password" value={novaSenha} onChange={e => setNovaSenha(e.target.value)} placeholder="Deixe em branco para não alterar" /></div>
            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn-primary" onClick={salvarEdit}>{Icons.check} Salvar</button>
              <button className="btn btn-secondary" onClick={() => setEditId(null)}>{Icons.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ===================== COMISSÕES =====================
function Comissoes() {
  const [regras, setRegras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({ produto: "", valor_minimo: "", percentual_empresa: "" });
  const [msg, setMsg] = useState(null);
  const [editId, setEditId] = useState(null);
  const [editData, setEditData] = useState({});

  async function carregar() {
    setLoading(true);
    try { const d = await sb("regras_comissao?select=*&order=produto.asc,valor_minimo.asc"); setRegras(d); }
    catch {}
    setLoading(false);
  }

  useEffect(() => { carregar(); }, []);

  async function criar() {
    if (!form.produto) { setMsg({ type: "error", text: "Informe a tabela/banco." }); return; }
    try {
      await sb("regras_comissao", { method: "POST", prefer: "return=minimal", body: JSON.stringify({ produto: form.produto.trim().toUpperCase(), valor_minimo: parseFloat(form.valor_minimo) || 0, percentual_empresa: parseFloat(form.percentual_empresa) || 0, percentual_vendedor: 0, ativo: true }) });
      setMsg({ type: "success", text: "Regra criada!" });
      setForm({ produto: "", valor_minimo: "", percentual_empresa: "" });
      carregar();
    } catch { setMsg({ type: "error", text: "Erro ao criar regra." }); }
  }

  async function salvarEdit() {
    try {
      await sb(`regras_comissao?id=eq.${editId}`, { method: "PATCH", prefer: "return=minimal", body: JSON.stringify({ produto: editData.produto?.trim().toUpperCase(), valor_minimo: parseFloat(editData.valor_minimo) || 0, percentual_empresa: parseFloat(editData.percentual_empresa) || 0, ativo: editData.ativo }) });
      setMsg({ type: "success", text: "Regra atualizada!" });
      setEditId(null); carregar();
    } catch { setMsg({ type: "error", text: "Erro ao atualizar." }); }
  }

  async function excluir(id) {
    if (!confirm("Excluir esta regra?")) return;
    await sb(`regras_comissao?id=eq.${id}`, { method: "DELETE", prefer: "return=minimal" });
    carregar();
  }

  return (
    <div>
      {msg && <Alert type={msg.type}>{msg.text}</Alert>}
      <div className="card">
        <div className="card-header"><div className="card-icon">{Icons.commission}</div><div className="card-title">Nova Regra de Comissão</div></div>
        <div className="form-row">
          <div className="form-group"><label className="form-label">Tabela / Banco</label><input className="form-input" value={form.produto} onChange={e => setForm(p => ({ ...p, produto: e.target.value }))} /></div>
          <div className="form-group"><label className="form-label">Valor Mínimo (R$)</label><input className="form-input" type="number" value={form.valor_minimo} onChange={e => setForm(p => ({ ...p, valor_minimo: e.target.value }))} /></div>
        </div>
        <div className="form-group" style={{ maxWidth: 240 }}>
          <label className="form-label">% Empresa</label>
          <input className="form-input" type="number" step="0.01" value={form.percentual_empresa} onChange={e => setForm(p => ({ ...p, percentual_empresa: e.target.value }))} />
        </div>
        <button className="btn btn-primary" onClick={criar}>{Icons.plus} Criar Regra</button>
      </div>

      {loading ? <div className="page-loading"><div className="spinner" /></div> : (
        <div className="card">
          <div className="card-header"><div className="card-icon">{Icons.bank}</div><div className="card-title">Regras Cadastradas</div></div>
          {regras.length === 0 ? <div className="empty-state">{Icons.commission}<p>Nenhuma regra cadastrada.</p></div> : (
            <div className="table-wrap">
              <table>
                <thead><tr><th>ID</th><th>Tabela/Banco</th><th>Valor Mínimo</th><th>% Empresa</th><th>Ativo</th><th>Ações</th></tr></thead>
                <tbody>
                  {regras.map(r => (
                    <tr key={r.id}>
                      <td>#{r.id}</td>
                      <td className="td-primary">{r.produto}</td>
                      <td>{dinheiro(r.valor_minimo)}</td>
                      <td>{r.percentual_empresa}%</td>
                      <td>{r.ativo ? <span className="badge badge-pago">Ativo</span> : <span className="badge badge-cancelado">Inativo</span>}</td>
                      <td style={{ display: "flex", gap: 6 }}>
                        <button className="btn btn-secondary" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => { setEditId(r.id); setEditData({ ...r }); }}>{Icons.edit}</button>
                        <button className="btn btn-danger" style={{ padding: "5px 10px", fontSize: 12 }} onClick={() => excluir(r.id)}>{Icons.trash}</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {editId && (
        <div className="modal-overlay" onClick={() => setEditId(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <div className="card-title">Editar Regra #{editId}</div>
              <button className="modal-close" onClick={() => setEditId(null)}>×</button>
            </div>
            <div className="form-group"><label className="form-label">Tabela/Banco</label><input className="form-input" value={editData.produto || ""} onChange={e => setEditData(p => ({ ...p, produto: e.target.value }))} /></div>
            <div className="form-row">
              <div className="form-group"><label className="form-label">Valor Mínimo</label><input className="form-input" type="number" value={editData.valor_minimo || ""} onChange={e => setEditData(p => ({ ...p, valor_minimo: e.target.value }))} /></div>
              <div className="form-group"><label className="form-label">% Empresa</label><input className="form-input" type="number" step="0.01" value={editData.percentual_empresa || ""} onChange={e => setEditData(p => ({ ...p, percentual_empresa: e.target.value }))} /></div>
            </div>
            <div className="form-group">
              <label className="form-check"><input type="checkbox" checked={!!editData.ativo} onChange={e => setEditData(p => ({ ...p, ativo: e.target.checked }))} /><span>Ativo</span></label>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <button className="btn btn-primary" onClick={salvarEdit}>{Icons.check} Salvar</button>
              <button className="btn btn-secondary" onClick={() => setEditId(null)}>{Icons.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ===================== CHAT =====================
function Chat({ user }) {
  const [usuarios, setUsuarios] = useState([]);
  const [destId, setDestId] = useState(null);
  const [mensagens, setMensagens] = useState([]);
  const [texto, setTexto] = useState("");
  const [naoLidas, setNaoLidas] = useState(0);
  const msgsRef = useRef(null);
  const leitura = useRef(new Date().toISOString());

  useEffect(() => {
    sb(`usuarios?select=id,nome,usuario,tipo,ativo&ativo=eq.true&order=nome`).then(d => {
      setUsuarios(d.filter(u => u.id !== user.id));
    }).catch(() => {});
  }, []);

  useEffect(() => {
    if (!destId) return;
    carregarMsgs();
    const iv = setInterval(carregarMsgs, 5000);
    return () => clearInterval(iv);
  }, [destId]);

  async function carregarMsgs() {
    try {
      const res = await sb(`chat_interno?select=*&order=criado_em.desc&limit=300`);
      const meu = user.id; const outro = destId;
      const filtradas = res.filter(m => {
        const o = parseInt(m.usuario_id); const d2 = parseInt(m.destinatario_id);
        return (o === meu && d2 === outro) || (o === outro && d2 === meu);
      }).slice(-80).reverse();
      setMensagens(filtradas);
      setTimeout(() => { if (msgsRef.current) msgsRef.current.scrollTop = msgsRef.current.scrollHeight; }, 50);
    } catch {}
  }

  useEffect(() => {
    const iv = setInterval(async () => {
      try {
        const res = await sb(`chat_interno?select=*&destinatario_id=eq.${user.id}`);
        const ult = leitura.current;
        const total = res.filter(m => new Date(m.criado_em) > new Date(ult)).length;
        setNaoLidas(total);
      } catch {}
    }, 8000);
    return () => clearInterval(iv);
  }, []);

  async function enviar() {
    if (!texto.trim() || !destId) return;
    const dest = usuarios.find(u => u.id === destId);
    try {
      await sb("chat_interno", { method: "POST", prefer: "return=minimal", body: JSON.stringify({ usuario_id: user.id, destinatario_id: destId, nome: user.nome, tipo: user.tipo, mensagem: texto.trim(), criado_em: new Date().toISOString() }) });
      setTexto(""); leitura.current = new Date().toISOString();
      carregarMsgs();
    } catch {}
  }

  return (
    <div style={{ display: "flex", height: "calc(100vh - 64px)", gap: 0 }}>
      <div className="chat-list" style={{ background: "var(--bg2)", borderRight: "1px solid var(--border)" }}>
        <div className="section-title" style={{ margin: "12px 0 10px" }}>Conversas</div>
        {usuarios.length === 0 && <div style={{ color: "var(--text3)", fontSize: 13, padding: 8 }}>Nenhum usuário disponível.</div>}
        {usuarios.map(u => (
          <div key={u.id} className={`chat-user-item ${destId === u.id ? "active" : ""}`} onClick={() => setDestId(u.id)}>
            <div className="user-avatar" style={{ width: 32, height: 32, fontSize: 13 }}>{u.nome[0]?.toUpperCase()}</div>
            <div>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)" }}>{u.nome}</div>
              <div style={{ fontSize: 11, color: "var(--text3)" }}>{u.tipo}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="chat-main" style={{ flex: 1, display: "flex", flexDirection: "column", background: "var(--bg)" }}>
        {!destId ? (
          <div className="empty-state" style={{ margin: "auto" }}>
            {Icons.chat}
            <p>Selecione um usuário para conversar</p>
          </div>
        ) : (
          <>
            <div style={{ padding: "14px 20px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 10 }}>
              <div className="user-avatar">{usuarios.find(u => u.id === destId)?.nome[0]?.toUpperCase()}</div>
              <span style={{ fontWeight: 600 }}>{usuarios.find(u => u.id === destId)?.nome}</span>
            </div>
            <div className="chat-messages" ref={msgsRef}>
              {mensagens.map((m, i) => {
                const mine = parseInt(m.usuario_id) === user.id;
                return (
                  <div key={i} className={`chat-msg ${mine ? "mine" : "theirs"}`}>
                    {!mine && <div className="chat-msg-name">{m.nome}</div>}
                    {m.mensagem}
                    <div style={{ fontSize: 10, color: "var(--text3)", marginTop: 4, textAlign: mine ? "right" : "left" }}>
                      {m.criado_em ? new Date(m.criado_em).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" }) : ""}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="chat-input-row">
              <input className="form-input" placeholder="Digite sua mensagem..." value={texto}
                onChange={e => setTexto(e.target.value)}
                onKeyDown={e => e.key === "Enter" && enviar()}
                style={{ flex: 1 }} />
              <button className="btn btn-primary" onClick={enviar}>{Icons.send}</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

// ===================== APP =====================
export default function App() {
  const [user, setUser] = useState(null);
  const [menu, setMenu] = useState("Nova Venda");
  const [chatOpen, setChatOpen] = useState(false);

  function iniciais(nome) {
    return (nome || "U").split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase();
  }

  if (!user) return (
    <>
      <style>{CSS}</style>
      <Login onLogin={u => { setUser(u); }} />
    </>
  );

  const isAdmin = user.tipo === "admin";

  const menuItems = [
    { label: "OPERAÇÃO", section: true },
    { id: "Nova Venda", label: "Nova Venda", icon: Icons.sale },
    { id: "Painel", label: "Painel", icon: Icons.panel },
    ...(isAdmin ? [
      { label: "GESTÃO", section: true },
      { id: "Usuarios", label: "Usuários", icon: Icons.users },
      { id: "Comissoes", label: "Comissões", icon: Icons.commission },
    ] : []),
  ];

  function renderPage() {
    if (chatOpen) return <Chat user={user} />;
    switch (menu) {
      case "Nova Venda": return <NovaVenda user={user} />;
      case "Painel": return <Painel user={user} />;
      case "Usuarios": return isAdmin ? <Usuarios /> : null;
      case "Comissoes": return isAdmin ? <Comissoes /> : null;
      default: return null;
    }
  }

  return (
    <>
      <style>{CSS}</style>
      <div className="layout">
        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="sidebar-logo">
            <div className="logo-icon">🌀</div>
            <div>
              <div className="logo-text">OPERAX</div>
              <div className="logo-sub">SALES</div>
            </div>
          </div>

          <div className="sidebar-user">
            <div className="user-avatar">{iniciais(user.nome)}</div>
            <div>
              <div className="user-name">{user.nome}</div>
              <div className="user-role">{user.tipo}</div>
            </div>
            <div className="user-dot" />
          </div>

          {menuItems.map((item, i) => item.section ? (
            <div key={i} className="menu-section">{item.label}</div>
          ) : (
            <div key={item.id} className={`menu-item ${menu === item.id && !chatOpen ? "active" : ""}`}
              onClick={() => { setMenu(item.id); setChatOpen(false); }}>
              {item.icon}{item.label}
            </div>
          ))}

          <div className="sidebar-logout">
            <div className="menu-item" onClick={() => setUser(null)} style={{ color: "var(--danger)" }}>
              {Icons.logout} Sair
            </div>
          </div>
        </aside>

        {/* MAIN */}
        <div className="main">
          {/* TOPBAR */}
          <header className="topbar">
            <div className="topbar-logo">
              <div style={{ fontSize: 28 }}>🌀</div>
              <div>
                <div className="topbar-title">OPERAX <span>SALES</span></div>
                <div className="topbar-sub">Sistema inteligente de vendas e operações financeiras</div>
              </div>
            </div>

            <div className="topbar-pills">
              <div className="topbar-pill">{Icons.bolt} Painel inteligente</div>
              <div className="topbar-pill">{Icons.refresh} Atualização por ação</div>
              <div className="topbar-pill">{Icons.person} Controle por vendedor</div>
            </div>

            <div className="topbar-chat" onClick={() => setChatOpen(v => !v)}>
              {Icons.chat} Chat
            </div>
          </header>

          {/* CONTENT */}
          {chatOpen ? (
            <Chat user={user} />
          ) : (
            <div className="content">
              {renderPage()}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
