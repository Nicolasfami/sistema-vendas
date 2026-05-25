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
    res = (
        supabase.table("regras_comissao")
        .select("produto")
        .eq("ativo", True)
        .execute()
    )

    tabelas = sorted(list(set([r["produto"] for r in res.data if r.get("produto")])))

    if not tabelas:
        tabelas = ["CLT PADRAO", "V8 ACIMA 36X", "PRESENÇA", "HUBBIE", "OUTROS BANCOS"]

    return tabelas


def calcular_comissao_empresa(tabela_banco, valor):
    res = (
        supabase.table("regras_comissao")
        .select("*")
        .eq("produto", tabela_banco)
        .eq("ativo", True)
        .order("valor_minimo", desc=True)
        .execute()
    )

    percentual_empresa = 0

    for regra in res.data:
        if valor >= float(regra.get("valor_minimo") or 0):
            percentual_empresa = float(regra.get("percentual_empresa") or 0)
            break

    return percentual_empresa, valor * (percentual_empresa / 100)


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
        menu = st.sidebar.radio("Menu", ["📋 Nova Venda", "📊 Painel", "👥 Usuários", "💰 Comissões"])
    else:
        menu = st.sidebar.radio("Menu", ["📋 Nova Venda", "📊 Painel"])

    if menu == "📋 Nova Venda":
        st.header("📋 Cadastro de Venda")

        tabelas = carregar_tabelas()

        with st.form("form_venda"):
            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

            tabela_banco = st.selectbox("Tabela/Banco", tabelas)

            valor = st.number_input("Valor vendido", min_value=0.0, step=1000.0)

            status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])

            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar Venda")

            if salvar:
                perc_empresa, valor_empresa = calcular_comissao_empresa(tabela_banco, valor)

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
                st.success("Venda cadastrada com sucesso!")

    elif menu == "📊 Painel":
        st.header("📊 Painel de Vendas")

        vendas = supabase.table("vendas").select("*").order("id", desc=True).execute()
        df = pd.DataFrame(vendas.data)

        if df.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df["mes_num"] = df["data"].dt.month
            df["ano"] = df["data"].dt.year

            meses = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
            }

            st.subheader("🔎 Filtros")

            c1, c2, c3 = st.columns(3)

            mes_nome = c1.selectbox("Mês", list(meses.values()), index=datetime.now().month - 1)

            anos = sorted(df["ano"].dropna().unique().astype(int).tolist(), reverse=True)
            if not anos:
                anos = [datetime.now().year]

            ano_filtro = c2.selectbox("Ano", anos)

            status_filtro = c3.selectbox("Status", ["Todos", "Pago", "Pendente", "Cancelado"])

            tabelas_filtro = carregar_tabelas()
            tabela_filtro = st.selectbox("Tabela/Banco", ["Todas"] + tabelas_filtro)

            mes_num = [k for k, v in meses.items() if v == mes_nome][0]

            df = df[(df["mes_num"] == mes_num) & (df["ano"] == ano_filtro)]

            if st.session_state.tipo != "admin":
                df = df[df["vendedor_id"] == st.session_state.user_id]

            if status_filtro != "Todos":
                df = df[df["status"] == status_filtro]

            if tabela_filtro != "Todas":
                df = df[df["tabela_banco"] == tabela_filtro]

            if st.session_state.tipo == "admin":
                vendedores = sorted(df["vendedor"].dropna().unique().tolist())
                vendedor_filtro = st.selectbox("Vendedor", ["Todos"] + vendedores)

                if vendedor_filtro != "Todos":
                    df = df[df["vendedor"] == vendedor_filtro]

            total_vendido = df["valor"].fillna(0).sum()
            qtd = len(df)

            c1, c2, c3 = st.columns(3)

            c1.metric("💵 Total vendido", dinheiro(total_vendido))
            c2.metric("📋 Quantidade", qtd)
            c3.metric("🗓️ Mês", mes_nome)

            if st.session_state.tipo == "admin":
                total_empresa = df[df["status"] == "Pago"]["valor_comissao_empresa"].fillna(0).sum()
                st.metric("🏦 Comissão empresa", dinheiro(total_empresa))

                alteradas = df[df["alterado_vendedor"] == True]
                if not alteradas.empty:
                    st.warning(f"⚠️ Existem {len(alteradas)} proposta(s) alterada(s) pelo vendedor aguardando conferência.")

            st.subheader("📄 Propostas")

            if df.empty:
                st.info("Nenhuma proposta encontrada.")
            else:
                if st.session_state.tipo == "admin":
                    colunas = [
                        "id", "data", "vendedor", "cliente", "cpf", "telefone",
                        "tabela_banco", "valor", "status", "comissao_empresa",
                        "valor_comissao_empresa", "conferido", "alterado_vendedor",
                        "observacao", "observacao_admin", "observacao_alteracao"
                    ]
                else:
                    colunas = [
                        "id", "data", "cliente", "telefone",
                        "tabela_banco", "valor", "status", "conferido", "observacao"
                    ]

                colunas = [c for c in colunas if c in df.columns]
                st.dataframe(df[colunas], use_container_width=True)

                if st.session_state.tipo == "admin":
                    st.divider()
                    st.subheader("✅ Conferência rápida")

                    conf_df = df[["id", "cliente", "valor", "status", "conferido", "alterado_vendedor"]].copy()

                    editado = st.data_editor(
                        conf_df,
                        use_container_width=True,
                        disabled=["id", "cliente", "valor", "status", "alterado_vendedor"],
                        hide_index=True
                    )

                    if st.button("Salvar conferências"):
                        for _, row in editado.iterrows():
                            update = {"conferido": bool(row["conferido"])}

                            if bool(row["conferido"]):
                                update["alterado_vendedor"] = False

                            supabase.table("vendas").update(update).eq("id", int(row["id"])).execute()

                        st.success("Conferências salvas!")
                        st.rerun()

                st.divider()
                st.subheader("✏️ Editar proposta")

                venda_id = st.selectbox("Escolha o ID da proposta", df["id"].tolist())

                venda = df[df["id"] == venda_id].iloc[0]

                if st.session_state.tipo != "admin" and bool(venda.get("conferido", False)):
                    st.warning("🔒 Esta proposta já foi conferida pelo admin. O vendedor não pode mais editar.")
                else:
                    tabelas = carregar_tabelas()

                    with st.form("editar_proposta"):
                        cliente_edit = st.text_input("Cliente", value=str(venda.get("cliente", "") or ""))
                        cpf_edit = st.text_input("CPF", value=str(venda.get("cpf", "") or ""))
                        telefone_edit = st.text_input("Telefone", value=str(venda.get("telefone", "") or ""))

                        tabela_atual = str(venda.get("tabela_banco", "") or venda.get("produto", "") or "")
                        tabela_index = tabelas.index(tabela_atual) if tabela_atual in tabelas else 0

                        tabela_edit = st.selectbox("Tabela/Banco", tabelas, index=tabela_index)

                        valor_edit = st.number_input(
                            "Valor vendido",
                            min_value=0.0,
                            step=1000.0,
                            value=float(venda.get("valor") or 0)
                        )

                        status_lista = ["Pendente", "Pago", "Cancelado"]
                        status_atual = str(venda.get("status", "Pendente") or "Pendente")
                        status_index = status_lista.index(status_atual) if status_atual in status_lista else 0

                        status_edit = st.selectbox("Status", status_lista, index=status_index)

                        observacao_edit = st.text_area("Observação", value=str(venda.get("observacao", "") or ""))

                        if st.session_state.tipo == "admin":
                            conferido_edit = st.checkbox("✅ Conferido pelo admin", value=bool(venda.get("conferido", False)))

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
                            observacao_alteracao = st.text_area("Motivo da alteração")

                        salvar_edit = st.form_submit_button("Salvar alterações")

                        if salvar_edit:
                            if st.session_state.tipo == "admin":
                                valor_empresa = valor_edit * (perc_empresa_edit / 100)

                                update = {
                                    "cliente": cliente_edit,
                                    "cpf": cpf_edit,
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
                                perc_empresa, valor_empresa = calcular_comissao_empresa(tabela_edit, valor_edit)

                                update = {
                                    "cliente": cliente_edit,
                                    "cpf": cpf_edit,
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

                            supabase.table("vendas").update(update).eq("id", venda_id).execute()

                            st.success("Proposta atualizada!")
                            st.rerun()

    elif menu == "👥 Usuários":
        st.header("👥 Usuários")

        st.subheader("➕ Criar usuário")

        with st.form("novo_usuario"):
            nome = st.text_input("Nome")
            novo_usuario = st.text_input("Usuário/Login")
            nova_senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo", ["vendedor", "admin"])

            criar = st.form_submit_button("Criar usuário")

            if criar:
                if not nome or not novo_usuario or not nova_senha:
                    st.error("Preencha nome, usuário e senha.")
                else:
                    supabase.table("usuarios").insert({
                        "nome": nome.strip(),
                        "usuario": novo_usuario.strip().lower(),
                        "senha_hash": hash_senha(nova_senha),
                        "tipo": tipo,
                        "ativo": True
                    }).execute()

                    st.success("Usuário criado!")
                    st.rerun()

        usuarios = supabase.table("usuarios").select("*").order("id").execute()
        usuarios_df = pd.DataFrame(usuarios.data)

        if not usuarios_df.empty:
            st.subheader("📋 Usuários cadastrados")
            st.dataframe(usuarios_df[["id", "nome", "usuario", "tipo", "ativo"]], use_container_width=True)

            st.subheader("✏️ Editar usuário")
            user_id = st.selectbox("ID do usuário", usuarios_df["id"].tolist())
            user = usuarios_df[usuarios_df["id"] == user_id].iloc[0]

            novo_nome = st.text_input("Nome", value=str(user["nome"]))
            novo_login = st.text_input("Usuário/Login", value=str(user["usuario"]))
            novo_tipo = st.selectbox("Tipo", ["vendedor", "admin"], index=0 if user["tipo"] == "vendedor" else 1)

            if st.button("Salvar usuário"):
                supabase.table("usuarios").update({
                    "nome": novo_nome.strip(),
                    "usuario": novo_login.strip().lower(),
                    "tipo": novo_tipo
                }).eq("id", user_id).execute()

                st.success("Usuário atualizado!")
                st.rerun()

            st.subheader("🔑 Alterar senha")
            nova_senha = st.text_input("Nova senha", type="password")

            if st.button("Alterar senha"):
                if nova_senha:
                    supabase.table("usuarios").update({
                        "senha_hash": hash_senha(nova_senha)
                    }).eq("id", user_id).execute()

                    st.success("Senha alterada!")
                    st.rerun()

            st.subheader("✅ Ativar / Desativar")

            if st.button("Alterar status"):
                if str(user["usuario"]).lower() == "admin":
                    st.error("Não é permitido desativar o admin principal.")
                else:
                    supabase.table("usuarios").update({
                        "ativo": not bool(user["ativo"])
                    }).eq("id", user_id).execute()

                    st.success("Status alterado!")
                    st.rerun()

            st.subheader("🗑️ Excluir usuário")

            if st.button("Excluir usuário"):
                if str(user["usuario"]).lower() == "admin":
                    st.error("Não é permitido excluir o admin principal.")
                else:
                    supabase.table("usuarios").delete().eq("id", user_id).execute()
                    st.success("Usuário excluído!")
                    st.rerun()

    elif menu == "💰 Comissões":
        st.header("💰 Regras de Comissão")

        st.subheader("➕ Criar nova regra")

        with st.form("nova_regra"):
            produto = st.text_input("Produto/Banco")
            valor_minimo = st.number_input("Valor mínimo", min_value=0.0, step=1000.0)
            percentual_empresa = st.number_input("% empresa", min_value=0.0, step=0.01)

            salvar = st.form_submit_button("Salvar regra")

            if salvar:
                supabase.table("regras_comissao").insert({
                    "produto": produto.strip().upper(),
                    "valor_minimo": valor_minimo,
                    "percentual_vendedor": 0,
                    "percentual_empresa": percentual_empresa,
                    "ativo": True
                }).execute()

                st.success("Regra criada!")
                st.rerun()

        regras = supabase.table("regras_comissao").select("*").order("produto").order("valor_minimo").execute()
        regras_df = pd.DataFrame(regras.data)

        if regras_df.empty:
            st.warning("Nenhuma regra cadastrada.")
        else:
            st.subheader("📋 Regras cadastradas")
            st.dataframe(regras_df, use_container_width=True)

            st.subheader("✏️ Editar regra")

            regra_id = st.selectbox("ID da regra", regras_df["id"].tolist())
            regra = regras_df[regras_df["id"] == regra_id].iloc[0]

            with st.form("editar_regra"):
                produto_edit = st.text_input("Produto/Banco", value=str(regra["produto"]))
                valor_minimo_edit = st.number_input("Valor mínimo", min_value=0.0, step=1000.0, value=float(regra["valor_minimo"] or 0))
                percentual_empresa_edit = st.number_input("% empresa", min_value=0.0, step=0.01, value=float(regra["percentual_empresa"] or 0))
                ativo_edit = st.checkbox("Regra ativa", value=bool(regra["ativo"]))

                salvar_regra = st.form_submit_button("Salvar alterações")

                if salvar_regra:
                    supabase.table("regras_comissao").update({
                        "produto": produto_edit.strip().upper(),
                        "valor_minimo": valor_minimo_edit,
                        "percentual_vendedor": 0,
                        "percentual_empresa": percentual_empresa_edit,
                        "ativo": ativo_edit
                    }).eq("id", regra_id).execute()

                    st.success("Regra atualizada!")
                    st.rerun()

            st.subheader("🗑️ Excluir regra")

            confirmar = st.checkbox("Confirmo que quero excluir esta regra")

            if st.button("Excluir regra"):
                if not confirmar:
                    st.error("Marque a confirmação.")
                else:
                    supabase.table("regras_comissao").delete().eq("id", regra_id).execute()
                    st.success("Regra excluída!")
                    st.rerun()
