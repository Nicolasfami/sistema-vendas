import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ===============================
# CONFIG
# ===============================
ARQUIVO = "vendas.xlsx"

# ===============================
# LOGIN SIMPLES
# ===============================
usuarios = {
    "admin": {"senha": "123", "tipo": "admin"},
    "joao": {"senha": "123", "tipo": "vendedor"},
    "maria": {"senha": "123", "tipo": "vendedor"},
}

# ===============================
# CRIAR PLANILHA SE NÃO EXISTIR
# ===============================
if not os.path.exists(ARQUIVO):
    df = pd.DataFrame(columns=[
        "Data",
        "Vendedor",
        "Cliente",
        "CPF",
        "Telefone",
        "Valor",
        "Status",
        "Comissao",
        "Observacao"
    ])
    df.to_excel(ARQUIVO, index=False)

# ===============================
# LOGIN
# ===============================
st.set_page_config(page_title="Sistema de Vendas", layout="wide")

st.title("💰 Sistema de Vendas")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario in usuarios and usuarios[usuario]["senha"] == senha:

            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.tipo = usuarios[usuario]["tipo"]

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

# ===============================
# SISTEMA
# ===============================
else:

    st.sidebar.success(f"Logado como: {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    df = pd.read_excel(ARQUIVO)

    # ===============================
    # CADASTRO DE VENDA
    # ===============================
    st.header("📋 Nova Venda")

    with st.form("nova_venda"):

        cliente = st.text_input("Cliente")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        valor = st.number_input("Valor", min_value=0.0)
        status = st.selectbox("Status", [
            "Pendente",
            "Pago",
            "Cancelado"
        ])
        observacao = st.text_area("Observação")

        salvar = st.form_submit_button("Salvar Venda")

        if salvar:

            nova_venda = {
                "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": st.session_state.usuario,
                "Cliente": cliente,
                "CPF": cpf,
                "Telefone": telefone,
                "Valor": valor,
                "Status": status,
                "Comissao": "",
                "Observacao": observacao
            }

            df = pd.concat([df, pd.DataFrame([nova_venda])], ignore_index=True)

            df.to_excel(ARQUIVO, index=False)

            st.success("Venda cadastrada com sucesso!")

    # ===============================
    # FILTRO
    # ===============================
    st.header("📊 Vendas")

    if st.session_state.tipo == "admin":

        vendedor_filtro = st.selectbox(
            "Filtrar vendedor",
            ["Todos"] + list(df["Vendedor"].unique())
        )

        if vendedor_filtro != "Todos":
            df = df[df["Vendedor"] == vendedor_filtro]

    else:
        df = df[df["Vendedor"] == st.session_state.usuario]

    # ===============================
    # TOTAL
    # ===============================
    total = df["Valor"].sum()

    st.metric("💵 Total Vendido", f"R$ {total:,.2f}")

    # ===============================
    # ADMIN PODE EDITAR COMISSÃO
    # ===============================
    if st.session_state.tipo == "admin":

        st.subheader("✏️ Editar Comissão")

        if not df.empty:

            indice = st.selectbox(
                "Escolha a venda",
                df.index
            )

            nova_comissao = st.text_input("Comissão")

            if st.button("Salvar Comissão"):

                df_original = pd.read_excel(ARQUIVO)

                df_original.loc[indice, "Comissao"] = nova_comissao

                df_original.to_excel(ARQUIVO, index=False)

                st.success("Comissão atualizada!")

    # ===============================
    # TABELA
    # ===============================
    st.dataframe(df, use_container_width=True)

    # ===============================
    # EXPORTAR
    # ===============================
    st.download_button(
        label="📥 Baixar Excel",
        data=open(ARQUIVO, "rb"),
        file_name="vendas.xlsx"
    )