import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime

# ================= CONFIG =================

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="CRM TK Soluções", layout="wide")

# ================= USUÁRIOS =================

usuarios = {
    "admin": {
        "senha": "123",
        "tipo": "admin"
    },
    "bruna": {
        "senha": "123",
        "tipo": "vendedor"
    },
    "larissa": {
        "senha": "123",
        "tipo": "vendedor"
    }
}

# ================= LOGIN =================

st.title("💰 CRM TK Soluções")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    usuario = st.text_input("Usuário").strip().lower()
    senha = st.text_input("Senha", type="password").strip()

    if st.button("Entrar"):

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:

            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.tipo = usuarios[usuario]["tipo"]

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

# ================= SISTEMA =================

else:

    st.sidebar.success(f"Logado como: {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📊 Painel de Vendas")

    # ================= CADASTRAR VENDA =================

    with st.expander("➕ Nova Venda"):

        vendedor = st.text_input("Vendedor")
        cliente = st.text_input("Cliente")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")

        produto = st.selectbox(
            "Produto",
            [
                "CLT PADRAO OUTROS BANCOS E V8",
                "V8 PRESENÇA"
            ]
        )

        valor = st.number_input("Valor vendido", min_value=0.0)

        status = st.selectbox(
            "Status",
            [
                "Pendente",
                "Pago",
                "Cancelado"
            ]
        )

        observacao = st.text_area("Observação")

        percentual = 0

        # ================= COMISSÕES =================

        if produto == "CLT PADRAO OUTROS BANCOS E V8":

            if valor >= 190000:
                percentual = 0.50

            elif valor >= 130000:
                percentual = 0.35

            elif valor >= 100000:
                percentual = 0.25

        elif produto == "V8 PRESENÇA":

            if valor >= 180000:
                percentual = 1.20

            elif valor >= 120000:
                percentual = 1.00

            elif valor >= 70000:
                percentual = 0.80

        valor_comissao = valor * (percentual / 100)

        st.info(f"Percentual: {percentual}%")
        st.success(f"Comissão: R$ {valor_comissao:,.2f}")

        # ================= SALVAR =================

        if st.button("Salvar Venda"):

            dados = {
                "data": str(datetime.now()),
                "vendedor": vendedor,
                "cliente": cliente,
                "cpf": cpf,
                "telefone": telefone,
                "produto": produto,
                "valor": valor,
                "status": status,
                "percentual_comissao": percentual,
                "valor_comissao": valor_comissao,
                "observacao": observacao
            }

            supabase.table("vendas").insert(dados).execute()

            st.success("Venda salva com sucesso!")

    # ================= LISTAR VENDAS =================

    st.divider()

    st.subheader("📋 Vendas cadastradas")

    response = supabase.table("vendas").select("*").execute()

    dados = response.data

    if len(dados) > 0:

        df = pd.DataFrame(dados)

        # ================= VISÃO VENDEDOR =================

        if st.session_state.tipo == "vendedor":

            vendedor_logado = st.session_state.usuario

            df = df[df["vendedor"].str.lower() == vendedor_logado]

            colunas_vendedor = [
                "data",
                "cliente",
                "telefone",
                "produto",
                "valor",
                "status",
                "valor_comissao"
            ]

            df = df[colunas_vendedor]

        # ================= VISÃO ADMIN =================

        else:

            colunas_admin = [
                "data",
                "vendedor",
                "cliente",
                "cpf",
                "telefone",
                "produto",
                "valor",
                "status",
                "percentual_comissao",
                "valor_comissao",
                "observacao"
            ]

            df = df[colunas_admin]

        st.dataframe(df, use_container_width=True)

    else:
        st.warning("Nenhuma venda cadastrada.")
