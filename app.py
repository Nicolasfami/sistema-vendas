import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

usuarios = {
    "admin": {"senha": "123", "tipo": "admin"},
    "joao": {"senha": "123", "tipo": "vendedor"},
    "maria": {"senha": "123", "tipo": "vendedor"},
}

st.set_page_config(page_title="CRM TK Soluções", layout="wide")

st.title("💰 CRM TK Soluções")

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

else:
    st.sidebar.success(f"Logado como: {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.header("📋 Nova Venda")

    with st.form("nova_venda"):
        cliente = st.text_input("Cliente")
        cpf = st.text_input("CPF")
        telefone = st.text_input("Telefone")
        valor = st.number_input("Valor", min_value=0.0, step=10.0)
        status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])
        observacao = st.text_area("Observação")

        salvar = st.form_submit_button("Salvar Venda")

        if salvar:
            venda = {
                "vendedor": st.session_state.usuario,
                "cliente": cliente,
                "cpf": cpf,
                "telefone": telefone,
                "valor": valor,
                "status": status,
                "comissao": "",
                "observacao": observacao
            }

            supabase.table("vendas").insert(venda).execute()
            st.success("Venda cadastrada com sucesso no banco online!")

    st.header("📊 Vendas")

    dados = supabase.table("vendas").select("*").order("id", desc=True).execute()
    df = pd.DataFrame(dados.data)

    if df.empty:
        st.info("Nenhuma venda cadastrada ainda.")
    else:
        if st.session_state.tipo == "admin":
            vendedor_filtro = st.selectbox(
                "Filtrar vendedor",
                ["Todos"] + sorted(df["vendedor"].dropna().unique().tolist())
            )

            if vendedor_filtro != "Todos":
                df = df[df["vendedor"] == vendedor_filtro]
        else:
            df = df[df["vendedor"] == st.session_state.usuario]

        total = df["valor"].fillna(0).sum()
        st.metric("💵 Total Vendido", f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        if st.session_state.tipo == "admin":
            st.subheader("✏️ Editar Comissão")

            venda_id = st.selectbox(
                "Escolha o ID da venda",
                df["id"].tolist()
            )

            nova_comissao = st.text_input("Comissão")

            if st.button("Salvar Comissão"):
                supabase.table("vendas").update({
                    "comissao": nova_comissao
                }).eq("id", venda_id).execute()

                st.success("Comissão atualizada!")
                st.rerun()

        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="vendas.csv",
            mime="text/csv"
        )