import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="CRM TK Soluções", layout="wide")


def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def login(usuario, senha):
    usuario = usuario.strip().lower()
    senha_hash = hash_senha(senha.strip())

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

    if user["senha_hash"] == senha_hash:
        return user

    return None


def calcular_comissao(produto, valor):

    regras = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("produto", produto)
        .eq("ativo", True)
        .order("valor_minimo", desc=True)
        .execute()
    )

    percentual_vendedor = 0
    percentual_empresa = 0

    for regra in regras.data:

        if valor >= float(regra["valor_minimo"]):

            percentual_vendedor = float(
                regra["percentual_vendedor"]
            )

            percentual_empresa = float(
                regra["percentual_empresa"]
            )

            break

    valor_comissao_vendedor = (
        valor * (percentual_vendedor / 100)
    )

    valor_comissao_empresa = (
        valor * (percentual_empresa / 100)
    )

    return (
        percentual_vendedor,
        valor_comissao_vendedor,
        percentual_empresa,
        valor_comissao_empresa
    )


st.title("💰 CRM TK Soluções")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    usuario = st.text_input("Usuário")
    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        user = login(usuario, senha)

        if user:

            st.session_state.logado = True
            st.session_state.usuario = user["usuario"]
            st.session_state.nome = user["nome"]
            st.session_state.tipo = user["tipo"]

            st.rerun()

        else:
            st.error("Usuário ou senha inválidos")

else:

    st.sidebar.success(
        f"👤 {st.session_state.nome}"
    )

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    if st.session_state.tipo == "admin":

        menu = st.sidebar.radio(
            "Menu",
            [
                "📋 Nova Venda",
                "📊 Painel",
                "👥 Usuários",
                "💰 Comissões"
            ]
        )

    else:

        menu = st.sidebar.radio(
            "Menu",
            [
                "📋 Nova Venda",
                "📊 Painel"
            ]
        )

    # =========================
    # NOVA VENDA
    # =========================

    if menu == "📋 Nova Venda":

        st.header("📋 Cadastro de Venda")

        produtos_db = (
            supabase.table("regras_comissao")
            .select("produto")
            .execute()
        )

        produtos = list(
            set(
                [
                    x["produto"]
                    for x in produtos_db.data
                ]
            )
        )

        with st.form("form_venda"):

            vendedor = st.text_input(
                "Vendedor",
                value=st.session_state.usuario
            )

            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

            produto = st.selectbox(
                "Produto",
                produtos
            )

            valor = st.number_input(
                "Valor vendido",
                min_value=0.0,
                step=1000.0
            )

            status = st.selectbox(
                "Status",
                [
                    "Pendente",
                    "Pago",
                    "Cancelado"
                ]
            )

            observacao = st.text_area(
                "Observação"
            )

            salvar = st.form_submit_button(
                "Salvar Venda"
            )

            if salvar:

                (
                    perc_vend,
                    valor_vend,
                    perc_emp,
                    valor_emp
                ) = calcular_comissao(
                    produto,
                    valor
                )

                dados = {
                    "data": str(datetime.now()),
                    "vendedor": vendedor,
                    "cliente": cliente,
                    "cpf": cpf,
                    "telefone": telefone,
                    "produto": produto,
                    "valor": valor,
                    "status": status,
                    "percentual_comissao": perc_vend,
                    "valor_comissao": valor_vend,
                    "comissao_empresa": perc_emp,
                    "valor_comissao_empresa": valor_emp,
                    "conferido": False,
                    "observacao": observacao
                }

                supabase.table(
                    "vendas"
                ).insert(
                    dados
                ).execute()

                st.success(
                    "Venda cadastrada!"
                )

                st.info(
                    f"Comissão vendedor: "
                    f"{perc_vend:.2f}%"
                )
                    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":

        st.header("📊 Painel de Vendas")

        response = (
            supabase.table("vendas")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        dados = response.data

        if dados:

            df = pd.DataFrame(dados)

            if st.session_state.tipo != "admin":

                df = df[
                    df["vendedor"].str.lower()
                    ==
                    st.session_state.usuario.lower()
                ]

            total = df["valor"].fillna(0).sum()

            total_comissao = (
                df["valor_comissao"]
                .fillna(0)
                .sum()
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💵 Total vendido",
                f"R$ {total:,.2f}"
            )

            col2.metric(
                "📋 Quantidade",
                len(df)
            )

            col3.metric(
                "💰 Comissão",
                f"R$ {total_comissao:,.2f}"
            )

            st.divider()

            st.subheader("📄 Propostas")

            if st.session_state.tipo == "admin":

                st.dataframe(
                    df,
                    use_container_width=True
                )

            else:

                colunas = [
                    "id",
                    "cliente",
                    "produto",
                    "valor",
                    "status",
                    "percentual_comissao",
                    "valor_comissao"
                ]

                st.dataframe(
                    df[colunas],
                    use_container_width=True
                )

            st.divider()

            st.subheader(
                "✏️ Editar proposta"
            )

            venda_id = st.selectbox(
                "Escolha ID",
                df["id"].tolist()
            )

            venda = df[
                df["id"] == venda_id
            ].iloc[0]

            with st.form("editar"):

                cliente = st.text_input(
                    "Cliente",
                    value=str(
                        venda["cliente"]
                    )
                )

                telefone = st.text_input(
                    "Telefone",
                    value=str(
                        venda["telefone"]
                    )
                )

                valor = st.number_input(
                    "Valor",
                    value=float(
                        venda["valor"]
                    )
                )

                status = st.selectbox(
                    "Status",
                    [
                        "Pendente",
                        "Pago",
                        "Cancelado"
                    ],
                    index=[
                        "Pendente",
                        "Pago",
                        "Cancelado"
                    ].index(
                        venda["status"]
                    )
                )

                if st.session_state.tipo == "admin":

                    conferido = st.checkbox(
                        "✅ Conferido",
                        value=bool(
                            venda["conferido"]
                        )
                    )

                    perc_vend = st.number_input(
                        "% comissão vendedor",
                        value=float(
                            venda[
                                "percentual_comissao"
                            ]
                        )
                    )

                    perc_emp = st.number_input(
                        "% comissão empresa",
                        value=float(
                            venda[
                                "comissao_empresa"
                            ]
                        )
                    )

                salvar = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar:

                    valor_comissao = (
                        valor *
                        (
                            perc_vend / 100
                        )
                    ) if st.session_state.tipo == "admin" else venda["valor_comissao"]

                    valor_empresa = (
                        valor *
                        (
                            perc_emp / 100
                        )
                    ) if st.session_state.tipo == "admin" else venda["valor_comissao_empresa"]

                    update = {
                        "cliente": cliente,
                        "telefone": telefone,
                        "valor": valor,
                        "status": status
                    }

                    if st.session_state.tipo == "admin":

                        update[
                            "conferido"
                        ] = conferido

                        update[
                            "percentual_comissao"
                        ] = perc_vend

                        update[
                            "valor_comissao"
                        ] = valor_comissao

                        update[
                            "comissao_empresa"
                        ] = perc_emp

                        update[
                            "valor_comissao_empresa"
                        ] = valor_empresa

                    supabase.table(
                        "vendas"
                    ).update(
                        update
                    ).eq(
                        "id",
                        venda_id
                    ).execute()

                    st.success(
                        "Proposta atualizada!"
                    )

                    st.rerun()

    # =========================
    # USUÁRIOS
    # =========================

    elif menu == "👥 Usuários":

        st.header("👥 Usuários")

        usuarios = (
            supabase.table("usuarios")
            .select("*")
            .order("id")
            .execute()
        )

        usuarios_df = pd.DataFrame(
            usuarios.data
        )

        st.dataframe(
            usuarios_df[
                [
                    "id",
                    "nome",
                    "usuario",
                    "tipo",
                    "ativo"
                ]
            ],
            use_container_width=True
        )

    # =========================
    # COMISSÕES
    # =========================

    elif menu == "💰 Comissões":

        st.header(
            "💰 Regras de Comissão"
        )

        with st.form(
            "nova_regra"
        ):

            produto = st.text_input(
                "Produto/Banco"
            )

            valor_minimo = st.number_input(
                "Valor mínimo"
            )

            percentual_vendedor = st.number_input(
                "% vendedor"
            )

            percentual_empresa = st.number_input(
                "% empresa"
            )

            salvar = st.form_submit_button(
                "Salvar regra"
            )

            if salvar:

                supabase.table(
                    "regras_comissao"
                ).insert(
                    {
                        "produto": produto,
                        "valor_minimo": valor_minimo,
                        "percentual_vendedor": percentual_vendedor,
                        "percentual_empresa": percentual_empresa,
                        "ativo": True
                    }
                ).execute()

                st.success(
                    "Regra criada!"
                )

                st.rerun()

        regras = (
            supabase.table(
                "regras_comissao"
            )
            .select("*")
            .order(
                "produto"
            )
            .execute()
        )

        regras_df = pd.DataFrame(
            regras.data
        )

        st.dataframe(
            regras_df,
            use_container_width=True
        )
