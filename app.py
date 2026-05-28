import streamlit as st
import pandas as pd
import requests as _req
from supabase import create_client
from datetime import datetime
import hashlib
import re
from pathlib import Path

st.set_page_config(page_title="OPERAX SALES", layout="wide", page_icon="🌀")

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAILWAY_URL = "https://operax-whatsapp-production.up.railway.app"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f0f6ff !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px !important;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(14,165,233,0.22), transparent 35%),
        linear-gradient(180deg, #020c1e 0%, #031228 50%, #020b1a 100%) !important;
    border-right: 1px solid rgba(56,189,248,0.25) !important;
    min-width: 245px !important;
    max-width: 245px !important;
    box-shadow: 4px 0 40px rgba(14,165,233,0.18) !important;
}

section[data-testid="stSidebar"] > div {
    padding-left: 16px !important;
    padding-right: 16px !important;
    padding-top: 18px !important;
}

[data-testid="stSidebar"] * {
    color: #e2f4ff !important;
}

[data-testid="stSidebar"] .stButton button {
    color: #b8e3f8 !important;
    background: transparent !important;
    border: 0 !important;
    border-radius: 14px !important;
    box-shadow: none !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 700 !important;
    padding: 0.65rem 0.75rem !important;
    transition: all .18s ease-in-out;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(56,189,248,0.12) !important;
    transform: translateX(2px);
    color: #ffffff !important;
}

.sidebar-logo-icon-v8 {
    width: 52px;
    height: 52px;
    border-radius: 18px;
    background: radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 25px;
    font-weight: 900;
    color: #ffffff;
    box-shadow: 0 0 34px rgba(56,189,248,0.58), inset 0 0 0 1px rgba(255,255,255,0.22);
}

.sidebar-user-v8 {
    background: rgba(14,165,233,0.08);
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 16px;
    padding: 13px 14px;
    margin: 8px 0 20px 0;
    color: white !important;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sidebar-dot {
    width: 9px;
    height: 9px;
    background: #22c55e;
    border-radius: 50%;
    box-shadow: 0 0 8px #22c55e;
    flex-shrink: 0;
}

.menu-label-v8 {
    color: rgba(56,189,248,0.80) !important;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    margin: 18px 0 8px 6px;
}

.menu-ativo-v8 {
    background: linear-gradient(90deg, rgba(37,99,235,0.90), rgba(14,165,233,0.85)) !important;
    color: #ffffff !important;
    border-radius: 14px;
    border: 1px solid rgba(56,189,248,0.30) !important;
    padding: 13px 14px;
    margin: 5px 0;
    font-weight: 700;
    box-shadow: 0 0 22px rgba(56,189,248,0.40), inset 0 0 0 1px rgba(255,255,255,0.15);
    display: flex;
    align-items: center;
    gap: 12px;
    overflow: hidden;
    min-height: 50px;
}

.menu-ativo-v8 span {
    color: #ffffff !important;
    font-size: 15px;
    background: transparent !important;
}

.menu-ativo-v8 svg, .menu-svg-v8 svg {
    width: 20px;
    height: 20px;
    stroke-width: 2.2;
    flex-shrink: 0;
    stroke: #ffffff !important;
    background: transparent !important;
}

.menu-svg-v8 {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 42px;
    color: #38bdf8 !important;
    opacity: 0.95;
}

.menu-ativo-v8 pre, .menu-ativo-v8 code, .menu-ativo-v8 p { display: none !important; }
.menu-ativo-v8 * { background: transparent !important; box-shadow: none !important; }

.crm-hero {
    background: linear-gradient(135deg, rgba(3,18,45,0.97), rgba(4,22,55,0.95));
    border: 1px solid rgba(56,189,248,0.25);
    border-radius: 22px;
    padding: 22px 28px;
    margin-bottom: 26px;
    box-shadow: 0 0 0 1px rgba(56,189,248,0.08), 0 0 40px rgba(14,165,233,0.15), 0 16px 48px rgba(0,0,0,0.40);
    position: relative;
    overflow: hidden;
}

.crm-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%);
    pointer-events: none;
}

.crm-title {
    font-size: 36px;
    line-height: 1.02;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900;
    color: #ffffff !important;
    margin: 0;
    letter-spacing: 0.07em;
}

.crm-title span { color: #38bdf8 !important; }

.crm-subtitle {
    margin: 8px 0 0 0;
    color: #ffffff !important;
    font-size: 14px;
    font-weight: 500;
    opacity: 0.85;
}

.crm-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    margin-top: 12px;
    padding: 8px 14px;
    border-radius: 999px;
    background: linear-gradient(90deg, #2563eb, #0ea5e9);
    color: #ffffff !important;
    border: 1px solid rgba(14,165,233,0.22);
    font-weight: 700;
    font-size: 13px;
    box-shadow: 0 0 16px rgba(14,165,233,0.30);
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #ffffff !important;
    border: 1.5px solid rgba(56,189,248,0.45) !important;
    border-radius: 12px !important;
    color: #0f172a !important;
    box-shadow: 0 0 0 0px rgba(14,165,233,0.10);
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #0ea5e9 !important;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.18) !important;
}

div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {
    color: #94a3b8 !important;
}

div[data-baseweb="select"] {
    background: #ffffff !important;
    border: 1.5px solid rgba(56,189,248,0.45) !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] * {
    background: #ffffff !important;
    color: #0f172a !important;
}

[data-testid="stTextInput"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextArea"] label,
[data-testid="stSelectbox"] label,
.stCheckbox label {
    color: #0ea5e9 !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

.stButton button {
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important;
    border: 1px solid rgba(56,189,248,0.50) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.35), 0 8px 24px rgba(14,165,233,0.20) !important;
    transition: all 0.2s !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, #2563eb, #38bdf8) !important;
    box-shadow: 0 0 28px rgba(56,189,248,0.55), 0 12px 32px rgba(14,165,233,0.30) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1.5px solid rgba(14,165,233,0.45) !important;
    border-radius: 16px !important;
    padding: 18px 20px !important;
    box-shadow: 0 0 14px rgba(14,165,233,0.12), 0 4px 16px rgba(0,0,0,0.06) !important;
}

div[data-testid="stMetric"] label {
    color: #0ea5e9 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800 !important;
    font-size: 24px !important;
}

.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1.5px solid rgba(14,165,233,0.35) !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.10) !important;
}

h1, h2, h3 { color: #0f172a !important; letter-spacing: -0.02em; }

.stSuccess > div {
    background: #f0fdf4 !important;
    border: 1.5px solid #86efac !important;
    border-radius: 12px !important;
    color: #166534 !important;
}

.stError > div {
    background: #fef2f2 !important;
    border: 1.5px solid #fca5a5 !important;
    border-radius: 12px !important;
    color: #991b1b !important;
}

.stWarning > div {
    background: #fffbeb !important;
    border: 1.5px solid #fde68a !important;
    border-radius: 12px !important;
    color: #92400e !important;
}

.stInfo > div {
    background: #eff6ff !important;
    border: 1.5px solid rgba(14,165,233,0.50) !important;
    border-radius: 12px !important;
    color: #1d4ed8 !important;
}

div[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1.5px solid rgba(14,165,233,0.30) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.08) !important;
}

hr { border-color: rgba(14,165,233,0.25) !important; }

.stApp h2 {
    font-family: 'Orbitron', sans-serif !important;
    color: #ffffff !important;
    border-bottom: 2px solid rgba(14,165,233,0.45);
    padding-bottom: 8px;
}

.stApp p, .stApp span, .stApp div { color: #0f172a; }
.stCaption, small { color: #0369a1 !important; opacity: 1; }
header { background: transparent !important; }
.stForm [data-testid="InputInstructions"] { display: none !important; }
small[data-testid="InputInstructions"] { display: none !important; }
[data-testid="InputInstructions"] { display: none !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: rgba(2,12,30,0.5); }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.25); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

def achar_logo():
    nomes = ["logo_operax.png","logo_operax(1).png","logo_operax (1).png","logo.png"]
    for nome in nomes:
        caminho = Path(nome)
        if caminho.exists() and caminho.stat().st_size > 100:
            return caminho
    return None

def mostrar_cabecalho():
    st.markdown(
        """
        <div class="crm-hero">
            <div style="display:flex;align-items:center;gap:22px;">
                <div class="sidebar-logo-icon-v8" style="width:68px;height:68px;font-size:34px;border-radius:50%;flex-shrink:0;">🌀</div>
                <div>
                    <h1 class="crm-title">OPERAX <span>SALES</span></h1>
                    <p class="crm-subtitle">Sistema inteligente de vendas e operações financeiras</p>
                    <div class="crm-pill">⚡ Painel inteligente • Atualização por ação • Controle por vendedor</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def hash_senha(senha):
    return hashlib.sha256(str(senha).encode()).hexdigest()

def dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except Exception:
        return "R$ 0,00"

def limpar_documento(valor):
    return re.sub(r"\D","",str(valor or ""))

def validar_cpf(cpf):
    cpf_limpo = limpar_documento(cpf)
    if len(cpf_limpo) != 11: return False
    if cpf_limpo == cpf_limpo[0]*11: return False
    soma = sum(int(cpf_limpo[i])*(10-i) for i in range(9))
    d1 = (soma*10)%11
    if d1==10: d1=0
    soma = sum(int(cpf_limpo[i])*(11-i) for i in range(10))
    d2 = (soma*10)%11
    if d2==10: d2=0
    return d1==int(cpf_limpo[9]) and d2==int(cpf_limpo[10])

def validar_telefone(telefone):
    t = limpar_documento(telefone)
    if len(t) not in [10,11]: return False
    ddd = t[:2]
    numero = t[2:]
    if ddd=="00": return False
    if len(t)==11 and not numero.startswith("9"): return False
    return True

def converter_valor_brasileiro(valor):
    texto = str(valor or "").strip()
    if not texto: return 0.0
    texto = texto.replace("R$","").replace(" ","")
    if "," in texto:
        texto = texto.replace(".","").replace(",",".")
    try:
        return float(texto)
    except Exception:
        return 0.0

def formatar_valor_para_tela(valor):
    numero = converter_valor_brasileiro(valor)
    if numero==0: return ""
    return f"{numero:,.2f}".replace(",","X").replace(".",",").replace("X",".")

def login(usuario, senha):
    usuario = str(usuario).strip().lower()
    senha_hash = hash_senha(str(senha).strip())
    res = supabase.table("usuarios").select("*").eq("usuario",usuario).eq("ativo",True).execute()
    if not res.data: return None
    user = res.data[0]
    if user.get("senha_hash") == senha_hash: return user
    return None

def carregar_tabelas():
    res = supabase.table("regras_comissao").select("*").eq("ativo",True).execute()
    tabelas = sorted(list(set([r.get("produto") for r in res.data if r.get("produto")])))
    if not tabelas:
        tabelas = ["CLT PADRAO","V8 ACIMA 36X","PRESENÇA","HUBBIE","OUTROS BANCOS"]
    return tabelas

def calcular_comissao_montante(df_filtrado):
    total_empresa = 0
    if df_filtrado.empty: return 0
    if "status" not in df_filtrado.columns or "tabela_banco" not in df_filtrado.columns: return 0
    df_pagas = df_filtrado[df_filtrado["status"]=="Pago"].copy()
    if df_pagas.empty: return 0
    for tabela in df_pagas["tabela_banco"].dropna().unique():
        total_tabela = df_pagas[df_pagas["tabela_banco"]==tabela]["valor"].fillna(0).sum()
        regras = supabase.table("regras_comissao").select("*").eq("produto",tabela).eq("ativo",True).order("valor_minimo",desc=True).execute()
        percentual = 0
        for regra in regras.data:
            valor_minimo = float(regra.get("valor_minimo") or 0)
            if float(total_tabela) >= valor_minimo:
                percentual = float(regra.get("percentual_empresa") or 0)
                break
        total_empresa += float(total_tabela)*(percentual/100)
    return total_empresa

def calcular_percentual_empresa_venda(tabela_banco, valor):
    regras = supabase.table("regras_comissao").select("*").eq("produto",tabela_banco).eq("ativo",True).order("valor_minimo",desc=True).execute()
    percentual = 0
    for regra in regras.data:
        valor_minimo = float(regra.get("valor_minimo") or 0)
        if float(valor) >= valor_minimo:
            percentual = float(regra.get("percentual_empresa") or 0)
            break
    return percentual

def preparar_dataframe_vendas():
    vendas = supabase.table("vendas").select("*").order("id",desc=True).execute()
    df = pd.DataFrame(vendas.data)
    if df.empty: return df
    for col in ["data","vendedor_id","tabela_banco","valor","status","conferido","alterado_vendedor"]:
        if col not in df.columns:
            if col=="tabela_banco" and "produto" in df.columns:
                df["tabela_banco"] = df["produto"]
            elif col=="valor":
                df[col] = 0
            elif col=="status":
                df[col] = "Pendente"
            elif col in ["conferido","alterado_vendedor"]:
                df[col] = False
            else:
                df[col] = None
    df["data"] = pd.to_datetime(df["data"],errors="coerce")
    df["mes_num"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    return df

def destacar_linhas_pendentes(row, tipo_usuario):
    try:
        status = str(row.get("status","")).strip().lower()
        data_venda = row.get("data",None)
        if status not in ["pendente","aguardando pagamento","aguardando assinatura"]:
            return [""]*len(row)
        agora = pd.Timestamp.now()
        if pd.notna(data_venda):
            data_venda = pd.to_datetime(data_venda,errors="coerce")
            horas_pendente = (agora-data_venda).total_seconds()/3600
        else:
            horas_pendente = 0
        if status=="aguardando pagamento": return ["background-color: #dbeafe"]*len(row)
        if status=="aguardando assinatura": return ["background-color: #ede9fe"]*len(row)
        if tipo_usuario=="admin" and horas_pendente>=1: return ["background-color: #ffb3b3"]*len(row)
        return ["background-color: #fff3b0"]*len(row)
    except Exception:
        return [""]*len(row)

def carregar_usuarios_chat():
    try:
        res = supabase.table("usuarios").select("id,nome,usuario,tipo,ativo").eq("ativo",True).order("nome").execute()
        usuarios = res.data or []
        return [u for u in usuarios if int(u.get("id")) != int(st.session_state.user_id)]
    except Exception:
        return []

def carregar_mensagens_chat(destinatario_id, limite=80):
    try:
        meu_id = int(st.session_state.user_id)
        outro_id = int(destinatario_id)
        res = supabase.table("chat_interno").select("*").order("criado_em",desc=True).limit(300).execute()
        todas = res.data or []
        mensagens = []
        for msg in todas:
            origem = msg.get("usuario_id")
            destino = msg.get("destinatario_id")
            try:
                origem = int(origem) if origem is not None else None
                destino = int(destino) if destino is not None else None
            except Exception:
                origem = None; destino = None
            if ((origem==meu_id and destino==outro_id) or (origem==outro_id and destino==meu_id)):
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
        res = supabase.table("chat_interno").select("*").eq("destinatario_id",st.session_state.user_id).execute()
        mensagens = res.data or []
        ultima_leitura = pd.to_datetime(st.session_state.chat_lido_em,errors="coerce")
        total = 0
        for msg in mensagens:
            data_msg = pd.to_datetime(msg.get("criado_em"),errors="coerce")
            if pd.notna(data_msg) and pd.notna(ultima_leitura):
                if data_msg > ultima_leitura: total += 1
        return total
    except Exception:
        return 0

def mostrar_chat_popup():
    nao_lidas = contar_mensagens_nao_lidas()
    col_spacer, col_chat = st.columns([8,1.8])
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
        opcoes = {f"{u.get('nome',u.get('usuario'))} ({u.get('tipo','')})": u for u in usuarios_chat}
        escolhido_label = st.selectbox("Enviar mensagem para", list(opcoes.keys()))
        usuario_destino = opcoes[escolhido_label]
        destinatario_id = int(usuario_destino["id"])
        mensagens = carregar_mensagens_chat(destinatario_id, 80)
        chat_area = st.container(height=360)
        with chat_area:
            if not mensagens:
                st.info("Nenhuma mensagem nessa conversa ainda.")
            else:
                for msg in mensagens:
                    nome_msg = msg.get("nome","Usuário")
                    texto_msg = msg.get("mensagem","")
                    data_msg = str(msg.get("criado_em",""))[:16]
                    if int(msg.get("usuario_id")) == int(st.session_state.user_id):
                        st.markdown(f'''<div style="background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:1px solid #86efac;border-radius:16px;padding:10px 12px;margin:8px 0 8px auto;max-width:88%;text-align:right;"><div style="font-size:12px;color:#166534;font-weight:700;">Você • {data_msg}</div><div style="font-size:15px;color:#111827;">{texto_msg}</div></div>''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''<div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:10px 12px;margin:8px auto 8px 0;max-width:88%;"><div style="font-size:12px;color:#64748b;font-weight:700;">{nome_msg} • {data_msg}</div><div style="font-size:15px;color:#111827;">{texto_msg}</div></div>''', unsafe_allow_html=True)
        with st.form("form_chat_popup", clear_on_submit=True):
            mensagem = st.text_input("Mensagem", placeholder=f"Mensagem para {usuario_destino.get('nome','usuário')}...")
            enviar = st.form_submit_button("Enviar")
            if enviar:
                if not mensagem.strip():
                    st.error("Digite uma mensagem antes de enviar.")
                else:
                    enviar_mensagem_chat(st.session_state.user_id, destinatario_id, st.session_state.nome, st.session_state.tipo, mensagem.strip())
                    st.rerun()


def icone_svg(nome):
    icones = {
        "nova": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 3h7l4 4v14H7V3Z"/><path d="M14 3v5h5"/><path d="M9 14h6"/><path d="M12 11v6"/></svg>""",
        "painel": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 19V5"/><path d="M4 19h16"/><path d="M8 16v-5"/><path d="M12 16V8"/><path d="M16 16v-7"/><path d="M20 16v-3"/></svg>""",
        "usuarios": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
        "comissoes": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/><path d="M19 9l2-2-2-2"/><path d="M5 15l-2 2 2 2"/></svg>""",
        "ranking": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M6 9H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h2"/><path d="M18 9h2a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-2"/><path d="M6 3h12v10a6 6 0 0 1-12 0V3z"/><path d="M12 19v3"/><path d="M8 22h8"/></svg>""",
        "metas": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
        "custos": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 9h18M3 15h18M9 3v18M15 3v18M3 3h18v18H3z"/></svg>""",
        "chat_wp": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>""",
    }
    return icones.get(nome,"")


def menu_lateral_v8():
    if "menu_atual" not in st.session_state:
        st.session_state.menu_atual = "📋 Nova Venda"

    if st.session_state.tipo == "admin":
        opcoes = [
            ("📋 Nova Venda", "nova", "Operação"),
            ("📊 Painel", "painel", "Operação"),
            ("🏆 Ranking", "ranking", "Operação"),
            ("🎯 Metas", "metas", "Operação"),
            ("💬 WhatsApp", "chat_wp", "Operação"),
            ("👥 Usuários", "usuarios", "Gestão"),
            ("💰 Comissões", "comissoes", "Gestão"),
            ("🏢 Custos", "custos", "Gestão"),
        ]
    else:
        opcoes = [
            ("📋 Nova Venda", "nova", "Operação"),
            ("📊 Painel", "painel", "Operação"),
            ("🏆 Ranking", "ranking", "Operação"),
            ("🎯 Metas", "metas", "Operação"),
            ("💬 WhatsApp", "chat_wp", "Operação"),
        ]

    logo_path = achar_logo()
    if logo_path:
        try:
            st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:16px 8px 20px;gap:8px;">""", unsafe_allow_html=True)
            st.sidebar.image(str(logo_path), width=180)
            st.sidebar.markdown("""<div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin:4px auto 0;"></div></div>""", unsafe_allow_html=True)
        except Exception:
            st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;"><div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div><div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;text-shadow:0 0 18px rgba(56,189,248,0.65);">OPERAX</div><div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;text-shadow:0 0 10px rgba(56,189,248,0.50);">SALES</div><div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin-top:6px;"></div></div>""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;"><div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div><div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;text-shadow:0 0 18px rgba(56,189,248,0.65);">OPERAX</div><div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;text-shadow:0 0 10px rgba(56,189,248,0.50);">SALES</div><div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin-top:6px;"></div></div>""", unsafe_allow_html=True)

    st.sidebar.markdown(f'''<div class="sidebar-user-v8">{st.session_state.nome}</div>''', unsafe_allow_html=True)

    grupo_atual = None
    for nome, icone_nome, grupo in opcoes:
        nome_limpo = (nome.replace("📋 ","").replace("📊 ","").replace("👥 ","")
                      .replace("💰 ","").replace("🏆 ","").replace("🎯 ","")
                      .replace("🏢 ","").replace("💬 ",""))
        if grupo != grupo_atual:
            st.sidebar.markdown(f'''<div class="menu-label-v8">{grupo}</div>''', unsafe_allow_html=True)
            grupo_atual = grupo
        svg = icone_svg(icone_nome)
        if st.session_state.menu_atual == nome:
            st.sidebar.markdown(f'''<div class="menu-ativo-v8"><div class="menu-icon-wrap">{svg}</div><span class="menu-label-text">{nome_limpo}</span></div>''', unsafe_allow_html=True)
        else:
            col_icon, col_btn = st.sidebar.columns([0.23,0.77])
            with col_icon:
                st.markdown(f'''<div class="menu-svg-v8">{svg}</div>''', unsafe_allow_html=True)
            with col_btn:
                if st.button(nome_limpo, key=f"menu_{nome}", use_container_width=True):
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

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("""<style>
    .stApp {
        background:
            radial-gradient(ellipse at 20% 30%, rgba(14,165,233,0.13) 0%, transparent 45%),
            radial-gradient(ellipse at 80% 70%, rgba(37,99,235,0.10) 0%, transparent 40%),
            linear-gradient(160deg, #020b18 0%, #030f22 50%, #020b18 100%) !important;
    }
    [data-testid="stSidebar"] { display:none !important; }
    header[data-testid="stHeader"] { display:none !important; }
    .block-container {
        max-width: 420px !important; margin: 0 auto !important;
        padding: 40px 36px 36px !important;
        margin-top: calc(50vh - 320px) !important;
        background: rgba(7,18,48,0.96) !important;
        border: 1px solid rgba(56,189,248,0.28) !important;
        border-radius: 24px !important;
        box-shadow: 0 0 0 1px rgba(56,189,248,0.07), 0 0 60px rgba(14,165,233,0.18), 0 28px 80px rgba(0,0,0,0.85) !important;
    }
    .l-icon { width:88px;height:88px;border-radius:20px;margin:0 auto 18px auto;background:radial-gradient(circle at 38% 35%,#bfdbfe 0%,#3b82f6 28%,#1d4ed8 56%,#030a1a 88%);display:flex;align-items:center;justify-content:center;font-size:44px;box-shadow:0 0 0 2px rgba(56,189,248,0.45),0 0 28px rgba(56,189,248,0.85),0 0 55px rgba(14,165,233,0.45); }
    .l-title { font-family:Orbitron,sans-serif;font-size:24px;font-weight:900;letter-spacing:0.06em;color:#ffffff !important;margin-bottom:6px;text-align:center; }
    .l-title b { color:#38bdf8 !important; }
    .l-sub { color:#ffffff !important;font-size:13px;opacity:0.85;margin-bottom:28px;text-align:center;letter-spacing:0.01em; }
    div[data-testid="stTextInput"] input { background:rgba(5,14,40,0.98) !important;border:1.5px solid rgba(14,165,233,0.60) !important;border-radius:11px !important;color:#e2f4ff !important;font-size:15px !important;box-shadow:0 0 8px rgba(14,165,233,0.10) !important; }
    div[data-testid="stTextInput"] input::placeholder { color:rgba(125,211,252,0.28) !important; }
    div[data-testid="stTextInput"] input:focus { border-color:#0ea5e9 !important;box-shadow:0 0 0 3px rgba(14,165,233,0.22),0 0 18px rgba(14,165,233,0.22) !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stTextInput"] label p { color:#38bdf8 !important;font-size:11px !important;font-weight:700 !important;letter-spacing:0.14em !important;text-transform:uppercase !important; }
    .stButton > button { background:linear-gradient(90deg,#1848cc,#0ea5e9) !important;border:none !important;border-radius:12px !important;color:#fff !important;font-size:16px !important;font-weight:700 !important;height:52px !important;margin-top:6px !important;box-shadow:0 0 26px rgba(14,165,233,0.55),0 8px 22px rgba(14,165,233,0.30) !important;letter-spacing:0.04em !important; }
    .stButton > button:hover { box-shadow:0 0 40px rgba(56,189,248,0.75),0 10px 30px rgba(14,165,233,0.42) !important;transform:translateY(-1px) !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="l-icon">🌀</div>', unsafe_allow_html=True)
    st.markdown('<div class="l-title">OPERAX <b>SALES</b></div>', unsafe_allow_html=True)
    st.markdown('<div class="l-sub">Sistema inteligente de vendas e operações financeiras</div>', unsafe_allow_html=True)

    usuario = st.text_input("Usuário", placeholder="Seu login", key="login_user")
    senha   = st.text_input("Senha", type="password", placeholder="••••••••", key="login_pass")

    if st.button("⚡  Entrar", use_container_width=True, key="btn_entrar"):
        user = login(usuario, senha)
        if user:
            st.session_state.logado  = True
            st.session_state.user_id = user["id"]
            st.session_state.usuario = user["usuario"]
            st.session_state.nome    = user["nome"]
            st.session_state.tipo    = user["tipo"]
            st.rerun()
        else:
            st.markdown('<div style="background:#fee2e2;border:1.5px solid #ef4444;border-radius:10px;padding:10px 14px;color:#991b1b;font-weight:700;font-size:14px;margin-top:8px;">❌ Usuário ou senha inválidos</div>', unsafe_allow_html=True)


else:
    mostrar_cabecalho()
    menu = menu_lateral_v8()
    mostrar_chat_popup()

    if st.session_state.tipo != "admin":
        st.markdown("""<style>
        header[data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        </style>""", unsafe_allow_html=True)

    if "mostrar_comissao_empresa" not in st.session_state:
        st.session_state.mostrar_comissao_empresa = True
    if "msg_sucesso" not in st.session_state:
        st.session_state.msg_sucesso = ""
    if "form_count" not in st.session_state:
        st.session_state.form_count = 0


    if menu == "📋 Nova Venda":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;letter-spacing:0.04em;">Cadastro de Venda</span>
        </div>
        """, unsafe_allow_html=True)

        tabelas = carregar_tabelas()

        if st.session_state.get("msg_sucesso"):
            st.markdown(f"""
            <div style="background:rgba(34,197,94,0.12);border:1.5px solid rgba(34,197,94,0.45);border-radius:12px;padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;gap:10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                <span style="color:#4ade80;font-weight:700;font-size:14px;">{st.session_state.msg_sucesso}</span>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.msg_sucesso = ""

        fc = st.session_state.form_count
        cliente = st.text_input("Cliente", key=f"novo_cliente_{fc}")

        cpf_digitado = st.text_input("CPF", placeholder="Ex: 999.999.999-99", key=f"novo_cpf_{fc}")
        cpf = limpar_documento(cpf_digitado)
        if cpf_digitado:
            if len(cpf)<11: st.error(f"CPF incompleto: faltam {11-len(cpf)} número(s).")
            elif len(cpf)>11: st.error(f"CPF com números a mais: remova {len(cpf)-11} número(s).")
            elif validar_cpf(cpf): st.success(f"CPF válido: {cpf}")
            else: st.error("CPF inválido.")

        telefone_digitado = st.text_input("Telefone", placeholder="Ex: (11) 99976-7867", key=f"novo_telefone_{fc}")
        telefone = limpar_documento(telefone_digitado)
        if telefone_digitado:
            if len(telefone)<10: st.error("Telefone incompleto.")
            elif len(telefone)>11: st.error(f"Telefone com números a mais: remova {len(telefone)-11} número(s).")
            elif validar_telefone(telefone): st.success(f"Telefone válido: {telefone}")
            else: st.error("Telefone inválido.")

        tabela_banco = st.selectbox("Tabela/Banco", tabelas)
        valor_digitado = st.text_input("Valor vendido", placeholder="Ex: R$ 1.758,71", key=f"novo_valor_{fc}")
        valor = converter_valor_brasileiro(valor_digitado)
        if valor_digitado:
            if valor>0: st.success(f"Valor válido: {dinheiro(valor)}")
            else: st.error("Valor inválido.")

        status = st.selectbox("Status", ["Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"])
        observacao = st.text_area("Observação", key=f"nova_observacao_{fc}")

        if st.button("💾 Salvar Venda", use_container_width=True):
            if not validar_cpf(cpf):
                st.error("Corrija o CPF.")
            elif not validar_telefone(telefone):
                st.error("Corrija o telefone.")
            elif valor<=0:
                st.error("Corrija o valor.")
            else:
                perc_empresa = calcular_percentual_empresa_venda(tabela_banco, valor)
                valor_empresa = float(valor)*(perc_empresa/100)
                dados = {
                    "data": str(datetime.now()),
                    "vendedor_id": st.session_state.user_id,
                    "vendedor": st.session_state.usuario,
                    "cliente": cliente, "cpf": cpf, "telefone": telefone,
                    "produto": tabela_banco, "tabela_banco": tabela_banco,
                    "valor": valor, "status": status,
                    "percentual_comissao": 0, "valor_comissao": 0,
                    "comissao_empresa": perc_empresa, "valor_comissao_empresa": valor_empresa,
                    "conferido": False, "alterado_vendedor": False, "observacao": observacao
                }
                supabase.table("vendas").insert(dados).execute()
                st.session_state.msg_sucesso = "✅ Venda cadastrada com sucesso!"
                st.session_state.form_count += 1
                st.rerun()

    elif menu == "📊 Painel":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            </div>
            <span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;letter-spacing:0.04em;">Painel de Vendas</span>
        </div>
        """, unsafe_allow_html=True)
        df = preparar_dataframe_vendas()
        if df.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            meses = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
            col_f1,col_f2,col_f3,col_f4 = st.columns(4)
            mes_nome = col_f1.selectbox("Mês", list(meses.values()), index=datetime.now().month-1)
            anos = sorted(df["ano"].dropna().unique().astype(int).tolist(), reverse=True)
            if not anos: anos = [datetime.now().year]
            ano_filtro = col_f2.selectbox("Ano", anos)
            dias = ["Todos"]+list(range(1,32))
            dia_filtro = col_f3.selectbox("Dia", dias)
            status_filtro = col_f4.selectbox("Status", ["Todos","Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"])
            tabelas = carregar_tabelas()
            tabela_filtro = st.selectbox("Tabela/Banco", ["Todas"]+tabelas)
            mes_num = [k for k,v in meses.items() if v==mes_nome][0]
            df = df[(df["mes_num"]==mes_num)&(df["ano"]==ano_filtro)]
            if dia_filtro != "Todos": df = df[df["data"].dt.day==int(dia_filtro)]
            if st.session_state.tipo != "admin": df = df[df["vendedor_id"]==st.session_state.user_id]
            if status_filtro != "Todos": df = df[df["status"]==status_filtro]
            if tabela_filtro != "Todas": df = df[df["tabela_banco"]==tabela_filtro]
            if st.session_state.tipo == "admin":
                vendedores = sorted(df["vendedor"].dropna().unique().tolist())
                vendedor_filtro = st.selectbox("Vendedor", ["Todos"]+vendedores)
                if vendedor_filtro != "Todos": df = df[df["vendedor"]==vendedor_filtro]
            total_vendido = df["valor"].fillna(0).sum()
            qtd = len(df)
            total_pago = df[df["status"]=="Pago"]["valor"].fillna(0).sum()
            total_pendente = df[df["status"].isin(["Pendente","Aguardando Pagamento","Aguardando Assinatura"])]["valor"].fillna(0).sum()
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(34,197,94,0.18),rgba(16,185,129,0.12));border:2px solid rgba(34,197,94,0.55);border-radius:18px;padding:22px 28px;margin-bottom:14px;box-shadow:0 0 24px rgba(34,197,94,0.20);">
                <div style="font-size:11px;font-weight:700;color:#22c55e;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;">✅ Total Pago</div>
                <div style="font-size:34px;font-weight:900;color:#0f172a;letter-spacing:-0.02em;">{dinheiro(total_pago)}</div>
            </div>
            """, unsafe_allow_html=True)
            col1,col2,col3 = st.columns(3)
            col1.metric("💵 Total Vendido", dinheiro(total_vendido))
            col2.metric("⏳ Total Pendente", dinheiro(total_pendente))
            col3.metric("📋 Contratos", qtd)
            col4,col5 = st.columns(2)
            col4.metric("🗓️ Mês", mes_nome)
            col5.metric("📅 Dia", str(dia_filtro) if dia_filtro!="Todos" else "Todos")
            if st.session_state.tipo == "admin":
                total_empresa = calcular_comissao_montante(df)
                col_l,col_b = st.columns([4,1])
                with col_b:
                    if st.button("👁️" if st.session_state.mostrar_comissao_empresa else "🙈", key="btn_ocultar"):
                        st.session_state.mostrar_comissao_empresa = not st.session_state.mostrar_comissao_empresa
                        st.rerun()
                valor_tela = dinheiro(total_empresa) if st.session_state.mostrar_comissao_empresa else "R$ •••••"
                st.metric("🏦 Comissão empresa", valor_tela)
                alteradas = df[df["alterado_vendedor"]==True]
                if not alteradas.empty:
                    st.warning(f"⚠️ Existem {len(alteradas)} proposta(s) alterada(s) pelo vendedor.")
            st.divider()
            if df.empty:
                st.info("Nenhuma proposta encontrada.")
            else:
                if st.session_state.tipo=="admin":
                    colunas = ["id","data","vendedor","cliente","cpf","telefone","tabela_banco","valor","status","conferido","alterado_vendedor","observacao","observacao_admin","observacao_alteracao"]
                else:
                    colunas = ["id","data","cliente","telefone","tabela_banco","valor","status","conferido","observacao"]
                colunas = [c for c in colunas if c in df.columns]
                df_visao = df[colunas].copy()
                if "valor" in df_visao.columns: df_visao["valor"] = df_visao["valor"].apply(dinheiro)
                st.dataframe(df_visao.style.apply(destacar_linhas_pendentes, tipo_usuario=st.session_state.tipo, axis=1), use_container_width=True)
                if st.session_state.tipo=="admin":
                    st.divider()
                    acoes_df = df[["id","cliente","valor","status","conferido","alterado_vendedor"]].copy()
                    acoes_df["excluir"] = False
                    editado = st.data_editor(acoes_df, use_container_width=True, disabled=["id","cliente","valor","status","alterado_vendedor"], hide_index=True)
                    col_a,col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Salvar conferências"):
                            for _,row in editado.iterrows():
                                update = {"conferido": bool(row["conferido"])}
                                if bool(row["conferido"]): update["alterado_vendedor"] = False
                                supabase.table("vendas").update(update).eq("id",int(row["id"])).execute()
                            st.success("Conferências salvas!")
                            st.rerun()
                    with col_b:
                        confirmar = st.checkbox("Confirmo que quero excluir as propostas marcadas")
                        if st.button("🗑️ Excluir marcadas"):
                            if not confirmar: st.error("Marque a confirmação.")
                            else:
                                ids = editado[editado["excluir"]==True]["id"].tolist()
                                if not ids: st.warning("Nenhuma marcada.")
                                else:
                                    for vid in ids: supabase.table("vendas").delete().eq("id",int(vid)).execute()
                                    st.success(f"{len(ids)} excluída(s)!")
                                    st.rerun()
                st.divider()
                proposta_id = st.selectbox("Editar proposta (ID)", df["id"].tolist())
                proposta = df[df["id"]==proposta_id].iloc[0]
                bloqueada = (st.session_state.tipo!="admin" and bool(proposta.get("conferido",False)) is True)
                if bloqueada:
                    st.warning("🔒 Proposta conferida — não pode editar.")
                else:
                    with st.form("editar_proposta"):
                        cliente_edit = st.text_input("Cliente", value=str(proposta.get("cliente","") or ""))
                        cpf_edit = st.text_input("CPF", value=str(proposta.get("cpf","") or ""))
                        telefone_edit = st.text_input("Telefone", value=str(proposta.get("telefone","") or ""))
                        tabelas_edit = carregar_tabelas()
                        tabela_atual = str(proposta.get("tabela_banco","") or proposta.get("produto","") or "")
                        tabela_index = tabelas_edit.index(tabela_atual) if tabela_atual in tabelas_edit else 0
                        tabela_edit = st.selectbox("Tabela/Banco", tabelas_edit, index=tabela_index)
                        valor_edit_texto = st.text_input("Valor", value=dinheiro(proposta.get("valor") or 0).replace("R$ ",""))
                        valor_edit = converter_valor_brasileiro(valor_edit_texto)
                        status_lista = ["Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"]
                        status_atual = str(proposta.get("status","Pendente") or "Pendente")
                        status_index = status_lista.index(status_atual) if status_atual in status_lista else 0
                        status_edit = st.selectbox("Status", status_lista, index=status_index)
                        observacao_edit = st.text_area("Observação", value=str(proposta.get("observacao","") or ""))
                        if st.session_state.tipo=="admin":
                            conferido_edit = st.checkbox("✅ Conferido", value=bool(proposta.get("conferido",False)))
                            obs_admin_edit = st.text_area("Observação admin", value=str(proposta.get("observacao_admin","") or ""))
                        else:
                            obs_alt_edit = st.text_area("Motivo da alteração", placeholder="Ex: corrigi valor...")
                        if st.form_submit_button("Salvar alterações"):
                            cpf_l = limpar_documento(cpf_edit)
                            tel_l = limpar_documento(telefone_edit)
                            if not validar_cpf(cpf_l): st.error("CPF inválido.")
                            elif not validar_telefone(tel_l): st.error("Telefone inválido.")
                            elif valor_edit<=0: st.error("Valor inválido.")
                            else:
                                perc = calcular_percentual_empresa_venda(tabela_edit, valor_edit)
                                dados_update = {"cliente":cliente_edit,"cpf":cpf_l,"telefone":tel_l,"produto":tabela_edit,"tabela_banco":tabela_edit,"valor":valor_edit,"status":status_edit,"observacao":observacao_edit,"comissao_empresa":perc,"valor_comissao_empresa":valor_edit*(perc/100)}
                                if st.session_state.tipo=="admin":
                                    dados_update["conferido"]=conferido_edit
                                    dados_update["alterado_vendedor"]=False
                                    dados_update["observacao_admin"]=obs_admin_edit
                                else:
                                    dados_update["alterado_vendedor"]=True
                                    dados_update["data_alteracao_vendedor"]=str(datetime.now())
                                    dados_update["observacao_alteracao"]=obs_alt_edit
                                    dados_update["conferido"]=False
                                supabase.table("vendas").update(dados_update).eq("id",int(proposta_id)).execute()
                                st.success("Proposta atualizada!")
                                st.rerun()

    elif menu == "🏆 Ranking":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Ranking de Vendas</span>', unsafe_allow_html=True)
        df_rank = preparar_dataframe_vendas()
        if df_rank.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            tipo_filtro = st.radio("Tipo de filtro", ["Mês/Ano","Período personalizado"], horizontal=True, key="rank_tipo_filtro")
            if tipo_filtro == "Mês/Ano":
                meses_r = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
                col_r1,col_r2 = st.columns(2)
                mes_r = col_r1.selectbox("Mês", list(meses_r.values()), index=datetime.now().month-1, key="rank_mes")
                anos_r = sorted(df_rank["ano"].dropna().unique().astype(int).tolist(), reverse=True)
                ano_r = col_r2.selectbox("Ano", anos_r if anos_r else [datetime.now().year], key="rank_ano")
                mes_num_r = [k for k,v in meses_r.items() if v==mes_r][0]
                df_rank = df_rank[(df_rank["mes_num"]==mes_num_r)&(df_rank["ano"]==ano_r)]
            else:
                col_d1,col_d2 = st.columns(2)
                data_ini = col_d1.date_input("Data inicial", value=datetime.now().replace(day=1).date(), key="rank_data_ini")
                data_fim = col_d2.date_input("Data final", value=datetime.now().date(), key="rank_data_fim")
                if data_ini > data_fim: st.error("Data inicial > data final."); st.stop()
                df_rank = df_rank[(df_rank["data"].dt.date>=data_ini)&(df_rank["data"].dt.date<=data_fim)]
            if df_rank.empty:
                st.info("Nenhuma venda neste período.")
            else:
                total_geral = df_rank["valor"].fillna(0).sum()
                total_pago_r = df_rank[df_rank["status"]=="Pago"]["valor"].fillna(0).sum()
                total_pend_r = df_rank[df_rank["status"].isin(["Pendente","Aguardando Pagamento","Aguardando Assinatura"])]["valor"].fillna(0).sum()
                qtd_total = len(df_rank)
                qtd_pago = len(df_rank[df_rank["status"]=="Pago"])
                pct_pago = round((qtd_pago/qtd_total*100),1) if qtd_total>0 else 0
                k1,k2,k3,k4,k5 = st.columns(5)
                k1.metric("💰 Total Geral", dinheiro(total_geral))
                k2.metric("✅ Total Pago", dinheiro(total_pago_r))
                k3.metric("⏳ Total Pendente", dinheiro(total_pend_r))
                k4.metric("📋 Contratos", qtd_total)
                k5.metric("🎯 % Pagos", f"{pct_pago}%")
                grp = df_rank.groupby("vendedor").agg(
                    total_vendido=("valor","sum"),
                    contratos=("id","count"),
                    total_pago=("valor", lambda x: x[df_rank.loc[x.index,"status"]=="Pago"].sum()),
                    contratos_pagos=("status", lambda x: (x=="Pago").sum()),
                ).reset_index()
                grp["pct_pagos"] = (grp["contratos_pagos"]/grp["contratos"]*100).round(1)
                grp["ticket_medio"] = (grp["total_vendido"]/grp["contratos"]).round(2)
                grp = grp.sort_values("total_pago", ascending=False).reset_index(drop=True)
                grp.index += 1
                medalhas = {1:"🥇",2:"🥈",3:"🥉"}
                for i,row in grp.iterrows():
                    medalha = medalhas.get(i,f"#{i}")
                    pct_bar = min(int(row["pct_pagos"]),100)
                    bar_color = "#22c55e" if pct_bar>=70 else "#f59e0b" if pct_bar>=40 else "#ef4444"
                    st.markdown(f"""
                    <div style="background:#ffffff;border:1.5px solid rgba(14,165,233,0.30);border-radius:16px;padding:18px 22px;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                            <div style="display:flex;align-items:center;gap:14px;">
                                <span style="font-size:28px;">{medalha}</span>
                                <div>
                                    <div style="font-size:16px;font-weight:800;color:#0f172a;">{row["vendedor"]}</div>
                                    <div style="font-size:12px;color:#64748b;">Ticket médio: {dinheiro(row["ticket_medio"])}</div>
                                </div>
                            </div>
                            <div style="display:flex;gap:20px;flex-wrap:wrap;">
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#0ea5e9;">TOTAL VENDIDO</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{dinheiro(row["total_vendido"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#22c55e;">TOTAL PAGO</div><div style="font-size:18px;font-weight:800;color:#16a34a;">{dinheiro(row["total_pago"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#6366f1;">CONTRATOS</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{int(row["contratos"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#f59e0b;">% PAGOS</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{row["pct_pagos"]}%</div></div>
                            </div>
                        </div>
                        <div style="margin-top:14px;background:#f1f5f9;border-radius:999px;height:8px;overflow:hidden;">
                            <div style="width:{pct_bar}%;height:100%;background:{bar_color};border-radius:999px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    elif menu == "🎯 Metas":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Metas & Bônus</span>', unsafe_allow_html=True)

        def carregar_metas():
            try:
                res = supabase.table("metas_bonus").select("*").order("ordem").execute()
                if res.data: return res.data
            except Exception: pass
            return [{"ordem":1,"meta_valor":117000,"bonus_valor":300},{"ordem":2,"meta_valor":150000,"bonus_valor":600},{"ordem":3,"meta_valor":200000,"bonus_valor":1000},{"ordem":4,"meta_valor":250000,"bonus_valor":1500}]

        def salvar_metas(metas):
            try:
                supabase.table("metas_bonus").delete().neq("ordem",0).execute()
                for m in metas: supabase.table("metas_bonus").insert(m).execute()
                return True
            except Exception: return False

        metas = carregar_metas()
        if st.session_state.tipo=="admin":
            novas_metas = []
            cols_header = st.columns([1,2,2])
            cols_header[0].markdown("**Nível**"); cols_header[1].markdown("**Meta (R$)**"); cols_header[2].markdown("**Bônus (R$)**")
            for i,m in enumerate(metas):
                col_n,col_m,col_b = st.columns([1,2,2])
                estrelas = "⭐"*(i+1)
                col_n.markdown(f"<div style='padding:8px 0;font-weight:700;font-size:15px;'>{estrelas}</div>",unsafe_allow_html=True)
                meta_v = col_m.number_input(f"meta_{i}",value=float(m["meta_valor"]),min_value=0.0,step=1000.0,label_visibility="collapsed",key=f"meta_val_{i}")
                bonus_v = col_b.number_input(f"bonus_{i}",value=float(m["bonus_valor"]),min_value=0.0,step=100.0,label_visibility="collapsed",key=f"bonus_val_{i}")
                novas_metas.append({"ordem":i+1,"meta_valor":meta_v,"bonus_valor":bonus_v})
            if st.button("💾 Salvar metas",use_container_width=True):
                if salvar_metas(novas_metas): st.success("Metas salvas!"); st.rerun()
                else: st.error("Erro ao salvar.")
            st.divider()

        df_metas = preparar_dataframe_vendas()
        if not df_metas.empty:
            meses_mt = {1:"Janeiro",2:"Fevereiro",3:"Março",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
            col_m1,col_m2 = st.columns(2)
            mes_mt = col_m1.selectbox("Mês",list(meses_mt.values()),index=datetime.now().month-1,key="metas_mes")
            anos_mt = sorted(df_metas["ano"].dropna().unique().astype(int).tolist(),reverse=True)
            ano_mt = col_m2.selectbox("Ano",anos_mt if anos_mt else [datetime.now().year],key="metas_ano")
            mes_num_mt = [k for k,v in meses_mt.items() if v==mes_mt][0]
            df_metas = df_metas[(df_metas["mes_num"]==mes_num_mt)&(df_metas["ano"]==ano_mt)]
            if st.session_state.tipo!="admin": df_metas = df_metas[df_metas["vendedor_id"]==st.session_state.user_id]
            vendedores_mt = df_metas["vendedor"].dropna().unique().tolist() if st.session_state.tipo=="admin" else [st.session_state.usuario]
            for vend in vendedores_mt:
                df_v = df_metas[df_metas["vendedor"]==vend]
                total_pago_v = df_v[df_v["status"]=="Pago"]["valor"].fillna(0).sum()
                total_vend = df_v["valor"].fillna(0).sum()
                bonus_atingido = 0
                proxima_meta = metas[0]["meta_valor"] if metas else 0
                for m in metas:
                    if total_pago_v>=m["meta_valor"]: bonus_atingido=m["bonus_valor"]
                for m in metas:
                    if total_pago_v<m["meta_valor"]: proxima_meta=m["meta_valor"]; break
                pct_prog = min(int((total_pago_v/proxima_meta)*100),100) if proxima_meta>0 else 100
                falta = max(proxima_meta-total_pago_v,0)
                bar_color = "#22c55e" if pct_prog>=80 else "#f59e0b" if pct_prog>=40 else "#0ea5e9"
                iniciais_v = "".join([p[0].upper() for p in vend.split()[:2]])
                st.markdown(f"""
                <div style="background:#ffffff;border:1px solid rgba(14,165,233,0.25);border-radius:18px;padding:20px 24px;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:10px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#1d4ed8,#0ea5e9);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:15px;">{iniciais_v}</div>
                            <div><div style="font-size:16px;font-weight:800;color:#0f172a;">{vend}</div><div style="font-size:12px;color:#64748b;">Pago: {dinheiro(total_pago_v)} | Vendido: {dinheiro(total_vend)}</div></div>
                        </div>
                        {'<div style="background:#dcfce7;border-radius:10px;padding:6px 14px;"><span style="font-size:13px;font-weight:700;color:#16a34a;">+' + dinheiro(bonus_atingido) + ' bônus</span></div>' if bonus_atingido>0 else '<div style="background:#f1f5f9;border-radius:10px;padding:6px 14px;"><span style="font-size:13px;color:#64748b;">Sem bônus ainda</span></div>'}
                    </div>
                    <div style="background:#f1f5f9;border-radius:999px;height:10px;overflow:hidden;margin-bottom:4px;">
                        <div style="width:{pct_prog}%;height:100%;background:{bar_color};border-radius:999px;"></div>
                    </div>
                    <div style="font-size:11px;color:#94a3b8;">{'Meta atingida! 🎉' if falta==0 else f'Faltam {dinheiro(falta)} para a próxima meta'}</div>
                </div>
                """, unsafe_allow_html=True)
                cols_metas = st.columns(len(metas))
                for i,m in enumerate(metas):
                    atingida = total_pago_v>=m["meta_valor"]
                    estrelas_on = "⭐"*(i+1)
                    estrelas_off = "☆"*(i+1)
                    with cols_metas[i]:
                        if atingida:
                            st.markdown(f"""<div style="background:#fefce8;border:2px solid #facc15;border-radius:14px;padding:12px;text-align:center;"><div style="font-size:20px;">{estrelas_on}</div><div style="font-size:11px;font-weight:700;color:#92400e;">Meta {i+1}</div><div style="font-size:12px;color:#64748b;">{dinheiro(m["meta_valor"])}</div><div style="font-size:13px;font-weight:700;color:#16a34a;">+{dinheiro(m["bonus_valor"])} ✓</div></div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div style="background:#f8fafc;border:0.5px solid #e2e8f0;border-radius:14px;padding:12px;text-align:center;opacity:0.65;"><div style="font-size:20px;">{estrelas_off}</div><div style="font-size:11px;font-weight:700;color:#94a3b8;">Meta {i+1}</div><div style="font-size:12px;color:#94a3b8;">{dinheiro(m["meta_valor"])}</div><div style="font-size:12px;color:#94a3b8;">+{dinheiro(m["bonus_valor"])}</div></div>""", unsafe_allow_html=True)

    # =========================
    # WHATSAPP
    # =========================
    elif menu == "💬 WhatsApp":
        RAILWAY = "https://operax-whatsapp-production.up.railway.app"

        # Verifica status
        def wp_status_check():
            try:
                r = _req.get(f"{RAILWAY}/status", timeout=4)
                return r.json() if r.status_code == 200 else {}
            except Exception:
                return {}

        st_wp = wp_status_check()
        conectado = st_wp.get("status") == "connected" or st_wp.get("connected") is True

        st.markdown("""
        <style>
        .wp-page { background: linear-gradient(160deg,#020b18 0%,#030f22 60%,#020b18 100%);
            border-radius:20px; padding:50px 40px; text-align:center;
            border:1px solid rgba(56,189,248,0.20); min-height:400px;
            display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px; }
        .wp-big-logo { font-size:80px; filter:drop-shadow(0 0 28px rgba(56,189,248,0.80)); }
        .wp-big-title { font-family:'Orbitron',sans-serif; font-size:28px; font-weight:900;
            color:#fff; letter-spacing:.08em; }
        .wp-big-title span { color:#38bdf8; }
        .wp-big-sub { color:rgba(148,185,210,0.70); font-size:14px; max-width:480px; line-height:1.7; }
        .wp-open-btn { display:inline-flex; align-items:center; gap:10px;
            background:linear-gradient(135deg,#1d4ed8,#0ea5e9);
            color:#fff; font-size:16px; font-weight:700; padding:16px 36px;
            border-radius:14px; text-decoration:none; letter-spacing:.03em;
            box-shadow:0 0 32px rgba(14,165,233,0.50); transition:.2s; }
        .wp-open-btn:hover { box-shadow:0 0 48px rgba(56,189,248,0.75); }
        .wp-conn-btn { display:inline-flex; align-items:center; gap:8px;
            background:rgba(56,189,248,0.10); color:#7dd3fc; font-size:13px;
            font-weight:700; padding:10px 22px; border-radius:10px;
            text-decoration:none; border:1px solid rgba(56,189,248,0.30); }
        .wp-badge-ok  { display:inline-flex;align-items:center;gap:6px;background:#f0fdf4;
            border:1px solid #86efac;border-radius:8px;padding:5px 14px;
            font-size:13px;font-weight:700;color:#166534; }
        .wp-badge-err { display:inline-flex;align-items:center;gap:6px;background:#fef2f2;
            border:1px solid #fca5a5;border-radius:8px;padding:5px 14px;
            font-size:13px;font-weight:700;color:#991b1b; }
        .dot-g { width:9px;height:9px;background:#22c55e;border-radius:50%;
            box-shadow:0 0 8px #22c55e;display:inline-block; }
        .wp-features { display:flex; gap:14px; flex-wrap:wrap; justify-content:center; margin-top:10px; }
        .wp-feat { background:rgba(56,189,248,0.07); border:1px solid rgba(56,189,248,0.15);
            border-radius:10px; padding:10px 16px; font-size:12px; color:#7dd3fc; font-weight:600; }
        </style>
        """, unsafe_allow_html=True)

        chat_url = f"{RAILWAY}/chat"
        qr_url   = f"{RAILWAY}/qr"

        if conectado:
            badge = '''<span class="wp-badge-ok"><span class="dot-g"></span>WhatsApp conectado ✓</span>'''
            botao_extra = ""
        else:
            badge = '''<span class="wp-badge-err">⚠️ WhatsApp desconectado</span>'''
            botao_extra = f'''<a href="{qr_url}" target="_blank" class="wp-conn-btn">
                🔑 Conectar WhatsApp</a>'''

        st.markdown(f'''
        <div class="wp-page">
            <div class="wp-big-logo">🌀</div>
            <div class="wp-big-title">OPERAX <span>CHAT</span></div>
            <div>{badge}</div>
            <div class="wp-big-sub">
                Chat com seus clientes em tempo real via WhatsApp.<br>
                Propostas vinculadas automaticamente. Edite e sincronize com o Painel de Vendas.
            </div>
            <a href="{chat_url}" target="_blank" class="wp-open-btn">
                💬 Abrir Chat WhatsApp ↗
            </a>
            {botao_extra}
            <div class="wp-features">
                <span class="wp-feat">💬 Chat em tempo real</span>
                <span class="wp-feat">📄 Propostas vinculadas</span>
                <span class="wp-feat">⚡ Respostas rápidas</span>
                <span class="wp-feat">🔄 Sync com Painel</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("🔄 Verificar conexão", key="btn_wp_check"):
            st.rerun()


    elif menu == "💰 Comissões":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Regras de Comissão</span>', unsafe_allow_html=True)
        with st.form("nova_regra"):
            produto = st.text_input("Tabela/Banco")
            valor_minimo = st.number_input("Valor mínimo", min_value=0.0, step=1000.0)
            percentual_empresa = st.number_input("% empresa", min_value=0.0, step=0.01)
            if st.form_submit_button("Salvar regra"):
                if not produto: st.error("Preencha o nome da tabela/banco.")
                else:
                    supabase.table("regras_comissao").insert({"produto":produto.strip().upper(),"valor_minimo":valor_minimo,"percentual_empresa":percentual_empresa,"percentual_vendedor":0,"ativo":True}).execute()
                    st.success("Regra criada!"); st.rerun()
        regras = supabase.table("regras_comissao").select("*").order("produto").order("valor_minimo").execute()
        df_regras = pd.DataFrame(regras.data)
        if df_regras.empty:
            st.warning("Nenhuma regra cadastrada.")
        else:
            st.dataframe(df_regras, use_container_width=True)
            st.divider()
            regra_id = st.selectbox("ID da regra", df_regras["id"].tolist())
            regra = df_regras[df_regras["id"]==regra_id].iloc[0]
            with st.form("editar_regra"):
                produto_edit = st.text_input("Tabela/Banco", value=str(regra.get("produto","") or ""))
                vm_edit = st.number_input("Valor mínimo", min_value=0.0, step=1000.0, value=float(regra.get("valor_minimo") or 0))
                pe_edit = st.number_input("% empresa", min_value=0.0, step=0.01, value=float(regra.get("percentual_empresa") or 0))
                ativo_edit = st.checkbox("Ativo", value=bool(regra.get("ativo",True)))
                if st.form_submit_button("Salvar alterações"):
                    supabase.table("regras_comissao").update({"produto":produto_edit.strip().upper(),"valor_minimo":vm_edit,"percentual_empresa":pe_edit,"percentual_vendedor":0,"ativo":ativo_edit}).eq("id",int(regra_id)).execute()
                    st.success("Regra atualizada!"); st.rerun()
            st.divider()
            confirmar_r = st.checkbox("Confirmo que quero excluir esta regra")
            if st.button("Excluir regra"):
                if not confirmar_r: st.error("Marque a confirmação.")
                else:
                    supabase.table("regras_comissao").delete().eq("id",int(regra_id)).execute()
                    st.success("Regra excluída!"); st.rerun()

    elif menu == "🏢 Custos":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Custos Operacionais</span>', unsafe_allow_html=True)

        def carregar_custos():
            try:
                res = supabase.table("custos_operacionais").select("*").order("categoria").order("id").execute()
                return res.data or []
            except Exception: return []

        def salvar_custo(nome, categoria, valor):
            try:
                supabase.table("custos_operacionais").insert({"nome":nome,"categoria":categoria,"valor":valor,"mes":datetime.now().month,"ano":datetime.now().year}).execute()
                return True
            except Exception: return False

        def excluir_custo(cid):
            try:
                supabase.table("custos_operacionais").delete().eq("id",int(cid)).execute()
                return True
            except Exception: return False

        df_c = preparar_dataframe_vendas()
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        df_c = df_c[(df_c["mes_num"]==mes_atual)&(df_c["ano"]==ano_atual)]
        comissao_mes = df_c[df_c["status"]=="Pago"]["valor_comissao_empresa"].fillna(0).sum()
        if comissao_mes==0:
            comissao_mes = df_c[df_c["status"]=="Pago"]["valor"].fillna(0).sum()*0.038
        custos = carregar_custos()
        total_custos = sum(float(c.get("valor",0)) for c in custos)
        resultado = comissao_mes - total_custos
        taxa_media = 3.8
        vol_necessario = total_custos/(taxa_media/100) if taxa_media>0 else 0
        pct_cobertura = min(int((comissao_mes/total_custos*100)) if total_custos>0 else 0, 100)
        col_k1,col_k2,col_k3,col_k4 = st.columns(4)
        col_k1.metric("💸 Total custos", dinheiro(total_custos))
        col_k2.metric("💰 Comissão atual", dinheiro(comissao_mes))
        col_k3.metric("🎯 Vol. necessário", f"R$ {round(vol_necessario/1000)}k")
        col_k4.metric("📊 Resultado", dinheiro(resultado), delta=f"{pct_cobertura}% coberto")
        bar_color = "#22c55e" if pct_cobertura>=100 else "#0ea5e9" if pct_cobertura>=70 else "#ef4444"
        st.markdown(f"""
        <div style="background:#ffffff;border:1.5px solid rgba(14,165,233,0.25);border-radius:14px;padding:16px 20px;margin:10px 0 20px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:8px;"><span>Cobertura dos custos</span><span style="font-weight:700;color:{'#16a34a' if pct_cobertura>=100 else '#0ea5e9' if pct_cobertura>=70 else '#dc2626'};">{pct_cobertura}%</span></div>
            <div style="background:#f1f5f9;border-radius:999px;height:12px;overflow:hidden;">
                <div style="width:{pct_cobertura}%;height:100%;background:{bar_color};border-radius:999px;"></div>
            </div>
            <div style="font-size:11px;color:#94a3b8;margin-top:5px;">{"Superávit: "+dinheiro(resultado) if resultado>=0 else "Faltam: "+dinheiro(abs(resultado))}</div>
        </div>
        """, unsafe_allow_html=True)
        col_left,col_right = st.columns([1.6,1])
        with col_left:
            with st.form("form_novo_custo", clear_on_submit=True):
                col_n,col_cat,col_v,col_q = st.columns([2,1.5,1,0.8])
                nome_c = col_n.text_input("Descrição", placeholder="Ex: Salário mínimo")
                cat_c = col_cat.selectbox("Categoria", ["Pessoal","DP","Estrutura","Marketing","Outros"])
                val_c = col_v.number_input("Valor (R$)", min_value=0.0, step=100.0)
                qtd_c = col_q.number_input("Qtd", min_value=1, max_value=20, step=1, value=1)
                if st.form_submit_button("➕ Adicionar custo", use_container_width=True):
                    if nome_c and val_c>0:
                        nome_final = f"{nome_c} (x{qtd_c})" if qtd_c>1 else nome_c
                        if salvar_custo(nome_final, cat_c, val_c*qtd_c): st.success(f"Adicionado: {dinheiro(val_c*qtd_c)}"); st.rerun()
                    else: st.error("Preencha descrição e valor.")
            if custos:
                cat_atual = None
                for c in custos:
                    cat = c.get("categoria","Outros")
                    cat_label = "DP — Depart. Pessoal" if cat=="DP" else cat
                    if cat != cat_atual:
                        cat_atual = cat
                        st.markdown(f'<div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.10em;padding:8px 0 4px;">{cat_label}</div>', unsafe_allow_html=True)
                    col_desc,col_val,col_edit,col_del = st.columns([3,1.5,0.4,0.4])
                    col_desc.markdown(f'<div style="padding:8px 0;font-size:14px;color:#0f172a;">{c.get("nome","")}</div>', unsafe_allow_html=True)
                    col_val.markdown(f'<div style="padding:8px 0;font-size:14px;font-weight:700;color:#dc2626;">{dinheiro(c.get("valor",0))}</div>', unsafe_allow_html=True)
                    if col_edit.button("✏️", key=f"edit_custo_{c['id']}"):
                        st.session_state[f"editando_custo_{c['id']}"] = True
                    if col_del.button("✕", key=f"del_custo_{c['id']}"):
                        excluir_custo(c["id"]); st.rerun()
                    if st.session_state.get(f"editando_custo_{c['id']}"):
                        with st.form(f"form_edit_custo_{c['id']}"):
                            ec1,ec2,ec3 = st.columns([2,1.5,1])
                            novo_nome = ec1.text_input("Descrição", value=c.get("nome",""), key=f"en_{c['id']}")
                            nova_cat = ec2.selectbox("Categoria", ["Pessoal","DP","Estrutura","Marketing","Outros"],
                                index=["Pessoal","DP","Estrutura","Marketing","Outros"].index(c.get("categoria","Outros")) if c.get("categoria","Outros") in ["Pessoal","DP","Estrutura","Marketing","Outros"] else 0,
                                key=f"ec_{c['id']}")
                            novo_val = ec3.number_input("Valor", value=float(c.get("valor",0)), step=100.0, key=f"ev_{c['id']}")
                            cs1,cs2 = st.columns(2)
                            if cs1.form_submit_button("💾 Salvar"):
                                try:
                                    supabase.table("custos_operacionais").update({"nome":novo_nome,"categoria":nova_cat,"valor":novo_val}).eq("id",int(c["id"])).execute()
                                    st.session_state[f"editando_custo_{c['id']}"] = False
                                    st.success("Custo atualizado!"); st.rerun()
                                except Exception as e: st.error(f"Erro: {e}")
                            if cs2.form_submit_button("✕ Cancelar"):
                                st.session_state[f"editando_custo_{c['id']}"] = False; st.rerun()
            else:
                st.info("Nenhum custo cadastrado ainda.")
        with col_right:
            if custos:
                cats_total = {}
                for c in custos:
                    cat = c.get("categoria","Outros")
                    cats_total[cat] = cats_total.get(cat,0)+float(c.get("valor",0))
                cores = {"Pessoal":"#0ea5e9","DP":"#6366f1","Estrutura":"#1d9e75","Marketing":"#ba7517","Outros":"#888780"}
                for cat,val in sorted(cats_total.items(), key=lambda x: -x[1]):
                    pct = int((val/total_custos*100)) if total_custos>0 else 0
                    cor = cores.get(cat,"#0ea5e9")
                    st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span style="color:#0f172a;">{cat}</span><span style="color:#64748b;">{dinheiro(val)} ({pct}%)</span></div><div style="background:#f1f5f9;border-radius:999px;height:8px;overflow:hidden;"><div style="width:{pct}%;height:100%;background:{cor};border-radius:999px;"></div></div></div>""", unsafe_allow_html=True)
                st.divider()
                st.markdown(f'<div style="font-size:12px;color:#64748b;">Volume break-even</div><div style="font-size:20px;font-weight:800;color:#0f172a;">{dinheiro(vol_necessario)}</div><div style="font-size:12px;color:#94a3b8;">à taxa {taxa_media}%</div><div style="font-size:12px;color:#64748b;margin-top:8px;">Por vendedora (2)</div><div style="font-size:18px;font-weight:700;color:#0ea5e9;">{dinheiro(vol_necessario/2)}</div>', unsafe_allow_html=True)
            else:
                st.info("Adicione custos para ver a distribuição.")
