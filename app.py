import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib

# =========================
# CONFIG SUPABASE
# =========================

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# CONFIG PÁGINA
# =========================

st.set_page_config(
    page_title="CRM TK Soluções",
    layout="wide"
)

# =========================
# FUNÇÕES
# =========================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def login(usuario, senha):

    usuario = usuario.strip().lower()
    senha_hash = hash_senha(senha.strip())

    response = (
        supabase
        .table("usuarios")
        .select("*")
        .eq("usuario", usuario)
        .eq("ativo", True)
        .execute()
    )

    if not response.data:
        return None

    user = response.data[0]

    if user["senha_hash"] == senha_hash:
        return user

    return None


def calcular_comissao(produto, valor):

    percentual = 0

    # =========================
    # CLT PADRAO OUTROS BANCOS
    # =========================

    if produto == "CLT PADRAO OUTROS BANCOS":

        if valor >= 190000:
            percentual = 0.50

        elif valor >= 130000:
            percentual = 0.35

        elif valor >= 100000:
            percentual = 0.25

    # =========================
    # V8 PRESENÇA
    # =========================

    elif produto == "V8 PRESENÇA":

        if valor >= 180000:
            percentual = 1.20

        elif valor >= 120000:
            percentual = 1.00

        elif valor >= 70000:
            percentual = 0.80

    valor_comissao = valor * (percentual / 100)

    return percentual, valor_comissao


# =========================
# LOGIN
# =========================

st.title("💰 CRM TK Soluções")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

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

# =========================
# SISTEMA
# =========================

else:

    st.sidebar.success(f"👤 {st.session_state.nome}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # =========================
    # MENUS
    # =========================

    if st.session_state.tipo == "admin":

        menu = st.sidebar.radio(
            "Menu",
            [
                "📋 Nova Venda",
                "📊 Painel",
                "👥 Usuários"
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
                [
                    "CLT PADRAO OUTROS BANCOS",
                    "V8 PRESENÇA"
                ]
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

            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar Venda")

            if salvar:

                percentual, valor_comissao = calcular_comissao(produto, valor)

                dados = {
                    "data": str(datetime.now()),
                    "vendedor": vendedor,
                    "cliente": cliente,
                    "cpf": cpf,
                    "telefone": telefone,
                    "produto": produto,
                    "valor": valor,
                    "status": status,
                    "comissao": percentual,
                    "valor_comissao": valor_comissao,
                    "observacao": observacao
                }

                supabase.table("vendas").insert(dados).execute()

                st.success("Venda cadastrada com sucesso!")

                st.info(
                    f"Comissão: {percentual:.2f}% | "
                    f"R$ {valor_comissao:,.2f}"
                )

    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":

        st.header("📊 Painel de Vendas")

        response = (
            supabase
            .table("vendas")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        dados = response.data

        if len(dados) > 0:

            df = pd.DataFrame(dados)

            # =========================
            # VENDEDOR VE APENAS AS DELE
            # =========================

            if st.session_state.tipo != "admin":

                df = df[
                    df["vendedor"].str.lower()
                    == st.session_state.usuario.lower()
                ]

            total_vendas = df["valor"].fillna(0).sum()

            total_comissao = (
                df["valor_comissao"]
                .fillna(0)
                .sum()
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💵 Total vendido",
                f"R$ {total_vendas:,.2f}"
            )

            col2.metric(
                "📋 Quantidade",
                len(df)
            )

            col3.metric(
                "💰 Comissão",
                f"R$ {total_comissao:,.2f}"
            )

            # =========================
            # ADMIN VE TUDO
            # =========================

            if st.session_state.tipo == "admin":

                st.dataframe(
                    df,
                    use_container_width=True
                )

            # =========================
            # VENDEDOR VE LIMITADO
            # =========================

            else:

                colunas = [
                    "data",
                    "cliente",
                    "telefone",
                    "produto",
                    "valor",
                    "status",
                    "comissao",
                    "valor_comissao"
                ]

                st.dataframe(
                    df[colunas],
                    use_container_width=True
                )

        else:

            st.warning("Nenhuma venda cadastrada.")

    # =========================
    # USUÁRIOS (SÓ ADMIN)
    # =========================

    elif menu == "👥 Usuários":

        st.header("👥 Usuários")

        # =========================
        # CADASTRAR
        # =========================

        with st.form("novo_usuario"):

            nome = st.text_input("Nome")
            novo_usuario = st.text_input("Usuário")
            nova_senha = st.text_input(
                "Senha",
                type="password"
            )

            tipo = st.selectbox(
                "Tipo",
                [
                    "vendedor",
                    "admin"
                ]
            )

            criar = st.form_submit_button(
                "Criar usuário"
            )

            if criar:

                dados_usuario = {
                    "nome": nome,
                    "usuario": novo_usuario.lower(),
                    "senha_hash": hash_senha(nova_senha),
                    "tipo": tipo,
                    "ativo": True
                }

                try:

                    supabase.table(
                        "usuarios"
                    ).insert(
                        dados_usuario
                    ).execute()

                    st.success(
                        "Usuário criado com sucesso!"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Erro ao criar usuário: {e}"
                    )

        st.divider()

        # =========================
        # LISTA USUÁRIOS
        # =========================

        usuarios = (
            supabase
            .table("usuarios")
            .select("*")
            .order("id")
            .execute()
        )

        usuarios_df = pd.DataFrame(
            usuarios.data
        )

        if not usuarios_df.empty:

            st.subheader("Usuários cadastrados")

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

            st.divider()

            # =========================
            # ALTERAR SENHA
            # =========================

            st.subheader("Alterar senha")

            user_id = st.selectbox(
                "Escolha o ID",
                usuarios_df["id"].tolist()
            )

            nova_senha_alt = st.text_input(
                "Nova senha",
                type="password"
            )

            if st.button("Alterar senha"):

                if nova_senha_alt:

                    supabase.table(
                        "usuarios"
                    ).update(
                        {
                            "senha_hash":
                            hash_senha(
                                nova_senha_alt
                            )
                        }
                    ).eq(
                        "id",
                        user_id
                    ).execute()

                    st.success(
                        "Senha alterada!"
                    )

                    st.rerun()

            # =========================
            # ATIVAR / DESATIVAR
            # =========================

            st.subheader(
                "Ativar / Desativar usuário"
            )

            user_id_status = st.selectbox(
                "Usuário",
                usuarios_df["id"].tolist(),
                key="status"
            )

            if st.button(
                "Alterar status"
            ):

                usuario_atual = usuarios_df[
                    usuarios_df["id"]
                    == user_id_status
                ].iloc[0]

                novo_status = (
                    not usuario_atual["ativo"]
                )

                supabase.table(
                    "usuarios"
                ).update(
                    {
                        "ativo": novo_status
                    }
                ).eq(
                    "id",
                    user_id_status
                ).execute()

                st.success(
                    "Status atualizado!"
                )

                st.rerun()
