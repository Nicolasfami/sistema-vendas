import { useState, useEffect, useRef } from "react";

/* ─── SUPABASE ─── */
const URL  = "https://ynxpowhzhnwqazdxshch.supabase.co";
const KEY  = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt";

async function api(path, opts = {}) {
  const r = await fetch(`${URL}/rest/v1/${path}`, {
    headers: {
      apikey: KEY, Authorization: `Bearer ${KEY}`,
      "Content-Type": "application/json",
      Prefer: opts.prefer || "return=representation",
      ...opts.headers,
    }, ...opts,
  });
  const txt = await r.text();
  if (!r.ok) throw new Error(txt);
  return txt ? JSON.parse(txt) : [];
}

async function hashSenha(s) {
  const buf  = new TextEncoder().encode(String(s));
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return [...new Uint8Array(hash)].map(b => b.toString(16).padStart(2,"0")).join("");
}

/* ─── HELPERS ─── */
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

/* ─── ESTILOS DARK ESPACIAL ─── */
const G = `
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Exo+2:wght@300;400;500;600;700;800;900&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,#root{min-height:100vh;font-family:'Exo 2',sans-serif;background:#020b18}

:root{
  --bg:       #020b18;
  --bg2:      #030f22;
  --bg3:      #03122a;
  --sidebar-top: #020c1e;
  --sidebar-bot: #030f28;
  --blue:     #0ea5e9;
  --blue2:    #2563eb;
  --blue3:    #38bdf8;
  --text:     #e2f4ff;
  --text2:    #7dd3fc;
  --text3:    #334e68;
  --card:     rgba(3,18,45,0.88);
  --border:   rgba(56,189,248,0.18);
  --border2:  rgba(56,189,248,0.32);
  --success:  #22c55e;
  --warn:     #f59e0b;
  --danger:   #ef4444;
  --radius:   14px;
  --radius2:  18px;
}

/* LAYOUT */
.layout{
  display:flex;min-height:100vh;
  background:
    radial-gradient(ellipse at 15% 20%, rgba(14,165,233,0.12) 0%, transparent 40%),
    radial-gradient(ellipse at 85% 80%, rgba(37,99,235,0.10) 0%, transparent 35%),
    linear-gradient(160deg, #020b18 0%, #030f22 50%, #020b18 100%);
}

/* ── SIDEBAR ── */
.sidebar{
  width:255px;min-width:255px;
  background:
    radial-gradient(ellipse at 10% 5%, rgba(14,165,233,0.20) 0%, transparent 35%),
    linear-gradient(180deg, var(--sidebar-top) 0%, #031228 50%, var(--sidebar-bot) 100%);
  border-right:1px solid rgba(56,189,248,0.22);
  box-shadow:4px 0 40px rgba(14,165,233,0.15), inset -1px 0 0 rgba(56,189,248,0.10);
  display:flex;flex-direction:column;overflow:hidden;position:relative;
}
.sidebar *{color:var(--text)}

.sb-logo{
  display:flex;flex-direction:column;align-items:center;
  padding:22px 16px 18px;gap:4px;
}
.sb-logo-title{
  font-family:'Rajdhani',sans-serif;font-size:26px;font-weight:700;
  letter-spacing:0.18em;color:#fff!important;
  text-shadow:0 0 28px rgba(56,189,248,0.65),0 0 50px rgba(14,165,233,0.3);
  line-height:1;
}
.sb-logo-sub{
  font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;
  color:var(--blue3)!important;letter-spacing:0.55em;
  text-shadow:0 0 14px rgba(56,189,248,0.45);margin-top:2px;
}
.sb-logo-divider{width:80%;height:1px;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.35),transparent);margin-top:14px}

.sb-user{
  background:rgba(14,165,233,0.07);
  border:1px solid rgba(56,189,248,0.20);
  border-radius:14px;padding:11px 13px;
  margin:4px 12px 16px;
  display:flex;align-items:center;gap:9px;
}
.sb-avatar{
  width:34px;height:34px;border-radius:50%;flex-shrink:0;
  background:linear-gradient(135deg,#1d4ed8,#0ea5e9);
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:800;color:#fff;
  box-shadow:0 0 12px rgba(14,165,233,0.4);
}
.sb-uname{font-size:13px;font-weight:700;color:#fff!important;line-height:1.2}
.sb-urole{font-size:10px;color:var(--blue3)!important;text-transform:uppercase;letter-spacing:.07em}
.sb-dot{width:8px;height:8px;border-radius:50%;background:#22c55e;box-shadow:0 0 7px #22c55e;margin-left:auto;flex-shrink:0}

.sb-section{
  font-family:'Rajdhani',sans-serif;
  font-size:10px;font-weight:700;
  color:rgba(56,189,248,0.65)!important;
  text-transform:uppercase;letter-spacing:0.20em;
  margin:16px 0 6px 18px;
}

.sb-item{
  display:flex;align-items:center;gap:11px;
  padding:11px 14px;margin:2px 8px;border-radius:12px;
  cursor:pointer;transition:all .18s;
  color:rgba(180,220,255,0.80)!important;
  font-size:14px;font-weight:600;font-family:'Exo 2',sans-serif;
}
.sb-item:hover{background:rgba(56,189,248,0.11);transform:translateX(2px);color:#fff!important}
.sb-item.active{
  background:linear-gradient(90deg,rgba(37,99,235,0.88),rgba(14,165,233,0.80));
  color:#fff!important;
  border:1px solid rgba(56,189,248,0.30);
  box-shadow:0 0 22px rgba(56,189,248,0.30),inset 0 1px 0 rgba(255,255,255,0.12);
}
.sb-item svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:2.2;flex-shrink:0}
.sb-footer{margin-top:auto;border-top:1px solid rgba(56,189,248,0.10);padding:12px 8px}

/* ── MAIN ── */
.main{flex:1;display:flex;flex-direction:column;min-width:0}

/* ── TOPBAR ── */
.topbar{
  padding:18px 26px 16px;
  background:linear-gradient(135deg,rgba(3,18,45,0.96),rgba(4,22,55,0.92));
  border-bottom:1px solid rgba(56,189,248,0.18);
  box-shadow:0 16px 48px rgba(0,0,0,0.35);
  position:relative;overflow:hidden;
}
.topbar::after{
  content:'';position:absolute;top:-50px;right:-50px;
  width:200px;height:200px;
  background:radial-gradient(circle,rgba(14,165,233,0.10) 0%,transparent 70%);
  pointer-events:none;
}
.topbar-inner{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.topbar-brand{display:flex;align-items:center;gap:16px}
.topbar-title{
  font-family:'Rajdhani',sans-serif;font-size:38px;line-height:1;font-weight:700;
  letter-spacing:0.10em;color:#fff;
  text-shadow:0 0 35px rgba(56,189,248,0.45);
}
.topbar-title span{color:var(--blue3);text-shadow:0 0 25px rgba(56,189,248,0.70)}
.topbar-sub{margin-top:5px;color:var(--text2);font-size:13px;font-weight:400;letter-spacing:0.04em;opacity:0.85}
.topbar-pills{display:flex;gap:7px;flex-wrap:wrap;margin-top:10px}
.topbar-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 13px;border-radius:999px;
  background:rgba(14,165,233,0.10);
  color:var(--text2);border:1px solid rgba(56,189,248,0.28);
  font-weight:600;font-size:12px;letter-spacing:0.03em;
  backdrop-filter:blur(8px);
}
.topbar-right{margin-left:auto;display:flex;align-items:center;gap:10px;flex-shrink:0}
.chat-btn{
  display:flex;align-items:center;gap:7px;
  padding:9px 18px;border-radius:12px;cursor:pointer;
  background:linear-gradient(135deg,#1d4ed8,#0ea5e9);
  color:#fff;font-family:'Exo 2',sans-serif;font-size:14px;font-weight:700;
  border:1px solid rgba(56,189,248,0.35);
  box-shadow:0 8px 24px rgba(14,165,233,0.28);transition:all .18s;position:relative;
}
.chat-btn:hover{box-shadow:0 12px 32px rgba(56,189,248,0.45);transform:translateY(-1px)}
.chat-btn svg{width:16px;height:16px;stroke:#fff;fill:none;stroke-width:2.5}
.chat-badge{
  position:absolute;top:-7px;right:-7px;background:#ef4444;
  color:#fff;font-size:10px;font-weight:900;
  width:18px;height:18px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 0 8px rgba(239,68,68,0.6);
}

/* ── CONTENT ── */
.content{flex:1;overflow-y:auto;padding:24px 28px}
.content::-webkit-scrollbar{width:5px}
.content::-webkit-scrollbar-track{background:rgba(2,12,30,0.5)}
.content::-webkit-scrollbar-thumb{background:rgba(56,189,248,0.22);border-radius:3px}

/* ── CARD ── */
.card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius2);padding:22px;margin-bottom:18px;
  box-shadow:0 0 0 1px rgba(56,189,248,0.05),0 16px 48px rgba(0,0,0,0.4);
}
.card-hdr{display:flex;align-items:center;gap:12px;margin-bottom:20px}
.card-icon{
  width:40px;height:40px;border-radius:11px;
  background:linear-gradient(135deg,rgba(37,99,235,0.20),rgba(14,165,233,0.18));
  border:1px solid rgba(56,189,248,0.28);
  display:flex;align-items:center;justify-content:center;
}
.card-icon svg{width:20px;height:20px;stroke:var(--blue3);fill:none;stroke-width:2}
.card-title{font-family:'Rajdhani',sans-serif;font-size:20px;font-weight:700;color:var(--text);letter-spacing:0.05em}

/* ── METRICS ── */
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:12px;margin-bottom:20px}
.metric{
  background:rgba(3,18,45,0.90);
  border:1px solid rgba(56,189,248,0.16);border-radius:16px;padding:16px 18px;
  box-shadow:0 0 0 1px rgba(56,189,248,0.05),0 10px 28px rgba(0,0,0,0.35);
  position:relative;overflow:hidden;
}
.metric::before{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#2563eb,#38bdf8);
}
.metric-lbl{font-size:10px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:0.10em;margin-bottom:7px;opacity:0.75}
.metric-val{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:var(--text);line-height:1;text-shadow:0 0 15px rgba(56,189,248,0.2)}
.metric-val.ok{color:#4ade80}
.metric-val.warn{color:#fbbf24}
.metric-val.bad{color:#f87171}
.metric-val.info{color:var(--blue3)}

/* ── FORM ── */
.fg{margin-bottom:15px}
.fg label{display:block;font-size:11px;font-weight:700;color:var(--text2);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:6px}
.fi,.fs,.fta{
  width:100%;padding:11px 14px;
  background:rgba(2,12,30,0.90);
  border:1px solid rgba(56,189,248,0.20)!important;
  border-radius:12px!important;
  color:var(--text);
  font-family:'Exo 2',sans-serif;font-size:14px;outline:none;
  transition:border-color .16s,box-shadow .16s;appearance:none;
}
.fi:focus,.fs:focus,.fta:focus{
  border-color:rgba(56,189,248,0.55)!important;
  box-shadow:0 0 0 3px rgba(14,165,233,0.13)!important;
}
.fi::placeholder{color:rgba(125,211,252,0.30)}
.fs{
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2338bdf8' stroke-width='2'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 12px center;padding-right:36px;
}
.fs option{background:#03122a;color:var(--text)}
.fta{resize:vertical;min-height:88px}
.fr{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.fe{font-size:12px;color:#f87171;margin-top:4px}
.fs2{font-size:12px;color:#4ade80;margin-top:4px}
.prefix-wrap{display:flex}
.prefix{
  padding:11px 12px;
  background:rgba(14,165,233,0.10);
  border:1px solid rgba(56,189,248,0.20);border-right:none;
  border-radius:12px 0 0 12px;font-size:14px;font-weight:700;
  color:var(--blue3);white-space:nowrap;
}
.prefix-wrap .fi{border-radius:0 12px 12px 0!important}

/* ── BUTTONS ── */
.btn{
  display:inline-flex;align-items:center;gap:7px;
  padding:10px 18px;border-radius:12px;
  font-family:'Exo 2',sans-serif;font-size:14px;font-weight:700;
  cursor:pointer;transition:all .18s;border:none;white-space:nowrap;
}
.btn svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2.5}
.btn-p{
  background:linear-gradient(135deg,#1d4ed8,#0ea5e9);color:#fff;
  border:1px solid rgba(56,189,248,0.35)!important;
  box-shadow:0 8px 22px rgba(14,165,233,0.25);
}
.btn-p:hover{box-shadow:0 12px 30px rgba(56,189,248,0.40);transform:translateY(-1px)}
.btn-s{
  background:rgba(14,165,233,0.10);color:var(--blue3);
  border:1px solid rgba(56,189,248,0.25)!important;
}
.btn-s:hover{background:rgba(14,165,233,0.20)}
.btn-d{
  background:rgba(239,68,68,0.10);color:#f87171;
  border:1px solid rgba(239,68,68,0.28)!important;
}
.btn-d:hover{background:rgba(239,68,68,0.20)}
.btn:disabled{opacity:.45;cursor:not-allowed;transform:none!important}

/* ── ALERTS ── */
.alert{
  display:flex;align-items:center;gap:8px;
  padding:11px 15px;border-radius:12px;
  font-size:13px;font-weight:600;margin-bottom:13px;
}
.alert svg{width:15px;height:15px;stroke:currentColor;fill:none;stroke-width:2.5;flex-shrink:0}
.a-ok{background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.35);color:#4ade80}
.a-err{background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.35);color:#f87171}
.a-info{background:rgba(14,165,233,0.12);border:1px solid rgba(56,189,248,0.30);color:var(--blue3)}

/* ── TABLE ── */
.tw{overflow-x:auto;border-radius:var(--radius);border:1px solid rgba(56,189,248,0.14);box-shadow:0 12px 36px rgba(0,0,0,0.4)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{
  background:rgba(2,12,30,0.95);color:rgba(125,211,252,0.65);
  font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;
  padding:10px 13px;border-bottom:1px solid rgba(56,189,248,0.14);text-align:left;white-space:nowrap;
}
td{padding:10px 13px;border-bottom:1px solid rgba(56,189,248,0.07);color:#b0c8e0;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(14,165,233,0.05)}
.td-p{color:var(--text);font-weight:600}

/* ── BADGES ── */
.badge{display:inline-flex;align-items:center;padding:3px 9px;border-radius:6px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em}
.b-ok{background:rgba(34,197,94,0.14);color:#4ade80;border:1px solid rgba(34,197,94,0.30)}
.b-pend{background:rgba(251,191,36,0.13);color:#fbbf24;border:1px solid rgba(251,191,36,0.28)}
.b-bad{background:rgba(239,68,68,0.12);color:#f87171;border:1px solid rgba(239,68,68,0.28)}
.b-wait{background:rgba(56,189,248,0.12);color:var(--blue3);border:1px solid rgba(56,189,248,0.25)}
.b-adm{background:rgba(167,139,250,0.13);color:#c4b5fd;border:1px solid rgba(167,139,250,0.28)}
.b-vend{background:rgba(34,197,94,0.12);color:#4ade80;border:1px solid rgba(34,197,94,0.28)}

/* ── LOGIN ── */
.login-wrap{
  min-height:100vh;display:flex;align-items:center;justify-content:center;
  background:
    radial-gradient(ellipse at 15% 25%, rgba(14,165,233,0.14) 0%, transparent 40%),
    radial-gradient(ellipse at 85% 75%, rgba(37,99,235,0.10) 0%, transparent 35%),
    linear-gradient(160deg, #020b18 0%, #030f22 50%, #020b18 100%);
}
.login-card{
  background:rgba(3,18,45,0.92);
  border:1px solid rgba(56,189,248,0.22);
  border-radius:24px;padding:40px 36px;width:420px;max-width:95vw;
  box-shadow:0 0 0 1px rgba(56,189,248,0.08),0 28px 80px rgba(0,0,0,0.6),inset 0 1px 0 rgba(56,189,248,0.10);
}
.login-hero{text-align:center;margin-bottom:30px}
.login-icon{
  width:72px;height:72px;border-radius:20px;margin:0 auto 14px;
  background:radial-gradient(circle at 50% 50%,#020617 0%,#020617 32%,#0ea5e9 44%,#2563eb 70%,#38bdf8 100%);
  display:flex;align-items:center;justify-content:center;font-size:36px;
  box-shadow:0 0 36px rgba(14,165,233,0.55);
}
.login-title{
  font-family:'Rajdhani',sans-serif;font-size:32px;font-weight:700;
  color:#fff;letter-spacing:0.08em;
  text-shadow:0 0 30px rgba(56,189,248,0.4);
}
.login-title span{color:var(--blue3)}
.login-sub{font-size:13px;color:var(--text2);margin-top:5px;opacity:0.8}

/* ── MODAL ── */
.overlay{
  position:fixed;inset:0;background:rgba(0,0,0,0.65);
  backdrop-filter:blur(4px);display:flex;align-items:center;
  justify-content:center;z-index:200;padding:16px;
}
.modal{
  background:rgba(3,18,45,0.98);
  border:1px solid rgba(56,189,248,0.25);
  border-radius:20px;padding:26px;width:100%;max-width:560px;max-height:90vh;overflow-y:auto;
  box-shadow:0 0 0 1px rgba(56,189,248,0.08),0 28px 80px rgba(0,0,0,0.7);
}
.modal::-webkit-scrollbar{width:4px}
.modal::-webkit-scrollbar-thumb{background:rgba(56,189,248,0.25);border-radius:2px}
.modal-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.modal-close{
  background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.30);
  color:#f87171;border-radius:8px;padding:5px 10px;cursor:pointer;font-size:18px;line-height:1;transition:.15s;
}
.modal-close:hover{background:rgba(239,68,68,0.22)}

/* ── CHAT ── */
.chat-layout{display:flex;height:calc(100vh - 130px);min-height:400px}
.chat-users{
  width:220px;min-width:220px;border-right:1px solid rgba(56,189,248,0.14);
  overflow-y:auto;background:rgba(2,12,30,0.60);padding:10px;
}
.chat-ui{display:flex;align-items:center;gap:9px;padding:9px 10px;border-radius:11px;cursor:pointer;margin-bottom:3px;transition:.15s}
.chat-ui:hover{background:rgba(14,165,233,0.09)}
.chat-ui.act{background:rgba(14,165,233,0.13);border:1px solid rgba(56,189,248,0.22)}
.chat-av{
  width:32px;height:32px;border-radius:50%;
  background:linear-gradient(135deg,#1d4ed8,#0ea5e9);
  display:flex;align-items:center;justify-content:center;
  color:#fff;font-size:12px;font-weight:800;flex-shrink:0;
}
.chat-main{flex:1;display:flex;flex-direction:column;min-width:0}
.chat-msgs{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:9px}
.chat-msgs::-webkit-scrollbar{width:4px}
.chat-msgs::-webkit-scrollbar-thumb{background:rgba(56,189,248,0.20);border-radius:2px}
.msg{max-width:72%;padding:9px 13px;border-radius:14px;font-size:14px;line-height:1.5}
.msg.mine{
  background:linear-gradient(135deg,rgba(14,165,233,0.16),rgba(37,99,235,0.13));
  border:1px solid rgba(56,189,248,0.26);align-self:flex-end;border-bottom-right-radius:4px;
  color:var(--text);
}
.msg.theirs{
  background:rgba(3,18,45,0.80);border:1px solid rgba(56,189,248,0.14);
  align-self:flex-start;border-bottom-left-radius:4px;color:#b0c8e0;
}
.msg-name{font-size:10px;font-weight:700;color:var(--text2);margin-bottom:3px}
.msg-time{font-size:10px;color:rgba(125,211,252,0.45);margin-top:4px}
.chat-inp{
  padding:12px 18px;border-top:1px solid rgba(56,189,248,0.12);
  display:flex;gap:9px;background:rgba(2,12,30,0.50);
}

/* ── MISC ── */
.spinner{
  width:34px;height:34px;
  border:3px solid rgba(56,189,248,0.15);border-top-color:var(--blue3);
  border-radius:50%;animation:spin .7s linear infinite;margin:40px auto;display:block;
}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:44px 20px;color:rgba(125,211,252,0.40)}
.empty svg{width:44px;height:44px;stroke:rgba(125,211,252,0.30);fill:none;stroke-width:1.5;margin:0 auto 13px;display:block}
.empty p{font-size:14px}
.divider{border:none;border-top:1px solid rgba(56,189,248,0.10);margin:20px 0}
.sec-title{
  font-family:'Rajdhani',sans-serif;
  font-size:16px;font-weight:700;color:var(--text);
  margin-bottom:13px;display:flex;align-items:center;gap:9px;
  letter-spacing:0.04em;
}
.sec-title::before{content:'';display:block;width:3px;height:16px;background:linear-gradient(#2563eb,#38bdf8);border-radius:2px}
.check-row{display:flex;align-items:center;gap:8px;cursor:pointer}
.check-row input{width:15px;height:15px;accent-color:var(--blue3);cursor:pointer}
.check-row span{font-size:14px;color:var(--text2)}
`;

/* ─── ICONS ─── */
const I = {
  sale:   <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>,
  panel:  <svg viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>,
  users:  <svg viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>,
  coin:   <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M9 9h4.5a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3H15"/></svg>,
  logout: <svg viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>,
  chat:   <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>,
  plus:   <svg viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>,
  edit:   <svg viewBox="0 0 24 24"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>,
  trash:  <svg viewBox="0 0 24 24"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>,
  check:  <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>,
  x:      <svg viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>,
  send:   <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  info:   <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>,
  bank:   <svg viewBox="0 0 24 24"><line x1="3" y1="22" x2="21" y2="22"/><line x1="6" y1="18" x2="6" y2="11"/><line x1="10" y1="18" x2="10" y2="11"/><line x1="14" y1="18" x2="14" y2="11"/><line x1="18" y1="18" x2="18" y2="11"/><polygon points="12 2 20 7 4 7"/></svg>,
  ref:    <svg viewBox="0 0 24 24"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15A9 9 0 1 1 5.19 5.19L1 1"/></svg>,
};

function Alert({type="info", children}) {
  const cls = {ok:"a-ok",err:"a-err",info:"a-info"}[type]||"a-info";
  const ico = type==="ok"?I.check:type==="err"?I.x:I.info;
  return <div className={`alert ${cls}`}>{ico}{children}</div>;
}

/* ─── LOGIN ─── */
function Login({onLogin}) {
  const [u,setU]=useState(""); const [s,setS]=useState("");
  const [loading,setL]=useState(false); const [err,setE]=useState("");

  async function enter() {
    if(!u||!s){setE("Preencha usuário e senha.");return}
    setL(true);setE("");
    try {
      const uLow = u.trim().toLowerCase();
      const rows  = await api(`usuarios?select=*&usuario=eq.${encodeURIComponent(uLow)}&ativo=eq.true`);
      if (!rows.length){setE("Usuário não encontrado ou inativo.");setL(false);return}
      const row = rows[0];
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
        <div className="fg">
          <label>Usuário</label>
          <input className="fi" placeholder="Seu login" value={u} onChange={e=>setU(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enter()}/>
        </div>
        <div className="fg">
          <label>Senha</label>
          <input className="fi" type="password" placeholder="••••••••" value={s} onChange={e=>setS(e.target.value)} onKeyDown={e=>e.key==="Enter"&&enter()}/>
        </div>
        <button className="btn btn-p" style={{width:"100%",justifyContent:"center",marginTop:8}} onClick={enter} disabled={loading}>
          {loading?"Entrando...":"⚡  Entrar"}
        </button>
      </div>
    </div>
  );
}

/* ─── NOVA VENDA ─── */
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
    const h2={...hints};
    if(field==="cpf"&&val){
      const c=limpar(val);
      if(c.length<11) h2.cpf={t:"e",m:`CPF incompleto: faltam ${11-c.length} número(s).`};
      else if(c.length>11) h2.cpf={t:"e",m:"CPF com número(s) a mais."};
      else if(validarCPF(c)) h2.cpf={t:"ok",m:"CPF válido ✓"};
      else h2.cpf={t:"e",m:"CPF inválido. Confira os números."};
    } else delete h2.cpf;
    if(field==="tel"&&val){
      const t=limpar(val);
      if(t.length<10) h2.tel={t:"e",m:"Telefone incompleto. Informe DDD + número."};
      else if(t.length>11) h2.tel={t:"e",m:"Telefone com números a mais."};
      else if(validarTel(t)) h2.tel={t:"ok",m:"Telefone válido ✓"};
      else h2.tel={t:"e",m:"Telefone inválido. Use DDD + número."};
    } else delete h2.tel;
    if(field==="valor"&&val){
      const v=converterValor(val);
      if(v>0) h2.valor={t:"ok",m:`Valor: ${dinheiro(v)}`};
      else h2.valor={t:"e",m:"Valor inválido. Ex: R$ 1.758,71"};
    } else delete h2.valor;
    setH(h2);
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
        vendedor_id: user.id, vendedor: user.usuario, vendedor_nome: user.nome,
        cliente: form.cliente, cpf, telefone: tel,
        produto: form.tabela, tabela_banco: form.tabela,
        valor: val, status: form.status, observacao: form.obs,
        comissao_empresa: perc, valor_comissao_empresa: vEmp,
        conferido: false, alterado_vendedor: false,
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

/* ─── PAINEL ─── */
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
    if(old&&user.tipo==="admin") return {background:"rgba(239,68,68,0.06)"};
    return {background:"rgba(251,191,36,0.06)"};
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

      <div style={{display:"flex",gap:10,marginBottom:16,flexWrap:"wrap",alignItems:"flex-end"}}>
        <div className="fg" style={{margin:0}}>
          <select className="fs" style={{width:120}} value={mes} onChange={e=>setMes(+e.target.value)}>
            {meses.map((m,i)=><option key={i} value={i+1}>{m}</option>)}
          </select>
        </div>
        <div className="fg" style={{margin:0}}>
          <select className="fs" style={{width:95}} value={ano} onChange={e=>setAno(+e.target.value)}>
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
                      {user.tipo==="admin"&&<>
                        <td>{v.vendedor_nome||v.vendedor||"—"}</td>
                        <td>{v.conferido?<span className="badge b-ok">✓</span>:<span className="badge b-pend">—</span>}</td>
                      </>}
                      <td>
                        <button className="btn btn-s" style={{padding:"5px 10px",fontSize:12}} onClick={()=>{setEId(v.id);setEd({...v,tabela_banco:v.tabela_banco||v.produto||""})}}>
                          {I.edit}
                        </button>
                      </td>
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
              <span style={{fontWeight:700,fontSize:18,color:"var(--text)",fontFamily:"'Rajdhani',sans-serif",letterSpacing:"0.05em"}}>Editar Proposta #{editId}</span>
              <button className="modal-close" onClick={()=>setEId(null)}>×</button>
            </div>
            <div className="fg"><label>Cliente</label><input className="fi" value={ed.cliente||""} onChange={e=>setEd(p=>({...p,cliente:e.target.value}))}/></div>
            <div className="fr">
              <div className="fg"><label>CPF</label><input className="fi" value={ed.cpf||""} onChange={e=>setEd(p=>({...p,cpf:e.target.value}))}/></div>
              <div className="fg"><label>Telefone</label><input className="fi" value={ed.telefone||""} onChange={e=>setEd(p=>({...p,telefone:e.target.value}))}/></div>
            </div>
            <div className="fg"><label>Tabela/Banco</label>
              <select className="fs" value={ed.tabela_banco||""} onChange={e=>setEd(p=>({...p,tabela_banco:e.target.value}))}>
                {tabelas.map(t=><option key={t} value={t}>{t}</option>)}
              </select>
            </div>
            <div className="fr">
              <div className="fg"><label>Valor</label><input className="fi" value={ed.valor||""} onChange={e=>setEd(p=>({...p,valor:e.target.value}))}/></div>
              <div className="fg"><label>Status</label>
                <select className="fs" value={ed.status||"Pendente"} onChange={e=>setEd(p=>({...p,status:e.target.value}))}>
                  {["Pendente","Pago","Cancelado"].map(s=><option key={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div className="fg"><label>Observação</label><textarea className="fta" value={ed.observacao||""} onChange={e=>setEd(p=>({...p,observacao:e.target.value}))}/></div>
            {user.tipo==="admin"?(
              <>
                <div className="fg"><label className="check-row"><input type="checkbox" checked={!!ed.conferido} onChange={e=>setEd(p=>({...p,conferido:e.target.checked}))}/><span>Conferido</span></label></div>
                <div className="fg"><label>Observação Admin</label><textarea className="fta" value={ed.observacao_admin||""} onChange={e=>setEd(p=>({...p,observacao_admin:e.target.value}))}/></div>
              </>
            ):(
              <div className="fg"><label>Motivo da Alteração</label><textarea className="fta" placeholder="Ex: corrigi valor, telefone ou status..." value={ed.observacao_alteracao||""} onChange={e=>setEd(p=>({...p,observacao_alteracao:e.target.value}))}/></div>
            )}
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

/* ─── USUÁRIOS ─── */
function Usuarios() {
  const [lista,setL]=useState([]); const [loading,setLd]=useState(true);
  const [form,setF]=useState({nome:"",usuario:"",senha:"",tipo:"vendedor"});
  const [editId,setEId]=useState(null); const [ed,setEd]=useState({});
  const [novaSenha,setNS]=useState(""); const [msg,setM]=useState(null);

  async function load(){setLd(true);try{setL(await api("usuarios?select=*&order=id.asc"))}catch{}setLd(false)}
  useEffect(()=>{load()},[]);

  async function criar(){
    if(!form.nome||!form.usuario||!form.senha){setM({t:"err",m:"Preencha nome, usuário e senha."});return}
    try{
      const h=await hashSenha(form.senha.trim());
      await api("usuarios",{method:"POST",prefer:"return=minimal",body:JSON.stringify({nome:form.nome.trim(),usuario:form.usuario.trim().toLowerCase(),senha_hash:h,tipo:form.tipo,ativo:true})});
      setM({t:"ok",m:"Usuário criado!"}); setF({nome:"",usuario:"",senha:"",tipo:"vendedor"}); load();
    }catch(e){setM({t:"err",m:"Erro: "+e.message})}
  }

  async function salvarEdit(){
    try{
      let patch={nome:ed.nome?.trim(),usuario:ed.usuario?.trim().toLowerCase(),tipo:ed.tipo};
      if(novaSenha.trim()) patch.senha_hash=await hashSenha(novaSenha.trim());
      await api(`usuarios?id=eq.${editId}`,{method:"PATCH",prefer:"return=minimal",body:JSON.stringify(patch)});
      setM({t:"ok",m:"Usuário atualizado!"}); setEId(null); load();
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
        <div className="card-hdr"><div className="card-icon">{I.users}</div><div className="card-title">Novo Usuário</div></div>
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
            <div className="modal-hdr"><span style={{fontWeight:700,fontSize:18,color:"var(--text)"}}>Editar Usuário</span><button className="modal-close" onClick={()=>setEId(null)}>×</button></div>
            <div className="fg"><label>Nome</label><input className="fi" value={ed.nome||""} onChange={e=>setEd(p=>({...p,nome:e.target.value}))}/></div>
            <div className="fg"><label>Login</label><input className="fi" value={ed.usuario||""} onChange={e=>setEd(p=>({...p,usuario:e.target.value}))}/></div>
            <div className="fg"><label>Tipo</label>
              <select className="fs" value={ed.tipo||"vendedor"} onChange={e=>setEd(p=>({...p,tipo:e.target.value}))}>
                <option value="vendedor">Vendedor</option><option value="admin">Admin</option>
              </select>
            </div>
            <div className="fg"><label>Nova Senha (vazio = não altera)</label><input className="fi" type="password" value={novaSenha} onChange={e=>setNS(e.target.value)}/></div>
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

/* ─── COMISSÕES ─── */
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
          {regras.length===0?<div className="empty">{I.coin}<p>Nenhuma regra.</p></div>:(
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
            <div className="modal-hdr"><span style={{fontWeight:700,fontSize:18,color:"var(--text)"}}>Editar Regra #{editId}</span><button className="modal-close" onClick={()=>setEId(null)}>×</button></div>
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

/* ─── CHAT ─── */
function Chat({user}) {
  const [users,setU]=useState([]); const [dest,setD]=useState(null);
  const [msgs,setMs]=useState([]); const [txt,setTxt]=useState("");
  const ref=useRef(null); const lido=useRef(new Date().toISOString());

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
        <div style={{fontSize:10,fontWeight:700,color:"var(--text2)",textTransform:"uppercase",letterSpacing:".10em",margin:"4px 4px 10px",opacity:0.7}}>Conversas</div>
        {users.length===0&&<div style={{fontSize:13,color:"var(--text2)",padding:8,opacity:0.5}}>Nenhum usuário.</div>}
        {users.map(u=>(
          <div key={u.id} className={`chat-ui ${dest===u.id?"act":""}`} onClick={()=>setD(u.id)}>
            <div className="chat-av">{iniciais(u.nome)}</div>
            <div><div style={{fontSize:13,fontWeight:700,color:"var(--text)"}}>{u.nome}</div><div style={{fontSize:11,color:"var(--text2)",opacity:0.7}}>{u.tipo}</div></div>
          </div>
        ))}
      </div>
      <div className="chat-main">
        {!dest?(
          <div className="empty" style={{margin:"auto"}}>{I.chat}<p>Selecione um usuário para conversar</p></div>
        ):(
          <>
            <div style={{padding:"11px 18px",borderBottom:"1px solid rgba(56,189,248,0.12)",display:"flex",alignItems:"center",gap:10,background:"rgba(2,12,30,0.50)"}}>
              <div className="chat-av">{iniciais(users.find(u=>u.id===dest)?.nome||"")}</div>
              <span style={{fontWeight:700,color:"var(--text)",fontSize:14}}>{users.find(u=>u.id===dest)?.nome}</span>
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

/* ─── APP ROOT ─── */
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

        {/* SIDEBAR */}
        <aside className="sidebar">
          <div className="sb-logo">
            <div className="sb-logo-title">OPERAX</div>
            <div className="sb-logo-sub">SALES</div>
            <div className="sb-logo-divider"/>
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
            <div className="sb-item" style={{color:"rgba(248,113,113,0.85)"}} onClick={()=>setUser(null)}>
              {I.logout}Sair
            </div>
          </div>
        </aside>

        {/* MAIN */}
        <div className="main">
          <header className="topbar">
            <div className="topbar-inner">
              <div className="topbar-brand">
                <div>
                  <div className="topbar-title">OPERAX <span>SALES</span></div>
                  <div className="topbar-sub">Sistema inteligente de vendas e operações financeiras</div>
                  <div className="topbar-pills">
                    <span className="topbar-pill">⚡ Painel inteligente</span>
                    <span className="topbar-pill">🔄 Atualização por ação</span>
                    <span className="topbar-pill">👤 Controle por vendedor</span>
                  </div>
                </div>
              </div>
              <div className="topbar-right">
                <button className="chat-btn" onClick={()=>setChat(v=>!v)}>
                  {I.chat} Chat {naoLidas>0&&<span className="chat-badge">{naoLidas}</span>}
                </button>
              </div>
            </div>
          </header>

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
