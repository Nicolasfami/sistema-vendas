import streamlit as st
import pandas as pd
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

# ================= LOGIN =================

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

    menu = st.sidebar.radio(
        "Menu",
        ["Nova Venda", "Painel"]
    )

    # ================= REGRAS =================

    regras = {
        "CLT PADRAO OUTROS BANCOS ( v8 abaixo 36x)": [
            (190000, 0.50),
            (130000, 0.35),
            (100000, 0.25),
        ],

        "V8 - PRESENÇA": [
            (180000, 1.20),
            (120000, 1.00),
            (70000, 0.80),
        ]
    }

    # ================= CALCULO =================

    def calcular_comissao(produto, valor):

        percentual = 0

        if produto in regras:

            for minimo, pct in regras[produto]:

                if valor >= minimo:
                    percentual = pct
                    break

        valor_comissao = valor * (percentual / 100)

        return percentual, valor_comissao

    # ================= NOVA VENDA =================

    if menu == "Nova Venda":

        st.header("📋 Nova Venda")

        with st.form("form_venda"):

            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

            produto = st.selectbox(
                "Produto",
                [
                    "CLT PADRAO OUTROS BANCOS ( v8 abaixo 36x)",
                    "V8 - PRESENÇA"
                ]
            )

            valor = st.number_input(
                "Valor Vendido",
                min_value=0.0,
                step=1000.0
            )

            status = st.selectbox(
                "Status",
                ["Pendente", "Pago", "Cancelado"]
            )

            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar Venda")

            if salvar:

                percentual, valor_comissao = calcular_comissao(
                    produto,
                    valor
                )

                venda = {
                    "vendedor": st.session_state.usuario,
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

                supabase.table("vendas").insert(venda).execute()

                st.success("Venda cadastrada!")

                st.info(
                    f"Comissão calculada: "
                    f"{percentual:.2f}% | "
                    f"R$ {valor_comissao:,.2f}"
                )

    # ================= PAINEL =================

    if menu == "Painel":

        st.header("📊 Painel de Vendas")

        dados = supabase.table("vendas").select("*").order(
            "id",
            desc=True
        ).execute()

        df = pd.DataFrame(dados.data)

        if df.empty:

            st.warning("Nenhuma venda cadastrada.")

        else:

            if st.session_state.tipo != "admin":

                df = df[
                    df["vendedor"] ==
                    st.session_state.usuario
                ]

            total = df["valor"].sum()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💵 Total Vendido",
                f"R$ {total:,.2f}"
            )

            col2.metric(
                "🧾 Quantidade",
                len(df)
            )

            col3.metric(
                "💰 Comissão Total",
                f"R$ {df['valor_comissao'].sum():,.2f}"
            )

            st.subheader("📄 Vendas")

            if st.session_state.tipo == "admin":

                st.dataframe(
                    df[
                        [
                            "id",
                            "vendedor",
                            "cliente",
                            "produto",
                            "valor",
                            "percentual_comissao",
                            "valor_comissao",
                            "status"
                        ]
                    ],
                    use_container_width=True
                )

            else:

                st.dataframe(
                    df[
                        [
                            "cliente",
                            "produto",
                            "valor",
                            "percentual_comissao",
                            "valor_comissao",
                            "status"
                        ]
                    ],
                    use_container_width=True
                )
