
import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import hashlib

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

# =========================
# CONFIGURAÇÕES
# =========================

st.set_page_config(page_title="CRM TK Soluções", layout="wide")

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


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
            st.session_state.user_id = user["id"]
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
            ["📋 Nova Venda", "📊 Painel", "👥 Usuários", "💰 Comissões"]
        )
    else:
        menu = st.sidebar.radio(
            "Menu",
            ["📋 Nova Venda", "📊 Painel"]
        )

    # =========================
    # NOVA VENDA
    # =========================

    if menu == "📋 Nova Venda":
        st.header("📋 Cadastro de Venda")

        tabelas = carregar_tabelas()

        with st.form("form_venda", clear_on_submit=True):
            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

            tabela_banco = st.selectbox("Tabela/Banco", tabelas)

            valor = st.number_input("Valor vendido", min_value=0.0, step=1000.0)

            status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])

            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar venda")

            if salvar:
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
                st.success("Venda cadastrada!")
                st.rerun()

    # =========================
    # PAINEL
    # =========================

    elif menu == "📊 Painel":
        st.header("📊 Painel de Vendas")

        col_refresh_1, col_refresh_2 = st.columns([1, 4])

        with col_refresh_1:
            if st.button("🔄 Atualizar agora"):
                st.rerun()

        with col_refresh_2:
            st.caption("O painel atualiza automaticamente sem precisar apertar F5.")

        if st_autorefresh is not None:
            intervalo = 10000 if st.session_state.tipo == "admin" else 15000
            st_autorefresh(
                interval=intervalo,
                limit=None,
                key=f"auto_refresh_{st.session_state.tipo}"
            )

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

            st.subheader("🔎 Filtros")

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

                st.metric("🏦 Comissão empresa", dinheiro(total_empresa))

                alteradas = df[df["alterado_vendedor"] == True]

                if not alteradas.empty:
                    st.warning(
                        f"⚠️ Existem {len(alteradas)} proposta(s) alterada(s) pelo vendedor aguardando conferência."
                    )

            st.divider()
            st.subheader("📄 Propostas")

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

                st.dataframe(df[colunas], use_container_width=True)

                # =========================
                # AÇÕES RÁPIDAS ADMIN
                # =========================

                if st.session_state.tipo == "admin":
                    st.divider()
                    st.subheader("⚙️ Ações rápidas")

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
                st.subheader("✏️ Editar proposta")

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
                        telefone_edit = st.text_input("Telefone", value=str(proposta.get("telefone", "") or ""))

                        tabelas_edit = carregar_tabelas()
                        tabela_atual = str(proposta.get("tabela_banco", "") or proposta.get("produto", "") or "")
                        tabela_index = tabelas_edit.index(tabela_atual) if tabela_atual in tabelas_edit else 0

                        tabela_edit = st.selectbox("Tabela/Banco", tabelas_edit, index=tabela_index)

                        valor_edit = st.number_input(
                            "Valor",
                            min_value=0.0,
                            step=1000.0,
                            value=float(proposta.get("valor") or 0)
                        )

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
                            perc_empresa = calcular_percentual_empresa_venda(tabela_edit, valor_edit)
                            valor_empresa = float(valor_edit) * (perc_empresa / 100)

                            dados_update = {
                                "cliente": cliente_edit,
                                "cpf": cpf_edit,
                                "telefone": telefone_edit,
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
        st.header("👥 Usuários")

        st.subheader("➕ Criar usuário")

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
            st.subheader("📋 Usuários cadastrados")
            st.dataframe(df_users[["id", "nome", "usuario", "tipo", "ativo"]], use_container_width=True)

            st.divider()
            st.subheader("✏️ Editar usuário")

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
            st.subheader("🔑 Alterar senha")

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
            st.subheader("✅ Ativar / Desativar")

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
            st.subheader("🗑️ Excluir usuário")

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
        st.header("💰 Regras de Comissão")

        st.subheader("➕ Criar nova regra")

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
            st.subheader("📋 Regras cadastradas")
            st.dataframe(df_regras, use_container_width=True)

            st.divider()
            st.subheader("✏️ Editar regra")

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
            st.subheader("🗑️ Excluir regra")

            confirmar = st.checkbox("Confirmo que quero excluir esta regra")

            if st.button("Excluir regra"):
                if not confirmar:
                    st.error("Marque a confirmação.")
                else:
                    supabase.table("regras_comissao").delete().eq("id", int(regra_id)).execute()
                    st.success("Regra excluída!")
                    st.rerun()
