import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib

# =========================================
# CONFIGURAÇÕES
# =========================================

st.set_page_config(
    page_title="CRM TK Soluções",
    layout="wide"
)

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================================
# FUNÇÕES
# =========================================

def hash_senha(senha):
    return hashlib.sha256(
        senha.encode()
    ).hexdigest()


def dinheiro(valor):

    try:

        return (
            f"R$ {float(valor):,.2f}"
            .replace(",", "X")
            .replace(".", ",")
            .replace("X", ".")
        )

    except:
        return "R$ 0,00"


def login(usuario, senha):

    usuario = usuario.strip().lower()

    senha_hash = hash_senha(
        senha.strip()
    )

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


def carregar_tabelas():

    res = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("ativo", True)
        .execute()
    )

    tabelas = sorted(
        list(
            set([
                r["produto"]
                for r in res.data
                if r.get("produto")
            ])
        )
    )

    return tabelas


def calcular_comissao_empresa(
    tabela_banco,
    valor
):

    res = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("produto", tabela_banco)
        .eq("ativo", True)
        .order(
            "valor_minimo",
            desc=True
        )
        .execute()
    )

    percentual_empresa = 0

    for regra in res.data:

        valor_minimo = float(
            regra.get("valor_minimo") or 0
        )

        if valor >= valor_minimo:

            percentual_empresa = float(
                regra.get("percentual_empresa") or 0
            )

            break

    valor_empresa = (
        valor *
        (percentual_empresa / 100)
    )

    return (
        percentual_empresa,
        valor_empresa
    )


# =========================================
# LOGIN
# =========================================

st.title("💰 CRM TK Soluções")

if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:

    usuario = st.text_input(
        "Usuário"
    )

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        user = login(
            usuario,
            senha
        )

        if user:

            st.session_state.logado = True
            st.session_state.user_id = user["id"]
            st.session_state.usuario = user["usuario"]
            st.session_state.nome = user["nome"]
            st.session_state.tipo = user["tipo"]

            st.rerun()

        else:

            st.error(
                "Usuário ou senha inválidos"
            )

else:

    st.sidebar.success(
        f"👤 {st.session_state.nome}"
    )

    if st.sidebar.button("Sair"):

        st.session_state.clear()
        st.rerun()

    # =========================================
    # MENU
    # =========================================

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

    # =========================================
    # NOVA VENDA
    # =========================================

    if menu == "📋 Nova Venda":

        st.header(
            "📋 Cadastro de Venda"
        )

        tabelas = carregar_tabelas()

        with st.form("form_venda"):

            cliente = st.text_input(
                "Cliente"
            )

            cpf = st.text_input(
                "CPF"
            )

            telefone = st.text_input(
                "Telefone"
            )

            tabela_banco = st.selectbox(
                "Tabela/Banco",
                tabelas
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
                "Salvar venda"
            )

            if salvar:

                perc_empresa, valor_empresa = (
                    calcular_comissao_empresa(
                        tabela_banco,
                        valor
                    )
                )

                dados = {

                    "data": str(datetime.now()),

                    "vendedor_id":
                    st.session_state.user_id,

                    "vendedor":
                    st.session_state.usuario,

                    "cliente":
                    cliente,

                    "cpf":
                    cpf,

                    "telefone":
                    telefone,

                    "produto":
                    tabela_banco,

                    "tabela_banco":
                    tabela_banco,

                    "valor":
                    valor,

                    "status":
                    status,

                    "percentual_comissao":
                    0,

                    "valor_comissao":
                    0,

                    "comissao_empresa":
                    perc_empresa,

                    "valor_comissao_empresa":
                    valor_empresa,

                    "conferido":
                    False,

                    "alterado_vendedor":
                    False,

                    "observacao":
                    observacao
                }

                supabase.table(
                    "vendas"
                ).insert(
                    dados
                ).execute()

                st.success(
                    "Venda cadastrada!"
                )
                    # =========================================
    # PAINEL
    # =========================================

    elif menu == "📊 Painel":

        st.header("📊 Painel de Vendas")

        vendas = (
            supabase.table("vendas")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        df = pd.DataFrame(vendas.data)

        if df.empty:

            st.warning("Nenhuma venda cadastrada.")

        else:

            df["data"] = pd.to_datetime(
                df["data"],
                errors="coerce"
            )

            df["mes_num"] = df["data"].dt.month
            df["ano"] = df["data"].dt.year

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

            st.subheader("🔎 Filtros")

            col_f1, col_f2, col_f3 = st.columns(3)

            mes_nome = col_f1.selectbox(
                "Mês",
                list(meses.values()),
                index=datetime.now().month - 1
            )

            anos = sorted(
                df["ano"]
                .dropna()
                .unique()
                .astype(int)
                .tolist(),
                reverse=True
            )

            if not anos:
                anos = [datetime.now().year]

            ano_filtro = col_f2.selectbox(
                "Ano",
                anos
            )

            status_filtro = col_f3.selectbox(
                "Status",
                [
                    "Todos",
                    "Pago",
                    "Pendente",
                    "Cancelado"
                ]
            )

            tabelas = carregar_tabelas()

            tabela_filtro = st.selectbox(
                "Tabela/Banco",
                ["Todas"] + tabelas
            )

            mes_num = [
                k for k, v in meses.items()
                if v == mes_nome
            ][0]

            df = df[
                (df["mes_num"] == mes_num)
                &
                (df["ano"] == ano_filtro)
            ]

            # VENDEDOR VÊ SOMENTE AS VENDAS DELE PELO ID
            if st.session_state.tipo != "admin":

                if "vendedor_id" in df.columns:

                    df = df[
                        df["vendedor_id"]
                        ==
                        st.session_state.user_id
                    ]

                else:

                    df = df[
                        df["vendedor"]
                        ==
                        st.session_state.usuario
                    ]

            if status_filtro != "Todos":

                df = df[
                    df["status"] == status_filtro
                ]

            if tabela_filtro != "Todas":

                df = df[
                    df["tabela_banco"] == tabela_filtro
                ]

            if st.session_state.tipo == "admin":

                vendedores = sorted(
                    df["vendedor"]
                    .dropna()
                    .unique()
                    .tolist()
                )

                vendedor_filtro = st.selectbox(
                    "Vendedor",
                    ["Todos"] + vendedores
                )

                if vendedor_filtro != "Todos":

                    df = df[
                        df["vendedor"] == vendedor_filtro
                    ]

            total_vendido = (
                df["valor"]
                .fillna(0)
                .sum()
            )

            qtd = len(df)

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "💵 Total vendido",
                dinheiro(total_vendido)
            )

            col2.metric(
                "📋 Quantidade",
                qtd
            )

            col3.metric(
                "🗓️ Mês",
                mes_nome
            )

            if st.session_state.tipo == "admin":

                total_empresa = 0

df_pagas = df[df["status"] == "Pago"].copy()

if not df_pagas.empty:
    for tabela in df_pagas["tabela_banco"].dropna().unique():
        total_tabela = df_pagas[df_pagas["tabela_banco"] == tabela]["valor"].fillna(0).sum()

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
            if total_tabela >= float(regra.get("valor_minimo") or 0):
                percentual = float(regra.get("percentual_empresa") or 0)
                break

        total_empresa += total_tabela * (percentual / 100)

                st.metric(
                    "🏦 Comissão empresa",
                    dinheiro(total_empresa)
                )

                if "alterado_vendedor" in df.columns:

                    alteradas = df[
                        df["alterado_vendedor"] == True
                    ]

                    if not alteradas.empty:

                        st.warning(
                            f"⚠️ Existem {len(alteradas)} proposta(s) "
                            f"alterada(s) pelo vendedor aguardando conferência."
                        )

            st.subheader("📄 Propostas")

            if df.empty:

                st.info(
                    "Nenhuma proposta encontrada."
                )

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
                        "comissao_empresa",
                        "valor_comissao_empresa",
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

                colunas = [
                    c for c in colunas
                    if c in df.columns
                ]

                st.dataframe(
                    df[colunas],
                    use_container_width=True
                )
                            # =========================================
            # EXCLUIR PROPOSTAS (ADMIN)
            # =========================================

            if st.session_state.tipo == "admin":

                st.divider()

                st.subheader("🗑️ Excluir propostas")

                ids_excluir = st.multiselect(
                    "Selecione as propostas para excluir",
                    df["id"].tolist()
                )

                if st.button("Excluir propostas selecionadas"):

                    for venda_id in ids_excluir:

                        supabase.table("vendas") \
                            .delete() \
                            .eq("id", int(venda_id)) \
                            .execute()

                    st.success(
                        "Propostas excluídas!"
                    )

                    st.rerun()

            # =========================================
            # EDITAR PROPOSTA
            # =========================================

            st.divider()

            st.subheader("✏️ Editar proposta")

            ids = df["id"].tolist()

            proposta_id = st.selectbox(
                "Escolha a proposta",
                ids
            )

            proposta = df[
                df["id"] == proposta_id
            ].iloc[0]

            with st.form("editar_proposta"):

                cliente_edit = st.text_input(
                    "Cliente",
                    value=str(
                        proposta.get(
                            "cliente",
                            ""
                        )
                    )
                )

                telefone_edit = st.text_input(
                    "Telefone",
                    value=str(
                        proposta.get(
                            "telefone",
                            ""
                        )
                    )
                )

                valor_edit = st.number_input(
                    "Valor",
                    value=float(
                        proposta.get(
                            "valor",
                            0
                        ) or 0
                    )
                )

                status_edit = st.selectbox(
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
                        proposta.get(
                            "status",
                            "Pendente"
                        )
                    )
                )

                observacao_edit = st.text_area(
                    "Observação",
                    value=str(
                        proposta.get(
                            "observacao",
                            ""
                        ) or ""
                    )
                )

                if st.session_state.tipo == "admin":

                    conferido_edit = st.checkbox(
                        "✅ Conferido",
                        value=bool(
                            proposta.get(
                                "conferido",
                                False
                            )
                        )
                    )

                    observacao_admin = st.text_area(
                        "Observação admin",
                        value=str(
                            proposta.get(
                                "observacao_admin",
                                ""
                            ) or ""
                        )
                    )

                salvar_edit = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar_edit:

                    valor_empresa = proposta.get(
                        "valor_comissao_empresa",
                        0
                    )

                    perc_empresa = proposta.get(
                        "comissao_empresa",
                        0
                    )

                    tabela = proposta.get(
                        "tabela_banco",
                        ""
                    )

                    if status_edit == "Pago":

                        perc_empresa, valor_empresa = (
                            calcular_comissao_empresa(
                                tabela,
                                valor_edit
                            )
                        )

                    dados_update = {

                        "cliente":
                        cliente_edit,

                        "telefone":
                        telefone_edit,

                        "valor":
                        valor_edit,

                        "status":
                        status_edit,

                        "observacao":
                        observacao_edit
                    }

                    if st.session_state.tipo == "admin":

                        dados_update[
                            "conferido"
                        ] = conferido_edit

                        dados_update[
                            "alterado_vendedor"
                        ] = False

                        dados_update[
                            "observacao_admin"
                        ] = observacao_admin

                        dados_update[
                            "comissao_empresa"
                        ] = perc_empresa

                        dados_update[
                            "valor_comissao_empresa"
                        ] = valor_empresa

                    else:

                        dados_update[
                            "alterado_vendedor"
                        ] = True

                        dados_update[
                            "data_alteracao_vendedor"
                        ] = str(
                            datetime.now()
                        )

                    supabase.table(
                        "vendas"
                    ).update(
                        dados_update
                    ).eq(
                        "id",
                        int(proposta_id)
                    ).execute()

                    st.success(
                        "Proposta atualizada!"
                    )

                    st.rerun()

    # =========================================
    # USUÁRIOS
    # =========================================

    elif menu == "👥 Usuários":

        st.header("👥 Usuários")

        with st.form("novo_usuario"):

            nome = st.text_input("Nome")
            usuario = st.text_input("Usuário")
            senha = st.text_input(
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

                dados = {

                    "nome":
                    nome,

                    "usuario":
                    usuario.lower(),

                    "senha_hash":
                    hash_senha(senha),

                    "tipo":
                    tipo,

                    "ativo":
                    True
                }

                supabase.table(
                    "usuarios"
                ).insert(
                    dados
                ).execute()

                st.success(
                    "Usuário criado!"
                )

                st.rerun()

        usuarios = (
            supabase.table("usuarios")
            .select("*")
            .execute()
        )

        df_users = pd.DataFrame(
            usuarios.data
        )

        if not df_users.empty:

            st.subheader(
                "Usuários cadastrados"
            )

            st.dataframe(
                df_users[
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
                # =========================================
    # COMISSÕES
    # =========================================

    elif menu == "💰 Comissões":

        st.header("💰 Regras de Comissão")

        with st.form("nova_regra"):

            produto = st.text_input(
                "Tabela/Banco"
            )

            valor_minimo = st.number_input(
                "Valor mínimo",
                min_value=0.0,
                step=1000.0
            )

            percentual_empresa = st.number_input(
                "% comissão empresa",
                min_value=0.0,
                step=0.01
            )

            salvar = st.form_submit_button(
                "Salvar regra"
            )

            if salvar:

                dados = {

                    "produto":
                    produto.upper(),

                    "valor_minimo":
                    valor_minimo,

                    "percentual_vendedor":
                    0,

                    "percentual_empresa":
                    percentual_empresa,

                    "ativo":
                    True
                }

                supabase.table(
                    "regras_comissao"
                ).insert(
                    dados
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
            .order(
                "valor_minimo"
            )
            .execute()
        )

        df_regras = pd.DataFrame(
            regras.data
        )

        if not df_regras.empty:

            st.subheader(
                "📋 Regras cadastradas"
            )

            st.dataframe(
                df_regras,
                use_container_width=True
            )

            st.divider()

            st.subheader(
                "✏️ Editar regra"
            )

            regra_id = st.selectbox(
                "Escolha a regra",
                df_regras["id"].tolist()
            )

            regra = df_regras[
                df_regras["id"] == regra_id
            ].iloc[0]

            with st.form("editar_regra"):

                produto_edit = st.text_input(
                    "Tabela/Banco",
                    value=str(
                        regra.get(
                            "produto",
                            ""
                        )
                    )
                )

                valor_minimo_edit = st.number_input(
                    "Valor mínimo",
                    min_value=0.0,
                    step=1000.0,
                    value=float(
                        regra.get(
                            "valor_minimo",
                            0
                        ) or 0
                    )
                )

                percentual_empresa_edit = st.number_input(
                    "% comissão empresa",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        regra.get(
                            "percentual_empresa",
                            0
                        ) or 0
                    )
                )

                ativo_edit = st.checkbox(
                    "Ativo",
                    value=bool(
                        regra.get(
                            "ativo",
                            True
                        )
                    )
                )

                salvar_edit = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar_edit:

                    supabase.table(
                        "regras_comissao"
                    ).update({

                        "produto":
                        produto_edit.upper(),

                        "valor_minimo":
                        valor_minimo_edit,

                        "percentual_empresa":
                        percentual_empresa_edit,

                        "ativo":
                        ativo_edit

                    }).eq(
                        "id",
                        int(regra_id)
                    ).execute()

                    st.success(
                        "Regra atualizada!"
                    )

                    st.rerun()

            st.divider()

            st.subheader(
                "🗑️ Excluir regra"
            )

            regra_excluir = st.multiselect(
                "Selecione regras para excluir",
                df_regras["id"].tolist()
            )

            if st.button(
                "Excluir regras"
            ):

                for rid in regra_excluir:

                    supabase.table(
                        "regras_comissao"
                    ).delete().eq(
                        "id",
                        int(rid)
                    ).execute()

                st.success(
                    "Regras excluídas!"
                )

                st.rerun()
