import { useState, useEffect, useRef, useCallback } from "react";

/* ─────────────────────────────────────────────
   SUPABASE
───────────────────────────────────────────── */
const URL  = "https://ynxpowhzhnwqazdxshch.supabase.co";
const KEY  = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt";

async function api(path, opts = {}) {
  const r = await fetch(`${URL}/rest/v1/${path}`, {
    headers: {
      apikey: KEY,
      Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      Prefer: opts.prefer || "return=representation",
      ...opts.headers,
    },
    ...opts,
  });
  const txt = await r.text();
  if (!r.ok) throw new Error(txt);
  return txt ? JSON.parse(txt) : [];
}

/* hash idêntico ao Python: hashlib.sha256(str(senha).encode()).hexdigest() */
async function hashSenha(s) {
  const buf  = new TextEncoder().encode(String(s));
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2,"0")).join("");
}

/* ─────────────────────────────────────────────
   HELPERS
───────────────────────────────────────────── */
const limpar = v => String(v || "").replace(/\D/g, "");

function validarCPF(cpf) {
  const c = limpar(cpf);
  if (c.length !== 11 || c === c[0].repeat(11)) return false;
  let s = Array.from({length:9},(_,i)=>+c[i]*(10-i)).reduce((a,b)=>a+b,0);
  let d1 = (s*10)%11; if(d1===10) d1=0;
  s = Array.from({length:10},(_,i)=>+c[i]*(11-i)).reduce((a,b)=>a+b,0);
  let d2 = (s*10)%11; if(d2===10) d2=0;
  return d1===+c[9] && d2===+c[10];
}

function validarTel(t) {
  const c = limpar(t);
  if (![10,11].includes(c.length)) return false;
  if (c.slice(0,2)==="00") return false;
  if (c.length===11 && c[2]!=="9") return false;
  return true;
}

function converterValor(v) {
  let t = String(v||"").replace("R$","").replace(/\s/g,"");
  if (!t) return 0;
  if (t.includes(",")) t = t.replace(/\./g,"").replace(",",".");
  return parseFloat(t)||0;
}

function dinheiro(v) {
  return new Intl.NumberFormat("pt-BR",{style:"currency",currency:"BRL"}).format(parseFloat(v)||0);
}

function iniciais(nome) {
  return (nome||"U").split(" ").map(p=>p[0]).slice(0,2).join("").toUpperCase();
}

/* ─────────────────────────────────────────────
   ESTILOS GLOBAIS
───────────────────────────────────────────── */
const G = `
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,#root{min-height:100vh;font-family:'Inter',sans-serif}

:root{
  --bg:       #f8fbff;
  --bg2:      #eef6ff;
  --sidebar-top: #020617;
  --sidebar-mid: #061a3d;
  --sidebar-bot: #0f172a;
  --sidebar-glow: rgba(14,165,233,0.35);
  --blue:     #0ea5e9;
  --blue2:    #2563eb;
  --blue3:    #38bdf8;
  --text:     #0f172a;
  --text2:    #475569;
  --text3:    #94a3b8;
  --card:     rgba(255,255,255,0.90);
  --border:   rgba(14,165,233,0.12);
  --border2:  rgba(14,165,233,0.30);
  --success:  #16a34a;
  --warn:     #d97706;
  --danger:   #dc2626;
  --radius:   14px;
  --radius2:  22px;
}

/* layout */
.layout{display:flex;min-height:100vh;background:
  radial-gradient(circle at top left, rgba(14,165,233,0.13), transparent 25%),
  radial-gradient(circle at bottom right, rgba(37,99,235,0.10), transparent 30%),
  linear-gradient(135deg,#f8fbff 0%,#eef6ff 46%,#fff 100%)}

/* ── SIDEBAR ── */
.sidebar{
  width:245px;min-width:245px;
  background: radial-gradient(circle at top left, var(--sidebar-glow), transparent 30%),
    linear-gradient(180deg, var(--sidebar-top) 0%, var(--sidebar-mid) 48%, var(--sidebar-bot) 100%);
  border-right:1px solid rgba(56,189,248,0.38);
  box-shadow:18px 0 45px rgba(14,165,233,0.22);
  display:flex;flex-direction:column;overflow:hidden;position:relative;
}
.sidebar *{color:#fff}

.sb-logo{
  display:flex;align-items:center;gap:12px;
  padding:18px 16px 22px;
}
.sb-logo-icon{
  width:52px;height:52px;border-radius:18px;flex-shrink:0;
  background:radial-gradient(circle at 50% 50%,#020617 0%,#020617 32%,#0ea5e9 44%,#2563eb 70%,#38bdf8 100%);
  display:flex;align-items:center;justify-content:center;
  font-size:26px;font-weight:900;
  box-shadow:0 0 34px rgba(56,189,248,0.58),inset 0 0 0 1px rgba(255,255,255,0.22);
}
.sb-logo-title{font-size:20px;font-weight:900;letter-spacing:.08em;line-height:1.05}
.sb-logo-sub{font-size:12px;color:#38bdf8!important;letter-spacing:.28em;margin-top:3px}

.sb-user{
  background:rgba(255,255,255,0.075);
  border:1px solid rgba(56,189,248,0.30);
  border-radius:18px;padding:14px 14px;
  margin:4px 12px 16px;
  box-shadow:0 16px 34px rgba(14,165,233,0.18);
  display:flex;align-items:center;gap:10px;
}
.sb-avatar{
  width:36px;height:36px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,#2563eb,#38bdf8);
  display:flex;align-items:center;justify-content:center;
  font-size:14px;font-weight:800;
}
.sb-uname{font-size:14px;font-weight:700;line-height:1.2}
.sb-urole{font-size:11px;color:#7dd3fc!important;text-transform:uppercase;letter-spacing:.07em}
.sb-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 6px #22c55e;margin-left:auto;flex-shrink:0}

.sb-section{
  font-size:12px;font-weight:900;
  color:rgba(56,189,248,0.94)!important;
  text-transform:uppercase;letter-spacing:.08em;
  margin:16px 0 6px 16px;
}

.sb-item{
  display:flex;align-items:center;gap:12px;
  padding:12px 16px;margin:2px 8px;border-radius:14px;
  cursor:pointer;transition:all .16s;
  color:rgba(255,255,255,0.80)!important;
  font-size:15px;font-weight:700;
}
.sb-item:hover{background:rgba(56,189,248,0.14);transform:translateX(2px)}
.sb-item.active{
  background:linear-gradient(90deg,rgba(37,99,235,0.96),rgba(14,165,233,0.96));
  color:#fff!important;
  box-shadow:0 0 26px rgba(56,189,248,0.52),inset 0 0 0 1px rgba(255,255,255,0.22);
}
.sb-item svg{width:20px;height:20px;stroke:currentColor;fill:none;stroke-width:2.2;flex-shrink:0}

.sb-footer{margin-top:auto;border-top:1px solid rgba(255,255,255,0.08);padding:12px 8px}

/* ── MAIN ── */
.main{flex:1;display:flex;flex-direction:column;min-width:0}

/* ── TOPBAR (hero) ── */
.topbar{
  padding:20px 28px 18px;
  background:linear-gradient(135deg,rgba(255,255,255,0.94),rgba(239,246,255,0.86));
  border-bottom:1px solid var(--border2);
  box-shadow:0 22px 70px rgba(15,23,42,0.10);
  backdrop-filter:blur(14px);
}
.topbar-inner{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.topbar-brand{display:flex;align-items:center;gap:18px}
.topbar-icon{
  width:58px;height:58px;border-radius:18px;flex-shrink:0;
  background:radial-gradient(circle at 50% 50%,#020617 0%,#020617 32%,#0ea5e9 44%,#2563eb 70%,#38bdf8 100%);
  display:flex;align-items:center;justify-content:center;font-size:30px;
  box-shadow:0 0 28px rgba(14,165,233,0.5);
}
.topbar-title{font-size:42px;line-height:1;font-weight:900;letter-spacing:-0.05em;color:#0f172a}
.topbar-title span{color:#0ea5e9;letter-spacing:.05em}
.topbar-sub{margin-top:6px;color:#475569;font-size:15px;font-weight:500}
.topbar-pill{
  display:inline-flex;align-items:center;gap:8px;
  padding:9px 14px;border-radius:999px;
  background:linear-gradient(90deg,#2563eb,#0ea5e9);
  color:#fff;border:1px solid rgba(14,165,233,0.22);
  font-weight:800;font-size:13px;
  box-shadow:0 12px 28px rgba(14,165,233,0.24);
  margin-top:10px;
}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:10px;flex-shrink:0}
.chat-btn{
  display:flex;align-items:center;gap:7px;
  padding:9px 18px;border-radius:12px;cursor:pointer;
  background:linear-gradient(135deg,#2563eb,#0ea5e9);
  color:#fff;font-size:14px;font-weight:800;border:none;
  box-shadow:0 8px 24px rgba(14,165,233,0.28);transition:all .16s;position:relative;
}
.chat-btn:hover{box-shadow:0 12px 32px rgba(14,165,233,0.4);transform:translateY(-1px)}
.chat-btn svg{width:16px;height:16px;stroke:#fff;fill:none;stroke-width:2.5}
.chat-badge{
  position:absolute;top:-7px;right:-7px;background:#ef4444;
  color:#fff;font-size:10px;font-weight:900;
  width:19px;height:19px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 8px rgba(239,68,68,0.7);
}

/* ── CONTENT ── */
.content{flex:1;overflow-y:auto;padding:28px}
.content::-webkit-scrollbar{width:6px}
.content::-webkit-scrollbar-thumb{background:rgba(14,165,233,0.25);border-radius:3px}

/* ── CARD ── */
.card{
  background:var(--card);border:1px solid var(--border);
  border-radius:var(--radius2);padding:24px;margin-bottom:20px;
  box-shadow:0 18px 55px rgba(15,23,42,0.08);backdrop-filter:blur(14px);
}
.card-hdr{display:flex;align-items:center;gap:12px;margin-bottom:22px}
.card-icon{
  width:42px;height:42px;border-radius:12px;
  background:linear-gradient(135deg,rgba(37,99,235,0.12),rgba(14,165,233,0.12));
  border:1px solid var(--border2);
  display:flex;align-items:center;justify-content:center;
}
.card-icon svg{width:22px;height:22px;stroke:#0ea5e9;fill:none;stroke-width:2}
.card-title{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.03em}

/* ── METRICS ── */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:22px}
.metric{
  background:linear-gradient(135deg,rgba(255,255,255,0.96),rgba(239,246,255,0.78));
  border:1px solid rgba(14,165,233,0.13);border-radius:20px;padding:18px 20px;
  box-shadow:0 14px 38px rgba(15,23,42,0.08);position:relative;overflow:hidden;
}
.metric::after{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,#2563eb,#0ea5e9);
}
.metric-lbl{font-size:11px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px}
.metric-val{font-size:22px;font-weight:900;color:var(--text);line-height:1}
.metric-val.ok{color:var(--success)}
.metric-val.warn{color:var(--warn)}
.metric-val.bad{color:var(--danger)}
.metric-val.info{color:#2563eb}

/* ── FORM ── */
.fg{margin-bottom:16px}
.fg label{display:block;font-size:12px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}
.fi,.fs,.fta{
  width:100%;padding:11px 14px;
  background:rgba(255,255,255,0.94);
  border:1px solid rgba(14,165,233,0.18)!important;
  border-radius:15px!important;color:var(--text);
  font-family:'Inter',sans-serif;font-size:14px;outline:none;
  transition:border-color .16s,box-shadow .16s;appearance:none;
}
.fi:focus,.fs:focus,.fta:focus{
  border-color:rgba(14,165,233,0.68)!important;
  box-shadow:0 0 0 3px rgba(14,165,233,0.14)!important;
}
.fi::placeholder{color:var(--text3)}
.fs{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");background-repeat:no-repeat;background-position:right 12px center;background-color:rgba(255,255,255,0.94);padding-right:36px}
.fs option{background:#fff;color:var(--text)}
.fta{resize:vertical;min-height:90px}
.fr{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.fe{font-size:12px;color:var(--danger);margin-top:4px}
.fs2{font-size:12px;color:var(--success);margin-top:4px}
.prefix-wrap{display:flex}
.prefix{padding:11px 13px;background:rgba(14,165,233,0.08);border:1px solid rgba(14,165,233,0.18);border-right:none;border-radius:15px 0 0 15px;font-size:14px;font-weight:700;color:var(--text2);white-space:nowrap}
.prefix-wrap .fi{border-radius:0 15px 15px 0!important}

/* ── BUTTONS ── */
.btn{display:inline-flex;align-items:center;gap:7px;padding:10px 20px;border-radius:14px;font-family:'Inter',sans-serif;font-size:14px;font-weight:800;cursor:pointer;transition:all .16s;border:none;white-space:nowrap}
.btn svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.5}
.btn-p{background:linear-gradient(135deg,#2563eb,#0ea5e9);color:#fff;box-shadow:0 12px 26px rgba(14,165,233,0.24)}
.btn-p:hover{box-shadow:0 16px 34px rgba(14,165,233,0.36);transform:translateY(-1px)}
.btn-s{background:rgba(14,165,233,0.10);color:#2563eb;border:1px solid rgba(14,165,233,0.22)}
.btn-s:hover{background:rgba(14,165,233,0.20)}
.btn-d{background:rgba(220,38,38,0.10);color:var(--danger);border:1px solid rgba(220,38,38,0.25)}
.btn-d:hover{background:rgba(220,38,38,0.18)}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none!important}

/* ── ALERTS ── */
.alert{display:flex;align-items:center;gap:8px;padding:12px 16px;border-radius:14px;font-size:13px;font-weight:600;margin-bottom:14px}
.alert svg{width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.5;flex-shrink:0}
.a-ok{background:#dcfce7;border:1px solid #86efac;color:#166534}
.a-err{background:#fee2e2;border:1px solid #fca5a5;color:#991b1b}
.a-info{background:#dbeafe;border:1px solid #93c5fd;color:#1d4ed8}

/* ── TABLE ── */
.tw{overflow-x:auto;border-radius:var(--radius);border:1px solid rgba(14,165,233,0.13);box-shadow:0 14px 38px rgba(15,23,42,0.06)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{background:rgba(239,246,255,0.80);color:var(--text3);font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;padding:10px 14px;border-bottom:1px solid rgba(14,165,233,0.13);text-align:left;white-space:nowrap}
td{padding:11px 14px;border-bottom:1px solid rgba(14,165,233,0.06);color:var(--text2);vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(14,165,233,0.04)}
.td-p{color:var(--text);font-weight:600}

/* ── BADGES ── */
.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.b-ok{background:#dcfce7;color:#166534;border:1px solid #86efac}
.b-pend{background:#fef9c3;color:#854d0e;border:1px solid #fde047}
.b-bad{background:#fee2e2;color:#991b1b;border:1px solid #fca5a5}
.b-wait{background:#dbeafe;color:#1d4ed8;border:1px solid #93c5fd}
.b-adm{background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd}
.b-vend{background:#dcfce7;color:#166534;border:1px solid #86efac}

/* ── LOGIN ── */
.login-wrap{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at top left,rgba(14,165,233,0.13),transparent 25%),
    radial-gradient(circle at bottom right,rgba(37,99,235,0.10),transparent 30%),
    linear-gradient(135deg,#f8fbff 0%,#eef6ff 46%,#fff 100%);
}
.login-card{
  background:rgba(255,255,255,0.96);border:1px solid var(--border2);
  border-radius:28px;padding:40px 36px;width:420px;max-width:95vw;
  box-shadow:0 28px 80px rgba(14,165,233,0.18);
}
.login-hero{text-align:center;margin-bottom:32px}
.login-icon{
  width:76px;height:76px;border-radius:22px;margin:0 auto 16px;
  background:radial-gradient(circle at 50% 50%,#020617 0%,#020617 32%,#0ea5e9 44%,#2563eb 70%,#38bdf8 100%);
  display:flex;align-items:center;justify-content:center;font-size:38px;
  box-shadow:0 0 38px rgba(14,165,233,0.55);
}
.login-title{font-size:34px;font-weight:900;color:#0f172a;letter-spacing:-.04em}
.login-title span{color:#0ea5e9;letter-spacing:.05em}
.login-sub{font-size:14px;color:var(--text2);margin-top:6px}

/* ── MODAL ── */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,0.45);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;z-index:200;padding:16px}
.modal{background:#fff;border:1px solid var(--border2);border-radius:22px;padding:28px;width:100%;max-width:560px;max-height:90vh;overflow-y:auto;box-shadow:0 28px 80px rgba(14,165,233,0.18)}
.modal::-webkit-scrollbar{width:5px}
.modal::-webkit-scrollbar-thumb{background:rgba(14,165,233,0.25);border-radius:3px}
.modal-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}
.modal-close{background:#fee2e2;border:1px solid #fca5a5;color:#991b1b;border-radius:8px;padding:5px 10px;cursor:pointer;font-size:18px;line-height:1;transition:.15s}
.modal-close:hover{background:#fca5a5}

/* ── CHAT ── */
.chat-layout{display:flex;height:calc(100vh - 130px);min-height:400px}
.chat-users{width:230px;min-width:230px;border-right:1px solid var(--border);overflow-y:auto;background:rgba(255,255,255,0.7);padding:10px}
.chat-ui{display:flex;align-items:center;gap:9px;padding:10px 12px;border-radius:12px;cursor:pointer;margin-bottom:3px;transition:.15s}
.chat-ui:hover{background:rgba(14,165,233,0.08)}
.chat-ui.act{background:rgba(14,165,233,0.12);border:1px solid var(--border2)}
.chat-av{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,#2563eb,#0ea5e9);display:flex;align-items:center;justify-content:center;color:#fff;font-size:13px;font-weight:800;flex-shrink:0}
.chat-main{flex:1;display:flex;flex-direction:column;min-width:0}
.chat-msgs{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:10px}
.chat-msgs::-webkit-scrollbar{width:4px}
.chat-msgs::-webkit-scrollbar-thumb{background:rgba(14,165,233,0.2);border-radius:2px}
.msg{max-width:70%;padding:10px 14px;border-radius:16px;font-size:14px;line-height:1.5}
.msg.mine{background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:1px solid #86efac;align-self:flex-end;border-bottom-right-radius:4px}
.msg.theirs{background:#fff;border:1px solid #e5e7eb;align-self:flex-start;border-bottom-left-radius:4px}
.msg-name{font-size:11px;font-weight:700;color:var(--text3);margin-bottom:3px}
.msg-time{font-size:10px;color:var(--text3);margin-top:4px}
.chat-inp{padding:14px 20px;border-top:1px solid var(--border);display:flex;gap:10px}

/* ── MISC ── */
.spinner{width:36px;height:36px;border:3px solid rgba(14,165,233,0.15);border-top-color:#0ea5e9;border-radius:50%;animation:spin .7s linear infinite;margin:40px auto;display:block}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:48px 20px;color:var(--text3)}
.empty svg{width:48px;height:48px;stroke:var(--text3);fill:none;stroke-width:1.5;margin:0 auto 14px;display:block}
.divider{border:none;border-top:1px solid rgba(14,165,233,0.10);margin:22px 0}
.sec-title{font-size:16px;font-weight:800;color:var(--text);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.sec-title::before{content:'';display:block;width:3px;height:17px;background:linear-gradient(#2563eb,#0ea5e9);border-radius:2px}
.check-row{display:flex;align-items:center;gap:8px;cursor:pointer}
.check-row input{width:16px;height:16px;accent-color:#0ea5e9;cursor:pointer}
.check-row span{font-size:14px;color:var(--text2)}
`;

/* ─────────────────────────────────────────────
   ICONS
───────────────────────────────────────────── */
const I = {
  sale:   <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>,
  panel:  <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  users:  <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  coin:   <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M9 9h4.5a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3H15"/></svg>,
  logout: <svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  chat:   <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  bolt:   <svg viewBox="0 0 24 24"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>,
  ref:    <svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15A9 9 0 1 1 5.19 5.19L1 1"/></svg>,
  person: <svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>,
  plus:   <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  edit:   <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  trash:  <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
  check:  <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
  x:      <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  send:   <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  info:   <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  bank:   <svg viewBox="0 0 24 24"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>,
};

/* ─────────────────────────────────────────────
   ALERT
───────────────────────────────────────────── */
function Alert({type="info", children}) {
  const cls = {ok:"a-ok",err:"a-err",info:"a-info"}[type]||"a-info";
  const ico = type==="ok"?I.check:type==="err"?I.x:I.info;
  return <div className={`alert ${cls}`}>{ico}{children}</div>;
}

/* ─────────────────────────────────────────────
   LOGIN
───────────────────────────────────────────── */
function Login({onLogin}) {
  const [u,setU]=useState(""); const [s,setS]=useState(""); const [loading,setL]=useState(false); const [err,setE]=useState("");

  async function enter() {
    if(!u||!s){setE("Preencha usuário e senha.");return}
    setL(true);setE("");
    try {
      const uLow = u.trim().toLowerCase();
      const rows  = await api(`usuarios?select=*&usuario=eq.${encodeURIComponent(uLow)}&ativo=eq.true`);
      if (!rows.length){setE("Usuário não encontrado ou inativo.");setL(false);return}
      const row = rows[0];
      // testa str(senha).strip() — exatamente como Python hash_senha(str(senha).strip())
      const h1 = await hashSenha(s.trim());
      const h2 = await hashSenha(s);
      if (row.senha_hash!==h1 && row.senha_hash!==h2) {setE("Senha incorreta.");setL(false);return}
      onLogin(row);
    } catch(e){setE("Erro de conexão: "+e.message);setL(false)}
  }

  return (
    <div className="login-wrap">
      <div className="login-card">
        <div className="login-hero">
          <div className="login-icon">🌀</div>
          <div className="login-title">OPERAX <span>SALES</span></div>
          <div className="login-sub">Sistema inteligente de vendas e operações financeiras</div>
        </div>
        {err&&<Alert type="err">{err}</Alert>}
        <div className="fg"><label>Usuário</label>
          <input className="fi" placeholder="Seu login" value={u} onChange={e=>setU(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enter()}/>
        </div>
        <div className="fg"><label>Senha</label>
          <input className="fi" type="password" placeholder="Sua senha" value={s} onChange={e=>setS(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enter()}/>
        </div>
        <button className="btn btn-p" style={{width:"100%",justifyContent:"center",marginTop:8}} onClick={enter} disabled={loading}>
          {loading?"Entrando...":"Entrar"}
        </button>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   NOVA VENDA
───────────────────────────────────────────── */
function NovaVenda({user}) {
  const [tabelas,setTab]=useState([]);
  const [form,setF]=useState({cliente:"",cpf:"",tel:"",tabela:"",valor:"",status:"Pendente",obs:""});
  const [hints,setH]=useState({});
  const [loading,setL]=useState(false);
  const [msg,setM]=useState(null);

  useEffect(()=>{
    api("regras_comissao?select=produto&ativo=eq.true").then(d=>{
      const u=[...new Set(d.map(r=>r.produto).filter(Boolean))].sort();
      const list = u.length?u:["CLT PADRAO","V8 ACIMA 36X","PRESENÇA","HUBBIE","OUTROS BANCOS"];
      setTab(list); setF(p=>({...p,tabela:list[0]}));
    }).catch(()=>setTab(["CLT PADRAO","V8 ACIMA 36X","PRESENÇA","HUBBIE","OUTROS BANCOS"]));
  },[]);

  function chk(field,val) {
    const hints2={...hints};
    if(field==="cpf"&&val){
      const c=limpar(val);
      if(c.length<11) hints2.cpf={t:"e",m:`CPF incompleto: faltam ${11-c.length} número(s).`};
      else if(c.length>11) hints2.cpf={t:"e",m:`CPF com número(s) a mais.`};
      else if(validarCPF(c)) hints2.cpf={t:"ok",m:"CPF válido ✓"};
      else hints2.cpf={t:"e",m:"CPF inválido. Confira os números."};
    } else delete hints2.cpf;
    if(field==="tel"&&val){
      const t=limpar(val);
      if(t.length<10) hints2.tel={t:"e",m:"Telefone incompleto. Informe DDD + número."};
      else if(t.length>11) hints2.tel={t:"e",m:"Telefone com números a mais."};
      else if(validarTel(t)) hints2.tel={t:"ok",m:"Telefone válido ✓"};
      else hints2.tel={t:"e",m:"Telefone inválido. Use DDD + número."};
    } else delete hints2.tel;
    if(field==="valor"&&val){
      const v=converterValor(val);
      if(v>0) hints2.valor={t:"ok",m:`Valor válido: ${dinheiro(v)}`};
      else hints2.valor={t:"e",m:"Valor inválido. Ex: R$ 1.758,71"};
    } else delete hints2.valor;
    setH(hints2);
  }

  function set(f,v){setF(p=>({...p,[f]:v}));chk(f,v)}

  async function getPerc(tab,val){
    try{
      const r=await api(`regras_comissao?produto=eq.${encodeURIComponent(tab)}&ativo=eq.true&order=valor_minimo.desc`);
      for(const x of r) if(parseFloat(val)>=parseFloat(x.valor_minimo||0)) return parseFloat(x.percentual_empresa||0);
    }catch{}
    return 0;
  }

  async function salvar(){
    const cpf=limpar(form.cpf); const tel=limpar(form.tel);
    const val=converterValor(form.valor);
    if(!validarCPF(cpf)){setM({t:"err",m:"Corrija o CPF antes de salvar."});return}
    if(!validarTel(tel)){setM({t:"err",m:"Corrija o telefone antes de salvar."});return}
    if(val<=0){setM({t:"err",m:"Corrija o valor antes de salvar."});return}
    setL(true);setM(null);
    try{
      const perc=await getPerc(form.tabela,val);
      const vEmp=val*(perc/100);
      await api("vendas",{method:"POST",prefer:"return=minimal",body:JSON.stringify({
        data: new Date().toISOString(),
        vendedor_id: user.id,
        vendedor: user.usuario,
        vendedor_nome: user.nome,
        cliente: form.cliente,
        cpf, telefone: tel,
        produto: form.tabela,
        tabela_banco: form.tabela,
        valor: val,
        status: form.status,
        observacao: form.obs,
        comissao_empresa: perc,
        valor_comissao_empresa: vEmp,
        conferido: false,
        alterado_vendedor: false,
      })});
      setM({t:"ok",m:"Venda cadastrada com sucesso!"});
      setF(p=>({...p,cliente:"",cpf:"",tel:"",valor:"",obs:"",status:"Pendente"}));
      setH({});
    }catch(e){setM({t:"err",m:"Erro ao salvar: "+e.message})}
    setL(false);
  }

  return (
    <div>
      {msg&&<Alert type={msg.t}>{msg.m}</Alert>}
      <div className="card">
        <div className="card-hdr"><div className="card-icon">{I.sale}</div><div className="card-title">Cadastro de Venda</div></div>

        <div className="fg"><label>Cliente</label>
          <input className="fi" placeholder="Digite o nome do cliente..." value={form.cliente} onChange={e=>setF(p=>({...p,cliente:e.target.value}))}/>
        </div>

        <div className="fr">
          <div className="fg"><label>CPF</label>
            <input className="fi" placeholder="Ex: 999.999.999-99" value={form.cpf} onChange={e=>set("cpf",e.target.value)}/>
            {hints.cpf&&<div className={hints.cpf.t==="ok"?"fs2":"fe"}>{hints.cpf.m}</div>}
          </div>
          <div className="fg"><label>Telefone</label>
            <input className="fi" placeholder="Ex: (11) 99976-7867" value={form.tel} onChange={e=>set("tel",e.target.value)}/>
            {hints.tel&&<div className={hints.tel.t==="ok"?"fs2":"fe"}>{hints.tel.m}</div>}
          </div>
        </div>

        <div className="fg"><label>Tabela / Banco</label>
          <select className="fs" value={form.tabela} onChange={e=>setF(p=>({...p,tabela:e.target.value}))}>
            {tabelas.map(t=><option key={t} value={t}>{t}</option>)}
          </select>
        </div>

        <div className="fr">
          <div className="fg"><label>Valor Vendido</label>
            <div className="prefix-wrap">
              <span className="prefix">R$</span>
              <input className="fi" placeholder="Ex: 1.758,71" value={form.valor} onChange={e=>set("valor",e.target.value)}/>
            </div>
            {hints.valor&&<div className={hints.valor.t==="ok"?"fs2":"fe"}>{hints.valor.m}</div>}
          </div>
          <div className="fg"><label>Status</label>
            <select className="fs" value={form.status} onChange={e=>setF(p=>({...p,status:e.target.value}))}>
              {["Pendente","Pago","Cancelado"].map(s=><option key={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <div className="fg"><label>Observação</label>
          <textarea className="fta" placeholder="Observações adicionais..." value={form.obs} onChange={e=>setF(p=>({...p,obs:e.target.value}))}/>
        </div>

        <button className="btn btn-p" onClick={salvar} disabled={loading}>
          {I.plus}{loading?"Salvando...":"Salvar Venda"}
        </button>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   PAINEL
───────────────────────────────────────────── */
function Painel({user}) {
  const [vendas,setV]=useState([]); const [loading,setL]=useState(true);
  const [mes,setMes]=useState(new Date().getMonth()+1);
  const [ano,setAno]=useState(new Date().getFullYear());
  const [tabelas,setTab]=useState([]);
  const [editId,setEId]=useState(null); const [ed,setEd]=useState({});
  const [msg,setM]=useState(null);

  async function load(){
    setL(true);
    try{
      let url="vendas?select=*&order=id.desc";
      if(user.tipo!=="admin") url+=`&vendedor_id=eq.${user.id}`;
      setV(await api(url));
    }catch{}
    setL(false);
  }

  useEffect(()=>{load()},[]);
  useEffect(()=>{
    api("regras_comissao?select=produto&ativo=eq.true").then(d=>{
      const u=[...new Set(d.map(r=>r.produto).filter(Boolean))].sort();
      setTab(u.length?u:["CLT PADRAO","V8 ACIMA 36X","PRESENÇA","HUBBIE","OUTROS BANCOS"]);
    }).catch(()=>{});
  },[]);

  const meses=["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];

  const fil=vendas.filter(v=>{
    if(!v.data) return false;
    const d=new Date(v.data);
    return d.getMonth()+1===mes && d.getFullYear()===ano;
  });

  const tot=fil.reduce((s,v)=>s+parseFloat(v.valor||0),0);
  const pago=fil.filter(v=>v.status==="Pago").reduce((s,v)=>s+parseFloat(v.valor||0),0);
  const pend=fil.filter(v=>v.status==="Pendente").reduce((s,v)=>s+parseFloat(v.valor||0),0);
  const emp=fil.reduce((s,v)=>s+parseFloat(v.valor_comissao_empresa||0),0);

  function badge(s){
    const m={Pago:"b-ok",Pendente:"b-pend",Cancelado:"b-bad",Aguardando:"b-wait"};
    return <span className={`badge ${m[s]||"b-wait"}`}>{s}</span>;
  }

  function rowBg(v){
    if(v.status!=="Pendente") return {};
    const old=new Date()-new Date(v.data)>3600000;
    if(old&&user.tipo==="admin") return {background:"rgba(220,38,38,0.06)"};
    return {background:"rgba(250,204,21,0.08)"};
  }

  async function salvarEdit(){
    try{
      const val=converterValor(String(ed.valor));
      let patch={
        cliente:ed.cliente, cpf:limpar(ed.cpf||""),
        telefone:limpar(ed.telefone||""),
        produto:ed.tabela_banco, tabela_banco:ed.tabela_banco,
        valor:val, status:ed.status, observacao:ed.observacao,
      };
      if(user.tipo==="admin"){
        patch.conferido=ed.conferido; patch.alterado_vendedor=false;
        patch.observacao_admin=ed.observacao_admin;
      } else {
        patch.alterado_vendedor=true;
        patch.data_alteracao_vendedor=new Date().toISOString();
        patch.observacao_alteracao=ed.observacao_alteracao;
        patch.conferido=false;
      }
      await api(`vendas?id=eq.${editId}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify(patch)});
      setM({t:"ok",m:"Proposta atualizada!"}); setEId(null); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  return (
    <div>
      {msg&&<Alert type={msg.t}>{msg.m}</Alert>}
      <div className="metrics">
        <div className="metric"><div className="metric-lbl">Total Vendas</div><div className="metric-val info">{dinheiro(tot)}</div></div>
        <div className="metric"><div className="metric-lbl">Pago</div><div className="metric-val ok">{dinheiro(pago)}</div></div>
        <div className="metric"><div className="metric-lbl">Pendente</div><div className="metric-val warn">{dinheiro(pend)}</div></div>
        {user.tipo==="admin"&&<div className="metric"><div className="metric-lbl">Comissão Empresa</div><div className="metric-val info">{dinheiro(emp)}</div></div>}
        <div className="metric"><div className="metric-lbl">Qtd</div><div className="metric-val">{fil.length}</div></div>
      </div>

      <div style={{display:"flex",gap:10,marginBottom:18,flexWrap:"wrap",alignItems:"flex-end"}}>
        <div className="fg" style={{margin:0}}>
          <select className="fs" style={{width:130}} value={mes} onChange={e=>setMes(+e.target.value)}>
            {meses.map((m,i)=><option key={i} value={i+1}>{m}</option>)}
          </select>
        </div>
        <div className="fg" style={{margin:0}}>
          <select className="fs" style={{width:100}} value={ano} onChange={e=>setAno(+e.target.value)}>
            {[2024,2025,2026].map(a=><option key={a}>{a}</option>)}
          </select>
        </div>
        <button className="btn btn-s" onClick={load}>{I.ref} Atualizar</button>
      </div>

      {loading?<div className="spinner"/>:(
        <div className="card">
          {fil.length===0?(
            <div className="empty">{I.sale}<p>Nenhuma venda neste período.</p></div>
          ):(
            <div className="tw">
              <table>
                <thead><tr>
                  <th>ID</th><th>Cliente</th><th>CPF</th><th>Tabela/Banco</th>
                  <th>Valor</th><th>Status</th><th>Data</th>
                  {user.tipo==="admin"&&<><th>Vendedor</th><th>Conf.</th></>}
                  <th></th>
                </tr></thead>
                <tbody>
                  {fil.map(v=>(
                    <tr key={v.id} style={rowBg(v)}>
                      <td className="td-p">#{v.id}</td>
                      <td className="td-p">{v.cliente}</td>
                      <td>{v.cpf||"—"}</td>
                      <td>{v.tabela_banco||v.produto||"—"}</td>
                      <td className="td-p">{dinheiro(v.valor)}</td>
                      <td>{badge(v.status)}</td>
                      <td>{v.data?new Date(v.data).toLocaleDateString("pt-BR"):"—"}</td>
                      {user.tipo==="admin"&&<><td>{v.vendedor_nome||v.vendedor||"—"}</td>
                      <td>{v.conferido?<span className="badge b-ok">✓</span>:<span className="badge b-pend">—</span>}</td></>}
                      <td><button className="btn btn-s" style={{padding:"5px 10px",fontSize:12}} onClick={()=>{setEId(v.id);setEd({...v,tabela_banco:v.tabela_banco||v.produto||""})}}>{I.edit}</button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {editId&&(
        <div className="overlay" onClick={()=>setEId(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-hdr">
              <span style={{fontWeight:800,fontSize:18}}>Editar Proposta #{editId}</span>
              <button className="modal-close" onClick={()=>setEId(null)}>×</button>
            </div>
            <div className="fg"><label>Cliente</label><input className="fi" value={ed.cliente||""} onChange={e=>setEd(p=>({...p,cliente:e.target.value}))}/></div>
            <div className="fr">
              <div className="fg"><label>CPF</label><input className="fi" value={ed.cpf||""} onChange={e=>setEd(p=>({...p,cpf:e.target.value}))}/></div>
              <div className="fg"><label>Telefone</label><input className="fi" value={ed.telefone||""} onChange={e=>setEd(p=>({...p,telefone:e.target.value}))}/></div>
            </div>
            <div className="fg"><label>Tabela/Banco</label>
              <select className="fs" value={ed.tabela_banco||""} onChange={e=>setEd(p=>({...p,tabela_banco:e.target.value}))}>
                {tabelas.map(t=><option key={t}>{t}</option>)}
              </select>
            </div>
            <div className="fr">
              <div className="fg"><label>Valor</label><input className="fi" value={ed.valor||""} onChange={e=>setEd(p=>({...p,valor:e.target.value}))}/></div>
              <div className="fg"><label>Status</label>
                <select className="fs" value={ed.status||"Pendente"} onChange={e=>setEd(p=>({...p,status:e.target.value}))}>
                  {["Pendente","Aguardando","Pago","Cancelado"].map(s=><option key={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div className="fg"><label>Observação</label><textarea className="fta" value={ed.observacao||""} onChange={e=>setEd(p=>({...p,observacao:e.target.value}))}/></div>
            {user.tipo==="admin"&&<>
              <div className="fg"><label>Obs. Admin</label><textarea className="fta" value={ed.observacao_admin||""} onChange={e=>setEd(p=>({...p,observacao_admin:e.target.value}))}/></div>
              <div className="fg"><label className="check-row"><input type="checkbox" checked={!!ed.conferido} onChange={e=>setEd(p=>({...p,conferido:e.target.checked}))}/><span>Conferido</span></label></div>
            </>}
            {user.tipo!=="admin"&&<div className="fg"><label>Motivo da alteração</label><textarea className="fta" value={ed.observacao_alteracao||""} onChange={e=>setEd(p=>({...p,observacao_alteracao:e.target.value}))}/></div>}
            <div style={{display:"flex",gap:10,marginTop:8}}>
              <button className="btn btn-p" onClick={salvarEdit}>{I.check} Salvar</button>
              <button className="btn btn-s" onClick={()=>setEId(null)}>{I.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────
   USUÁRIOS
───────────────────────────────────────────── */
function Usuarios() {
  const [lista,setL]=useState([]); const [loading,setLd]=useState(true);
  const [form,setF]=useState({nome:"",usuario:"",senha:"",tipo:"vendedor"});
  const [editId,setEId]=useState(null); const [ed,setEd]=useState({});
  const [novaSenha,setNS]=useState(""); const [msg,setM]=useState(null);

  async function load(){setLd(true);try{setL(await api("usuarios?select=*&order=id"))}catch{}setLd(false)}
  useEffect(()=>{load()},[]);

  async function criar(){
    if(!form.nome||!form.usuario||!form.senha){setM({t:"err",m:"Preencha nome, usuário e senha."});return}
    try{
      const h=await hashSenha(form.senha);
      await api("usuarios",{method:"POST",prefer:"return=minimal",body:JSON.stringify({nome:form.nome.trim(),usuario:form.usuario.trim().toLowerCase(),senha_hash:h,tipo:form.tipo,ativo:true})});
      setM({t:"ok",m:"Usuário criado!"}); setF({nome:"",usuario:"",senha:"",tipo:"vendedor"}); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  async function salvarEdit(){
    try{
      await api(`usuarios?id=eq.${editId}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify({nome:ed.nome?.trim(),usuario:ed.usuario?.trim().toLowerCase(),tipo:ed.tipo})});
      if(novaSenha){const h=await hashSenha(novaSenha);await api(`usuarios?id=eq.${editId}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify({senha_hash:h})})}
      setM({t:"ok",m:"Usuário atualizado!"}); setEId(null); setNS(""); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  async function toggle(u){
    if(u.usuario==="admin"){setM({t:"err",m:"Não é permitido desativar o admin principal."});return}
    await api(`usuarios?id=eq.${u.id}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify({ativo:!u.ativo})}); load();
  }

  async function excluir(u){
    if(u.usuario==="admin"){setM({t:"err",m:"Não é permitido excluir o admin principal."});return}
    if(!confirm(`Excluir ${u.nome}?`)) return;
    await api(`usuarios?id=eq.${u.id}`,{method:"DELETE",prefer:"return=minimal"}); load();
  }

  return (
    <div>
      {msg&&<Alert type={msg.t}>{msg.m}</Alert>}
      <div className="card">
        <div className="card-hdr"><div className="card-icon">{I.plus}</div><div className="card-title">Criar Usuário</div></div>
        <div className="fr">
          <div className="fg"><label>Nome</label><input className="fi" value={form.nome} onChange={e=>setF(p=>({...p,nome:e.target.value}))}/></div>
          <div className="fg"><label>Login</label><input className="fi" value={form.usuario} onChange={e=>setF(p=>({...p,usuario:e.target.value}))}/></div>
        </div>
        <div className="fr">
          <div className="fg"><label>Senha</label><input className="fi" type="password" value={form.senha} onChange={e=>setF(p=>({...p,senha:e.target.value}))}/></div>
          <div className="fg"><label>Tipo</label>
            <select className="fs" value={form.tipo} onChange={e=>setF(p=>({...p,tipo:e.target.value}))}>
              <option value="vendedor">Vendedor</option><option value="admin">Admin</option>
            </select>
          </div>
        </div>
        <button className="btn btn-p" onClick={criar}>{I.plus} Criar</button>
      </div>

      {loading?<div className="spinner"/>:(
        <div className="card">
          <div className="card-hdr"><div className="card-icon">{I.users}</div><div className="card-title">Usuários</div></div>
          <div className="tw"><table>
            <thead><tr><th>ID</th><th>Nome</th><th>Login</th><th>Tipo</th><th>Status</th><th>Ações</th></tr></thead>
            <tbody>{lista.map(u=>(
              <tr key={u.id}>
                <td>#{u.id}</td><td className="td-p">{u.nome}</td><td>{u.usuario}</td>
                <td><span className={`badge ${u.tipo==="admin"?"b-adm":"b-vend"}`}>{u.tipo}</span></td>
                <td>{u.ativo?<span className="badge b-ok">Ativo</span>:<span className="badge b-bad">Inativo</span>}</td>
                <td style={{display:"flex",gap:6}}>
                  <button className="btn btn-s" style={{padding:"5px 10px",fontSize:12}} onClick={()=>{setEId(u.id);setEd({...u});setNS("")}}>{I.edit}</button>
                  <button className="btn btn-s" style={{padding:"5px 10px",fontSize:12}} onClick={()=>toggle(u)}>{u.ativo?I.x:I.check}</button>
                  <button className="btn btn-d" style={{padding:"5px 10px",fontSize:12}} onClick={()=>excluir(u)}>{I.trash}</button>
                </td>
              </tr>
            ))}</tbody>
          </table></div>
        </div>
      )}

      {editId&&(
        <div className="overlay" onClick={()=>setEId(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-hdr"><span style={{fontWeight:800,fontSize:18}}>Editar Usuário</span><button className="modal-close" onClick={()=>setEId(null)}>×</button></div>
            <div className="fg"><label>Nome</label><input className="fi" value={ed.nome||""} onChange={e=>setEd(p=>({...p,nome:e.target.value}))}/></div>
            <div className="fg"><label>Login</label><input className="fi" value={ed.usuario||""} onChange={e=>setEd(p=>({...p,usuario:e.target.value}))}/></div>
            <div className="fg"><label>Tipo</label>
              <select className="fs" value={ed.tipo||"vendedor"} onChange={e=>setEd(p=>({...p,tipo:e.target.value}))}>
                <option value="vendedor">Vendedor</option><option value="admin">Admin</option>
              </select>
            </div>
            <div className="fg"><label>Nova Senha (deixe vazio para não alterar)</label><input className="fi" type="password" value={novaSenha} onChange={e=>setNS(e.target.value)}/></div>
            <div style={{display:"flex",gap:10}}>
              <button className="btn btn-p" onClick={salvarEdit}>{I.check} Salvar</button>
              <button className="btn btn-s" onClick={()=>setEId(null)}>{I.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────
   COMISSÕES
───────────────────────────────────────────── */
function Comissoes() {
  const [regras,setR]=useState([]); const [loading,setL]=useState(true);
  const [form,setF]=useState({produto:"",valor_minimo:"",percentual_empresa:""});
  const [editId,setEId]=useState(null); const [ed,setEd]=useState({});
  const [msg,setM]=useState(null);

  async function load(){setL(true);try{setR(await api("regras_comissao?select=*&order=produto.asc,valor_minimo.asc"))}catch{}setL(false)}
  useEffect(()=>{load()},[]);

  async function criar(){
    if(!form.produto){setM({t:"err",m:"Informe a tabela/banco."});return}
    try{
      await api("regras_comissao",{method:"POST",prefer:"return=minimal",body:JSON.stringify({produto:form.produto.trim().toUpperCase(),valor_minimo:parseFloat(form.valor_minimo)||0,percentual_empresa:parseFloat(form.percentual_empresa)||0,percentual_vendedor:0,ativo:true})});
      setM({t:"ok",m:"Regra criada!"}); setF({produto:"",valor_minimo:"",percentual_empresa:""}); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  async function salvarEdit(){
    try{
      await api(`regras_comissao?id=eq.${editId}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify({produto:ed.produto?.trim().toUpperCase(),valor_minimo:parseFloat(ed.valor_minimo)||0,percentual_empresa:parseFloat(ed.percentual_empresa)||0,percentual_vendedor:0,ativo:ed.ativo})});
      setM({t:"ok",m:"Regra atualizada!"}); setEId(null); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  async function excluir(id){
    if(!confirm("Excluir esta regra?")) return;
    await api(`regras_comissao?id=eq.${id}`,{method:"DELETE",prefer:"return=minimal"}); load();
  }

  return (
    <div>
      {msg&&<Alert type={msg.t}>{msg.m}</Alert>}
      <div className="card">
        <div className="card-hdr"><div className="card-icon">{I.coin}</div><div className="card-title">Nova Regra de Comissão</div></div>
        <div className="fr">
          <div className="fg"><label>Tabela/Banco</label><input className="fi" value={form.produto} onChange={e=>setF(p=>({...p,produto:e.target.value}))}/></div>
          <div className="fg"><label>Valor Mínimo (R$)</label><input className="fi" type="number" value={form.valor_minimo} onChange={e=>setF(p=>({...p,valor_minimo:e.target.value}))}/></div>
        </div>
        <div className="fg" style={{maxWidth:240}}><label>% Empresa</label><input className="fi" type="number" step="0.01" value={form.percentual_empresa} onChange={e=>setF(p=>({...p,percentual_empresa:e.target.value}))}/></div>
        <button className="btn btn-p" onClick={criar}>{I.plus} Criar Regra</button>
      </div>

      {loading?<div className="spinner"/>:(
        <div className="card">
          <div className="card-hdr"><div className="card-icon">{I.bank}</div><div className="card-title">Regras Cadastradas</div></div>
          {regras.length===0?<div className="empty">{I.coin}<p>Nenhuma regra cadastrada.</p></div>:(
            <div className="tw"><table>
              <thead><tr><th>ID</th><th>Tabela/Banco</th><th>Valor Mínimo</th><th>% Empresa</th><th>Ativo</th><th>Ações</th></tr></thead>
              <tbody>{regras.map(r=>(
                <tr key={r.id}>
                  <td>#{r.id}</td><td className="td-p">{r.produto}</td>
                  <td>{dinheiro(r.valor_minimo)}</td><td>{r.percentual_empresa}%</td>
                  <td>{r.ativo?<span className="badge b-ok">Ativo</span>:<span className="badge b-bad">Inativo</span>}</td>
                  <td style={{display:"flex",gap:6}}>
                    <button className="btn btn-s" style={{padding:"5px 10px",fontSize:12}} onClick={()=>{setEId(r.id);setEd({...r})}}>{I.edit}</button>
                    <button className="btn btn-d" style={{padding:"5px 10px",fontSize:12}} onClick={()=>excluir(r.id)}>{I.trash}</button>
                  </td>
                </tr>
              ))}</tbody>
            </table></div>
          )}
        </div>
      )}

      {editId&&(
        <div className="overlay" onClick={()=>setEId(null)}>
          <div className="modal" onClick={e=>e.stopPropagation()}>
            <div className="modal-hdr"><span style={{fontWeight:800,fontSize:18}}>Editar Regra #{editId}</span><button className="modal-close" onClick={()=>setEId(null)}>×</button></div>
            <div className="fg"><label>Tabela/Banco</label><input className="fi" value={ed.produto||""} onChange={e=>setEd(p=>({...p,produto:e.target.value}))}/></div>
            <div className="fr">
              <div className="fg"><label>Valor Mínimo</label><input className="fi" type="number" value={ed.valor_minimo||""} onChange={e=>setEd(p=>({...p,valor_minimo:e.target.value}))}/></div>
              <div className="fg"><label>% Empresa</label><input className="fi" type="number" step="0.01" value={ed.percentual_empresa||""} onChange={e=>setEd(p=>({...p,percentual_empresa:e.target.value}))}/></div>
            </div>
            <div className="fg"><label className="check-row"><input type="checkbox" checked={!!ed.ativo} onChange={e=>setEd(p=>({...p,ativo:e.target.checked}))}/><span>Ativo</span></label></div>
            <div style={{display:"flex",gap:10}}>
              <button className="btn btn-p" onClick={salvarEdit}>{I.check} Salvar</button>
              <button className="btn btn-s" onClick={()=>setEId(null)}>{I.x} Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─────────────────────────────────────────────
   CHAT
───────────────────────────────────────────── */
function Chat({user}) {
  const [users,setU]=useState([]); const [dest,setD]=useState(null);
  const [msgs,setMs]=useState([]); const [txt,setTxt]=useState("");
  const [naoLidas,setNL]=useState(0); const ref=useRef(null);
  const lido=useRef(new Date().toISOString());

  useEffect(()=>{
    api(`usuarios?select=id,nome,usuario,tipo,ativo&ativo=eq.true&order=nome`)
      .then(d=>setU(d.filter(u=>u.id!==user.id))).catch(()=>{});
  },[]);

  useEffect(()=>{
    if(!dest) return;
    const load=async()=>{
      try{
        const all=await api("chat_interno?select=*&order=criado_em.desc&limit=300");
        const f=all.filter(m=>{
          const o=parseInt(m.usuario_id); const d2=parseInt(m.destinatario_id);
          return(o===user.id&&d2===dest)||(o===dest&&d2===user.id);
        }).slice(-80).reverse();
        setMs(f); setTimeout(()=>{if(ref.current)ref.current.scrollTop=ref.current.scrollHeight},50);
      }catch{}
    };
    load();
    const iv=setInterval(load,5000);
    return()=>clearInterval(iv);
  },[dest]);

  useEffect(()=>{
    const iv=setInterval(async()=>{
      try{
        const r=await api(`chat_interno?select=criado_em&destinatario_id=eq.${user.id}`);
        setNL(r.filter(m=>new Date(m.criado_em)>new Date(lido.current)).length);
      }catch{}
    },8000);
    return()=>clearInterval(iv);
  },[]);

  async function enviar(){
    if(!txt.trim()||!dest) return;
    try{
      await api("chat_interno",{method:"POST",prefer:"return=minimal",body:JSON.stringify({usuario_id:user.id,destinatario_id:dest,nome:user.nome,tipo:user.tipo,mensagem:txt.trim(),criado_em:new Date().toISOString()})});
      setTxt(""); lido.current=new Date().toISOString();
    }catch{}
  }

  return (
    <div className="chat-layout">
      <div className="chat-users">
        <div style={{fontSize:12,fontWeight:700,color:"var(--text3)",textTransform:"uppercase",letterSpacing:".07em",margin:"4px 4px 10px"}}>Conversas</div>
        {users.length===0&&<div style={{fontSize:13,color:"var(--text3)",padding:8}}>Nenhum usuário.</div>}
        {users.map(u=>(
          <div key={u.id} className={`chat-ui ${dest===u.id?"act":""}`} onClick={()=>setD(u.id)}>
            <div className="chat-av">{iniciais(u.nome)}</div>
            <div><div style={{fontSize:13,fontWeight:700,color:"var(--text)"}}>{u.nome}</div><div style={{fontSize:11,color:"var(--text3)"}}>{u.tipo}</div></div>
          </div>
        ))}
      </div>
      <div className="chat-main">
        {!dest?(
          <div className="empty" style={{margin:"auto"}}>{I.chat}<p>Selecione um usuário para conversar</p></div>
        ):(
          <>
            <div style={{padding:"12px 20px",borderBottom:"1px solid var(--border)",display:"flex",alignItems:"center",gap:10}}>
              <div className="chat-av">{iniciais(users.find(u=>u.id===dest)?.nome||"")}</div>
              <span style={{fontWeight:700,color:"var(--text)"}}>{users.find(u=>u.id===dest)?.nome}</span>
            </div>
            <div className="chat-msgs" ref={ref}>
              {msgs.map((m,i)=>{
                const mine=parseInt(m.usuario_id)===user.id;
                return(
                  <div key={i} className={`msg ${mine?"mine":"theirs"}`}>
                    {!mine&&<div className="msg-name">{m.nome}</div>}
                    <div>{m.mensagem}</div>
                    <div className="msg-time" style={{textAlign:mine?"right":"left"}}>
                      {m.criado_em?new Date(m.criado_em).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"}):""}
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="chat-inp">
              <input className="fi" style={{flex:1}} placeholder="Digite sua mensagem..." value={txt}
                onChange={e=>setTxt(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enviar()}/>
              <button className="btn btn-p" onClick={enviar}>{I.send}</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────
   APP ROOT
───────────────────────────────────────────── */
export default function App() {
  const [user,setUser]=useState(null);
  const [menu,setMenu]=useState("Nova Venda");
  const [chatOpen,setChat]=useState(false);
  const [naoLidas,setNL]=useState(0);
  const lido=useRef(new Date().toISOString());

  useEffect(()=>{
    if(!user) return;
    const iv=setInterval(async()=>{
      try{
        const r=await api(`chat_interno?select=criado_em&destinatario_id=eq.${user.id}`);
        setNL(r.filter(m=>new Date(m.criado_em)>new Date(lido.current)).length);
      }catch{}
    },10000);
    return()=>clearInterval(iv);
  },[user]);

  if(!user) return <><style>{G}</style><Login onLogin={setUser}/></>;

  const isAdmin=user.tipo==="admin";

  const navOp=[
    {id:"Nova Venda",label:"Nova Venda",icon:I.sale},
    {id:"Painel",label:"Painel",icon:I.panel},
  ];
  const navGest=isAdmin?[
    {id:"Usuarios",label:"Usuários",icon:I.users},
    {id:"Comissoes",label:"Comissões",icon:I.coin},
  ]:[];

  function goMenu(id){setMenu(id);setChat(false)}

  function renderPage(){
    if(chatOpen) return <Chat user={user}/>;
    switch(menu){
      case "Nova Venda": return <NovaVenda user={user}/>;
      case "Painel":     return <Painel user={user}/>;
      case "Usuarios":   return isAdmin?<Usuarios/>:null;
      case "Comissoes":  return isAdmin?<Comissoes/>:null;
      default:           return null;
    }
  }

  return (
    <>
      <style>{G}</style>
      <div className="layout">

        {/* ── SIDEBAR ── */}
        <aside className="sidebar">
          <div className="sb-logo">
            <div className="sb-logo-icon">🌀</div>
            <div>
              <div className="sb-logo-title">OPERAX</div>
              <div className="sb-logo-sub">SALES</div>
            </div>
          </div>

          <div className="sb-user">
            <div className="sb-avatar">{iniciais(user.nome)}</div>
            <div>
              <div className="sb-uname">{user.nome}</div>
              <div className="sb-urole">{user.tipo}</div>
            </div>
            <div className="sb-dot"/>
          </div>

          <div className="sb-section">Operação</div>
          {navOp.map(n=>(
            <div key={n.id} className={`sb-item ${menu===n.id&&!chatOpen?"active":""}`} onClick={()=>goMenu(n.id)}>
              {n.icon}{n.label}
            </div>
          ))}

          {navGest.length>0&&<>
            <div className="sb-section">Gestão</div>
            {navGest.map(n=>(
              <div key={n.id} className={`sb-item ${menu===n.id&&!chatOpen?"active":""}`} onClick={()=>goMenu(n.id)}>
                {n.icon}{n.label}
              </div>
            ))}
          </>}

          <div className="sb-footer">
            <div className="sb-item" style={{color:"rgba(239,68,68,0.85)"}} onClick={()=>setUser(null)}>
              {I.logout}Sair
            </div>
          </div>
        </aside>

        {/* ── MAIN ── */}
        <div className="main">

          {/* HERO TOPBAR */}
          <header className="topbar">
            <div className="topbar-inner">
              <div className="topbar-brand">
                <div className="topbar-icon">🌀</div>
                <div>
                  <div className="topbar-title">OPERAX <span>SALES</span></div>
                  <div className="topbar-sub">Sistema inteligente de vendas e operações financeiras</div>
                  <div className="topbar-pill">⚡ Painel inteligente • Atualização por ação • Controle por vendedor</div>
                </div>
              </div>
              <div className="topbar-right">
                <button className="chat-btn" onClick={()=>setChat(v=>!v)}>
                  {I.chat} Chat {naoLidas>0&&<span className="chat-badge">{naoLidas}</span>}
                </button>
              </div>
            </div>
          </header>

          {/* PAGE CONTENT */}
          {chatOpen?(
            <Chat user={user}/>
          ):(
            <div className="content">{renderPage()}</div>
          )}
        </div>
      </div>
    </>
  );
}
