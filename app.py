import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib
import re
from pathlib import Path

# =========================
# CONFIGURACOES
# =========================

st.set_page_config(page_title="OPERAX SALES", layout="wide", page_icon="🌀")

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# DESIGN DARK
# =========================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* FUNDO DARK GERAL */
.stApp {
    background: #f0f6ff !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1180px !important;
}

/* SIDEBAR DARK */
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

.sidebar-logo-v8 {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 4px 22px 4px;
    color: white;
    font-size: 22px;
    font-weight: 900;
    letter-spacing: .02em;
}

.sidebar-logo-v8 img {
    width: 190px !important;
    max-width: 190px !important;
    height: auto !important;
    object-fit: contain !important;
    filter: drop-shadow(0 0 18px rgba(56,189,248,0.60)) !important;
}

.sidebar-logo-title {
    line-height: 1.05;
    font-weight: 900;
    letter-spacing: .08em;
    color: #ffffff !important;
    font-size: 22px;
}

.sidebar-logo-sub {
    font-size: 12px;
    color: #38bdf8 !important;
    letter-spacing: .28em;
    margin-top: 4px;
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

/* HEADER PRINCIPAL DARK */
.crm-hero {
    background: linear-gradient(135deg, #ffffff, #eff6ff);
    border: 1.5px solid rgba(14,165,233,0.40);
    border-radius: 22px;
    padding: 22px 28px;
    margin-bottom: 26px;
    box-shadow: 0 0 22px rgba(14,165,233,0.14), 0 8px 32px rgba(0,0,0,0.06);
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

.crm-hero img {
    width: 220px !important;
    max-width: 220px !important;
    height: auto !important;
    object-fit: contain !important;
    filter: drop-shadow(0 0 22px rgba(56,189,248,0.60)) brightness(1.1) !important;
}

.crm-title {
    font-size: 40px;
    line-height: 1.02;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 800;
    color: #0f172a !important;
    margin: 0;
    letter-spacing: 0.04em;
}

.crm-title span {
    color: #0ea5e9 !important;
}

.crm-subtitle {
    margin: 8px 0 0 0;
    color: #475569 !important;
    font-size: 15px;
    font-weight: 400;
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

/* LOGIN CARD DARK - igual à foto */
.login-dark-wrap {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.login-dark-card {
    background: rgba(3, 15, 35, 0.95);
    border: 1px solid rgba(56,189,248,0.22);
    border-radius: 24px;
    padding: 44px 40px;
    width: 100%;
    max-width: 440px;
    box-shadow:
        0 0 0 1px rgba(56,189,248,0.08),
        0 28px 80px rgba(0,0,0,0.65),
        inset 0 1px 0 rgba(56,189,248,0.10);
    text-align: center;
}

.login-icon-dark {
    width: 80px;
    height: 80px;
    border-radius: 22px;
    margin: 0 auto 18px auto;
    background: radial-gradient(circle at 50% 50%, #020617 0%, #020617 30%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 40px;
    box-shadow: 0 0 40px rgba(14,165,233,0.60);
}

.login-title-dark {
    font-size: 30px;
    font-weight: 900;
    color: #ffffff !important;
    letter-spacing: 0.04em;
    margin-bottom: 6px;
}

.login-title-dark span {
    color: #38bdf8 !important;
}

.login-sub-dark {
    color: #7dd3fc !important;
    font-size: 14px;
    margin-bottom: 28px;
    opacity: 0.80;
}

/* INPUTS CLAROS COM BORDA NEON */
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

/* SELECT CLARO COM BORDA NEON */
div[data-baseweb="select"] {
    background: #ffffff !important;
    border: 1.5px solid rgba(56,189,248,0.45) !important;
    border-radius: 12px !important;
}

div[data-baseweb="select"] * {
    background: #ffffff !important;
    color: #0f172a !important;
}

/* LABELS */
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

/* BOTOES AZUL NEON */
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

/* METRICAS CLARAS COM BORDA NEON */
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

/* DATAFRAME CLARO COM BORDA NEON */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1.5px solid rgba(14,165,233,0.35) !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.10) !important;
}

/* HEADERS */
h1, h2, h3 {
    color: #0f172a !important;
    letter-spacing: -0.02em;
}

/* ALERTS */
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

/* FORM */
div[data-testid="stForm"] {
    background: #ffffff !important;
    border: 1.5px solid rgba(14,165,233,0.30) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    box-shadow: 0 0 18px rgba(14,165,233,0.08) !important;
}

/* DIVIDER */
hr { border-color: rgba(14,165,233,0.25) !important; }

/* SUBHEADER */
.stApp h2 {
    color: #0f172a !important;
    border-bottom: 2px solid rgba(14,165,233,0.35);
    padding-bottom: 8px;
}

/* TEXTO GERAL */
.stApp p, .stApp span, .stApp div { color: #1e293b; }
.stCaption, small { color: #0ea5e9 !important; opacity: 0.9; }

header { background: transparent !important; }

/* SCROLLBAR */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: rgba(2,12,30,0.5); }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.25); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

def achar_logo():
    nomes = [
        "logo_operax.png",
        "logo_operax(1).png",
        "logo_operax (1).png",
        "logo.png"
    ]

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
        """,
        unsafe_allow_html=True
    )



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

            .bolinha-verde {
                width: 11px;
                height: 11px;
                background: #22c55e;
                border-radius: 999px;
                animation: piscarChat 1s infinite;
            }
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

    logo_path = achar_logo()

    if logo_path:
        try:
            st.sidebar.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;padding:16px 8px 20px;gap:8px;">
            """, unsafe_allow_html=True)
            st.sidebar.image(str(logo_path), width=180)
            st.sidebar.markdown("""
            <div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin:4px auto 0;"></div>
            </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.sidebar.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;">
                <div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div>
                <div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;text-shadow:0 0 18px rgba(56,189,248,0.65);">OPERAX</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;text-shadow:0 0 10px rgba(56,189,248,0.50);">SALES</div>
                <div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin-top:6px;"></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;">
            <div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;text-shadow:0 0 18px rgba(56,189,248,0.65);">OPERAX</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;text-shadow:0 0 10px rgba(56,189,248,0.50);">SALES</div>
            <div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin-top:6px;"></div>
        </div>
        """, unsafe_allow_html=True)

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
                    <div class="menu-icon-wrap">{svg}</div>
                    <span class="menu-label-text">{nome_limpo}</span>
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
        padding: 0 !important;
        max-width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: 100vh !important;
    }
    div[data-testid="stTextInput"] input {
        background: rgba(8,22,58,0.95) !important;
        border: 1px solid rgba(56,189,248,0.30) !important;
        border-radius: 14px !important;
        color: #e2f4ff !important;
        font-size: 15px !important;
        padding: 12px 16px !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: rgba(125,211,252,0.35) !important; }
    div[data-testid="stTextInput"] input:focus {
        border-color: rgba(56,189,248,0.65) !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.18) !important;
    }
    div[data-testid="stTextInput"] label {
        color: #38bdf8 !important;
        font-size: 11px !important;
        font-weight: 700 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #1a56db, #0ea5e9) !important;
        border: none !important;
        border-radius: 14px !important;
        color: #fff !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        letter-spacing: 0.04em !important;
        box-shadow: 0 0 26px rgba(14,165,233,0.50), 0 8px 24px rgba(14,165,233,0.28) !important;
        height: 54px !important;
        margin-top: 6px !important;
    }
    .stButton>button:hover {
        box-shadow: 0 0 40px rgba(56,189,248,0.70), 0 12px 32px rgba(14,165,233,0.40) !important;
        transform: translateY(-1px) !important;
    }
    </style>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("""
<div style="background:rgba(7,18,48,0.95);border:1px solid rgba(56,189,248,0.22);border-radius:26px;padding:46px 40px 40px;text-align:center;box-shadow:0 0 60px rgba(14,165,233,0.14),0 28px 80px rgba(0,0,0,0.80);margin-top:30px;">
<div style="width:90px;height:90px;border-radius:22px;margin:0 auto 18px auto;background:radial-gradient(circle at 38% 35%,#bfdbfe 0%,#3b82f6 28%,#1d4ed8 56%,#030a1a 88%);display:flex;align-items:center;justify-content:center;font-size:44px;box-shadow:0 0 0 2px rgba(56,189,248,0.45),0 0 28px rgba(56,189,248,0.80),0 0 55px rgba(14,165,233,0.45);">🌀</div>
<div style="font-family:Orbitron,sans-serif;font-size:26px;font-weight:900;color:#ffffff;letter-spacing:0.07em;margin-bottom:8px;text-shadow:0 0 22px rgba(56,189,248,0.55);">OPERAX <span style="color:#38bdf8;text-shadow:0 0 18px rgba(56,189,248,0.90);">SALES</span></div>
<div style="color:#7dd3fc;font-size:13px;opacity:0.75;margin-bottom:32px;letter-spacing:0.02em;">Sistema inteligente de vendas e operações financeiras</div>
</div>""", unsafe_allow_html=True)

        usuario = st.text_input("USUÁRIO", placeholder="Seu login", key="login_user")
        senha   = st.text_input("SENHA", type="password", placeholder="••••••••", key="login_pass")

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
                st.error("Usuário ou senha inválidos")

else:
    mostrar_cabecalho()
    menu = menu_lateral_v8()

    mostrar_chat_popup()

    if "mostrar_comissao_empresa" not in st.session_state:
        st.session_state.mostrar_comissao_empresa = True

    if "msg_sucesso" not in st.session_state:
        st.session_state.msg_sucesso = ""

    if "form_count" not in st.session_state:
        st.session_state.form_count = 0



    # =========================
    # NOVA VENDA
    # =========================

    if menu == "📋 Nova Venda":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <span style="font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Cadastro de Venda</span>
        </div>
        """, unsafe_allow_html=True)

        tabelas = carregar_tabelas()

        # Mostra mensagem de sucesso se existir (vem do rerun anterior)
        if st.session_state.get("msg_sucesso"):
            st.markdown(f"""
            <div style="
                background: rgba(34,197,94,0.12);
                border: 1.5px solid rgba(34,197,94,0.45);
                border-radius: 12px;
                padding: 14px 18px;
                margin-bottom: 16px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 0 16px rgba(34,197,94,0.15);
            ">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                <span style="color:#4ade80;font-weight:700;font-size:14px;">{st.session_state.msg_sucesso}</span>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.msg_sucesso = ""

        fc = st.session_state.form_count
        cliente = st.text_input("Cliente", key=f"novo_cliente_{fc}")

        cpf_digitado = st.text_input(
            "CPF",
            placeholder="Ex: 999.999.999-99",
            key=f"novo_cpf_{fc}"
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
            key=f"novo_telefone_{fc}"
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
            key=f"novo_valor_{fc}"
        )
        valor = converter_valor_brasileiro(valor_digitado)

        if valor_digitado:
            if valor > 0:
                st.success(f"Valor válido: {dinheiro(valor)}")
            else:
                st.error("Valor inválido. Exemplo correto: R$ 1.758,71")

        status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])

        observacao = st.text_area("Observação", key=f"nova_observacao_{fc}")

        if st.button("💾 Salvar Venda", use_container_width=True):
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

                # Mensagem de sucesso
                st.session_state.msg_sucesso = "✅ Venda cadastrada com sucesso!"

                # Incrementa counter -> todos os keys mudam -> campos ficam em branco
                st.session_state.form_count += 1

                st.rerun()

    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            </div>
            <span style="font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Painel de Vendas</span>
        </div>
        """, unsafe_allow_html=True)
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

            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 12px 0;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;letter-spacing:0.01em;">Filtros</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 12px 0;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;letter-spacing:0.01em;">Propostas</span>
        </div>
        """, unsafe_allow_html=True)
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
                    st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 12px 0;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;letter-spacing:0.01em;">Ações rápidas</span>
        </div>
        """, unsafe_allow_html=True)

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
                st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 12px 0;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;letter-spacing:0.01em;">Editar proposta</span>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <span style="font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Usuários</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Criar usuário</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 0 2-2h2a2 2 0 0 0 2 2"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Usuários cadastrados</span>
        </div>
        """, unsafe_allow_html=True)
            st.dataframe(df_users[["id", "nome", "usuario", "tipo", "ativo"]], use_container_width=True)

            st.divider()
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Editar usuário</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Alterar senha</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Ativar / Desativar</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6l-1 14H6L5 6M10 11v6M14 11v6M9 6V4h6v2"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Excluir usuário</span>
        </div>
        """, unsafe_allow_html=True)

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
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v12M9 9h4.5a1.5 1.5 0 0 1 0 3h-3a1.5 1.5 0 0 0 0 3H15"/></svg>
            </div>
            <span style="font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-0.02em;">Regras de Comissão</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Criar nova regra</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Regras cadastradas</span>
        </div>
        """, unsafe_allow_html=True)
            st.dataframe(df_regras, use_container_width=True)

            st.divider()
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Editar regra</span>
        </div>
        """, unsafe_allow_html=True)

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
            st.markdown("""
        <div style="display:flex;align-items:center;gap:9px;margin:16px 0 10px 0;">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6l-1 14H6L5 6"/></svg>
            <span style="font-size:15px;font-weight:700;color:#0f172a;">Excluir regra</span>
        </div>
        """, unsafe_allow_html=True)

            confirmar = st.checkbox("Confirmo que quero excluir esta regra")

            if st.button("Excluir regra"):
                if not confirmar:
                    st.error("Marque a confirmação.")
                else:
                    supabase.table("regras_comissao").delete().eq("id", int(regra_id)).execute()
                    st.success("Regra excluída!")
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
