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

st.set_page_config(page_title="CRM TK Soluções", layout="wide")


# =========================
# FUNÇÕES
# =========================

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()


def dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


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


def carregar_tabelas():
    regras = (
        supabase.table("regras_comissao")
        .select("produto")
        .eq("ativo", True)
        .execute()
    )

    tabelas = sorted(list(set([r["produto"] for r in regras.data])))

    if not tabelas:
        tabelas = [
            "CLT PADRAO",
            "V8 ACIMA 36X",
            "PRESENÇA",
            "HUBBIE",
            "OUTROS BANCOS"
        ]

    return tabelas


def calcular_comissao_empresa(tabela_banco, valor):
    regras = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("produto", tabela_banco)
        .eq("ativo", True)
        .order("valor_minimo", desc=True)
        .execute()
    )

    percentual_empresa = 0

    for regra in regras.data:
        if valor >= float(regra["valor_minimo"]):
            percentual_empresa = float(regra["percentual_empresa"] or 0)
            break

    valor_empresa = valor * (percentual_empresa / 100)

    return percentual_empresa, valor_empresa


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

else:

    st.sidebar.success(f"👤 {st.session_state.nome}")

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

        tabelas = carregar_tabelas()

        with st.form("form_venda"):

            vendedor = st.text_input(
                "Vendedor",
                value=st.session_state.usuario
            )

            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

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

            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar Venda")

            if salvar:

                perc_empresa, valor_empresa = calcular_comissao_empresa(
                    tabela_banco,
                    valor
                )

                dados = {
                    "data": str(datetime.now()),
                    "vendedor": vendedor.strip().lower(),
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

                st.success("Venda cadastrada com sucesso!")
                    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":

        st.header("📊 Painel de Vendas")

        vendas = supabase.table("vendas").select("*").execute()

        df = pd.DataFrame(vendas.data)

        if not df.empty:

            df["data"] = pd.to_datetime(df["data"])

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

            df["mes_num"] = df["data"].dt.month
            df["mes"] = df["mes_num"].map(meses)
            df["ano"] = df["data"].dt.year

            # =========================
            # FILTROS
            # =========================

            st.subheader("🔎 Filtros")

            c1, c2, c3 = st.columns(3)

            with c1:
                mes_filtro = st.selectbox(
                    "Mês",
                    list(meses.values()),
                    index=datetime.now().month - 1
                )

            with c2:
                ano_filtro = st.selectbox(
                    "Ano",
                    sorted(df["ano"].unique(), reverse=True)
                )

            with c3:
                status_filtro = st.selectbox(
                    "Status",
                    ["Todos", "Pago", "Pendente", "Cancelado"]
                )

            tabelas = sorted(df["tabela_banco"].dropna().unique())

            tabela_filtro = st.selectbox(
                "Tabela/Banco",
                ["Todas"] + list(tabelas)
            )

            # =========================
            # FILTRO VENDEDOR
            # =========================

            if st.session_state.tipo != "admin":
                df = df[
                    df["vendedor"] ==
                    st.session_state.usuario
                ]

            else:

                vendedores = sorted(df["vendedor"].dropna().unique())

                vendedor_filtro = st.selectbox(
                    "Vendedor",
                    ["Todos"] + list(vendedores)
                )

                if vendedor_filtro != "Todos":
                    df = df[
                        df["vendedor"] == vendedor_filtro
                    ]

            # =========================
            # APLICA FILTROS
            # =========================

            mes_num = [
                k for k, v in meses.items()
                if v == mes_filtro
            ][0]

            df = df[
                (df["mes_num"] == mes_num)
                &
                (df["ano"] == ano_filtro)
            ]

            if status_filtro != "Todos":
                df = df[
                    df["status"] == status_filtro
                ]

            if tabela_filtro != "Todas":
                df = df[
                    df["tabela_banco"] == tabela_filtro
                ]

            # =========================
            # RESUMO
            # =========================

            total_vendido = df["valor"].sum()

            qtd = len(df)

            total_empresa = df[
                df["status"] == "Pago"
            ]["valor_comissao_empresa"].sum()

            c1, c2, c3, c4 = st.columns(4)

            with c1:
                st.metric(
                    "💵 Total vendido",
                    dinheiro(total_vendido)
                )

            with c2:
                st.metric(
                    "📋 Quantidade",
                    qtd
                )

            with c3:

                if st.session_state.tipo == "admin":

                    st.metric(
                        "🏦 Comissão empresa",
                        dinheiro(total_empresa)
                    )

            with c4:
                st.metric(
                    "🗓️ Mês",
                    mes_filtro
                )

            # =========================
            # ALERTAS
            # =========================

            if st.session_state.tipo == "admin":

                alteradas = df[
                    df["alterado_vendedor"] == True
                ]

                if len(alteradas) > 0:

                    st.warning(
                        f"⚠️ Existem "
                        f"{len(alteradas)} "
                        f"proposta(s) alterada(s) "
                        f"pelo vendedor aguardando conferência."
                    )

            # =========================
            # LISTAGEM
            # =========================

            st.subheader("📄 Propostas")

            colunas = [
                "id",
                "data",
                "cliente",
                "telefone",
                "produto",
                "valor",
                "status"
            ]

            if st.session_state.tipo == "admin":

                colunas += [
                    "comissao_empresa",
                    "valor_comissao_empresa",
                    "conferido",
                    "alterado_vendedor"
                ]

            st.dataframe(
                df[colunas],
                use_container_width=True
            )
                        # =========================
            # EDITAR PROPOSTA
            # =========================

            st.divider()
            st.subheader("✏️ Editar proposta")

            if df.empty:

                st.info("Nenhuma proposta para editar nesse filtro.")

            else:

                venda_id = st.selectbox(
                    "Escolha o ID da proposta",
                    df["id"].tolist()
                )

                venda = df[df["id"] == venda_id].iloc[0]

                if (
                    st.session_state.tipo != "admin"
                    and bool(venda.get("conferido", False)) == True
                ):

                    st.warning(
                        "🔒 Esta proposta já foi conferida pelo admin. "
                        "O vendedor não pode mais editar."
                    )

                else:

                    tabelas = carregar_tabelas()

                    with st.form("editar_proposta"):

                        cliente_edit = st.text_input(
                            "Cliente",
                            value=str(venda.get("cliente", "") or "")
                        )

                        telefone_edit = st.text_input(
                            "Telefone",
                            value=str(venda.get("telefone", "") or "")
                        )

                        tabela_atual = str(
                            venda.get("tabela_banco", "")
                            or venda.get("produto", "")
                            or ""
                        )

                        tabela_index = (
                            tabelas.index(tabela_atual)
                            if tabela_atual in tabelas
                            else 0
                        )

                        tabela_edit = st.selectbox(
                            "Tabela/Banco",
                            tabelas,
                            index=tabela_index
                        )

                        valor_edit = st.number_input(
                            "Valor vendido",
                            min_value=0.0,
                            step=1000.0,
                            value=float(venda.get("valor") or 0)
                        )

                        status_lista = [
                            "Pendente",
                            "Pago",
                            "Cancelado"
                        ]

                        status_atual = str(
                            venda.get("status", "Pendente")
                            or "Pendente"
                        )

                        status_index = (
                            status_lista.index(status_atual)
                            if status_atual in status_lista
                            else 0
                        )

                        status_edit = st.selectbox(
                            "Status",
                            status_lista,
                            index=status_index
                        )

                        observacao_edit = st.text_area(
                            "Observação",
                            value=str(venda.get("observacao", "") or "")
                        )

                        if st.session_state.tipo == "admin":

                            conferido_edit = st.checkbox(
                                "✅ Conferido pelo admin",
                                value=bool(venda.get("conferido", False))
                            )

                            perc_empresa_edit = st.number_input(
                                "% comissão empresa",
                                min_value=0.0,
                                step=0.01,
                                value=float(venda.get("comissao_empresa") or 0)
                            )

                            observacao_admin_edit = st.text_area(
                                "Observação interna admin",
                                value=str(venda.get("observacao_admin", "") or "")
                            )

                        else:

                            observacao_alteracao = st.text_area(
                                "Motivo da alteração",
                                placeholder=(
                                    "Ex: alterei status para pago, "
                                    "corrigi valor ou telefone..."
                                )
                            )

                        salvar_edit = st.form_submit_button(
                            "Salvar alterações"
                        )

                        if salvar_edit:

                            if st.session_state.tipo == "admin":

                                valor_empresa = (
                                    valor_edit *
                                    (perc_empresa_edit / 100)
                                )

                                update = {
                                    "cliente": cliente_edit,
                                    "telefone": telefone_edit,
                                    "produto": tabela_edit,
                                    "tabela_banco": tabela_edit,
                                    "valor": valor_edit,
                                    "status": status_edit,
                                    "observacao": observacao_edit,
                                    "conferido": conferido_edit,
                                    "comissao_empresa": perc_empresa_edit,
                                    "valor_comissao_empresa": valor_empresa,
                                    "observacao_admin": observacao_admin_edit
                                }

                                if conferido_edit:
                                    update["alterado_vendedor"] = False

                            else:

                                perc_empresa, valor_empresa = (
                                    calcular_comissao_empresa(
                                        tabela_edit,
                                        valor_edit
                                    )
                                )

                                update = {
                                    "cliente": cliente_edit,
                                    "telefone": telefone_edit,
                                    "produto": tabela_edit,
                                    "tabela_banco": tabela_edit,
                                    "valor": valor_edit,
                                    "status": status_edit,
                                    "observacao": observacao_edit,
                                    "comissao_empresa": perc_empresa,
                                    "valor_comissao_empresa": valor_empresa,
                                    "alterado_vendedor": True,
                                    "data_alteracao_vendedor": str(datetime.now()),
                                    "observacao_alteracao": observacao_alteracao,
                                    "conferido": False
                                }

                            supabase.table("vendas").update(update).eq(
                                "id",
                                venda_id
                            ).execute()

                            st.success("Proposta atualizada com sucesso!")
                            st.rerun()

        else:

            st.warning("Nenhuma venda cadastrada.")

    # =========================
    # USUÁRIOS
    # =========================

    elif menu == "👥 Usuários":

        st.header("👥 Usuários")

        st.subheader("➕ Criar usuário")

        with st.form("novo_usuario"):

            nome = st.text_input("Nome")
            novo_usuario = st.text_input("Usuário/Login")
            nova_senha = st.text_input("Senha", type="password")

            tipo = st.selectbox(
                "Tipo",
                [
                    "vendedor",
                    "admin"
                ]
            )

            criar = st.form_submit_button("Criar usuário")

            if criar:

                if not nome or not novo_usuario or not nova_senha:

                    st.error("Preencha nome, usuário e senha.")

                else:

                    dados_usuario = {
                        "nome": nome.strip(),
                        "usuario": novo_usuario.strip().lower(),
                        "senha_hash": hash_senha(nova_senha),
                        "tipo": tipo,
                        "ativo": True
                    }

                    try:

                        supabase.table("usuarios").insert(
                            dados_usuario
                        ).execute()

                        st.success("Usuário criado com sucesso!")
                        st.rerun()

                    except Exception as e:

                        st.error(f"Erro ao criar usuário: {e}")

        st.divider()

        usuarios = (
            supabase.table("usuarios")
            .select("*")
            .order("id")
            .execute()
        )

        usuarios_df = pd.DataFrame(usuarios.data)

        if not usuarios_df.empty:

            st.subheader("📋 Usuários cadastrados")

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

            st.subheader("✏️ Editar usuário")

            user_id_editar = st.selectbox(
                "Escolha o ID para editar",
                usuarios_df["id"].tolist(),
                key="editar_user"
            )

            usuario_atual = usuarios_df[
                usuarios_df["id"] == user_id_editar
            ].iloc[0]

            novo_nome_edit = st.text_input(
                "Nome",
                value=str(usuario_atual["nome"])
            )

            novo_usuario_edit = st.text_input(
                "Usuário/Login",
                value=str(usuario_atual["usuario"])
            )

            tipo_index = (
                0
                if usuario_atual["tipo"] == "vendedor"
                else 1
            )

            novo_tipo_edit = st.selectbox(
                "Tipo",
                [
                    "vendedor",
                    "admin"
                ],
                index=tipo_index
            )

            if st.button("Salvar alterações do usuário"):

                supabase.table("usuarios").update({
                    "nome": novo_nome_edit.strip(),
                    "usuario": novo_usuario_edit.strip().lower(),
                    "tipo": novo_tipo_edit
                }).eq("id", user_id_editar).execute()

                st.success("Usuário atualizado!")
                st.rerun()

            st.divider()

            st.subheader("🔑 Alterar senha")

            user_id_senha = st.selectbox(
                "Escolha o ID para alterar senha",
                usuarios_df["id"].tolist(),
                key="senha_user"
            )

            nova_senha_alt = st.text_input(
                "Nova senha",
                type="password"
            )

            if st.button("Alterar senha"):

                if nova_senha_alt:

                    supabase.table("usuarios").update({
                        "senha_hash": hash_senha(nova_senha_alt)
                    }).eq("id", user_id_senha).execute()

                    st.success("Senha alterada!")
                    st.rerun()

                else:

                    st.error("Digite a nova senha.")

            st.divider()

            st.subheader("✅ Ativar / Desativar usuário")

            user_id_status = st.selectbox(
                "Escolha o ID para ativar/desativar",
                usuarios_df["id"].tolist(),
                key="status_user"
            )

            if st.button("Alterar status"):

                usuario_status = usuarios_df[
                    usuarios_df["id"] == user_id_status
                ].iloc[0]

                if str(usuario_status["usuario"]).lower() == "admin":

                    st.error(
                        "Não é permitido desativar o administrador principal."
                    )

                else:

                    novo_status = not bool(usuario_status["ativo"])

                    supabase.table("usuarios").update({
                        "ativo": novo_status
                    }).eq("id", user_id_status).execute()

                    st.success("Status atualizado!")
                    st.rerun()

            st.divider()

            st.subheader("🗑️ Excluir usuário")

            user_id_excluir = st.selectbox(
                "Escolha o ID para excluir",
                usuarios_df["id"].tolist(),
                key="excluir_user"
            )

            if st.button("Excluir usuário"):

                usuario_excluir = usuarios_df[
                    usuarios_df["id"] == user_id_excluir
                ].iloc[0]

                if str(usuario_excluir["usuario"]).lower() == "admin":

                    st.error(
                        "Não é permitido excluir o administrador principal."
                    )

                else:

                    supabase.table("usuarios").delete().eq(
                        "id",
                        user_id_excluir
                    ).execute()

                    st.success("Usuário excluído!")
                    st.rerun()

    # =========================
    # COMISSÕES
    # =========================

    elif menu == "💰 Comissões":

        st.header("💰 Regras de Comissão")

        st.subheader("➕ Criar nova regra")

        with st.form("nova_regra"):

            produto = st.text_input("Produto/Banco")

            valor_minimo = st.number_input(
                "Valor mínimo",
                min_value=0.0,
                step=1000.0
            )

            percentual_vendedor = st.number_input(
                "% vendedor",
                min_value=0.0,
                step=0.01
            )

            percentual_empresa = st.number_input(
                "% empresa",
                min_value=0.0,
                step=0.01
            )

            salvar = st.form_submit_button("Salvar regra")

            if salvar:

                supabase.table("regras_comissao").insert({
                    "produto": produto.strip().upper(),
                    "valor_minimo": valor_minimo,
                    "percentual_vendedor": percentual_vendedor,
                    "percentual_empresa": percentual_empresa,
                    "ativo": True
                }).execute()

                st.success("Regra criada!")
                st.rerun()

        st.divider()

        regras = (
            supabase.table("regras_comissao")
            .select("*")
            .order("produto")
            .order("valor_minimo")
            .execute()
        )

        regras_df = pd.DataFrame(regras.data)

        if regras_df.empty:

            st.warning("Nenhuma regra cadastrada ainda.")

        else:

            st.subheader("📋 Regras cadastradas")

            st.dataframe(
                regras_df,
                use_container_width=True
            )

            st.divider()

            st.subheader("✏️ Editar regra")

            regra_id = st.selectbox(
                "Escolha o ID da regra",
                regras_df["id"].tolist(),
                key="editar_regra"
            )

            regra_atual = regras_df[
                regras_df["id"] == regra_id
            ].iloc[0]

            with st.form("editar_regra_form"):

                produto_edit = st.text_input(
                    "Produto/Banco",
                    value=str(regra_atual["produto"])
                )

                valor_minimo_edit = st.number_input(
                    "Valor mínimo",
                    min_value=0.0,
                    step=1000.0,
                    value=float(regra_atual["valor_minimo"] or 0)
                )

                percentual_vendedor_edit = st.number_input(
                    "% vendedor",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        regra_atual["percentual_vendedor"] or 0
                    )
                )

                percentual_empresa_edit = st.number_input(
                    "% empresa",
                    min_value=0.0,
                    step=0.01,
                    value=float(
                        regra_atual["percentual_empresa"] or 0
                    )
                )

                ativo_edit = st.checkbox(
                    "Regra ativa",
                    value=bool(regra_atual["ativo"])
                )

                salvar_edicao = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar_edicao:

                    supabase.table("regras_comissao").update({
                        "produto": produto_edit.strip().upper(),
                        "valor_minimo": valor_minimo_edit,
                        "percentual_vendedor": percentual_vendedor_edit,
                        "percentual_empresa": percentual_empresa_edit,
                        "ativo": ativo_edit
                    }).eq("id", regra_id).execute()

                    st.success("Regra atualizada!")
                    st.rerun()

            st.divider()

            st.subheader("🗑️ Excluir regra")

            regra_id_excluir = st.selectbox(
                "Escolha o ID para excluir",
                regras_df["id"].tolist(),
                key="excluir_regra"
            )

            confirmar = st.checkbox(
                "Confirmo que quero excluir esta regra"
            )

            if st.button("Excluir regra"):

                if not confirmar:

                    st.error(
                        "Marque a confirmação antes de excluir."
                    )

                else:

                    supabase.table("regras_comissao").delete().eq(
                        "id",
                        regra_id_excluir
                    ).execute()

                    st.success("Regra excluída!")
                    st.rerun()
