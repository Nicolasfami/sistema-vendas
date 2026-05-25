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

    res = supabase.table("usuarios").select("*").eq("usuario", usuario).eq("ativo", True).execute()

    if not res.data:
        return None

    user = res.data[0]

    if user["senha_hash"] == senha_hash:
        return user

    return None


def calcular_comissao(produto, valor):
    percentual = 0

    if produto == "CLT PADRAO OUTROS BANCOS":
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

    return percentual, valor * (percentual / 100)


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
        menu = st.sidebar.radio("Menu", ["📋 Nova Venda", "📊 Painel", "👥 Usuários"])
    else:
        menu = st.sidebar.radio("Menu", ["📋 Nova Venda", "📊 Painel"])

    if menu == "📋 Nova Venda":
        st.header("📋 Cadastro de Venda")

        with st.form("form_venda"):
            vendedor = st.text_input("Vendedor", value=st.session_state.usuario)
            cliente = st.text_input("Cliente")
            cpf = st.text_input("CPF")
            telefone = st.text_input("Telefone")

            produto = st.selectbox("Produto", ["CLT PADRAO OUTROS BANCOS", "V8 PRESENÇA"])
            valor = st.number_input("Valor vendido", min_value=0.0, step=1000.0)

            status = st.selectbox("Status", ["Pendente", "Pago", "Cancelado"])
            observacao = st.text_area("Observação")

            salvar = st.form_submit_button("Salvar Venda")

            if salvar:
                percentual, valor_comissao = calcular_comissao(produto, valor)

                dados = {
                    "data": str(datetime.now()),
                    "vendedor": vendedor.strip().lower(),
                    "cliente": cliente,
                    "cpf": cpf,
                    "telefone": telefone,
                    "produto": produto,
                    "valor": valor,
                    "status": status,
                    "percentual_comissao": percentual,
                    "valor_comissao": valor_comissao,
                    "conferido": False,
                    "observacao": observacao
                }

                supabase.table("vendas").insert(dados).execute()

                st.success("Venda cadastrada com sucesso!")
                st.info(f"Comissão: {percentual:.2f}% | R$ {valor_comissao:,.2f}")

    elif menu == "📊 Painel":
        st.header("📊 Painel de Vendas")

        response = supabase.table("vendas").select("*").order("id", desc=True).execute()
        dados = response.data

        if not dados:
            st.warning("Nenhuma venda cadastrada.")
        else:
            df = pd.DataFrame(dados)

            if st.session_state.tipo != "admin":
                df = df[df["vendedor"].str.lower() == st.session_state.usuario.lower()]

            total_vendas = df["valor"].fillna(0).sum()
            total_comissao = df["valor_comissao"].fillna(0).sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("💵 Total vendido", f"R$ {total_vendas:,.2f}")
            col2.metric("📋 Quantidade", len(df))
            col3.metric("💰 Comissão vendedor", f"R$ {total_comissao:,.2f}")

            st.divider()

            st.subheader("📄 Propostas")

            if st.session_state.tipo == "admin":
                st.dataframe(df, use_container_width=True)
            else:
                colunas_vendedor = [
                    "id", "data", "cliente", "telefone", "produto",
                    "valor", "status", "percentual_comissao",
                    "valor_comissao", "observacao"
                ]
                st.dataframe(df[colunas_vendedor], use_container_width=True)

            st.divider()

            st.subheader("✏️ Editar proposta")

            if df.empty:
                st.warning("Nenhuma proposta para editar.")
            else:
                venda_id = st.selectbox("Escolha o ID da proposta", df["id"].tolist())

                venda_atual = df[df["id"] == venda_id].iloc[0]

                with st.form("editar_venda"):
                    cliente_edit = st.text_input("Cliente", value=str(venda_atual.get("cliente", "")))
                    cpf_edit = st.text_input("CPF", value=str(venda_atual.get("cpf", "")))
                    telefone_edit = st.text_input("Telefone", value=str(venda_atual.get("telefone", "")))

                    produto_lista = ["CLT PADRAO OUTROS BANCOS", "V8 PRESENÇA"]
                    produto_atual = venda_atual.get("produto", "CLT PADRAO OUTROS BANCOS")
                    produto_index = produto_lista.index(produto_atual) if produto_atual in produto_lista else 0

                    produto_edit = st.selectbox("Produto", produto_lista, index=produto_index)

                    valor_edit = st.number_input(
                        "Valor vendido",
                        min_value=0.0,
                        step=1000.0,
                        value=float(venda_atual.get("valor") or 0)
                    )

                    status_lista = ["Pendente", "Pago", "Cancelado"]
                    status_atual = venda_atual.get("status", "Pendente")
                    status_index = status_lista.index(status_atual) if status_atual in status_lista else 0

                    status_edit = st.selectbox("Status", status_lista, index=status_index)

                    observacao_edit = st.text_area(
                        "Observação",
                        value=str(venda_atual.get("observacao") or "")
                    )

                    if st.session_state.tipo == "admin":
                        conferido_edit = st.checkbox(
                            "Conferido pelo admin",
                            value=bool(venda_atual.get("conferido") or False)
                        )

                        perc_vendedor_edit = st.number_input(
                            "Percentual comissão vendedor (%)",
                            min_value=0.0,
                            step=0.05,
                            value=float(venda_atual.get("percentual_comissao") or 0)
                        )

                        comissao_empresa_edit = st.number_input(
                            "Percentual comissão empresa (%)",
                            min_value=0.0,
                            step=0.05,
                            value=float(venda_atual.get("comissao_empresa") or 0)
                        )

                        observacao_admin_edit = st.text_area(
                            "Observação interna admin",
                            value=str(venda_atual.get("observacao_admin") or "")
                        )
                    else:
                        perc_vendedor_edit, _ = calcular_comissao(produto_edit, valor_edit)
                        conferido_edit = bool(venda_atual.get("conferido") or False)
                        comissao_empresa_edit = float(venda_atual.get("comissao_empresa") or 0)
                        observacao_admin_edit = str(venda_atual.get("observacao_admin") or "")

                    salvar_edicao = st.form_submit_button("Salvar alterações")

                    if salvar_edicao:
                        if st.session_state.tipo == "admin":
                            percentual_final = perc_vendedor_edit
                        else:
                            percentual_final, _ = calcular_comissao(produto_edit, valor_edit)

                        valor_comissao_final = valor_edit * (percentual_final / 100)
                        valor_comissao_empresa_final = valor_edit * (comissao_empresa_edit / 100)

                        atualizacao = {
                            "cliente": cliente_edit,
                            "cpf": cpf_edit,
                            "telefone": telefone_edit,
                            "produto": produto_edit,
                            "valor": valor_edit,
                            "status": status_edit,
                            "observacao": observacao_edit,
                            "percentual_comissao": percentual_final,
                            "valor_comissao": valor_comissao_final,
                        }

                        if st.session_state.tipo == "admin":
                            atualizacao["conferido"] = conferido_edit
                            atualizacao["comissao_empresa"] = comissao_empresa_edit
                            atualizacao["valor_comissao_empresa"] = valor_comissao_empresa_final
                            atualizacao["observacao_admin"] = observacao_admin_edit

                        supabase.table("vendas").update(atualizacao).eq("id", venda_id).execute()

                        st.success("Proposta atualizada com sucesso!")
                        st.rerun()

    elif menu == "👥 Usuários":
        st.header("👥 Usuários")

        st.subheader("➕ Criar usuário")

        with st.form("novo_usuario"):
            nome = st.text_input("Nome")
            novo_usuario = st.text_input("Usuário")
            nova_senha = st.text_input("Senha", type="password")
            tipo = st.selectbox("Tipo", ["vendedor", "admin"])

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
                        supabase.table("usuarios").insert(dados_usuario).execute()
                        st.success("Usuário criado com sucesso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao criar usuário: {e}")

        st.divider()

        usuarios = supabase.table("usuarios").select("*").order("id").execute()
        usuarios_df = pd.DataFrame(usuarios.data)

        if not usuarios_df.empty:
            st.subheader("📋 Usuários cadastrados")

            st.dataframe(
                usuarios_df[["id", "nome", "usuario", "tipo", "ativo"]],
                use_container_width=True
            )

            st.divider()

            st.subheader("✏️ Editar usuário")

            user_id_editar = st.selectbox("Escolha o ID para editar", usuarios_df["id"].tolist(), key="editar")
            usuario_atual = usuarios_df[usuarios_df["id"] == user_id_editar].iloc[0]

            novo_nome_edit = st.text_input("Nome", value=usuario_atual["nome"])
            novo_usuario_edit = st.text_input("Usuário/Login", value=usuario_atual["usuario"])

            tipo_atual = usuario_atual["tipo"]
            tipo_index = 0 if tipo_atual == "vendedor" else 1

            novo_tipo_edit = st.selectbox("Tipo", ["vendedor", "admin"], index=tipo_index)

            if st.button("Salvar alterações do usuário"):
                supabase.table("usuarios").update({
                    "nome": novo_nome_edit.strip(),
                    "usuario": novo_usuario_edit.strip().lower(),
                    "tipo": novo_tipo_edit
                }).eq("id", user_id_editar).execute()

                st.success("Usuário atualizado com sucesso!")
                st.rerun()

            st.divider()

            st.subheader("🔑 Alterar senha")

            user_id_senha = st.selectbox("Escolha o ID para alterar senha", usuarios_df["id"].tolist(), key="senha")
            nova_senha_alt = st.text_input("Nova senha", type="password")

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
                key="status"
            )

            if st.button("Alterar status"):
                usuario_status = usuarios_df[usuarios_df["id"] == user_id_status].iloc[0]

                if user_id_status == 1:
                    st.error("Não é permitido desativar o administrador principal.")
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
                key="excluir"
            )

            if st.button("Excluir usuário"):
                if user_id_excluir == 1:
                    st.error("Não é permitido excluir o administrador principal.")
                else:
                    supabase.table("usuarios").delete().eq("id", user_id_excluir).execute()

                    st.success("Usuário excluído com sucesso!")
                    st.rerun()
