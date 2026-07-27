import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests as _req
from supabase import create_client
from datetime import datetime
import hashlib
import re
from pathlib import Path
import io
import math
import time
import threading

st.set_page_config(page_title="OPERAX SALES", layout="wide", page_icon="🌀")

# ============================================================
# PWA - INSTALA O APP NO CELULAR
# ============================================================
st.markdown("""
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#0ea5e9">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="OPERAX">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/service-worker.js');
        }
    </script>
""", unsafe_allow_html=True)

SUPABASE_URL = "https://ynxpowhzhnwqazdxshch.supabase.co"
SUPABASE_KEY = "sb_publishable_aATPGJyG-Q8KuLLflByr8w_nrHxt0mt"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RAILWAY_URL = "https://operax-whatsapp-production.up.railway.app"

# ============================================================
# ANEXO DE DOCUMENTOS NA VENDA (contracheque, comprovante, etc.)
# ============================================================
BUCKET_DOCUMENTOS_VENDA = "documentos-vendas"
TABELA_PRODUTOS_DOC = "produtos_requer_documento"
TABELA_VENDA_DOCUMENTOS = "venda_documentos"
TAMANHO_MAXIMO_DOCUMENTO_MB = 5
TIPOS_DOCUMENTO_PERMITIDOS = {"application/pdf", "image/jpeg", "image/jpg", "image/png"}
CATEGORIAS_DOCUMENTO_VENDA = ["Contracheque", "Comprovante de Endereço", "RG/CPF", "Outros"]


def carregar_produtos_requer_documento():
    try:
        res = supabase.table(TABELA_PRODUTOS_DOC).select("produto").execute()
        return set(r["produto"] for r in (res.data or []))
    except Exception:
        return set()


def alternar_produto_requer_documento(produto, requer):
    try:
        if requer:
            supabase.table(TABELA_PRODUTOS_DOC).upsert({"produto": produto}, on_conflict="produto").execute()
        else:
            supabase.table(TABELA_PRODUTOS_DOC).delete().eq("produto", produto).execute()
        return True
    except Exception:
        return False


def validar_arquivo_documento(arquivo):
    if arquivo is None:
        return True, ""
    tamanho_mb = arquivo.size / (1024 * 1024)
    if tamanho_mb > TAMANHO_MAXIMO_DOCUMENTO_MB:
        return False, f"'{arquivo.name}' tem {tamanho_mb:.1f}MB — o limite é {TAMANHO_MAXIMO_DOCUMENTO_MB}MB."
    if arquivo.type not in TIPOS_DOCUMENTO_PERMITIDOS:
        return False, f"'{arquivo.name}' tem um tipo não permitido. Envie PDF, JPG ou PNG."
    return True, ""


def enviar_documento_para_storage(arquivo, cpf, tipo_documento):
    extensao = Path(arquivo.name).suffix or ""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nome_seguro = re.sub(r"[^a-zA-Z0-9_.-]", "_", Path(arquivo.name).stem) + extensao
    tipo_seguro = re.sub(r"[^a-zA-Z0-9_-]", "_", tipo_documento)
    caminho = f"{cpf}/{timestamp}_{tipo_seguro}_{nome_seguro}"
    conteudo = arquivo.getvalue()
    supabase.storage.from_(BUCKET_DOCUMENTOS_VENDA).upload(
        path=caminho,
        file=conteudo,
        file_options={"content-type": arquivo.type}
    )
    return caminho, len(conteudo)


def salvar_registro_documento_venda(venda_id, tipo_documento, nome_arquivo, caminho_storage, tamanho_bytes, enviado_por):
    try:
        supabase.table(TABELA_VENDA_DOCUMENTOS).insert({
            "venda_id": venda_id,
            "tipo_documento": tipo_documento,
            "nome_arquivo": nome_arquivo,
            "caminho_storage": caminho_storage,
            "tamanho_bytes": tamanho_bytes,
            "enviado_por": enviado_por,
        }).execute()
        return True
    except Exception:
        return False


def carregar_documentos_da_venda(venda_id):
    try:
        res = supabase.table(TABELA_VENDA_DOCUMENTOS).select("*").eq("venda_id", venda_id).order("enviado_em").execute()
        return res.data or []
    except Exception:
        return []


def excluir_arquivos_storage_da_venda(venda_id):
    try:
        documentos = carregar_documentos_da_venda(venda_id)
        caminhos = [d.get("caminho_storage") for d in documentos if d.get("caminho_storage")]
        if caminhos:
            supabase.storage.from_(BUCKET_DOCUMENTOS_VENDA).remove(caminhos)
    except Exception:
        pass


def contar_documentos_por_vendas(lista_venda_ids):
    if not lista_venda_ids:
        return {}
    try:
        res = supabase.table(TABELA_VENDA_DOCUMENTOS).select("venda_id").in_("venda_id", lista_venda_ids).execute()
        contagem = {}
        for r in (res.data or []):
            vid = r.get("venda_id")
            contagem[vid] = contagem.get(vid, 0) + 1
        return contagem
    except Exception:
        return {}


def gerar_link_download_documento(caminho_storage, validade_segundos=3600, nome_arquivo=None):
    try:
        opcoes = {"download": nome_arquivo or True}
        try:
            resultado = supabase.storage.from_(BUCKET_DOCUMENTOS_VENDA).create_signed_url(caminho_storage, validade_segundos, opcoes)
        except TypeError:
            resultado = supabase.storage.from_(BUCKET_DOCUMENTOS_VENDA).create_signed_url(caminho_storage, validade_segundos)
        return resultado.get("signedURL") or resultado.get("signedUrl")
    except Exception:
        return None

# ============================================================
# CONSULTA FGTS - CONFIGURAÇÃO V8 DIGITAL
# ============================================================
V8_CLIENT_ID = "DHWogdaYmEI8n5bwwxPDzulMlSK7dwIn"
V8_AUDIENCE = "https://bff.v8sistema.com"
V8_AUTH_URL = "https://auth.v8sistema.com/oauth/token"
V8_BASE_URL = "https://bff.v8sistema.com"
V8_PROVIDER = "sants"

SEGUNDOS_ENTRE_TENTATIVAS_POLL = 15
MAX_TENTATIVAS_POLL = 4
SEGUNDOS_ENTRE_TENTATIVAS_POST = 1

_v8_token_cache = {}
_v8_ultima_falha_auth = {}
_V8_INTERVALO_MINIMO_FALHA = 30
_v8_cache_lock = threading.Lock()

ROTULOS_OBSERVACAO_FGTS = {
    "nao_autorizado": "Não autorizado pelo cliente",
    "saldo_insuficiente": "Saldo insuficiente (parcelas < R$100,00)",
    "operacao_em_andamento": "Operação fiduciária em andamento (tentar mais tarde)",
}


class ResultadoFinalNegocioFGTS(Exception):
    def __init__(self, motivo):
        self.motivo = motivo
        super().__init__(motivo)


class AutenticacaoEmEsperaSeguranca(Exception):
    pass


def v8_obter_token(username, password, forcar_novo=False):
    agora = time.time()

    with _v8_cache_lock:
        cache = _v8_token_cache.get(username)
        if not forcar_novo and cache and cache.get("access_token"):
            if agora - cache["obtained_at"] < cache["expires_in"] - 60:
                return cache["access_token"]

        ultima_falha = _v8_ultima_falha_auth.get(username, 0)
        if agora - ultima_falha < _V8_INTERVALO_MINIMO_FALHA:
            segundos_restantes = round(_V8_INTERVALO_MINIMO_FALHA - (agora - ultima_falha))
            raise AutenticacaoEmEsperaSeguranca(
                f"Aguardando {segundos_restantes}s de intervalo de segurança antes de tentar de novo (não testou a senha ainda)."
            )

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "audience": V8_AUDIENCE,
        "scope": "offline_access",
        "client_id": V8_CLIENT_ID,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = _req.post(V8_AUTH_URL, data=payload, headers=headers, timeout=30)

    if resp.status_code != 200:
        with _v8_cache_lock:
            _v8_ultima_falha_auth[username] = agora
        raise RuntimeError(f"Falha na autenticação V8 ({username}) (HTTP {resp.status_code}): {resp.text}")

    data = resp.json()
    with _v8_cache_lock:
        _v8_token_cache[username] = {
            "access_token": data["access_token"],
            "obtained_at": agora,
            "expires_in": data.get("expires_in", 86400),
        }
    return data["access_token"]


def v8_headers(username, password):
    return {"Authorization": f"Bearer {v8_obter_token(username, password)}", "Content-Type": "application/json"}


def v8_classificar_mensagem_negocio(texto_resposta):
    if not texto_resposta:
        return None
    texto_lower = texto_resposta.lower()
    if any(t in texto_lower for t in [
        "não autoriza", "nao autoriza", "não possui autorização",
        "nao possui autorizacao", "não autorizado", "nao autorizado",
    ]):
        return "nao_autorizado"
    if "saldo insuficiente" in texto_lower:
        return "saldo_insuficiente"
    if v8_eh_operacao_em_andamento(texto_resposta):
        return "operacao_em_andamento"
    return None


def v8_eh_tente_novamente(texto_resposta):
    if not texto_resposta:
        return False
    return "tente novamente" in texto_resposta.lower()


def v8_eh_operacao_em_andamento(texto_resposta):
    if not texto_resposta:
        return False
    texto_lower = texto_resposta.lower()
    return "operação fiduciária em andamento" in texto_lower or "operacao fiduciaria em andamento" in texto_lower


def v8_iniciar_consulta_saldo(document_number, provider, username, password, parar_flag=None):
    url = f"{V8_BASE_URL}/fgts/balance"
    payload = {"documentNumber": document_number, "provider": provider.lower()}

    while True:
        if parar_flag is not None and parar_flag.get("parar"):
            if parar_flag.get("parar") == "pausar":
                raise RuntimeError("Rodada pausada pelo usuário.")
            raise RuntimeError("Rodada cancelada pelo usuário.")

        resp = _req.post(url, json=payload, headers=v8_headers(username, password), timeout=30)

        if resp.status_code == 401:
            resp = _req.post(url, json=payload, headers={
                "Authorization": f"Bearer {v8_obter_token(username, password, forcar_novo=True)}",
                "Content-Type": "application/json",
            }, timeout=30)

        if resp.status_code in (200, 201, 202, 204):
            return resp.text

        detalhe = resp.text
        try:
            detalhe = resp.json().get("detail", resp.text)
        except Exception:
            pass

        motivo_negocio = v8_classificar_mensagem_negocio(detalhe)
        if motivo_negocio:
            raise ResultadoFinalNegocioFGTS(detalhe)

        if v8_eh_tente_novamente(detalhe):
            time.sleep(SEGUNDOS_ENTRE_TENTATIVAS_POST)
            continue

        raise RuntimeError(f"Erro ao iniciar consulta (HTTP {resp.status_code}): {resp.text}")


def v8_consultar_resultado_saldo(document_number, username, password, provider=None):
    url = f"{V8_BASE_URL}/fgts/balance"
    params = {"search": document_number}
    resp = _req.get(url, params=params, headers=v8_headers(username, password), timeout=30)

    if resp.status_code == 401:
        resp = _req.get(url, params=params, headers={
            "Authorization": f"Bearer {v8_obter_token(username, password, forcar_novo=True)}",
            "Content-Type": "application/json",
        }, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(f"Erro ao consultar resultado (HTTP {resp.status_code}): {resp.text}")

    data = resp.json()
    registros = data.get("data", [])
    if not registros:
        return None

    if provider is None:
        return registros[0]

    candidatos = [r for r in registros if str(r.get("provider", "")).lower() == provider.lower()]
    if not candidatos:
        return None
    candidatos.sort(key=lambda r: r.get("updatedAt", ""), reverse=True)
    return candidatos[0]


def v8_aguardar_resultado_saldo(document_number, provider, username, password, parar_flag=None):
    tentativas_sem_registro = 0

    while tentativas_sem_registro < MAX_TENTATIVAS_POLL:
        if parar_flag is not None and parar_flag.get("parar"):
            if parar_flag.get("parar") == "pausar":
                raise RuntimeError("Rodada pausada pelo usuário.")
            raise RuntimeError("Rodada cancelada pelo usuário.")

        registro = v8_consultar_resultado_saldo(document_number, username, password, provider=provider)

        if registro and registro.get("status") == "success":
            return registro

        if registro and registro.get("status") == "fail":
            mensagem = registro.get("statusInfo")
            if v8_eh_tente_novamente(mensagem):
                time.sleep(SEGUNDOS_ENTRE_TENTATIVAS_POST)
                continue
            registro["_motivo_negocio"] = v8_classificar_mensagem_negocio(mensagem)
            return registro

        tentativas_sem_registro += 1
        time.sleep(SEGUNDOS_ENTRE_TENTATIVAS_POLL)

    return None


def v8_formatar_periodos(periods):
    if not periods:
        return ""
    return "; ".join(f"{p.get('dueDate')}: R$ {p.get('amount')}" for p in periods)


def fgts_processar_cpf(cpf, provider, rodada_id, username, password, parar_flag=None):
    inicio_cpf = time.time()

    def _tempo():
        return round(time.time() - inicio_cpf, 1)

    try:
        v8_iniciar_consulta_saldo(cpf, provider, username, password, parar_flag=parar_flag)
    except ResultadoFinalNegocioFGTS as e:
        motivo_rotulo = v8_classificar_mensagem_negocio(e.motivo) or "erro_tecnico"
        supabase.table("fgts_resultados").insert({
            "rodada_id": rodada_id,
            "cpf": cpf,
            "provider": provider,
            "status": motivo_rotulo,
            "saldo_disponivel": "",
            "periodos": "",
            "observacao": ROTULOS_OBSERVACAO_FGTS.get(motivo_rotulo, e.motivo or ""),
            "tempo_segundos": _tempo(),
        }).execute()
        return
    except Exception as e:
        if "cancelada pelo usuário" in str(e) or "pausada pelo usuário" in str(e):
            raise
        supabase.table("fgts_resultados").insert({
            "rodada_id": rodada_id,
            "cpf": cpf,
            "provider": provider,
            "status": "erro_tecnico",
            "saldo_disponivel": "",
            "periodos": "",
            "observacao": f"Erro técnico no POST: {e}",
            "tempo_segundos": _tempo(),
        }).execute()
        return

    registro = v8_aguardar_resultado_saldo(cpf, provider, username, password, parar_flag=parar_flag)

    if registro is None:
        supabase.table("fgts_resultados").insert({
            "rodada_id": rodada_id,
            "cpf": cpf,
            "provider": provider,
            "status": "erro_tecnico",
            "saldo_disponivel": "",
            "periodos": "",
            "observacao": "Tempo de espera esgotado sem retorno da V8.",
            "tempo_segundos": _tempo(),
        }).execute()
        return

    status = registro.get("status")
    mensagem_status = registro.get("statusInfo")

    if status == "fail":
        motivo_rotulo = registro.get("_motivo_negocio")
        if motivo_rotulo:
            supabase.table("fgts_resultados").insert({
                "rodada_id": rodada_id,
                "cpf": cpf,
                "provider": provider,
                "status": motivo_rotulo,
                "saldo_disponivel": "",
                "periodos": "",
                "observacao": ROTULOS_OBSERVACAO_FGTS.get(motivo_rotulo, mensagem_status or ""),
                "id_consulta": str(registro.get("id") or ""),
                "criado_em_v8": str(registro.get("createdAt") or ""),
                "atualizado_em_v8": str(registro.get("updatedAt") or ""),
                "tempo_segundos": _tempo(),
            }).execute()
        else:
            supabase.table("fgts_resultados").insert({
                "rodada_id": rodada_id,
                "cpf": cpf,
                "provider": provider,
                "status": "erro_tecnico",
                "saldo_disponivel": "",
                "periodos": "",
                "observacao": mensagem_status or "Falha na consulta (sem detalhe).",
                "tempo_segundos": _tempo(),
            }).execute()
        return

    supabase.table("fgts_resultados").insert({
        "rodada_id": rodada_id,
        "cpf": cpf,
        "provider": registro.get("provider"),
        "status": "success",
        "saldo_disponivel": str(registro.get("amount") or ""),
        "periodos": v8_formatar_periodos(registro.get("periods")),
        "observacao": "",
        "id_consulta": str(registro.get("id") or ""),
        "criado_em_v8": str(registro.get("createdAt") or ""),
        "atualizado_em_v8": str(registro.get("updatedAt") or ""),
        "tempo_segundos": _tempo(),
    }).execute()


def fgts_status_atual_rodada(rodada_id):
    try:
        res = supabase.table("fgts_rodadas").select("status").eq("id", rodada_id).execute()
        return res.data[0]["status"] if res.data else None
    except Exception:
        return None


def fgts_cpfs_ja_processados(rodada_id):
    try:
        res = supabase.table("fgts_resultados").select("cpf").eq("rodada_id", rodada_id).execute()
        return set(r["cpf"] for r in (res.data or []))
    except Exception:
        return set()


_fgts_contador_lock = threading.Lock()
_fgts_threads_ativas = {}
_fgts_threads_lock = threading.Lock()


def fgts_incrementar_processados(rodada_id):
    with _fgts_contador_lock:
        try:
            res_atual = supabase.table("fgts_rodadas").select("processados").eq("id", rodada_id).execute()
            processados_atual = (res_atual.data[0]["processados"] if res_atual.data else 0) or 0
            supabase.table("fgts_rodadas").update({
                "processados": processados_atual + 1,
                "ultimo_processamento_em": str(datetime.now()),
            }).eq("id", rodada_id).execute()
        except Exception:
            pass


TIMEOUT_MAXIMO_POR_CPF_SEGUNDOS = 180


def fgts_processar_cpf_com_watchdog(cpf, provider, rodada_id, username, password, parar_flag):
    resultado_pronto = {"concluido": False, "excecao": None}

    def _alvo():
        try:
            fgts_processar_cpf(cpf, provider, rodada_id, username, password, parar_flag=parar_flag)
        except Exception as e:
            resultado_pronto["excecao"] = e
        finally:
            resultado_pronto["concluido"] = True

    t_interna = threading.Thread(target=_alvo, daemon=True)
    t_interna.start()
    t_interna.join(timeout=TIMEOUT_MAXIMO_POR_CPF_SEGUNDOS)

    if not resultado_pronto["concluido"]:
        try:
            supabase.table("fgts_resultados").insert({
                "rodada_id": rodada_id,
                "cpf": cpf,
                "provider": provider,
                "status": "erro_tecnico",
                "saldo_disponivel": "",
                "periodos": "",
                "observacao": f"Timeout forçado pelo watchdog ({TIMEOUT_MAXIMO_POR_CPF_SEGUNDOS}s sem resposta).",
                "tempo_segundos": TIMEOUT_MAXIMO_POR_CPF_SEGUNDOS,
            }).execute()
        except Exception:
            pass
        return

    if resultado_pronto["excecao"] is not None:
        raise resultado_pronto["excecao"]


def fgts_registrar_erro_credencial(rodada_id, username_com_erro, apelido_com_erro, detalhe=""):
    try:
        res = supabase.table("fgts_rodadas").select("credenciais_com_erro").eq("id", rodada_id).execute()
        atual = (res.data[0].get("credenciais_com_erro") or "") if res.data else ""
        lista_atual = [c for c in atual.split(",") if c]
        if apelido_com_erro not in lista_atual:
            lista_atual.append(apelido_com_erro)
        update_dados = {"credenciais_com_erro": ",".join(lista_atual)}
        if detalhe:
            update_dados["detalhe_erro_autenticacao"] = f"{apelido_com_erro}: {detalhe}"[:1000]
        supabase.table("fgts_rodadas").update(update_dados).eq("id", rodada_id).execute()
    except Exception:
        pass


def fgts_thread_credencial(cpfs_fatia, rodada_id, username, password, parar_flag, inicio_geral, apelido=""):
    autenticado = False
    for _tentativa_auth in range(3):
        try:
            v8_obter_token(username, password)
            autenticado = True
            break
        except AutenticacaoEmEsperaSeguranca:
            time.sleep(_V8_INTERVALO_MINIMO_FALHA + 1)
            continue
        except Exception as e:
            fgts_registrar_erro_credencial(rodada_id, username, apelido or username, detalhe=str(e))
            fgts_finalizar_thread(rodada_id, status_se_ultima="concluida", inicio_geral=inicio_geral, motivo_individual="erro_autenticacao")
            return

    if not autenticado:
        fgts_registrar_erro_credencial(rodada_id, username, apelido or username, detalhe="Não foi possível autenticar após aguardar o intervalo de segurança 3 vezes.")
        fgts_finalizar_thread(rodada_id, status_se_ultima="concluida", inicio_geral=inicio_geral, motivo_individual="erro_autenticacao")
        return

    ja_processados = fgts_cpfs_ja_processados(rodada_id)

    for cpf in cpfs_fatia:
        if cpf in ja_processados:
            continue

        status_banco = fgts_status_atual_rodada(rodada_id)

        if status_banco == "cancelando" or parar_flag.get("parar") == "cancelar":
            fgts_finalizar_thread(rodada_id, status_se_ultima="cancelada", inicio_geral=inicio_geral)
            return

        if status_banco == "pausando" or parar_flag.get("parar") == "pausar":
            fgts_finalizar_thread(rodada_id, status_se_ultima="pausada", inicio_geral=inicio_geral)
            return

        try:
            fgts_processar_cpf_com_watchdog(cpf, V8_PROVIDER, rodada_id, username, password, parar_flag)
        except Exception as e:
            if "cancelada pelo usuário" in str(e):
                fgts_finalizar_thread(rodada_id, status_se_ultima="cancelada", inicio_geral=inicio_geral)
                return
            if "pausada pelo usuário" in str(e):
                fgts_finalizar_thread(rodada_id, status_se_ultima="pausada", inicio_geral=inicio_geral)
                return

        fgts_incrementar_processados(rodada_id)

    fgts_finalizar_thread(rodada_id, status_se_ultima="concluida", inicio_geral=inicio_geral)


_fgts_motivo_final = {}
_fgts_motivo_lock = threading.Lock()

_PRIORIDADE_STATUS = {"pausada": 3, "cancelada": 3, "erro_autenticacao": 2, "concluida": 1}


def fgts_finalizar_thread(rodada_id, status_se_ultima, inicio_geral, motivo_individual=None):
    status_para_registrar = motivo_individual or status_se_ultima

    with _fgts_motivo_lock:
        atual = _fgts_motivo_final.get(rodada_id)
        if atual is None or _PRIORIDADE_STATUS.get(status_para_registrar, 0) > _PRIORIDADE_STATUS.get(atual, 0):
            _fgts_motivo_final[rodada_id] = status_para_registrar

    with _fgts_threads_lock:
        _fgts_threads_ativas[rodada_id] = _fgts_threads_ativas.get(rodada_id, 1) - 1
        restantes = _fgts_threads_ativas[rodada_id]

    if restantes > 0:
        return

    with _fgts_motivo_lock:
        status_final_real = _fgts_motivo_final.pop(rodada_id, status_se_ultima)

    if status_final_real == "erro_autenticacao":
        try:
            res_check = supabase.table("fgts_resultados").select("id").eq("rodada_id", rodada_id).limit(1).execute()
            teve_algum_resultado = bool(res_check.data)
        except Exception:
            teve_algum_resultado = False
        if teve_algum_resultado:
            status_final_real = "concluida"

    tempo_total = round(time.time() - inicio_geral, 1)
    update_dados = {"status": status_final_real, "tempo_total_segundos": tempo_total}
    if status_final_real in ("concluida", "cancelada"):
        update_dados["finalizado_em"] = str(datetime.now())
    supabase.table("fgts_rodadas").update(update_dados).eq("id", rodada_id).execute()


def fgts_iniciar_threads(cpfs, rodada_id, credenciais, parar_flag):
    n_cred = len(credenciais)
    fatias = [cpfs[i::n_cred] for i in range(n_cred)]

    with _fgts_threads_lock:
        _fgts_threads_ativas[rodada_id] = n_cred

    inicio_geral = time.time()

    for i, cred in enumerate(credenciais):
        fatia = fatias[i]
        if not fatia:
            with _fgts_threads_lock:
                _fgts_threads_ativas[rodada_id] -= 1
            continue
        thread = threading.Thread(
            target=fgts_thread_credencial,
            args=(fatia, rodada_id, cred["username"], cred["password"], parar_flag, inicio_geral, cred.get("apelido", cred["username"])),
            daemon=True
        )
        thread.start()


_fgts_flags_globais = {}
LIMITE_INATIVIDADE_SEGUNDOS = 150


def fgts_buscar_rodada_ativa_global():
    try:
        res = supabase.table("fgts_rodadas").select("*").in_("status", ["em_andamento","pausando","cancelando"]).order("id", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


def fgts_buscar_credenciais_global(somente_ativas=True):
    try:
        q = supabase.table("fgts_credenciais").select("*").order("id")
        if somente_ativas:
            q = q.eq("ativo", True)
        res = q.execute()
        return res.data or []
    except Exception:
        return []


def fgts_checar_e_religar_rodada_ativa():
    rodada_ativa = fgts_buscar_rodada_ativa_global()
    if not rodada_ativa or rodada_ativa.get("status") != "em_andamento":
        return None

    rid_check = rodada_ativa["id"]
    ja_tem_thread_registrada = _fgts_flags_globais.get(rid_check) is not None

    referencia_pulso = rodada_ativa.get("ultimo_processamento_em") or rodada_ativa.get("iniciado_em")
    segundos_sem_pulso = None
    if referencia_pulso:
        try:
            dt_pulso = pd.to_datetime(referencia_pulso)
            segundos_sem_pulso = (pd.Timestamp.now() - dt_pulso).total_seconds()
        except Exception:
            pass

    thread_parece_morta = (not ja_tem_thread_registrada) and (
        segundos_sem_pulso is not None and segundos_sem_pulso > LIMITE_INATIVIDADE_SEGUNDOS
    )

    if not thread_parece_morta:
        return None

    cpfs_lista_str_auto = rodada_ativa.get("cpfs_lista") or ""
    cpfs_originais_auto = [c for c in cpfs_lista_str_auto.split(",") if c]
    cred_usadas_nomes = [n.strip() for n in (rodada_ativa.get("credenciais_usadas") or "").split(",") if n.strip()]
    todas_credenciais_auto = fgts_buscar_credenciais_global(somente_ativas=True)
    credenciais_para_retomar_auto = [c for c in todas_credenciais_auto if c.get("apelido") in cred_usadas_nomes] or todas_credenciais_auto[:1]

    if not (cpfs_originais_auto and credenciais_para_retomar_auto):
        return None

    flag_auto = {"parar": False}
    _fgts_flags_globais[rid_check] = flag_auto
    supabase.table("fgts_rodadas").update({
        "ultimo_processamento_em": str(datetime.now())
    }).eq("id", rid_check).execute()
    fgts_iniciar_threads(cpfs_originais_auto, rid_check, credenciais_para_retomar_auto, flag_auto)

    return f"Rodada #{rid_check} estava sem atividade há {round(segundos_sem_pulso)}s — religada automaticamente com {len(credenciais_para_retomar_auto)} credencial(is)."

# ============================================================
# CLT LOTE - CONFIGURAÇÃO API SOMA BP2 (Consignado Privado CLT)
# ============================================================
import os as _os_soma
import json as _json_soma

SOMA_BASE_URL = "https://api.somabp2.com.br"
def _soma_ler_credencial_secrets(nome_chave):
    try:
        if nome_chave in st.secrets:
            return st.secrets[nome_chave]
    except Exception:
        pass
    return _os_soma.environ.get(nome_chave, "")

SOMA_TOKEN_TTL_SEGUNDOS = 30 * 60  # 30 minutos

_soma_token_cache = {"access_token": None, "obtido_em": 0.0, "client_id_usado": None}
_soma_token_lock = threading.Lock()
_soma_cred_cache = {"credencial": None, "obtido_em": 0.0}
_soma_cred_cache_lock = threading.Lock()
SOMA_CRED_CACHE_TTL_SEGUNDOS = 30


def soma_buscar_credenciais():
    """Lista todas as credenciais Soma BP2 cadastradas no Supabase (mais recente primeiro)."""
    try:
        res = supabase.table("soma_credenciais").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def soma_buscar_credencial_ativa(forcar_novo=False):
    """Retorna (client_id, client_secret) da credencial ativa no Supabase.
    Cai para st.secrets/variável de ambiente se não houver nenhuma cadastrada no banco."""
    agora = time.time()
    with _soma_cred_cache_lock:
        if not forcar_novo and _soma_cred_cache["credencial"] is not None:
            if agora - _soma_cred_cache["obtido_em"] < SOMA_CRED_CACHE_TTL_SEGUNDOS:
                return _soma_cred_cache["credencial"]

    credencial = None
    try:
        res = supabase.table("soma_credenciais").select("*").eq("ativo", True).order("id", desc=True).limit(1).execute()
        if res.data:
            credencial = (res.data[0]["client_id"], res.data[0]["client_secret"])
    except Exception:
        pass

    if credencial is None:
        cid_secrets = _soma_ler_credencial_secrets("SOMA_CLIENT_ID")
        csec_secrets = _soma_ler_credencial_secrets("SOMA_CLIENT_SECRET")
        if cid_secrets and csec_secrets:
            credencial = (cid_secrets, csec_secrets)

    with _soma_cred_cache_lock:
        _soma_cred_cache["credencial"] = credencial
        _soma_cred_cache["obtido_em"] = agora

    return credencial


def soma_obter_token(forcar_novo=False):
    agora = time.time()
    credencial = soma_buscar_credencial_ativa(forcar_novo=forcar_novo)
    if not credencial:
        raise RuntimeError("Nenhuma credencial Soma BP2 ativa. Cadastre uma em 'Gerenciar credencial Soma BP2' na aba CLT Lote.")
    client_id, client_secret = credencial

    with _soma_token_lock:
        if not forcar_novo and _soma_token_cache["access_token"] and _soma_token_cache["client_id_usado"] == client_id:
            if agora - _soma_token_cache["obtido_em"] < (SOMA_TOKEN_TTL_SEGUNDOS - 60):
                return _soma_token_cache["access_token"]

    url = f"{SOMA_BASE_URL}/auth/oauth/token"
    payload = {
        "grantType": "client_credentials",
        "clientId": client_id,
        "clientSecret": client_secret,
    }
    resp = _req.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("accessToken")
    if not token:
        raise RuntimeError(f"Resposta de autenticação Soma sem 'accessToken': {data}")

    with _soma_token_lock:
        _soma_token_cache["access_token"] = token
        _soma_token_cache["obtido_em"] = agora
        _soma_token_cache["client_id_usado"] = client_id
    return token


def soma_consultar_margem(cpf, nome="", celular="", data_nascimento="", bancarizadora="UY3", max_retries=3):
    """Consulta margem/saldo (privado CLT) para um CPF via POST /v2/privado/externo/consultas/."""
    url = f"{SOMA_BASE_URL}/v2/privado/externo/consultas/"
    payload = {
        "bancarizadora": bancarizadora,
        "cpf": cpf,
        "nome": nome,
        "celular": celular,
        "dataNascimento": data_nascimento,
    }

    ultimo_erro = None
    for tentativa in range(1, max_retries + 1):
        try:
            token = soma_obter_token()
            headers = {"Authorization": f"Bearer {token}"}
            resp = _req.post(url, json=payload, headers=headers, timeout=25)

            if resp.status_code == 401:
                token = soma_obter_token(forcar_novo=True)
                headers = {"Authorization": f"Bearer {token}"}
                resp = _req.post(url, json=payload, headers=headers, timeout=25)

            if resp.status_code == 429:
                raise RuntimeError("Limite diário de consultas atingido na API Soma.")

            if resp.status_code == 400:
                try:
                    corpo_erro = resp.json()
                    detalhes = corpo_erro.get("detalhes")
                    if detalhes:
                        detalhes_txt = "; ".join(f"{d.get('campo')}: {d.get('mensagem')}" for d in detalhes)
                    else:
                        detalhes_txt = corpo_erro.get("message", resp.text)
                except Exception:
                    detalhes_txt = resp.text
                raise RuntimeError(f"HTTP 400 (validação): {detalhes_txt}")

            resp.raise_for_status()
            return resp.json()

        except RuntimeError as e:
            if str(e).startswith("HTTP 400"):
                raise
            ultimo_erro = e
            if tentativa < max_retries:
                time.sleep(2 ** tentativa)
        except Exception as e:
            ultimo_erro = e
            if tentativa < max_retries:
                time.sleep(2 ** tentativa)

    raise RuntimeError(f"Falha ao consultar CPF {cpf} na Soma após {max_retries} tentativas: {ultimo_erro}")


def soma_lote_status_atual_rodada(rodada_id):
    try:
        res = supabase.table("soma_lote_rodadas").select("status").eq("id", rodada_id).execute()
        return res.data[0]["status"] if res.data else None
    except Exception:
        return None


def soma_lote_cpfs_ja_processados(rodada_id):
    try:
        res = supabase.table("soma_lote_resultados").select("cpf").eq("rodada_id", rodada_id).execute()
        return set(r["cpf"] for r in (res.data or []))
    except Exception:
        return set()


_soma_lote_threads_ativas = {}
_soma_lote_threads_lock = threading.Lock()
SOMA_LOTE_NUM_WORKERS = 4


def soma_lote_processar_cpf(cpf, rodada_id, bancarizadora, nome="", celular="", data_nascimento=""):
    inicio_cpf = time.time()
    try:
        resultado = soma_consultar_margem(
            cpf, nome=nome, celular=celular,
            data_nascimento=data_nascimento, bancarizadora=bancarizadora
        )
        supabase.table("soma_lote_resultados").insert({
            "rodada_id": rodada_id,
            "cpf": cpf,
            "bancarizadora": bancarizadora,
            "status": "success",
            "status_soma": resultado.get("conStatusNome"),
            "margem_disponivel": resultado.get("conMargemDisponivel"),
            "margem_bruta": resultado.get("conMargemBruta"),
            "salario_bruto": resultado.get("conSalarioBruto"),
            "salario_liquido": resultado.get("conSalarioLiquido"),
            "empregador": resultado.get("conEmpregador"),
            "mensagem": resultado.get("conMensagem"),
            "resposta_completa": resultado,
            "tempo_segundos": round(time.time() - inicio_cpf, 1),
        }).execute()
    except Exception as e:
        supabase.table("soma_lote_resultados").insert({
            "rodada_id": rodada_id,
            "cpf": cpf,
            "bancarizadora": bancarizadora,
            "status": "erro",
            "mensagem": str(e),
            "tempo_segundos": round(time.time() - inicio_cpf, 1),
        }).execute()


def soma_lote_incrementar_processados(rodada_id):
    try:
        res_atual = supabase.table("soma_lote_rodadas").select("processados").eq("id", rodada_id).execute()
        processados_atual = (res_atual.data[0]["processados"] if res_atual.data else 0) or 0
        supabase.table("soma_lote_rodadas").update({
            "processados": processados_atual + 1,
            "ultimo_processamento_em": str(datetime.now()),
        }).eq("id", rodada_id).execute()
    except Exception:
        pass


def soma_lote_worker(registros_fatia, rodada_id, bancarizadora, parar_flag):
    ja_processados = soma_lote_cpfs_ja_processados(rodada_id)
    for registro in registros_fatia:
        cpf = registro["cpf"]
        if cpf in ja_processados:
            continue

        status_banco = soma_lote_status_atual_rodada(rodada_id)
        if status_banco == "cancelando" or parar_flag.get("parar") == "cancelar":
            break
        if status_banco == "pausando" or parar_flag.get("parar") == "pausar":
            break

        soma_lote_processar_cpf(
            cpf, rodada_id, bancarizadora,
            nome=registro.get("nome", ""), celular=registro.get("celular", "")
        )
        soma_lote_incrementar_processados(rodada_id)

    with _soma_lote_threads_lock:
        _soma_lote_threads_ativas[rodada_id] = _soma_lote_threads_ativas.get(rodada_id, 1) - 1
        restantes = _soma_lote_threads_ativas[rodada_id]

    if restantes <= 0:
        status_banco_final = soma_lote_status_atual_rodada(rodada_id)
        if status_banco_final == "cancelando":
            status_final = "cancelada"
        elif status_banco_final == "pausando":
            status_final = "pausada"
        else:
            status_final = "concluida"
        update_dados = {"status": status_final}
        if status_final in ("concluida", "cancelada"):
            update_dados["finalizado_em"] = str(datetime.now())
        supabase.table("soma_lote_rodadas").update(update_dados).eq("id", rodada_id).execute()


def soma_lote_iniciar_threads(registros, rodada_id, bancarizadora, parar_flag, n_workers=SOMA_LOTE_NUM_WORKERS):
    n_workers = max(1, min(n_workers, len(registros)))
    fatias = [registros[i::n_workers] for i in range(n_workers)]

    with _soma_lote_threads_lock:
        _soma_lote_threads_ativas[rodada_id] = n_workers

    for fatia in fatias:
        if not fatia:
            with _soma_lote_threads_lock:
                _soma_lote_threads_ativas[rodada_id] -= 1
            continue
        thread = threading.Thread(
            target=soma_lote_worker,
            args=(fatia, rodada_id, bancarizadora, parar_flag),
            daemon=True
        )
        thread.start()


def soma_lote_buscar_rodada_ativa():
    try:
        res = supabase.table("soma_lote_rodadas").select("*").in_("status", ["em_andamento","pausando","cancelando"]).order("id", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


def soma_lote_buscar_rodadas_pausadas():
    try:
        res = supabase.table("soma_lote_rodadas").select("*").eq("status", "pausada").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def soma_lote_buscar_historico(limite=15):
    try:
        res = supabase.table("soma_lote_rodadas").select("*").order("id", desc=True).limit(limite).execute()
        return res.data or []
    except Exception:
        return []


def soma_lote_buscar_resultados(rodada_id):
    try:
        res = supabase.table("soma_lote_resultados").select("*").eq("rodada_id", rodada_id).execute()
        return res.data or []
    except Exception:
        return []

# ============================================================
# CLT MULTI-BANCOS - V8 DIGITAL (Crédito Privado CLT)
# ============================================================
V8_CLT_AUTH_URL = "https://auth.v8sistema.com/oauth/token"
V8_CLT_BASE_URL = "https://bff.v8sistema.com"
V8_CLT_CLIENT_ID = "DHWogdaYmEI8n5bwwxPDzulMlSK7dwIn"  # mesmo client_id usado no FGTS
V8_CLT_AUDIENCE = "https://bff.v8sistema.com"
V8_CLT_PROVIDER = "QI"

_v8_clt_token_cache = {"access_token": None, "obtido_em": 0.0, "username_usado": None}
_v8_clt_token_lock = threading.Lock()
_v8_clt_cred_cache = {"credencial": None, "obtido_em": 0.0}
_v8_clt_cred_cache_lock = threading.Lock()


def v8_clt_buscar_credenciais():
    try:
        res = supabase.table("v8_clt_credenciais").select("*").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def v8_clt_buscar_credencial_ativa(forcar_novo=False):
    agora = time.time()
    with _v8_clt_cred_cache_lock:
        if not forcar_novo and _v8_clt_cred_cache["credencial"] is not None:
            if agora - _v8_clt_cred_cache["obtido_em"] < SOMA_CRED_CACHE_TTL_SEGUNDOS:
                return _v8_clt_cred_cache["credencial"]
    credencial = None
    try:
        res = supabase.table("v8_clt_credenciais").select("*").eq("ativo", True).order("id", desc=True).limit(1).execute()
        if res.data:
            credencial = (res.data[0]["username"], res.data[0]["password"])
    except Exception:
        pass
    with _v8_clt_cred_cache_lock:
        _v8_clt_cred_cache["credencial"] = credencial
        _v8_clt_cred_cache["obtido_em"] = agora
    return credencial


def v8_clt_obter_token(forcar_novo=False):
    agora = time.time()
    credencial = v8_clt_buscar_credencial_ativa(forcar_novo=forcar_novo)
    if not credencial:
        raise RuntimeError("Nenhuma credencial V8 (CLT) ativa. Cadastre uma em 'Gerenciar credencial V8'.")
    username, password = credencial

    with _v8_clt_token_lock:
        if not forcar_novo and _v8_clt_token_cache["access_token"] and _v8_clt_token_cache["username_usado"] == username:
            if agora - _v8_clt_token_cache["obtido_em"] < (86400 - 60):
                return _v8_clt_token_cache["access_token"]

    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "audience": V8_CLT_AUDIENCE,
        "scope": "offline_access",
        "client_id": V8_CLT_CLIENT_ID,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    resp = _req.post(V8_CLT_AUTH_URL, data=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    token = data.get("access_token")
    if not token:
        raise RuntimeError(f"Resposta de auth V8 (CLT) sem access_token: {data}")

    with _v8_clt_token_lock:
        _v8_clt_token_cache["access_token"] = token
        _v8_clt_token_cache["obtido_em"] = agora
        _v8_clt_token_cache["username_usado"] = username
    return token


def v8_clt_headers():
    return {"Authorization": f"Bearer {v8_clt_obter_token()}", "Content-Type": "application/json"}


def v8_clt_criar_consulta(cpf, nome, celular, data_nascimento, genero, email):
    """Gera o termo de consentimento / consulta. Retorna o consult_id."""
    ddd = celular[:2] if len(celular) >= 10 else ""
    numero = celular[2:] if len(celular) >= 10 else celular
    payload = {
        "borrowerDocumentNumber": cpf,
        "gender": genero,
        "birthDate": data_nascimento,
        "signerName": nome,
        "signerEmail": email,
        "signerPhone": {
            "phoneNumber": numero,
            "countryCode": "55",
            "areaCode": ddd,
        },
        "provider": V8_CLT_PROVIDER,
    }
    url = f"{V8_CLT_BASE_URL}/private-consignment/consult"
    resp = _req.post(url, json=payload, headers=v8_clt_headers(), timeout=30)

    if resp.status_code == 401:
        resp = _req.post(url, json=payload, headers={
            "Authorization": f"Bearer {v8_clt_obter_token(forcar_novo=True)}",
            "Content-Type": "application/json",
        }, timeout=30)

    if resp.status_code >= 400:
        raise RuntimeError(f"Erro ao criar consulta V8 (HTTP {resp.status_code}): {resp.text}")

    data = resp.json()
    consult_id = data.get("id")
    if not consult_id:
        raise RuntimeError(f"Resposta sem 'id' ao criar consulta V8: {data}")
    return consult_id


def v8_clt_autorizar_consulta(consult_id):
    url = f"{V8_CLT_BASE_URL}/private-consignment/consult/{consult_id}/authorize"
    payload = {
        "consult_id": consult_id,
        "operationalSystem": "Linux",
        "deviceModel": "OperaX-Robot",
        "deviceName": "OperaX-Robot",
        "deviceType": "desktop",
    }
    resp = _req.post(url, json=payload, headers=v8_clt_headers(), timeout=30)
    if resp.status_code == 401:
        resp = _req.post(url, json=payload, headers={
            "Authorization": f"Bearer {v8_clt_obter_token(forcar_novo=True)}",
            "Content-Type": "application/json",
        }, timeout=30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Erro ao autorizar consulta V8 (HTTP {resp.status_code}): {resp.text}")


def v8_clt_consultar_status(cpf, consult_id, tentativas=15, intervalo_segundos=4):
    """Faz polling na listagem até status final (SUCCESS/FAILED/REJECTED) ou esgotar tentativas."""
    url = f"{V8_CLT_BASE_URL}/private-consignment/consult"
    agora = datetime.now()
    inicio_periodo = (agora - pd.Timedelta(days=1)).strftime("%Y-%m-%dT00:00:00Z")
    fim_periodo = agora.strftime("%Y-%m-%dT23:59:59Z")
    params = {
        "startDate": inicio_periodo,
        "endDate": fim_periodo,
        "limit": 20,
        "page": 1,
        "search": cpf,
        "provider": V8_CLT_PROVIDER,
    }

    for _tentativa in range(tentativas):
        resp = _req.get(url, params=params, headers=v8_clt_headers(), timeout=30)
        if resp.status_code == 401:
            resp = _req.get(url, params=params, headers={
                "Authorization": f"Bearer {v8_clt_obter_token(forcar_novo=True)}",
                "Content-Type": "application/json",
            }, timeout=30)
        if resp.status_code >= 400:
            raise RuntimeError(f"Erro ao consultar status V8 (HTTP {resp.status_code}): {resp.text}")

        data = resp.json()
        registros = data.get("data", [])
        candidato = next((r for r in registros if r.get("id") == consult_id), None)
        if candidato is None and registros:
            candidato = registros[0]

        if candidato:
            status = candidato.get("status")
            if status in ("SUCCESS", "FAILED", "REJECTED"):
                return candidato

        time.sleep(intervalo_segundos)

    return None


def v8_clt_consultar_margem(cpf, nome, celular, data_nascimento, genero, email):
    """Fluxo completo: cria consulta -> autoriza -> aguarda resultado."""
    consult_id = v8_clt_criar_consulta(cpf, nome, celular, data_nascimento, genero, email)
    v8_clt_autorizar_consulta(consult_id)
    resultado = v8_clt_consultar_status(cpf, consult_id)
    if resultado is None:
        raise RuntimeError("Tempo de espera esgotado sem retorno da V8 (CLT).")
    return resultado


# Nomes comuns terminados em "a" que na verdade são masculinos (exceções à regra geral)
_NOMES_MASCULINOS_TERMINADOS_EM_A = {
    "luca", "joshua", "isaac", "elisha", "noah", "ezra", "yehoshua",
}

# Nomes femininos comuns no Brasil que não terminam em "a"/"e" típico (fogem da regra de sufixo)
_NOMES_FEMININOS_CONHECIDOS = {
    "viviane", "elisabete", "elisabeth", "jaqueline", "marilyn", "ruth", "esther",
    "raquel", "isis", "ingrid", "carol", "meire", "elizabeth", "nicole", "yasmin",
    "yasmim", "kelly", "kellen", "eloise", "heloise", "elis", "iris", "miriam",
    "abgail", "abigail", "jussara", "salete", "elaine", "solange", "helen",
}


def inferir_genero_por_nome(nome_completo):
    """Estimativa (não garantida) de gênero a partir do primeiro nome, usando
    a terminação mais comum em português (nomes terminados em 'a'/'ane'/etc -> feminino,
    mais listas pequenas de exceções conhecidas). Retorna 'male' ou 'female'."""
    if not nome_completo or not str(nome_completo).strip():
        return ""
    primeiro_nome = str(nome_completo).strip().split()[0].lower()
    primeiro_nome = re.sub(r"[^a-zà-ú]", "", primeiro_nome)
    if not primeiro_nome:
        return ""
    if primeiro_nome in _NOMES_FEMININOS_CONHECIDOS:
        return "female"
    if primeiro_nome in _NOMES_MASCULINOS_TERMINADOS_EM_A:
        return "male"
    if primeiro_nome.endswith(("a", "ane", "ete", "ice", "riz", "ana", "ela", "ina")):
        return "female"
    return "male"


# ============================================================
# CLT MULTI-BANCOS - PROCESSAMENTO EM LOTE UNIFICADO (SOMA + V8)
# ============================================================
def clt_mb_status_atual_rodada(rodada_id):
    try:
        res = supabase.table("clt_multibanco_rodadas").select("status").eq("id", rodada_id).execute()
        return res.data[0]["status"] if res.data else None
    except Exception:
        return None


def clt_mb_ja_processados(rodada_id):
    try:
        res = supabase.table("clt_multibanco_resultados").select("cpf,banco").eq("rodada_id", rodada_id).execute()
        return set((r["cpf"], r["banco"]) for r in (res.data or []))
    except Exception:
        return set()


def clt_mb_incrementar_processados(rodada_id):
    try:
        res_atual = supabase.table("clt_multibanco_rodadas").select("processados").eq("id", rodada_id).execute()
        processados_atual = (res_atual.data[0]["processados"] if res_atual.data else 0) or 0
        supabase.table("clt_multibanco_rodadas").update({
            "processados": processados_atual + 1,
            "ultimo_processamento_em": str(datetime.now()),
        }).eq("id", rodada_id).execute()
    except Exception:
        pass


def clt_mb_processar_um(registro, banco, rodada_id):
    inicio = time.time()
    cpf = registro["cpf"]
    try:
        if banco == "SOMA":
            resultado = soma_consultar_margem(
                cpf, nome=registro.get("nome", ""), celular=registro.get("celular", ""),
                data_nascimento=registro.get("data_nascimento", ""), bancarizadora="CELCOIN"
            )
            status = resultado.get("conStatusNome") or "success"
            margem = resultado.get("conMargemDisponivel")
            mensagem = resultado.get("conMensagem")
        elif banco == "V8":
            resultado = v8_clt_consultar_margem(
                cpf, nome=registro.get("nome", ""), celular=registro.get("celular", ""),
                data_nascimento=registro.get("data_nascimento", ""),
                genero=registro.get("genero", ""), email=registro.get("email", "")
            )
            status = resultado.get("status")
            margem_str = resultado.get("availableMarginValue")
            try:
                margem = float(margem_str) if margem_str not in (None, "") else None
            except Exception:
                margem = None
            mensagem = resultado.get("description")
        else:
            raise RuntimeError(f"Banco desconhecido: {banco}")

        supabase.table("clt_multibanco_resultados").insert({
            "rodada_id": rodada_id, "cpf": cpf, "banco": banco,
            "status": status, "margem_disponivel": margem, "mensagem": mensagem,
            "resposta_completa": resultado, "tempo_segundos": round(time.time() - inicio, 1),
        }).execute()
    except Exception as e:
        supabase.table("clt_multibanco_resultados").insert({
            "rodada_id": rodada_id, "cpf": cpf, "banco": banco,
            "status": "erro", "mensagem": str(e), "tempo_segundos": round(time.time() - inicio, 1),
        }).execute()


_clt_mb_threads_ativas = {}
_clt_mb_threads_lock = threading.Lock()
CLT_MB_NUM_WORKERS = 4


def _clt_mb_finalizar(rodada_id):
    with _clt_mb_threads_lock:
        _clt_mb_threads_ativas[rodada_id] = _clt_mb_threads_ativas.get(rodada_id, 1) - 1
        restantes = _clt_mb_threads_ativas[rodada_id]
    if restantes <= 0:
        status_banco_final = clt_mb_status_atual_rodada(rodada_id)
        if status_banco_final == "cancelando":
            status_final = "cancelada"
        elif status_banco_final == "pausando":
            status_final = "pausada"
        else:
            status_final = "concluida"
        update_dados = {"status": status_final}
        if status_final in ("concluida", "cancelada"):
            update_dados["finalizado_em"] = str(datetime.now())
        supabase.table("clt_multibanco_rodadas").update(update_dados).eq("id", rodada_id).execute()


def clt_mb_worker(registros_fatia, rodada_id, bancos, parar_flag):
    ja_processados = clt_mb_ja_processados(rodada_id)
    for registro in registros_fatia:
        for banco in bancos:
            if (registro["cpf"], banco) in ja_processados:
                continue
            status_banco = clt_mb_status_atual_rodada(rodada_id)
            if status_banco == "cancelando" or parar_flag.get("parar") == "cancelar":
                _clt_mb_finalizar(rodada_id)
                return
            if status_banco == "pausando" or parar_flag.get("parar") == "pausar":
                _clt_mb_finalizar(rodada_id)
                return
            clt_mb_processar_um(registro, banco, rodada_id)
            clt_mb_incrementar_processados(rodada_id)

    _clt_mb_finalizar(rodada_id)


def clt_mb_iniciar_threads(registros, rodada_id, bancos, parar_flag, n_workers=CLT_MB_NUM_WORKERS):
    n_workers = max(1, min(n_workers, len(registros)))
    fatias = [registros[i::n_workers] for i in range(n_workers)]
    with _clt_mb_threads_lock:
        _clt_mb_threads_ativas[rodada_id] = n_workers
    for fatia in fatias:
        if not fatia:
            with _clt_mb_threads_lock:
                _clt_mb_threads_ativas[rodada_id] -= 1
            continue
        thread = threading.Thread(target=clt_mb_worker, args=(fatia, rodada_id, bancos, parar_flag), daemon=True)
        thread.start()


def clt_mb_buscar_rodada_ativa():
    try:
        res = supabase.table("clt_multibanco_rodadas").select("*").in_("status", ["em_andamento","pausando","cancelando"]).order("id", desc=True).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


def clt_mb_buscar_rodadas_pausadas():
    try:
        res = supabase.table("clt_multibanco_rodadas").select("*").eq("status", "pausada").order("id", desc=True).execute()
        return res.data or []
    except Exception:
        return []


def clt_mb_buscar_historico(limite=15):
    try:
        res = supabase.table("clt_multibanco_rodadas").select("*").order("id", desc=True).limit(limite).execute()
        return res.data or []
    except Exception:
        return []


def clt_mb_buscar_resultados(rodada_id):
    try:
        res = supabase.table("clt_multibanco_resultados").select("*").eq("rodada_id", rodada_id).execute()
        return res.data or []
    except Exception:
        return []


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #f0f6ff !important; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; max-width: 1180px !important; }
[data-testid="stSidebar"] { background: radial-gradient(circle at top left, rgba(14,165,233,0.22), transparent 35%), linear-gradient(180deg, #020c1e 0%, #031228 50%, #020b1a 100%) !important; border-right: 1px solid rgba(56,189,248,0.25) !important; min-width: 245px !important; max-width: 245px !important; box-shadow: 4px 0 40px rgba(14,165,233,0.18) !important; }
section[data-testid="stSidebar"] > div { padding-left: 16px !important; padding-right: 16px !important; padding-top: 18px !important; }
[data-testid="stSidebar"] * { color: #e2f4ff !important; }
[data-testid="stSidebar"] .stButton button { color: #b8e3f8 !important; background: transparent !important; border: 0 !important; border-radius: 14px !important; box-shadow: none !important; text-align: left !important; justify-content: flex-start !important; font-weight: 700 !important; padding: 0.65rem 0.75rem !important; transition: all .18s ease-in-out; }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(56,189,248,0.12) !important; transform: translateX(2px); color: #ffffff !important; }
.sidebar-logo-icon-v8 { width: 52px; height: 52px; border-radius: 18px; background: radial-gradient(circle at 50% 50%, #020617 0%, #020617 32%, #0ea5e9 44%, #2563eb 70%, #38bdf8 100%); display: flex; align-items: center; justify-content: center; font-size: 25px; font-weight: 900; color: #ffffff; box-shadow: 0 0 34px rgba(56,189,248,0.58), inset 0 0 0 1px rgba(255,255,255,0.22); }
.sidebar-user-v8 { background: rgba(14,165,233,0.08); border: 1px solid rgba(56,189,248,0.25); border-radius: 16px; padding: 13px 14px; margin: 8px 0 20px 0; color: white !important; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.sidebar-dot { width: 9px; height: 9px; background: #22c55e; border-radius: 50%; box-shadow: 0 0 8px #22c55e; flex-shrink: 0; }
.menu-label-v8 { color: rgba(56,189,248,0.80) !important; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .12em; margin: 18px 0 8px 6px; }
.menu-ativo-v8 { background: linear-gradient(90deg, rgba(37,99,235,0.90), rgba(14,165,233,0.85)) !important; color: #ffffff !important; border-radius: 14px; border: 1px solid rgba(56,189,248,0.30) !important; padding: 13px 14px; margin: 5px 0; font-weight: 700; box-shadow: 0 0 22px rgba(56,189,248,0.40), inset 0 0 0 1px rgba(255,255,255,0.15); display: flex; align-items: center; gap: 12px; overflow: hidden; min-height: 50px; }
.menu-ativo-v8 span { color: #ffffff !important; font-size: 15px; background: transparent !important; }
.menu-ativo-v8 svg, .menu-svg-v8 svg { width: 20px; height: 20px; stroke-width: 2.2; flex-shrink: 0; stroke: #ffffff !important; background: transparent !important; }
.menu-svg-v8 { display: flex; align-items: center; justify-content: center; min-height: 42px; color: #38bdf8 !important; opacity: 0.95; }
.menu-ativo-v8 pre, .menu-ativo-v8 code, .menu-ativo-v8 p { display: none !important; }
.menu-ativo-v8 * { background: transparent !important; box-shadow: none !important; }
.crm-hero { background: linear-gradient(135deg, rgba(3,18,45,0.97), rgba(4,22,55,0.95)); border: 1px solid rgba(56,189,248,0.25); border-radius: 22px; padding: 22px 28px; margin-bottom: 26px; box-shadow: 0 0 0 1px rgba(56,189,248,0.08), 0 0 40px rgba(14,165,233,0.15), 0 16px 48px rgba(0,0,0,0.40); position: relative; overflow: hidden; }
.crm-hero::before { content: ''; position: absolute; top: -60px; right: -60px; width: 220px; height: 220px; background: radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%); pointer-events: none; }
.crm-title { font-size: 36px; line-height: 1.02; font-family: 'Orbitron', sans-serif !important; font-weight: 900; color: #ffffff !important; margin: 0; letter-spacing: 0.07em; }
.crm-title span { color: #38bdf8 !important; }
.crm-subtitle { margin: 8px 0 0 0; color: #ffffff !important; font-size: 14px; font-weight: 500; opacity: 0.85; }
.crm-pill { display: inline-flex; align-items: center; gap: 8px; margin-top: 12px; padding: 8px 14px; border-radius: 999px; background: linear-gradient(90deg, #2563eb, #0ea5e9); color: #ffffff !important; border: 1px solid rgba(14,165,233,0.22); font-weight: 700; font-size: 13px; box-shadow: 0 0 16px rgba(14,165,233,0.30); }
div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea { background: #ffffff !important; border: 1.5px solid rgba(56,189,248,0.45) !important; border-radius: 12px !important; color: #0f172a !important; }
div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus { border-color: #0ea5e9 !important; box-shadow: 0 0 0 3px rgba(14,165,233,0.18) !important; }
div[data-testid="stTextInput"] input::placeholder, div[data-testid="stTextArea"] textarea::placeholder { color: #94a3b8 !important; }
div[data-baseweb="select"] { background: #ffffff !important; border: 1.5px solid rgba(56,189,248,0.45) !important; border-radius: 12px !important; }
div[data-baseweb="select"] * { background: #ffffff !important; color: #0f172a !important; }
[data-testid="stTextInput"] label, [data-testid="stNumberInput"] label, [data-testid="stTextArea"] label, [data-testid="stSelectbox"] label, .stCheckbox label { color: #0ea5e9 !important; font-weight: 700 !important; font-size: 12px !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
.stButton button { background: linear-gradient(135deg, #1d4ed8, #0ea5e9) !important; border: 1px solid rgba(56,189,248,0.50) !important; border-radius: 12px !important; color: #ffffff !important; font-weight: 700 !important; box-shadow: 0 0 18px rgba(14,165,233,0.35), 0 8px 24px rgba(14,165,233,0.20) !important; transition: all 0.2s !important; }
.stButton button:hover { background: linear-gradient(135deg, #2563eb, #38bdf8) !important; box-shadow: 0 0 28px rgba(56,189,248,0.55), 0 12px 32px rgba(14,165,233,0.30) !important; transform: translateY(-1px) !important; }
div[data-testid="stMetric"] { background: #ffffff !important; border: 1.5px solid rgba(14,165,233,0.45) !important; border-radius: 16px !important; padding: 18px 20px !important; box-shadow: 0 0 14px rgba(14,165,233,0.12), 0 4px 16px rgba(0,0,0,0.06) !important; }
div[data-testid="stMetric"] label { color: #0ea5e9 !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #0f172a !important; font-weight: 800 !important; font-size: 24px !important; }
.stDataFrame { border-radius: 14px !important; overflow: hidden !important; border: 1.5px solid rgba(14,165,233,0.35) !important; box-shadow: 0 0 18px rgba(14,165,233,0.10) !important; }
h1, h2, h3 { color: #0f172a !important; letter-spacing: -0.02em; }
.stSuccess > div { background: #f0fdf4 !important; border: 1.5px solid #86efac !important; border-radius: 12px !important; color: #166534 !important; }
.stError > div { background: #fef2f2 !important; border: 1.5px solid #fca5a5 !important; border-radius: 12px !important; color: #991b1b !important; }
.stWarning > div { background: #fffbeb !important; border: 1.5px solid #fde68a !important; border-radius: 12px !important; color: #92400e !important; }
.stInfo > div { background: #eff6ff !important; border: 1.5px solid rgba(14,165,233,0.50) !important; border-radius: 12px !important; color: #1d4ed8 !important; }
div[data-testid="stForm"] { background: #ffffff !important; border: 1.5px solid rgba(14,165,233,0.30) !important; border-radius: 16px !important; padding: 20px !important; box-shadow: 0 0 18px rgba(14,165,233,0.08) !important; }
hr { border-color: rgba(14,165,233,0.25) !important; }
.stApp h2 { font-family: 'Orbitron', sans-serif !important; color: #ffffff !important; border-bottom: 2px solid rgba(14,165,233,0.45); padding-bottom: 8px; }
.stApp p, .stApp span, .stApp div { color: #0f172a; }
.stCaption, small { color: #0369a1 !important; opacity: 1; }
header { background: transparent !important; }
.stForm [data-testid="InputInstructions"] { display: none !important; }
small[data-testid="InputInstructions"] { display: none !important; }
[data-testid="InputInstructions"] { display: none !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: rgba(2,12,30,0.5); }
::-webkit-scrollbar-thumb { background: rgba(56,189,248,0.25); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

def achar_logo():
    nomes = ["logo_operax.png","logo_operax(1).png","logo_operax (1).png","logo.png"]
    for nome in nomes:
        caminho = Path(nome)
        if caminho.exists() and caminho.stat().st_size > 100:
            return caminho
    return None

def mostrar_cabecalho():
    logo_url = "https://raw.githubusercontent.com/Nicolasfami/sistema-vendas/main/logo_sem_escrita.png"
    st.markdown(f"""
        <div class="crm-hero">
            <div style="display:flex;align-items:center;gap:22px;">
                <img src="{logo_url}" style="width:72px;height:72px;border-radius:20px;flex-shrink:0;object-fit:cover;box-shadow:0 0 28px rgba(56,189,248,0.70);">
                <div>
                    <h1 class="crm-title">OPERAX <span>SALES</span></h1>
                    <p class="crm-subtitle">Sistema inteligente de vendas e operações financeiras</p>
                    <div class="crm-pill">⚡ Painel inteligente • Atualização por ação • Controle por vendedor</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def hash_senha(senha):
    return hashlib.sha256(str(senha).encode()).hexdigest()

def dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except Exception:
        return "R$ 0,00"



def gerar_svg_pizza_bancos(labels, valores, cores, titulo="Contratos por banco"):
    total = sum(valores)
    if total <= 0:
        return '<div style="font-family:Inter,Arial;padding:18px;border:1px solid #e2e8f0;border-radius:16px;background:#fff;color:#64748b;text-align:center;">Nenhum dado para montar o gráfico.</div>'

    cx, cy, r = 130, 130, 105
    angulo_atual = -90.0
    fatias = []
    legendas = []

    for i, (label, val) in enumerate(zip(labels, valores)):
        fracao = val / total
        angulo_fatia = fracao * 360.0
        angulo_fim = angulo_atual + angulo_fatia
        cor = cores[i % len(cores)]

        if len(valores) == 1:
            fatias.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{cor}" stroke="#ffffff" stroke-width="3"/>')
            lx, ly = cx, cy
        else:
            x1 = cx + r * math.cos(math.radians(angulo_atual))
            y1 = cy + r * math.sin(math.radians(angulo_atual))
            x2 = cx + r * math.cos(math.radians(angulo_fim))
            y2 = cy + r * math.sin(math.radians(angulo_fim))
            large_arc = 1 if angulo_fatia > 180 else 0
            fatias.append(f'<path d="M{cx},{cy} L{x1:.2f},{y1:.2f} A{r},{r} 0 {large_arc} 1 {x2:.2f},{y2:.2f} Z" fill="{cor}" stroke="#ffffff" stroke-width="3"/>')
            ang_meio = math.radians((angulo_atual + angulo_fim) / 2)
            lx = cx + (r * 0.62) * math.cos(ang_meio)
            ly = cy + (r * 0.62) * math.sin(ang_meio)

        if fracao >= 0.045:
            fatias.append(f'<text x="{lx:.2f}" y="{ly:.2f}" text-anchor="middle" dominant-baseline="middle" font-size="16" font-weight="800" fill="#ffffff" font-family="Inter,Arial">{int(val)}</text>')

        pct = fracao * 100
        label_safe = str(label).replace("<", "&lt;").replace(">", "&gt;")
        legendas.append(f'<div class="legend-row"><span class="legend-color" style="background:{cor};"></span><span class="legend-name">{label_safe}</span><span class="legend-value">{int(val)} • {pct:.1f}%</span></div>')
        angulo_atual = angulo_fim

    fatias_html = ''.join(fatias)
    legendas_html = ''.join(legendas)
    return f'''
    <html>
    <head>
        <style>
            body {{ margin:0; font-family: Inter, Arial, sans-serif; background: transparent; }}
            .wrap {{ background:#ffffff; border:1.5px solid rgba(14,165,233,0.28); border-radius:18px; padding:18px; box-shadow:0 8px 28px rgba(15,23,42,0.06); }}
            .title {{ font-size:15px; font-weight:900; color:#0f172a; margin-bottom:12px; }}
            .content {{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; }}
            .chart {{ width:260px; min-width:260px; }}
            .legend {{ flex:1; min-width:240px; }}
            .legend-row {{ display:flex; align-items:center; gap:9px; padding:7px 0; border-bottom:1px solid #eef2f7; }}
            .legend-color {{ width:12px; height:12px; border-radius:4px; flex-shrink:0; }}
            .legend-name {{ flex:1; font-size:13px; font-weight:750; color:#0f172a; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
            .legend-value {{ font-size:12px; color:#64748b; font-weight:800; }}
            .total {{ margin-top:10px; font-size:12px; color:#0369a1; font-weight:900; text-transform:uppercase; letter-spacing:.06em; }}
        </style>
    </head>
    <body>
        <div class="wrap">
            <div class="title">{titulo}</div>
            <div class="content">
                <div class="chart"><svg width="260" height="260" viewBox="0 0 260 260" xmlns="http://www.w3.org/2000/svg">{fatias_html}</svg></div>
                <div class="legend">{legendas_html}<div class="total">Total: {int(total)} contrato(s)</div></div>
            </div>
        </div>
    </body>
    </html>
    '''


def renderizar_pizza_bancos(df_base, titulo="Contratos por banco"):
    if df_base.empty or "tabela_banco" not in df_base.columns:
        st.info("Nenhum dado de banco/tabela para mostrar.")
        return

    df_tmp = df_base.copy()
    df_tmp = df_tmp[df_tmp["tabela_banco"].notna()]
    df_tmp["tabela_banco"] = df_tmp["tabela_banco"].astype(str).str.strip()
    df_tmp = df_tmp[df_tmp["tabela_banco"] != ""]

    if df_tmp.empty:
        st.info("Nenhum dado de banco/tabela para mostrar.")
        return

    resumo = df_tmp.groupby("tabela_banco").agg(
        contratos=("id", "count"),
        valor_total=("valor", "sum")
    ).reset_index().sort_values(["contratos", "valor_total"], ascending=False)

    cores = ["#0ea5e9", "#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#14b8a6", "#ec4899", "#84cc16", "#f97316", "#06b6d4", "#8b5cf6"]
    labels = resumo["tabela_banco"].tolist()
    valores = resumo["contratos"].astype(int).tolist()
    html = gerar_svg_pizza_bancos(labels, valores, cores, titulo=titulo)
    components.html(html, height=340, scrolling=False)

    tabela = resumo.rename(columns={"tabela_banco":"Banco/Tabela", "contratos":"Contratos", "valor_total":"Valor produzido"})
    tabela["Valor produzido"] = tabela["Valor produzido"].apply(dinheiro)
    st.dataframe(tabela, use_container_width=True, hide_index=True)


def limpar_documento(valor):
    return re.sub(r"\D","",str(valor or ""))

def validar_cpf(cpf):
    cpf_limpo = limpar_documento(cpf)
    if len(cpf_limpo) != 11: return False
    if cpf_limpo == cpf_limpo[0]*11: return False
    soma = sum(int(cpf_limpo[i])*(10-i) for i in range(9))
    d1 = (soma*10)%11
    if d1==10: d1=0
    soma = sum(int(cpf_limpo[i])*(11-i) for i in range(10))
    d2 = (soma*10)%11
    if d2==10: d2=0
    return d1==int(cpf_limpo[9]) and d2==int(cpf_limpo[10])

def validar_telefone(telefone):
    t = limpar_documento(telefone)
    if len(t) not in [10,11]: return False
    ddd = t[:2]
    numero = t[2:]
    if ddd=="00": return False
    if len(t)==11 and not numero.startswith("9"): return False
    return True

def converter_valor_brasileiro(valor):
    texto = str(valor or "").strip()
    if not texto: return 0.0
    texto = texto.replace("R$","").replace(" ","")
    if "," in texto:
        texto = texto.replace(".","").replace(",",".")
    try:
        return float(texto)
    except Exception:
        return 0.0

def login(usuario, senha):
    usuario = str(usuario).strip().lower()
    senha_hash = hash_senha(str(senha).strip())
    res = supabase.table("usuarios").select("*").eq("usuario",usuario).eq("ativo",True).execute()
    if not res.data: return None
    user = res.data[0]
    if user.get("senha_hash") == senha_hash: return user
    return None

def carregar_tabelas():
    res = supabase.table("regras_comissao").select("*").eq("ativo",True).execute()
    tabelas = sorted(list(set([r.get("produto") for r in res.data if r.get("produto")])))
    if not tabelas:
        tabelas = ["CLT PADRAO","V8 ACIMA 36X","PRESENCA","HUBBIE","OUTROS BANCOS"]
    return tabelas

def calcular_comissao_montante(df_filtrado):
    total_empresa = 0
    if df_filtrado.empty: return 0
    if "status" not in df_filtrado.columns or "tabela_banco" not in df_filtrado.columns: return 0
    df_pagas = df_filtrado[df_filtrado["status"]=="Pago"].copy()
    if df_pagas.empty: return 0
    for tabela in df_pagas["tabela_banco"].dropna().unique():
        total_tabela = df_pagas[df_pagas["tabela_banco"]==tabela]["valor"].fillna(0).sum()
        regras = supabase.table("regras_comissao").select("*").eq("produto",tabela).eq("ativo",True).order("valor_minimo",desc=True).execute()
        percentual = 0
        for regra in regras.data:
            valor_minimo = float(regra.get("valor_minimo") or 0)
            if float(total_tabela) >= valor_minimo:
                percentual = float(regra.get("percentual_empresa") or 0)
                break
        total_empresa += float(total_tabela)*(percentual/100)
    return total_empresa

def calcular_percentual_empresa_venda(tabela_banco, valor):
    regras = supabase.table("regras_comissao").select("*").eq("produto",tabela_banco).eq("ativo",True).order("valor_minimo",desc=True).execute()
    percentual = 0
    for regra in regras.data:
        valor_minimo = float(regra.get("valor_minimo") or 0)
        if float(valor) >= valor_minimo:
            percentual = float(regra.get("percentual_empresa") or 0)
            break
    return percentual


def converter_data_supabase_coluna(serie):
    s = serie.astype(str).str.strip()
    s = s.replace({"None": None, "none": None, "nan": None, "NaT": None, "": None})
    s = s.str.replace("Z", "", regex=False)
    dt = pd.to_datetime(s, errors="coerce", format="mixed", dayfirst=False)
    try:
        if getattr(dt.dt, "tz", None) is not None:
            dt = dt.dt.tz_localize(None)
    except (TypeError, AttributeError):
        pass
    return dt


def preparar_dataframe_vendas():
    try:
        todos = []
        inicio = 0
        passo = 1000

        while True:
            res = (
                supabase
                .table("vendas")
                .select("*")
                .order("id", desc=True)
                .range(inicio, inicio + passo - 1)
                .execute()
            )

            lote = res.data or []
            todos.extend(lote)

            if len(lote) < passo:
                break

            inicio += passo

        df = pd.DataFrame(todos)

    except Exception as e:
        st.error(f"Erro ao buscar vendas no Supabase: {e}")
        return pd.DataFrame()

    if df.empty:
        return df

    for col in ["data","vendedor_id","vendedor","tabela_banco","valor","status","conferido","alterado_vendedor","ultima_alteracao_em","ultima_alteracao_por","ultima_alteracao_resumo"]:
        if col not in df.columns:
            if col=="tabela_banco" and "produto" in df.columns:
                df["tabela_banco"] = df["produto"]
            elif col=="valor":
                df[col] = 0
            elif col=="status":
                df[col] = "Pendente"
            elif col in ["conferido","alterado_vendedor"]:
                df[col] = False
            else:
                df[col] = None

    df["data_original_supabase"] = df["data"]
    df["data"] = converter_data_supabase_coluna(df["data"])

    df["mes_num"] = df["data"].dt.month
    df["ano"] = df["data"].dt.year
    df["dia"] = df["data"].dt.day

    return df

def destacar_linhas_pendentes(row, tipo_usuario):
    try:
        status_key = "Status" if "Status" in row.index else "status"
        status = str(row.get(status_key,"")).strip().lower()
        data_key = "Data" if "Data" in row.index else "data"
        data_venda = row.get(data_key, None)
        if status not in ["pendente","aguardando pagamento","aguardando assinatura"]:
            return [""]*len(row)
        agora = pd.Timestamp.now()
        if pd.notna(data_venda):
            data_venda = pd.to_datetime(data_venda,errors="coerce")
            horas_pendente = (agora-data_venda).total_seconds()/3600
        else:
            horas_pendente = 0
        if status=="aguardando pagamento": return ["background-color: #dbeafe"]*len(row)
        if status=="aguardando assinatura": return ["background-color: #ede9fe"]*len(row)
        if tipo_usuario=="admin" and horas_pendente>=1: return ["background-color: #ffb3b3"]*len(row)
        return ["background-color: #fff3b0"]*len(row)
    except Exception:
        return [""]*len(row)

def carregar_usuarios_chat():
    try:
        res = supabase.table("usuarios").select("id,nome,usuario,tipo,ativo").eq("ativo",True).order("nome").execute()
        usuarios = res.data or []
        return [u for u in usuarios if int(u.get("id")) != int(st.session_state.user_id)]
    except Exception:
        return []

def carregar_mensagens_chat(destinatario_id, limite=80):
    try:
        meu_id = int(st.session_state.user_id)
        outro_id = int(destinatario_id)
        res = supabase.table("chat_interno").select("*").order("criado_em",desc=True).limit(300).execute()
        todas = res.data or []
        mensagens = []
        for msg in todas:
            origem = msg.get("usuario_id")
            destino = msg.get("destinatario_id")
            try:
                origem = int(origem) if origem is not None else None
                destino = int(destino) if destino is not None else None
            except Exception:
                origem = None; destino = None
            if ((origem==meu_id and destino==outro_id) or (origem==outro_id and destino==meu_id)):
                mensagens.append(msg)
        mensagens = mensagens[-limite:]
        mensagens.reverse()
        return mensagens
    except Exception:
        return []

def enviar_mensagem_chat(usuario_id, destinatario_id, nome, tipo, mensagem):
    supabase.table("chat_interno").insert({
        "usuario_id": usuario_id,
        "destinatario_id": destinatario_id,
        "nome": nome,
        "tipo": tipo,
        "mensagem": mensagem,
        "criado_em": str(datetime.now())
    }).execute()

def contar_mensagens_nao_lidas():
    try:
        if "chat_lido_em" not in st.session_state:
            st.session_state.chat_lido_em = str(datetime.now())
        res = supabase.table("chat_interno").select("*").eq("destinatario_id",st.session_state.user_id).execute()
        mensagens = res.data or []
        ultima_leitura = pd.to_datetime(st.session_state.chat_lido_em,errors="coerce")
        total = 0
        for msg in mensagens:
            data_msg = pd.to_datetime(msg.get("criado_em"),errors="coerce")
            if pd.notna(data_msg) and pd.notna(ultima_leitura):
                if data_msg > ultima_leitura: total += 1
        return total
    except Exception:
        return 0

def mostrar_chat_popup():
    nao_lidas = contar_mensagens_nao_lidas()
    col_spacer, col_chat = st.columns([8,1.8])
    with col_chat:
        label_chat = f"🟢 💬 Chat ({nao_lidas})" if nao_lidas > 0 else "💬 Chat"
        try:
            chat_context = st.popover(label_chat, use_container_width=True)
        except Exception:
            chat_context = st.expander(label_chat, expanded=False)
    with chat_context:
        st.session_state.chat_lido_em = str(datetime.now())
        st.markdown("### Chat interno")
        usuarios_chat = carregar_usuarios_chat()
        if not usuarios_chat:
            st.info("Nenhum outro usuário ativo encontrado.")
            return
        opcoes = {f"{u.get('nome',u.get('usuario'))} ({u.get('tipo','')})": u for u in usuarios_chat}
        escolhido_label = st.selectbox("Enviar mensagem para", list(opcoes.keys()))
        usuario_destino = opcoes[escolhido_label]
        destinatario_id = int(usuario_destino["id"])
        mensagens = carregar_mensagens_chat(destinatario_id, 80)
        chat_area = st.container(height=360)
        with chat_area:
            if not mensagens:
                st.info("Nenhuma mensagem nessa conversa ainda.")
            else:
                for msg in mensagens:
                    nome_msg = msg.get("nome","Usuario")
                    texto_msg = msg.get("mensagem","")
                    data_msg = str(msg.get("criado_em",""))[:16]
                    if int(msg.get("usuario_id")) == int(st.session_state.user_id):
                        st.markdown(f'''<div style="background:linear-gradient(135deg,#dcfce7,#bbf7d0);border:1px solid #86efac;border-radius:16px;padding:10px 12px;margin:8px 0 8px auto;max-width:88%;text-align:right;"><div style="font-size:12px;color:#166534;font-weight:700;">Voce • {data_msg}</div><div style="font-size:15px;color:#111827;">{texto_msg}</div></div>''', unsafe_allow_html=True)
                    else:
                        st.markdown(f'''<div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;padding:10px 12px;margin:8px auto 8px 0;max-width:88%;"><div style="font-size:12px;color:#64748b;font-weight:700;">{nome_msg} • {data_msg}</div><div style="font-size:15px;color:#111827;">{texto_msg}</div></div>''', unsafe_allow_html=True)
        with st.form("form_chat_popup", clear_on_submit=True):
            mensagem = st.text_input("Mensagem", placeholder=f"Mensagem para {usuario_destino.get('nome','usuario')}...")
            enviar = st.form_submit_button("Enviar")
            if enviar:
                if not mensagem.strip():
                    st.error("Digite uma mensagem antes de enviar.")
                else:
                    enviar_mensagem_chat(st.session_state.user_id, destinatario_id, st.session_state.nome, st.session_state.tipo, mensagem.strip())
                    st.rerun()

def icone_svg(nome):
    icones = {
        "nova": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M7 3h7l4 4v14H7V3Z"/><path d="M14 3v5h5"/><path d="M9 14h6"/><path d="M12 11v6"/></svg>""",
        "painel": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M4 19V5"/><path d="M4 19h16"/><path d="M8 16v-5"/><path d="M12 16V8"/><path d="M16 16v-7"/><path d="M20 16v-3"/></svg>""",
        "usuarios": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="9.5" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
        "comissoes": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7H14a3.5 3.5 0 0 1 0 7H6"/></svg>""",
        "ranking": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M6 9H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h2"/><path d="M18 9h2a2 2 0 0 0 2-2V5a2 2 0 0 0-2-2h-2"/><path d="M6 3h12v10a6 6 0 0 1-12 0V3z"/><path d="M12 19v3"/><path d="M8 22h8"/></svg>""",
        "metas": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
        "custos": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M3 9h18M3 15h18M9 3v18M15 3v18M3 3h18v18H3z"/></svg>""",
        "chat_wp": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>""",
        "fgts": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>""",
        "clt_lote": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><rect x="3" y="6" width="18" height="14" rx="2"/><path d="M3 10h18"/><path d="M8 3v4"/><path d="M16 3v4"/></svg>""",
        "clt_multi": """<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.5 4 6 4 9s-1.5 6.5-4 9c-2.5-2.5-4-6-4-9s1.5-6.5 4-9Z"/></svg>""",
    }
    return icones.get(nome,"")

def menu_lateral_v8():
    if "menu_atual" not in st.session_state:
        st.session_state.menu_atual = "📋 Nova Venda"

    if st.session_state.tipo == "admin":
        opcoes = [
            ("📋 Nova Venda", "nova", "Operacao"),
            ("📊 Painel", "painel", "Operacao"),
            ("🏆 Ranking", "ranking", "Operacao"),
            ("🎯 Metas", "metas", "Operacao"),
            ("💬 WhatsApp", "chat_wp", "Operacao"),
            ("👥 Usuarios", "usuarios", "Gestao"),
            ("💰 Comissoes", "comissoes", "Gestao"),
            ("🏢 Custos", "custos", "Gestao"),
            ("📑 Consulta FGTS", "fgts", "Gestao"),
            ("🏦 CLT Lote", "clt_lote", "Gestao"),
            ("🌐 CLT Multi-Bancos", "clt_multi", "Gestao"),
        ]
    else:
        opcoes = [
            ("📋 Nova Venda", "nova", "Operacao"),
            ("📊 Painel", "painel", "Operacao"),
            ("🏆 Ranking", "ranking", "Operacao"),
            ("🎯 Metas", "metas", "Operacao"),
            ("💬 WhatsApp", "chat_wp", "Operacao"),
        ]

    logo_path = achar_logo()
    if logo_path:
        try:
            st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:16px 8px 20px;gap:8px;">""", unsafe_allow_html=True)
            st.sidebar.image(str(logo_path), width=180)
            st.sidebar.markdown("""<div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin:4px auto 0;"></div></div>""", unsafe_allow_html=True)
        except Exception:
            st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;"><div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div><div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;">OPERAX</div><div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;">SALES</div></div>""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""<div style="display:flex;flex-direction:column;align-items:center;padding:18px 8px 20px;gap:6px;"><div class="sidebar-logo-icon-v8" style="width:64px;height:64px;font-size:32px;">🌀</div><div style="font-family:'Orbitron',sans-serif;font-size:17px;font-weight:800;color:#fff;letter-spacing:0.14em;">OPERAX</div><div style="font-family:'Rajdhani',sans-serif;font-size:11px;font-weight:600;color:#38bdf8;letter-spacing:0.50em;">SALES</div><div style="height:1px;width:80%;background:linear-gradient(90deg,transparent,rgba(56,189,248,0.40),transparent);margin-top:6px;"></div></div>""", unsafe_allow_html=True)

    st.sidebar.markdown(f'''<div class="sidebar-user-v8">{st.session_state.nome}</div>''', unsafe_allow_html=True)

    grupo_atual = None
    for nome, icone_nome, grupo in opcoes:
        nome_limpo = (nome.replace("📋 ","").replace("📊 ","").replace("👥 ","")
                      .replace("💰 ","").replace("🏆 ","").replace("🎯 ","")
                      .replace("🏢 ","").replace("💬 ","").replace("📑 ","")
                      .replace("🏦 ","").replace("🌐 ",""))
        if grupo != grupo_atual:
            st.sidebar.markdown(f'''<div class="menu-label-v8">{grupo}</div>''', unsafe_allow_html=True)
            grupo_atual = grupo
        svg = icone_svg(icone_nome)
        if st.session_state.menu_atual == nome:
            st.sidebar.markdown(f'''<div class="menu-ativo-v8"><div class="menu-icon-wrap">{svg}</div><span class="menu-label-text">{nome_limpo}</span></div>''', unsafe_allow_html=True)
        else:
            col_icon, col_btn = st.sidebar.columns([0.23,0.77])
            with col_icon:
                st.markdown(f'''<div class="menu-svg-v8">{svg}</div>''', unsafe_allow_html=True)
            with col_btn:
                if st.button(nome_limpo, key=f"menu_{nome}", use_container_width=True):
                    st.session_state.menu_atual = nome
                    st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Sair  ↪", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    return st.session_state.menu_atual

# =========================
# WATCHDOG EXTERNO (cron job)
# =========================
WATCHDOG_SENHA_SECRETA = "OPERAX_FGTS_WATCHDOG_2026"

_parametros_url = st.query_params
if _parametros_url.get("watchdog") == WATCHDOG_SENHA_SECRETA:
    resultado_watchdog = fgts_checar_e_religar_rodada_ativa()
    if resultado_watchdog:
        st.write(f"✅ {resultado_watchdog}")
    else:
        st.write("ℹ️ Nenhuma rodada travada encontrada. Tudo OK.")
    st.stop()

# =========================
# LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.markdown("""<style>
    .stApp { background: radial-gradient(ellipse at 20% 30%, rgba(14,165,233,0.13) 0%, transparent 45%), radial-gradient(ellipse at 80% 70%, rgba(37,99,235,0.10) 0%, transparent 40%), linear-gradient(160deg, #020b18 0%, #030f22 50%, #020b18 100%) !important; }
    [data-testid="stSidebar"] { display:none !important; }
    header[data-testid="stHeader"] { display:none !important; }
    .block-container { max-width: 420px !important; margin: 0 auto !important; padding: 40px 36px 36px !important; margin-top: calc(50vh - 320px) !important; background: rgba(7,18,48,0.96) !important; border: 1px solid rgba(56,189,248,0.28) !important; border-radius: 24px !important; box-shadow: 0 0 0 1px rgba(56,189,248,0.07), 0 0 60px rgba(14,165,233,0.18), 0 28px 80px rgba(0,0,0,0.85) !important; }
    .l-icon { width:220px;height:220px;margin:0 auto 6px auto;background:transparent;display:flex;align-items:center;justify-content:center; }
    .l-title { font-family:Orbitron,sans-serif;font-size:24px;font-weight:900;letter-spacing:0.06em;color:#ffffff !important;margin-bottom:2px;margin-top:6px;text-align:center; }
    .l-title b { color:#38bdf8 !important; }
    .l-sub { color:#ffffff !important;font-size:13px;opacity:0.85;margin-bottom:16px;text-align:center; }
    div[data-testid="stTextInput"] input { background:rgba(5,14,40,0.98) !important;border:1.5px solid rgba(14,165,233,0.60) !important;border-radius:11px !important;color:#e2f4ff !important;font-size:15px !important; }
    div[data-testid="stTextInput"] input::placeholder { color:rgba(125,211,252,0.28) !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stTextInput"] label p { color:#38bdf8 !important;font-size:11px !important;font-weight:700 !important;letter-spacing:0.14em !important;text-transform:uppercase !important; }
    .stButton > button { background:linear-gradient(90deg,#1848cc,#0ea5e9) !important;border:none !important;border-radius:12px !important;color:#fff !important;font-size:16px !important;font-weight:700 !important;height:52px !important;margin-top:6px !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown('<div class="l-icon"><img src="https://raw.githubusercontent.com/Nicolasfami/sistema-vendas/main/logo_sem_escrita.png" style="width:220px;height:220px;object-fit:contain;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="l-title">OPERAX <b>SALES</b></div>', unsafe_allow_html=True)
    st.markdown('<div class="l-sub">Sistema inteligente de vendas e operacoes financeiras</div>', unsafe_allow_html=True)

    usuario = st.text_input("Usuario", placeholder="Seu login", key="login_user")
    senha   = st.text_input("Senha", type="password", placeholder="••••••••", key="login_pass")

    if st.button("⚡  Entrar", use_container_width=True, key="btn_entrar"):
        user = login(usuario, senha)
        if user:
            st.session_state.logado  = True
            st.session_state.user_id = user["id"]
            st.session_state.usuario = user["usuario"]
            st.session_state.nome    = user["nome"]
            st.session_state.tipo    = user["tipo"]
            st.rerun()
        else:
            st.markdown('<div style="background:#fee2e2;border:1.5px solid #ef4444;border-radius:10px;padding:10px 14px;color:#991b1b;font-weight:700;font-size:14px;margin-top:8px;">❌ Usuario ou senha invalidos</div>', unsafe_allow_html=True)

else:
    mostrar_cabecalho()
    menu = menu_lateral_v8()
    mostrar_chat_popup()

    if st.session_state.tipo != "admin":
        st.markdown("""<style>
        header[data-testid="stHeader"] { display: none !important; }
        [data-testid="stToolbar"] { display: none !important; }
        #MainMenu { display: none !important; }
        footer { display: none !important; }
        </style>""", unsafe_allow_html=True)

    if "mostrar_comissao_empresa" not in st.session_state:
        st.session_state.mostrar_comissao_empresa = True
    if "msg_sucesso" not in st.session_state:
        st.session_state.msg_sucesso = ""
    if "form_count" not in st.session_state:
        st.session_state.form_count = 0

    if menu == "📋 Nova Venda":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
            </div>
            <span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;letter-spacing:0.04em;">Cadastro de Venda</span>
        </div>
        """, unsafe_allow_html=True)

        tabelas = carregar_tabelas()

        if st.session_state.get("msg_sucesso"):
            st.markdown(f"""
            <div style="background:rgba(34,197,94,0.12);border:1.5px solid rgba(34,197,94,0.45);border-radius:12px;padding:14px 18px;margin-bottom:16px;display:flex;align-items:center;gap:10px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4ade80" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                <span style="color:#4ade80;font-weight:700;font-size:14px;">{st.session_state.msg_sucesso}</span>
            </div>
            """, unsafe_allow_html=True)
            st.session_state.msg_sucesso = ""

        fc = st.session_state.form_count
        cliente = st.text_input("Cliente", key=f"novo_cliente_{fc}")

        cpf_digitado = st.text_input("CPF", placeholder="Ex: 999.999.999-99", key=f"novo_cpf_{fc}")
        cpf = limpar_documento(cpf_digitado)
        if cpf_digitado:
            if len(cpf)<11: st.error(f"CPF incompleto: faltam {11-len(cpf)} numero(s).")
            elif len(cpf)>11: st.error(f"CPF com numeros a mais: remova {len(cpf)-11} numero(s).")
            elif validar_cpf(cpf): st.success(f"CPF valido: {cpf}")
            else: st.error("CPF invalido.")

        telefone_digitado = st.text_input("Telefone", placeholder="Ex: (11) 99976-7867", key=f"novo_telefone_{fc}")
        telefone = limpar_documento(telefone_digitado)
        if telefone_digitado:
            if len(telefone)<10: st.error("Telefone incompleto.")
            elif len(telefone)>11: st.error(f"Telefone com numeros a mais: remova {len(telefone)-11} numero(s).")
            elif validar_telefone(telefone): st.success(f"Telefone valido: {telefone}")
            else: st.error("Telefone invalido.")

        tabela_banco = st.selectbox("Tabela/Banco", tabelas)
        valor_digitado = st.text_input("Valor vendido", placeholder="Ex: R$ 1.758,71", key=f"novo_valor_{fc}")
        valor = converter_valor_brasileiro(valor_digitado)
        if valor_digitado:
            if valor>0: st.success(f"Valor valido: {dinheiro(valor)}")
            else: st.error("Valor invalido.")

        status = st.selectbox("Status", ["Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"])
        observacao = st.text_area("Observacao", key=f"nova_observacao_{fc}")

        # ── ANEXO DE DOCUMENTOS (aparece só para produtos configurados) ──
        produtos_com_doc = carregar_produtos_requer_documento()
        arquivos_documento_venda = {}

        if tabela_banco in produtos_com_doc:
            st.markdown("### 📎 Documentos do Cliente")
            st.caption(f"Opcional. Formatos aceitos: PDF, JPG, PNG — até {TAMANHO_MAXIMO_DOCUMENTO_MB}MB por arquivo.")
            for categoria in CATEGORIAS_DOCUMENTO_VENDA:
                multiplos = (categoria == "Outros")
                arquivos = st.file_uploader(
                    categoria,
                    type=["pdf", "jpg", "jpeg", "png"],
                    accept_multiple_files=multiplos,
                    key=f"doc_{categoria}_{fc}"
                )
                if arquivos:
                    arquivos_documento_venda[categoria] = arquivos if multiplos else [arquivos]

        if st.button("💾 Salvar Venda", use_container_width=True):
            erro_arquivo = ""
            for _categoria, _lista_arquivos in arquivos_documento_venda.items():
                for _arq in _lista_arquivos:
                    _valido, _motivo = validar_arquivo_documento(_arq)
                    if not _valido:
                        erro_arquivo = _motivo
                        break
                if erro_arquivo:
                    break

            if not validar_cpf(cpf):
                st.error("Corrija o CPF.")
            elif not validar_telefone(telefone):
                st.error("Corrija o telefone.")
            elif valor<=0:
                st.error("Corrija o valor.")
            elif erro_arquivo:
                st.error(f"Documento inválido: {erro_arquivo}")
            else:
                try:
                    perc_empresa = calcular_percentual_empresa_venda(tabela_banco, valor)
                    valor_empresa = float(valor)*(perc_empresa/100)
                    dados = {
                        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "vendedor_id": st.session_state.user_id,
                        "vendedor": st.session_state.usuario,
                        "cliente": cliente, "cpf": cpf, "telefone": telefone,
                        "produto": tabela_banco, "tabela_banco": tabela_banco,
                        "valor": valor, "status": status,
                        "percentual_comissao": 0, "valor_comissao": 0,
                        "comissao_empresa": perc_empresa, "valor_comissao_empresa": valor_empresa,
                        "conferido": False, "alterado_vendedor": False, "observacao": observacao
                    }
                    resposta_insert = supabase.table("vendas").insert(dados).execute()
                    if not resposta_insert.data:
                        st.error("⚠️ O Supabase não retornou confirmação de que a venda foi salva. Verifique as permissões (RLS) da tabela 'vendas' para INSERT.")
                    else:
                        venda_id_nova = resposta_insert.data[0].get("id")
                        qtd_docs_enviados = 0
                        qtd_docs_com_erro = 0
                        for categoria_doc, lista_arquivos in arquivos_documento_venda.items():
                            for arquivo_doc in lista_arquivos:
                                try:
                                    caminho_doc, tamanho_doc = enviar_documento_para_storage(arquivo_doc, cpf, categoria_doc)
                                    salvar_registro_documento_venda(
                                        venda_id_nova, categoria_doc, arquivo_doc.name,
                                        caminho_doc, tamanho_doc,
                                        st.session_state.get("nome", st.session_state.get("usuario",""))
                                    )
                                    qtd_docs_enviados += 1
                                except Exception:
                                    qtd_docs_com_erro += 1

                        msg_docs = ""
                        if qtd_docs_enviados:
                            msg_docs = f" • {qtd_docs_enviados} documento(s) anexado(s)"
                        if qtd_docs_com_erro:
                            msg_docs += f" • ⚠️ {qtd_docs_com_erro} documento(s) falharam ao subir"

                        st.session_state.msg_sucesso = f"✅ Venda cadastrada com sucesso! (ID {venda_id_nova}){msg_docs}"
                        st.session_state.form_count += 1
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao salvar a venda no Supabase: {e}")
                    st.caption("Causas comuns: policy de RLS bloqueando INSERT para a chave publishable, coluna obrigatória faltando/tipo incompatível, ou constraint violada no banco.")

    elif menu == "📊 Painel":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
            </div>
            <span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;letter-spacing:0.04em;">Painel de Vendas</span>
        </div>
        """, unsafe_allow_html=True)
        df = preparar_dataframe_vendas()
        if df.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            total_bruto_banco = len(df)

            if st.session_state.tipo == "admin":
                qtd_nat = int(df["data"].isna().sum())
                with st.expander(f"🔧 Diagnóstico de datas — {qtd_nat} de {total_bruto_banco} vendas com data não reconhecida", expanded=(qtd_nat > 0)):
                    if qtd_nat == 0:
                        st.success("Todas as datas foram convertidas corretamente.")
                    else:
                        st.error(f"{qtd_nat} venda(s) têm a coluna 'data' num formato que o app não conseguiu converter — por isso elas não aparecem em nenhum filtro de Mês/Ano/Dia (só aparecem com Mês = Todos, Ano = Todos, Dia = Todos).")
                        df_problema = df[df["data"].isna()][["id","cliente","vendedor","status","data_original_supabase"]]
                        st.dataframe(df_problema, use_container_width=True, hide_index=True)

            meses = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
            col_f1,col_f2,col_f3,col_f4 = st.columns(4)

            mes_atual_nome = meses.get(datetime.now().month, "Janeiro")
            opcoes_mes = list(meses.values()) + ["Todos"]
            index_mes = opcoes_mes.index(mes_atual_nome) if mes_atual_nome in opcoes_mes else 0
            mes_nome = col_f1.selectbox("Mes", opcoes_mes, index=index_mes)

            anos = sorted(df["ano"].dropna().unique().astype(int).tolist(), reverse=True)
            ano_atual = datetime.now().year
            if not anos:
                anos = [ano_atual]
            opcoes_ano = anos + ["Todos"]
            index_ano = opcoes_ano.index(ano_atual) if ano_atual in opcoes_ano else 0
            ano_filtro = col_f2.selectbox("Ano", opcoes_ano, index=index_ano)

            dias = ["Todos"]+list(range(1,32))
            dia_filtro = col_f3.selectbox("Dia", dias)
            status_filtro = col_f4.selectbox("Status", ["Todos","Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"])

            tabelas = carregar_tabelas()
            tabela_filtro = st.selectbox("Tabela/Banco", ["Todas"]+tabelas)

            if mes_nome != "Todos":
                mes_num = [k for k,v in meses.items() if v==mes_nome][0]
                df = df[df["mes_num"]==mes_num]

            if ano_filtro != "Todos":
                df = df[df["ano"]==int(ano_filtro)]

            if dia_filtro != "Todos":
                df = df[df["dia"]==int(dia_filtro)]
            if st.session_state.tipo != "admin": df = df[df["vendedor_id"]==st.session_state.user_id]
            if status_filtro != "Todos": df = df[df["status"]==status_filtro]
            if tabela_filtro != "Todas": df = df[df["tabela_banco"]==tabela_filtro]
            if st.session_state.tipo == "admin":
                vendedores = sorted(df["vendedor"].dropna().unique().tolist())
                vendedor_filtro = st.selectbox("Vendedor", ["Todos"]+vendedores)
                if vendedor_filtro != "Todos": df = df[df["vendedor"]==vendedor_filtro]
            total_vendido = df["valor"].fillna(0).sum()
            qtd = len(df)
            total_pago = df[df["status"]=="Pago"]["valor"].fillna(0).sum()
            total_pendente = df[df["status"].isin(["Pendente","Aguardando Pagamento","Aguardando Assinatura"])]["valor"].fillna(0).sum()
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,rgba(34,197,94,0.18),rgba(16,185,129,0.12));border:2px solid rgba(34,197,94,0.55);border-radius:18px;padding:22px 28px;margin-bottom:14px;box-shadow:0 0 24px rgba(34,197,94,0.20);">
                <div style="font-size:11px;font-weight:700;color:#22c55e;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:6px;">✅ Total Pago</div>
                <div style="font-size:34px;font-weight:900;color:#0f172a;letter-spacing:-0.02em;">{dinheiro(total_pago)}</div>
            </div>
            """, unsafe_allow_html=True)
            col1,col2,col3 = st.columns(3)
            col1.metric("💵 Total Vendido", dinheiro(total_vendido))
            col2.metric("⏳ Total Pendente", dinheiro(total_pendente))
            col3.metric("📋 Contratos", qtd)
            col4,col5 = st.columns(2)
            col4.metric("🗓️ Mes", mes_nome)
            col5.metric("📅 Dia", str(dia_filtro) if dia_filtro!="Todos" else "Todos")
            if st.session_state.tipo == "admin":
                total_empresa = calcular_comissao_montante(df)
                col_l,col_b = st.columns([4,1])
                with col_b:
                    if st.button("👁️" if st.session_state.mostrar_comissao_empresa else "🙈", key="btn_ocultar"):
                        st.session_state.mostrar_comissao_empresa = not st.session_state.mostrar_comissao_empresa
                        st.rerun()
                valor_tela = dinheiro(total_empresa) if st.session_state.mostrar_comissao_empresa else "R$ •••••"
                st.metric("🏦 Comissao empresa", valor_tela)
                alteradas = df[df["alterado_vendedor"]==True]
                if not alteradas.empty:
                    st.warning(f"⚠️ Existem {len(alteradas)} proposta(s) alterada(s) pelo vendedor.")
            st.caption(f"Registros encontrados no banco antes dos filtros: {total_bruto_banco} | Registros após filtros: {len(df)}")
            st.divider()
            if df.empty:
                st.info("Nenhuma proposta encontrada para esse filtro.")
                st.caption("Se aparecer 0 em Maio/Junho, deixe Mês e Ano como Todos para conferir. A conversão agora usa a coluna data do Supabase com dayfirst=True.")
            else:
                if st.session_state.tipo=="admin":
                    colunas = ["id","data","vendedor","cliente","cpf","telefone","tabela_banco","valor","status","conferido","alterado_vendedor","ultima_alteracao_em","ultima_alteracao_por","ultima_alteracao_resumo","observacao","observacao_admin","observacao_alteracao"]
                else:
                    colunas = ["id","data","cliente","telefone","tabela_banco","valor","status","conferido","observacao"]
                colunas = [c for c in colunas if c in df.columns]
                df_visao = df[colunas].copy()

                if "data_original_supabase" in df.columns and "data" in df_visao.columns:
                    df_visao["data"] = df.loc[df_visao.index, "data_original_supabase"].astype(str)
                elif "data" in df_visao.columns:
                    df_visao["data"] = df_visao["data"].astype(str)

                if "valor" in df_visao.columns:
                    df_visao["valor"] = df_visao["valor"].apply(dinheiro)

                contagem_docs_painel = contar_documentos_por_vendas(df_visao["id"].tolist()) if "id" in df_visao.columns else {}
                if "id" in df_visao.columns:
                    df_visao["anexos"] = df_visao["id"].apply(lambda vid: f"📎 {contagem_docs_painel.get(vid,0)}" if contagem_docs_painel.get(vid,0) > 0 else "—")

                traducao_cols = {
                    "id": "ID", "data": "Data", "vendedor": "Vendedor",
                    "cliente": "Cliente", "cpf": "CPF", "telefone": "Telefone",
                    "tabela_banco": "Tabela/Banco", "valor": "Valor", "status": "Status",
                    "conferido": "Conferido", "alterado_vendedor": "Alterado",
                    "observacao": "Observacao", "observacao_admin": "Obs Admin",
                    "observacao_alteracao": "Obs Alteracao",
                    "ultima_alteracao_em": "Ultima Alteracao Em",
                    "ultima_alteracao_por": "Ultima Alteracao Por",
                    "ultima_alteracao_resumo": "Ultima Alteracao",
                    "anexos": "📎 Anexos"
                }
                df_visao = df_visao.rename(columns=traducao_cols)

                def _renderizar_proposta_completa(dados_proposta):
                    st.markdown(f"### Venda #{int(dados_proposta.get('id'))}")
                    col_view1, col_view2 = st.columns(2)
                    with col_view1:
                        st.markdown(f"**Cliente:** {dados_proposta.get('cliente','') or '—'}")
                        st.markdown(f"**CPF:** {dados_proposta.get('cpf','') or '—'}")
                        st.markdown(f"**Telefone:** {dados_proposta.get('telefone','') or '—'}")
                        st.markdown(f"**Vendedor:** {dados_proposta.get('vendedor','') or '—'}")
                    with col_view2:
                        st.markdown(f"**Tabela/Banco:** {dados_proposta.get('tabela_banco','') or '—'}")
                        st.markdown(f"**Valor:** {dinheiro(dados_proposta.get('valor',0))}")
                        st.markdown(f"**Status:** {dados_proposta.get('status','') or '—'}")
                        data_txt = str(dados_proposta.get('data_original_supabase') or dados_proposta.get('data') or '')[:16]
                        st.markdown(f"**Data:** {data_txt or '—'}")
                    if str(dados_proposta.get('observacao') or '').strip():
                        st.markdown(f"**Observação:** {dados_proposta.get('observacao')}")
                    st.divider()
                    docs_view = carregar_documentos_da_venda(int(dados_proposta.get('id')))
                    if docs_view:
                        st.markdown(f"**📎 Documentos anexados ({len(docs_view)})**")
                        for doc_view in docs_view:
                            col_dv1, col_dv2 = st.columns([4, 1])
                            with col_dv1:
                                tamanho_kb_v = round((doc_view.get("tamanho_bytes") or 0) / 1024)
                                st.caption(f"{doc_view.get('tipo_documento','')} — {doc_view.get('nome_arquivo','')} ({tamanho_kb_v} KB)")
                            with col_dv2:
                                link_doc_v = gerar_link_download_documento(doc_view.get("caminho_storage",""), nome_arquivo=doc_view.get("nome_arquivo"))
                                if link_doc_v:
                                    st.link_button("⬇️ Baixar", link_doc_v, use_container_width=True)
                                else:
                                    st.caption("⚠️ Indisponível")
                    else:
                        st.caption("📎 Nenhum documento anexado a esta venda.")

                usar_dialog_nativo = hasattr(st, "dialog")
                if usar_dialog_nativo:
                    @st.dialog("Detalhes da Venda", width="large")
                    def _abrir_dialog_proposta(id_venda_dialog):
                        linha_dialog = df[df["id"] == id_venda_dialog]
                        if not linha_dialog.empty:
                            _renderizar_proposta_completa(linha_dialog.iloc[0].to_dict())

                try:
                    evento_tabela_painel = st.dataframe(
                        df_visao.style.apply(destacar_linhas_pendentes, tipo_usuario=st.session_state.tipo, axis=1),
                        use_container_width=True,
                        on_select="rerun",
                        selection_mode="single-row",
                        key="tabela_vendas_painel"
                    )
                    if usar_dialog_nativo:
                        try:
                            linhas_sel = evento_tabela_painel.selection["rows"]
                        except Exception:
                            linhas_sel = getattr(getattr(evento_tabela_painel, "selection", None), "rows", [])
                        if linhas_sel:
                            id_venda_sel = int(df_visao.iloc[linhas_sel[0]]["ID"])
                            _abrir_dialog_proposta(id_venda_sel)
                    else:
                        st.caption("Clique numa linha da tabela pra ver os dados completos + anexos. (Se não abrir, use o campo 'Editar proposta (ID)' abaixo.)")
                except TypeError:
                    st.dataframe(df_visao.style.apply(destacar_linhas_pendentes, tipo_usuario=st.session_state.tipo, axis=1), use_container_width=True)

                buf = io.BytesIO()
                df_export = df_visao.copy()
                with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                    df_export.to_excel(writer, index=False, sheet_name="Vendas")
                buf.seek(0)
                col_exp1, col_exp2 = st.columns([4, 1])
                with col_exp2:
                    st.download_button(
                        label="📥 Exportar Excel",
                        data=buf,
                        file_name=f"vendas_{mes_nome}_{ano_filtro}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                if st.session_state.tipo=="admin":
                    st.divider()
                    acoes_df = df[["id","cliente","valor","status","conferido","alterado_vendedor"]].copy()
                    acoes_df["excluir"] = False
                    editado = st.data_editor(acoes_df, use_container_width=True, disabled=["id","cliente","valor","status","alterado_vendedor"], hide_index=True)
                    col_a,col_b = st.columns(2)
                    with col_a:
                        if st.button("✅ Salvar conferencias"):
                            for _,row in editado.iterrows():
                                update = {"conferido": bool(row["conferido"])}
                                if bool(row["conferido"]): update["alterado_vendedor"] = False
                                supabase.table("vendas").update(update).eq("id",int(row["id"])).execute()
                            st.success("Conferencias salvas!")
                            st.rerun()
                    with col_b:
                        confirmar = st.checkbox("Confirmo que quero excluir as propostas marcadas")
                        if st.button("🗑️ Excluir marcadas"):
                            if not confirmar: st.error("Marque a confirmacao.")
                            else:
                                ids = editado[editado["excluir"]==True]["id"].tolist()
                                if not ids: st.warning("Nenhuma marcada.")
                                else:
                                    for vid in ids:
                                        excluir_arquivos_storage_da_venda(int(vid))
                                        supabase.table("vendas").delete().eq("id",int(vid)).execute()
                                    st.success(f"{len(ids)} excluida(s)!")
                                    st.rerun()
                st.divider()
                proposta_id = st.selectbox("Editar proposta (ID)", df["id"].tolist())
                proposta = df[df["id"]==proposta_id].iloc[0]

                documentos_da_proposta = carregar_documentos_da_venda(int(proposta_id))
                if documentos_da_proposta:
                    st.markdown(f"**📎 Documentos anexados ({len(documentos_da_proposta)})**")
                    for doc in documentos_da_proposta:
                        col_doc1, col_doc2 = st.columns([4, 1])
                        with col_doc1:
                            tamanho_kb = round((doc.get("tamanho_bytes") or 0) / 1024)
                            st.caption(f"{doc.get('tipo_documento','')} — {doc.get('nome_arquivo','')} ({tamanho_kb} KB)")
                        with col_doc2:
                            link_doc = gerar_link_download_documento(doc.get("caminho_storage",""), nome_arquivo=doc.get("nome_arquivo"))
                            if link_doc:
                                st.link_button("⬇️ Baixar", link_doc, use_container_width=True)
                            else:
                                st.caption("⚠️ Link indisponível")
                    st.divider()
                bloqueada = (st.session_state.tipo!="admin" and bool(proposta.get("conferido",False)) is True)

                if bloqueada:
                    st.warning("🔒 Proposta conferida — nao pode editar.")
                else:
                    st.markdown("### ✏️ Editar proposta")

                    if st.session_state.tipo == "admin":
                        st.caption("Gestão/Admin pode alterar data, vendedor, cliente, CPF, telefone, tabela, valor, status e observações.")
                    else:
                        st.caption("Vendedor pode editar somente propostas não conferidas.")

                    with st.form("editar_proposta"):
                        data_original = pd.to_datetime(proposta.get("data"), errors="coerce")
                        if pd.isna(data_original):
                            data_original = pd.Timestamp.now()

                        if st.session_state.tipo == "admin":
                            col_data_edit, col_hora_edit = st.columns([1, 1])
                            data_contrato_edit = col_data_edit.date_input(
                                "Data do contrato",
                                value=data_original.date(),
                                key=f"data_contrato_edit_{proposta_id}"
                            )
                            hora_contrato_edit = col_hora_edit.time_input(
                                "Hora do contrato",
                                value=data_original.time().replace(microsecond=0),
                                key=f"hora_contrato_edit_{proposta_id}"
                            )

                            try:
                                usuarios_res = supabase.table("usuarios").select("id,nome,usuario,tipo,ativo").eq("ativo", True).order("nome").execute()
                                usuarios_lista = usuarios_res.data or []
                            except Exception:
                                usuarios_lista = []

                            usuarios_vendedores = []
                            for u in usuarios_lista:
                                tipo_u = str(u.get("tipo","")).lower()
                                if tipo_u in ["vendedor", "admin"]:
                                    usuarios_vendedores.append(u)

                            if not usuarios_vendedores:
                                usuarios_vendedores = [{
                                    "id": proposta.get("vendedor_id"),
                                    "nome": str(proposta.get("vendedor","") or "Vendedor"),
                                    "usuario": str(proposta.get("vendedor","") or "")
                                }]

                            vendedor_atual_id = proposta.get("vendedor_id")
                            try:
                                vendedor_atual_id_int = int(vendedor_atual_id)
                            except Exception:
                                vendedor_atual_id_int = None

                            index_vendedor = 0
                            for i, u in enumerate(usuarios_vendedores):
                                try:
                                    if int(u.get("id")) == vendedor_atual_id_int:
                                        index_vendedor = i
                                        break
                                except Exception:
                                    pass

                            vendedor_escolhido = st.selectbox(
                                "Vendedor responsável",
                                usuarios_vendedores,
                                index=index_vendedor,
                                format_func=lambda u: f"{u.get('nome', u.get('usuario',''))} ({u.get('usuario','')})",
                                key=f"vendedor_edit_{proposta_id}"
                            )

                        else:
                            st.text_input(
                                "Data do contrato",
                                value=data_original.strftime("%d/%m/%Y %H:%M"),
                                disabled=True
                            )
                            st.text_input(
                                "Vendedor responsável",
                                value=str(proposta.get("vendedor","") or ""),
                                disabled=True
                            )
                            data_contrato_edit = data_original.date()
                            hora_contrato_edit = data_original.time().replace(microsecond=0)
                            vendedor_escolhido = {
                                "id": proposta.get("vendedor_id"),
                                "usuario": proposta.get("vendedor"),
                                "nome": proposta.get("vendedor")
                            }

                        cliente_edit = st.text_input("Cliente", value=str(proposta.get("cliente","") or ""))
                        cpf_edit = st.text_input("CPF", value=str(proposta.get("cpf","") or ""))
                        telefone_edit = st.text_input("Telefone", value=str(proposta.get("telefone","") or ""))

                        tabelas_edit = carregar_tabelas()
                        tabela_atual = str(proposta.get("tabela_banco","") or proposta.get("produto","") or "")
                        tabela_index = tabelas_edit.index(tabela_atual) if tabela_atual in tabelas_edit else 0
                        tabela_edit = st.selectbox("Tabela/Banco", tabelas_edit, index=tabela_index)

                        valor_edit_texto = st.text_input("Valor", value=dinheiro(proposta.get("valor") or 0).replace("R$ ",""))
                        valor_edit = converter_valor_brasileiro(valor_edit_texto)

                        status_lista = ["Pendente","Aguardando Pagamento","Aguardando Assinatura","Pago","Cancelado"]
                        status_atual = str(proposta.get("status","Pendente") or "Pendente")
                        status_index = status_lista.index(status_atual) if status_atual in status_lista else 0
                        status_edit = st.selectbox("Status", status_lista, index=status_index)

                        observacao_edit = st.text_area("Observacao", value=str(proposta.get("observacao","") or ""))

                        if st.session_state.tipo=="admin":
                            conferido_edit = st.checkbox("✅ Conferido", value=bool(proposta.get("conferido",False)))
                            obs_admin_edit = st.text_area("Observacao admin", value=str(proposta.get("observacao_admin","") or ""))
                        else:
                            obs_alt_edit = st.text_area("Motivo da alteracao", placeholder="Ex: corrigi valor...")

                        ultima_em = proposta.get("ultima_alteracao_em", "")
                        ultima_por = proposta.get("ultima_alteracao_por", "")
                        ultima_resumo = proposta.get("ultima_alteracao_resumo", "")
                        if ultima_em or ultima_por or ultima_resumo:
                            st.info(f"Última alteração: {ultima_em} | Por: {ultima_por} | {ultima_resumo}")

                        if st.form_submit_button("Salvar alteracoes"):
                            cpf_l = limpar_documento(cpf_edit)
                            tel_l = limpar_documento(telefone_edit)

                            if not validar_cpf(cpf_l):
                                st.error("CPF invalido.")
                            elif not validar_telefone(tel_l):
                                st.error("Telefone invalido.")
                            elif valor_edit<=0:
                                st.error("Valor invalido.")
                            else:
                                perc = calcular_percentual_empresa_venda(tabela_edit, valor_edit)

                                dados_update = {
                                    "cliente": cliente_edit,
                                    "cpf": cpf_l,
                                    "telefone": tel_l,
                                    "produto": tabela_edit,
                                    "tabela_banco": tabela_edit,
                                    "valor": valor_edit,
                                    "status": status_edit,
                                    "observacao": observacao_edit,
                                    "comissao_empresa": perc,
                                    "valor_comissao_empresa": valor_edit*(perc/100)
                                }

                                resumo_mudancas = []

                                def mudou(campo, antigo, novo):
                                    antigo_s = "" if pd.isna(antigo) else str(antigo)
                                    novo_s = "" if novo is None else str(novo)
                                    if antigo_s != novo_s:
                                        resumo_mudancas.append(f"{campo}: {antigo_s} -> {novo_s}")

                                mudou("Cliente", proposta.get("cliente",""), cliente_edit)
                                mudou("CPF", proposta.get("cpf",""), cpf_l)
                                mudou("Telefone", proposta.get("telefone",""), tel_l)
                                mudou("Tabela/Banco", proposta.get("tabela_banco",""), tabela_edit)
                                mudou("Valor", proposta.get("valor",""), valor_edit)
                                mudou("Status", proposta.get("status",""), status_edit)

                                if st.session_state.tipo=="admin":
                                    nova_data_contrato = datetime.combine(data_contrato_edit, hora_contrato_edit)
                                    data_antiga_txt = data_original.strftime("%Y-%m-%d %H:%M:%S")
                                    data_nova_txt = nova_data_contrato.strftime("%Y-%m-%d %H:%M:%S")
                                    if data_antiga_txt != data_nova_txt:
                                        resumo_mudancas.append(f"Data: {data_antiga_txt} -> {data_nova_txt}")

                                    vendedor_id_novo = vendedor_escolhido.get("id")
                                    vendedor_usuario_novo = vendedor_escolhido.get("usuario") or vendedor_escolhido.get("nome") or ""

                                    try:
                                        vendedor_id_novo = int(vendedor_id_novo)
                                    except Exception:
                                        vendedor_id_novo = proposta.get("vendedor_id")

                                    if str(proposta.get("vendedor_id","")) != str(vendedor_id_novo):
                                        resumo_mudancas.append(f"Vendedor: {proposta.get('vendedor','')} -> {vendedor_usuario_novo}")

                                    dados_update["data"] = str(nova_data_contrato)
                                    dados_update["vendedor_id"] = vendedor_id_novo
                                    dados_update["vendedor"] = vendedor_usuario_novo
                                    dados_update["conferido"] = conferido_edit
                                    dados_update["alterado_vendedor"] = False
                                    dados_update["observacao_admin"] = obs_admin_edit
                                else:
                                    dados_update["alterado_vendedor"] = True
                                    dados_update["data_alteracao_vendedor"] = str(datetime.now())
                                    dados_update["observacao_alteracao"] = obs_alt_edit
                                    dados_update["conferido"] = False

                                agora_alteracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                usuario_alteracao = str(st.session_state.get("nome", st.session_state.get("usuario","")))
                                resumo_final = "; ".join(resumo_mudancas[:12]) if resumo_mudancas else "Sem mudança relevante detectada"

                                dados_update_com_auditoria = dict(dados_update)
                                dados_update_com_auditoria["ultima_alteracao_em"] = agora_alteracao
                                dados_update_com_auditoria["ultima_alteracao_por"] = usuario_alteracao
                                dados_update_com_auditoria["ultima_alteracao_resumo"] = resumo_final

                                try:
                                    supabase.table("vendas").update(dados_update_com_auditoria).eq("id", int(proposta_id)).execute()
                                except Exception:
                                    supabase.table("vendas").update(dados_update).eq("id", int(proposta_id)).execute()

                                st.success("Proposta atualizada!")
                                st.rerun()

    elif menu == "🏆 Ranking":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Ranking de Vendas</span>', unsafe_allow_html=True)
        df_rank = preparar_dataframe_vendas()
        if df_rank.empty:
            st.warning("Nenhuma venda cadastrada.")
        else:
            tipo_filtro = st.radio("Tipo de filtro", ["Mes/Ano","Periodo personalizado"], horizontal=True, key="rank_tipo_filtro")
            if tipo_filtro == "Mes/Ano":
                meses_r = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
                col_r1,col_r2 = st.columns(2)
                mes_r = col_r1.selectbox("Mes", list(meses_r.values()), index=datetime.now().month-1, key="rank_mes")
                anos_r = sorted(df_rank["ano"].dropna().unique().astype(int).tolist(), reverse=True)
                ano_r = col_r2.selectbox("Ano", anos_r if anos_r else [datetime.now().year], key="rank_ano")
                mes_num_r = [k for k,v in meses_r.items() if v==mes_r][0]
                df_rank = df_rank[(df_rank["mes_num"]==mes_num_r)&(df_rank["ano"]==ano_r)]
            else:
                col_d1,col_d2 = st.columns(2)
                data_ini = col_d1.date_input("Data inicial", value=datetime.now().replace(day=1).date(), key="rank_data_ini")
                data_fim = col_d2.date_input("Data final", value=datetime.now().date(), key="rank_data_fim")
                if data_ini > data_fim: st.error("Data inicial > data final."); st.stop()
                df_rank = df_rank[(df_rank["data"].dt.date>=data_ini)&(df_rank["data"].dt.date<=data_fim)]
            if df_rank.empty:
                st.info("Nenhuma venda neste periodo.")
            else:
                total_geral = df_rank["valor"].fillna(0).sum()
                total_pago_r = df_rank[df_rank["status"]=="Pago"]["valor"].fillna(0).sum()
                total_pend_r = df_rank[df_rank["status"].isin(["Pendente","Aguardando Pagamento","Aguardando Assinatura"])]["valor"].fillna(0).sum()
                qtd_total = len(df_rank)
                qtd_pago = len(df_rank[df_rank["status"]=="Pago"])
                pct_pago = round((qtd_pago/qtd_total*100),1) if qtd_total>0 else 0
                k1,k2,k3,k4,k5 = st.columns(5)
                k1.metric("💰 Total Geral", dinheiro(total_geral))
                k2.metric("✅ Total Pago", dinheiro(total_pago_r))
                k3.metric("⏳ Total Pendente", dinheiro(total_pend_r))
                k4.metric("📋 Contratos", qtd_total)
                k5.metric("🎯 % Pagos", f"{pct_pago}%")
                grp = df_rank.groupby("vendedor").agg(
                    total_vendido=("valor","sum"),
                    contratos=("id","count"),
                    total_pago=("valor", lambda x: x[df_rank.loc[x.index,"status"]=="Pago"].sum()),
                    contratos_pagos=("status", lambda x: (x=="Pago").sum()),
                ).reset_index()
                grp["pct_pagos"] = (grp["contratos_pagos"]/grp["contratos"]*100).round(1)
                grp["ticket_medio"] = (grp["total_vendido"]/grp["contratos"]).round(2)
                grp = grp.sort_values("total_pago", ascending=False).reset_index(drop=True)
                grp.index += 1
                medalhas = {1:"🥇",2:"🥈",3:"🥉"}
                for i,row in grp.iterrows():
                    medalha = medalhas.get(i,f"#{i}")
                    pct_bar = min(int(row["pct_pagos"]),100)
                    bar_color = "#22c55e" if pct_bar>=70 else "#f59e0b" if pct_bar>=40 else "#ef4444"
                    st.markdown(f"""
                    <div style="background:#ffffff;border:1.5px solid rgba(14,165,233,0.30);border-radius:16px;padding:18px 22px;margin-bottom:12px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                            <div style="display:flex;align-items:center;gap:14px;">
                                <span style="font-size:28px;">{medalha}</span>
                                <div>
                                    <div style="font-size:16px;font-weight:800;color:#0f172a;">{row["vendedor"]}</div>
                                    <div style="font-size:12px;color:#64748b;">Ticket medio: {dinheiro(row["ticket_medio"])}</div>
                                </div>
                            </div>
                            <div style="display:flex;gap:20px;flex-wrap:wrap;">
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#0ea5e9;">TOTAL VENDIDO</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{dinheiro(row["total_vendido"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#22c55e;">TOTAL PAGO</div><div style="font-size:18px;font-weight:800;color:#16a34a;">{dinheiro(row["total_pago"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#6366f1;">CONTRATOS</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{int(row["contratos"])}</div></div>
                                <div style="text-align:center;"><div style="font-size:11px;font-weight:700;color:#f59e0b;">% PAGOS</div><div style="font-size:18px;font-weight:800;color:#0f172a;">{row["pct_pagos"]}%</div></div>
                            </div>
                        </div>
                        <div style="margin-top:14px;background:#f1f5f9;border-radius:999px;height:8px;overflow:hidden;">
                            <div style="width:{pct_bar}%;height:100%;background:{bar_color};border-radius:999px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    elif menu == "🎯 Metas":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Metas & Bonus</span>', unsafe_allow_html=True)

        def carregar_metas():
            try:
                res = supabase.table("metas_bonus").select("*").order("ordem").execute()
                if res.data: return res.data
            except Exception: pass
            return [{"ordem":1,"meta_valor":117000,"bonus_valor":300},{"ordem":2,"meta_valor":150000,"bonus_valor":600},{"ordem":3,"meta_valor":200000,"bonus_valor":1000},{"ordem":4,"meta_valor":250000,"bonus_valor":1500}]

        def salvar_metas(metas):
            try:
                supabase.table("metas_bonus").delete().neq("ordem",0).execute()
                for m in metas: supabase.table("metas_bonus").insert(m).execute()
                return True
            except Exception: return False

        metas = carregar_metas()
        if st.session_state.tipo=="admin":
            novas_metas = []
            cols_header = st.columns([1,2,2])
            cols_header[0].markdown("**Nivel**"); cols_header[1].markdown("**Meta (R$)**"); cols_header[2].markdown("**Bonus (R$)**")
            for i,m in enumerate(metas):
                col_n,col_m,col_b = st.columns([1,2,2])
                estrelas = "⭐"*(i+1)
                col_n.markdown(f"<div style='padding:8px 0;font-weight:700;font-size:15px;'>{estrelas}</div>",unsafe_allow_html=True)
                meta_v = col_m.number_input(f"meta_{i}",value=float(m["meta_valor"]),min_value=0.0,step=1000.0,label_visibility="collapsed",key=f"meta_val_{i}")
                bonus_v = col_b.number_input(f"bonus_{i}",value=float(m["bonus_valor"]),min_value=0.0,step=100.0,label_visibility="collapsed",key=f"bonus_val_{i}")
                novas_metas.append({"ordem":i+1,"meta_valor":meta_v,"bonus_valor":bonus_v})
            if st.button("💾 Salvar metas",use_container_width=True):
                if salvar_metas(novas_metas): st.success("Metas salvas!"); st.rerun()
                else: st.error("Erro ao salvar.")
            st.divider()

        df_metas = preparar_dataframe_vendas()
        if not df_metas.empty:
            meses_mt = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
            col_m1,col_m2 = st.columns(2)
            mes_mt = col_m1.selectbox("Mes",list(meses_mt.values()),index=datetime.now().month-1,key="metas_mes")
            anos_mt = sorted(df_metas["ano"].dropna().unique().astype(int).tolist(),reverse=True)
            ano_mt = col_m2.selectbox("Ano",anos_mt if anos_mt else [datetime.now().year],key="metas_ano")
            mes_num_mt = [k for k,v in meses_mt.items() if v==mes_mt][0]
            df_metas = df_metas[(df_metas["mes_num"]==mes_num_mt)&(df_metas["ano"]==ano_mt)]
            if st.session_state.tipo!="admin": df_metas = df_metas[df_metas["vendedor_id"]==st.session_state.user_id]
            vendedores_mt = df_metas["vendedor"].dropna().unique().tolist() if st.session_state.tipo=="admin" else [st.session_state.usuario]
            for vend in vendedores_mt:
                df_v = df_metas[df_metas["vendedor"]==vend]
                total_pago_v = df_v[df_v["status"]=="Pago"]["valor"].fillna(0).sum()
                total_vend = df_v["valor"].fillna(0).sum()
                bonus_atingido = 0
                proxima_meta = metas[0]["meta_valor"] if metas else 0
                for m in metas:
                    if total_pago_v>=m["meta_valor"]: bonus_atingido=m["bonus_valor"]
                for m in metas:
                    if total_pago_v<m["meta_valor"]: proxima_meta=m["meta_valor"]; break
                pct_prog = min(int((total_pago_v/proxima_meta)*100),100) if proxima_meta>0 else 100
                falta = max(proxima_meta-total_pago_v,0)
                bar_color = "#22c55e" if pct_prog>=80 else "#f59e0b" if pct_prog>=40 else "#0ea5e9"
                iniciais_v = "".join([p[0].upper() for p in vend.split()[:2]])
                st.markdown(f"""
                <div style="background:#ffffff;border:1px solid rgba(14,165,233,0.25);border-radius:18px;padding:20px 24px;margin-bottom:16px;">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px;flex-wrap:wrap;gap:10px;">
                        <div style="display:flex;align-items:center;gap:12px;">
                            <div style="width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#1d4ed8,#0ea5e9);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:15px;">{iniciais_v}</div>
                            <div><div style="font-size:16px;font-weight:800;color:#0f172a;">{vend}</div><div style="font-size:12px;color:#64748b;">Pago: {dinheiro(total_pago_v)} | Vendido: {dinheiro(total_vend)}</div></div>
                        </div>
                        {'<div style="background:#dcfce7;border-radius:10px;padding:6px 14px;"><span style="font-size:13px;font-weight:700;color:#16a34a;">+' + dinheiro(bonus_atingido) + ' bonus</span></div>' if bonus_atingido>0 else '<div style="background:#f1f5f9;border-radius:10px;padding:6px 14px;"><span style="font-size:13px;color:#64748b;">Sem bonus ainda</span></div>'}
                    </div>
                    <div style="background:#f1f5f9;border-radius:999px;height:10px;overflow:hidden;margin-bottom:4px;">
                        <div style="width:{pct_prog}%;height:100%;background:{bar_color};border-radius:999px;"></div>
                    </div>
                    <div style="font-size:11px;color:#94a3b8;">{'Meta atingida! 🎉' if falta==0 else f'Faltam {dinheiro(falta)} para a proxima meta'}</div>
                </div>
                """, unsafe_allow_html=True)
                cols_metas = st.columns(len(metas))
                for i,m in enumerate(metas):
                    atingida = total_pago_v>=m["meta_valor"]
                    estrelas_on = "⭐"*(i+1)
                    estrelas_off = "☆"*(i+1)
                    with cols_metas[i]:
                        if atingida:
                            st.markdown(f"""<div style="background:#fefce8;border:2px solid #facc15;border-radius:14px;padding:12px;text-align:center;"><div style="font-size:20px;">{estrelas_on}</div><div style="font-size:11px;font-weight:700;color:#92400e;">Meta {i+1}</div><div style="font-size:12px;color:#64748b;">{dinheiro(m["meta_valor"])}</div><div style="font-size:13px;font-weight:700;color:#16a34a;">+{dinheiro(m["bonus_valor"])} ✓</div></div>""", unsafe_allow_html=True)
                        else:
                            st.markdown(f"""<div style="background:#f8fafc;border:0.5px solid #e2e8f0;border-radius:14px;padding:12px;text-align:center;opacity:0.65;"><div style="font-size:20px;">{estrelas_off}</div><div style="font-size:11px;font-weight:700;color:#94a3b8;">Meta {i+1}</div><div style="font-size:12px;color:#94a3b8;">{dinheiro(m["meta_valor"])}</div><div style="font-size:12px;color:#94a3b8;">+{dinheiro(m["bonus_valor"])}</div></div>""", unsafe_allow_html=True)

    elif menu == "💬 WhatsApp":
        RAILWAY = "https://operax-whatsapp-production.up.railway.app"

        def wp_status_check():
            try:
                r = _req.get(f"{RAILWAY}/status", timeout=4)
                return r.json() if r.status_code == 200 else {}
            except Exception:
                return {}

        st_wp = wp_status_check()
        conectado = st_wp.get("status") == "connected" or st_wp.get("connected") is True

        st.markdown("""
        <style>
        .wp-page { background: linear-gradient(160deg,#020b18 0%,#030f22 60%,#020b18 100%); border-radius:20px; padding:50px 40px; text-align:center; border:1px solid rgba(56,189,248,0.20); min-height:400px; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:20px; }
        .wp-big-title { font-family:'Orbitron',sans-serif; font-size:28px; font-weight:900; color:#fff; letter-spacing:.08em; }
        .wp-big-title span { color:#38bdf8; }
        .wp-big-sub { color:rgba(148,185,210,0.70); font-size:14px; max-width:480px; line-height:1.7; }
        .wp-open-btn { display:inline-flex; align-items:center; gap:10px; background:linear-gradient(135deg,#1d4ed8,#0ea5e9); color:#fff; font-size:16px; font-weight:700; padding:16px 36px; border-radius:14px; text-decoration:none; letter-spacing:.03em; box-shadow:0 0 32px rgba(14,165,233,0.50); }
        .wp-conn-btn { display:inline-flex; align-items:center; gap:8px; background:rgba(56,189,248,0.10); color:#7dd3fc; font-size:13px; font-weight:700; padding:10px 22px; border-radius:10px; text-decoration:none; border:1px solid rgba(56,189,248,0.30); }
        .wp-badge-ok { display:inline-flex;align-items:center;gap:6px;background:#f0fdf4;border:1px solid #86efac;border-radius:8px;padding:5px 14px;font-size:13px;font-weight:700;color:#166534; }
        .wp-badge-err { display:inline-flex;align-items:center;gap:6px;background:#fef2f2;border:1px solid #fca5a5;border-radius:8px;padding:5px 14px;font-size:13px;font-weight:700;color:#991b1b; }
        .dot-g { width:9px;height:9px;background:#22c55e;border-radius:50%;box-shadow:0 0 8px #22c55e;display:inline-block; }
        .wp-features { display:flex; gap:14px; flex-wrap:wrap; justify-content:center; margin-top:10px; }
        .wp-feat { background:rgba(56,189,248,0.07); border:1px solid rgba(56,189,248,0.15); border-radius:10px; padding:10px 16px; font-size:12px; color:#7dd3fc; font-weight:600; }
        </style>
        """, unsafe_allow_html=True)

        chat_url = f"{RAILWAY}/chat"
        qr_url   = f"{RAILWAY}/qr"

        if conectado:
            badge = '<span class="wp-badge-ok"><span class="dot-g"></span>WhatsApp conectado</span>'
            botao_extra = ""
        else:
            badge = '<span class="wp-badge-err">WhatsApp desconectado</span>'
            botao_extra = f'<a href="{qr_url}" target="_blank" class="wp-conn-btn">Conectar WhatsApp</a>'

        st.markdown(f'''
        <div class="wp-page">
            <div style="font-size:80px;">🌀</div>
            <div class="wp-big-title">OPERAX <span>CHAT</span></div>
            <div>{badge}</div>
            <div class="wp-big-sub">Chat com seus clientes em tempo real via WhatsApp.<br>Propostas vinculadas automaticamente.</div>
            <a href="{chat_url}" target="_blank" class="wp-open-btn">💬 Abrir Chat WhatsApp</a>
            {botao_extra}
            <div class="wp-features">
                <span class="wp-feat">💬 Chat em tempo real</span>
                <span class="wp-feat">📄 Propostas vinculadas</span>
                <span class="wp-feat">⚡ Respostas rapidas</span>
                <span class="wp-feat">🔄 Sync com Painel</span>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("🔄 Verificar conexao", key="btn_wp_check"):
            st.rerun()

    elif menu == "👥 Usuarios":
        st.markdown("""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <div style="width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,rgba(37,99,235,0.15),rgba(14,165,233,0.15));border:1px solid rgba(14,165,233,0.35);display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
            </div>
            <span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;letter-spacing:0.04em;">Usuários</span>
        </div>
        """, unsafe_allow_html=True)

        # ── CRIAR NOVO USUÁRIO ──
        st.markdown("### ➕ Criar usuário")
        with st.form("novo_usuario", clear_on_submit=True):
            nome_novo_usuario = st.text_input("Nome")
            login_novo_usuario = st.text_input("Usuário (login)")
            senha_novo_usuario = st.text_input("Senha", type="password")
            tipo_novo_usuario = st.selectbox("Tipo", ["vendedor", "admin"])

            criar_usuario_btn = st.form_submit_button("Criar usuário", use_container_width=True)

            if criar_usuario_btn:
                if not nome_novo_usuario or not login_novo_usuario or not senha_novo_usuario:
                    st.error("Preencha nome, usuário e senha.")
                else:
                    login_normalizado = login_novo_usuario.strip().lower()
                    ja_existe = supabase.table("usuarios").select("id").eq("usuario", login_normalizado).execute()
                    if ja_existe.data:
                        st.error(f"Já existe um usuário com o login '{login_normalizado}'.")
                    else:
                        try:
                            supabase.table("usuarios").insert({
                                "nome": nome_novo_usuario.strip(),
                                "usuario": login_normalizado,
                                "senha_hash": hash_senha(senha_novo_usuario),
                                "tipo": tipo_novo_usuario,
                                "ativo": True
                            }).execute()
                            st.success(f"Usuário '{nome_novo_usuario}' criado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao criar usuário: {e}")

        st.divider()

        # ── LISTA DE USUÁRIOS CADASTRADOS ──
        st.markdown("### 📋 Usuários cadastrados")
        try:
            usuarios_res = supabase.table("usuarios").select("*").order("nome").execute()
            df_usuarios = pd.DataFrame(usuarios_res.data or [])
        except Exception as e:
            st.error(f"Erro ao carregar usuários: {e}")
            df_usuarios = pd.DataFrame()

        if df_usuarios.empty:
            st.info("Nenhum usuário cadastrado ainda.")
        else:
            colunas_exibir_usuarios = [c for c in ["id", "nome", "usuario", "tipo", "ativo"] if c in df_usuarios.columns]
            df_usuarios_visao = df_usuarios[colunas_exibir_usuarios].rename(columns={
                "id": "ID", "nome": "Nome", "usuario": "Usuário/Login",
                "tipo": "Tipo", "ativo": "Ativo"
            })
            st.dataframe(df_usuarios_visao, use_container_width=True, hide_index=True)

            st.divider()

            # ── EDITAR / GERENCIAR USUÁRIO SELECIONADO ──
            st.markdown("### ✏️ Editar usuário")

            opcoes_usuario = {
                f"{row.get('nome','')} ({row.get('usuario','')})": row.get("id")
                for _, row in df_usuarios.iterrows()
            }
            escolha_usuario_label = st.selectbox("Selecione o usuário", list(opcoes_usuario.keys()), key="sel_usuario_editar")
            usuario_id_selecionado = opcoes_usuario[escolha_usuario_label]
            usuario_selecionado = df_usuarios[df_usuarios["id"] == usuario_id_selecionado].iloc[0]

            usuario_login_atual = str(usuario_selecionado.get("usuario", "") or "").lower()
            eh_admin_principal = usuario_login_atual == "admin"

            with st.form(f"editar_usuario_{usuario_id_selecionado}"):
                nome_edit_usuario = st.text_input("Nome", value=str(usuario_selecionado.get("nome", "") or ""))
                login_edit_usuario = st.text_input("Usuário/Login", value=str(usuario_selecionado.get("usuario", "") or ""))

                tipo_atual_usuario = str(usuario_selecionado.get("tipo", "vendedor") or "vendedor")
                tipo_index_usuario = 0 if tipo_atual_usuario == "vendedor" else 1
                tipo_edit_usuario = st.selectbox("Tipo", ["vendedor", "admin"], index=tipo_index_usuario)

                salvar_edicao_usuario = st.form_submit_button("💾 Salvar alterações", use_container_width=True)

                if salvar_edicao_usuario:
                    if not nome_edit_usuario.strip() or not login_edit_usuario.strip():
                        st.error("Nome e usuário/login não podem ficar em branco.")
                    else:
                        login_edit_normalizado = login_edit_usuario.strip().lower()
                        conflito = supabase.table("usuarios").select("id").eq("usuario", login_edit_normalizado).neq("id", int(usuario_id_selecionado)).execute()
                        if conflito.data:
                            st.error(f"Já existe outro usuário com o login '{login_edit_normalizado}'.")
                        else:
                            try:
                                supabase.table("usuarios").update({
                                    "nome": nome_edit_usuario.strip(),
                                    "usuario": login_edit_normalizado,
                                    "tipo": tipo_edit_usuario
                                }).eq("id", int(usuario_id_selecionado)).execute()
                                st.success("Usuário atualizado!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar usuário: {e}")

            st.divider()

            # ── ALTERAR SENHA ──
            st.markdown("### 🔑 Alterar senha")
            with st.form(f"alterar_senha_{usuario_id_selecionado}", clear_on_submit=True):
                nova_senha_usuario = st.text_input("Nova senha", type="password")
                alterar_senha_btn = st.form_submit_button("Alterar senha", use_container_width=True)

                if alterar_senha_btn:
                    if not nova_senha_usuario:
                        st.error("Digite uma nova senha.")
                    else:
                        try:
                            supabase.table("usuarios").update({
                                "senha_hash": hash_senha(nova_senha_usuario)
                            }).eq("id", int(usuario_id_selecionado)).execute()
                            st.success("Senha alterada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao alterar senha: {e}")

            st.divider()

            # ── ATIVAR / DESATIVAR ──
            st.markdown("### 🔄 Ativar / Desativar")
            status_atual_usuario = bool(usuario_selecionado.get("ativo", True))
            st.caption(f"Status atual: {'🟢 Ativo' if status_atual_usuario else '⚪ Inativo'}")

            if eh_admin_principal:
                st.info("O admin principal não pode ser desativado.")
            else:
                label_toggle = "🔴 Desativar usuário" if status_atual_usuario else "🟢 Ativar usuário"
                if st.button(label_toggle, use_container_width=True, key=f"toggle_ativo_{usuario_id_selecionado}"):
                    try:
                        supabase.table("usuarios").update({
                            "ativo": not status_atual_usuario
                        }).eq("id", int(usuario_id_selecionado)).execute()
                        st.success("Status alterado!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao alterar status: {e}")

            st.divider()

            # ── EXCLUIR USUÁRIO ──
            st.markdown("### 🗑️ Excluir usuário")
            if eh_admin_principal:
                st.info("O admin principal não pode ser excluído.")
            else:
                confirmar_exclusao_usuario = st.checkbox(
                    "Confirmo que quero excluir este usuário permanentemente",
                    key=f"confirma_exclusao_usuario_{usuario_id_selecionado}"
                )
                if st.button("🗑️ Excluir usuário", use_container_width=True, key=f"btn_excluir_usuario_{usuario_id_selecionado}"):
                    if not confirmar_exclusao_usuario:
                        st.error("Marque a confirmação antes de excluir.")
                    else:
                        try:
                            supabase.table("usuarios").delete().eq("id", int(usuario_id_selecionado)).execute()
                            st.success("Usuário excluído!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir usuário: {e}")

    elif menu == "💰 Comissoes":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Regras de Comissao</span>', unsafe_allow_html=True)

        st.markdown("### 📊 Produção por banco/tabela")
        df_pizza_com = preparar_dataframe_vendas()
        if df_pizza_com.empty:
            st.info("Nenhuma venda cadastrada para montar o gráfico.")
        else:
            meses_pc = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}
            col_pc1, col_pc2, col_pc3, col_pc4 = st.columns(4)
            mes_pc = col_pc1.selectbox("Mês do gráfico", list(meses_pc.values()), index=datetime.now().month-1, key="pizza_mes")
            anos_pc = sorted(df_pizza_com["ano"].dropna().unique().astype(int).tolist(), reverse=True)
            ano_pc = col_pc2.selectbox("Ano do gráfico", anos_pc if anos_pc else [datetime.now().year], key="pizza_ano")
            status_pc = col_pc3.selectbox("Status do gráfico", ["Todos", "Pago", "Pendente", "Aguardando Pagamento", "Aguardando Assinatura", "Cancelado"], index=0, key="pizza_status")
            vendedores_pc = sorted(df_pizza_com["vendedor"].dropna().unique().tolist())
            vendedor_pc = col_pc4.selectbox("Vendedor", ["Geral"] + vendedores_pc, key="pizza_vendedor")

            mes_num_pc = [k for k, v in meses_pc.items() if v == mes_pc][0]
            df_pizza_com = df_pizza_com[(df_pizza_com["mes_num"] == mes_num_pc) & (df_pizza_com["ano"] == ano_pc)]
            if status_pc != "Todos":
                df_pizza_com = df_pizza_com[df_pizza_com["status"] == status_pc]
            if vendedor_pc != "Geral":
                df_pizza_com = df_pizza_com[df_pizza_com["vendedor"] == vendedor_pc]

            total_contratos_pc = len(df_pizza_com)
            total_valor_pc = df_pizza_com["valor"].fillna(0).sum() if not df_pizza_com.empty else 0
            mpc1, mpc2 = st.columns(2)
            mpc1.metric("📋 Contratos no gráfico", total_contratos_pc)
            mpc2.metric("💰 Valor produzido", dinheiro(total_valor_pc))

            titulo_pizza = f"{vendedor_pc} • {mes_pc}/{ano_pc}"
            renderizar_pizza_bancos(df_pizza_com, titulo=titulo_pizza)

        st.divider()
        st.markdown("### 🏦 Grupos de Bancos")

        def carregar_grupos():
            try:
                res = supabase.table("grupos_banco").select("*").order("nome").execute()
                return res.data or []
            except Exception: return []

        def carregar_tabelas_grupo(grupo_id):
            try:
                res = supabase.table("grupos_banco_tabelas").select("*").eq("grupo_id", grupo_id).execute()
                return [r["tabela_banco"] for r in (res.data or [])]
            except Exception: return []

        def salvar_grupo(nome, dias, tipo, dia_sem):
            try:
                supabase.table("grupos_banco").insert({"nome": nome.strip().upper(), "dias_uteis": dias, "tipo_pagamento": tipo, "dia_semana": dia_sem}).execute()
                return True
            except Exception: return False

        def atualizar_grupo(grupo_id, dias, tipo, dia_sem):
            try:
                supabase.table("grupos_banco").update({"dias_uteis": dias, "tipo_pagamento": tipo, "dia_semana": dia_sem}).eq("id", grupo_id).execute()
                return True
            except Exception: return False

        def salvar_tabelas_grupo(grupo_id, tabelas):
            try:
                supabase.table("grupos_banco_tabelas").delete().eq("grupo_id", grupo_id).execute()
                for tab in tabelas:
                    supabase.table("grupos_banco_tabelas").insert({"grupo_id": grupo_id, "tabela_banco": tab}).execute()
                return True
            except Exception: return False

        def excluir_grupo(grupo_id):
            try:
                supabase.table("grupos_banco").delete().eq("id", grupo_id).execute()
                return True
            except Exception: return False

        dias_semana_opts = ["Segunda","Terca","Quarta","Quinta","Sexta"]

        grupos = carregar_grupos()
        todas_tabelas = carregar_tabelas()

        tabelas_ja_usadas = set()
        tabelas_por_grupo = {}
        for g in grupos:
            tabs = carregar_tabelas_grupo(g["id"])
            tabelas_por_grupo[g["id"]] = tabs
            tabelas_ja_usadas.update(tabs)

        tabelas_livres = [t for t in todas_tabelas if t not in tabelas_ja_usadas]

        tipo_novo = st.selectbox("Tipo de pagamento", ["Dias úteis após a venda", "Dia fixo da semana"], key="tipo_novo_sel")

        with st.form("form_novo_grupo"):
            col_ng1, col_ng2 = st.columns([2, 2])
            nome_grupo = col_ng1.text_input("Nome do grupo", placeholder="Ex: 3RN CAPITAL")
            if tipo_novo == "Dias úteis após a venda":
                dias_grupo = col_ng2.number_input("Dias úteis após a venda", min_value=1, max_value=60, value=4, step=1, key="dias_novo")
                dia_sem_novo = "Segunda"
            else:
                dias_grupo = 0
                dia_sem_novo = col_ng2.selectbox("Dia fixo de pagamento", dias_semana_opts, key="diasem_novo")
            if tabelas_livres:
                st.markdown("**Selecione as tabelas deste grupo:**")
                cols_nl = st.columns(2)
                selecionadas_novo = []
                for i, tab in enumerate(tabelas_livres):
                    if cols_nl[i % 2].checkbox(tab, key=f"new_tab_{i}"):
                        selecionadas_novo.append(tab)
            else:
                st.info("Todas as tabelas já estão vinculadas a grupos.")
                selecionadas_novo = []
            if st.form_submit_button("➕ Criar grupo", use_container_width=True):
                if not nome_grupo.strip():
                    st.error("Digite o nome do grupo.")
                else:
                    salvar_grupo(nome_grupo, dias_grupo, "dias" if tipo_novo=="Dias úteis após a venda" else "semana", dia_sem_novo)
                    res_g = supabase.table("grupos_banco").select("id").eq("nome", nome_grupo.strip().upper()).execute()
                    if res_g.data and selecionadas_novo:
                        salvar_tabelas_grupo(res_g.data[0]["id"], selecionadas_novo)
                    st.success("Grupo criado!"); st.rerun()

        for grupo in grupos:
            gid = grupo["id"]
            gnome = grupo["nome"]
            gdias = int(grupo.get("dias_uteis") or 0)
            gtipo = grupo.get("tipo_pagamento") or "dias"
            gdiasem = grupo.get("dia_semana") or "Segunda"
            tabelas_do_grupo = carregar_tabelas_grupo(gid)
            qtd = len(tabelas_do_grupo)
            resumo = f"{gdias} dias úteis" if gtipo=="dias" else f"Toda {gdiasem}"

            with st.expander(f"🏦 {gnome} — {qtd} tabela(s) • {resumo}"):
                tipo_edit = st.selectbox("Tipo de pagamento",
                    ["Dias úteis após a venda","Dia fixo da semana"],
                    index=0 if gtipo=="dias" else 1,
                    key=f"tipo_sel_{gid}")

                with st.form(f"form_grupo_{gid}"):
                    if tipo_edit == "Dias úteis após a venda":
                        novo_dias = st.number_input("Dias úteis após a venda", min_value=1, max_value=60, value=gdias if gdias>0 else 4, step=1, key=f"dias_{gid}")
                        novo_diasem = gdiasem
                    else:
                        novo_dias = 0
                        idx_sem = dias_semana_opts.index(gdiasem) if gdiasem in dias_semana_opts else 0
                        novo_diasem = st.selectbox("Dia fixo de pagamento (paga o produzido na semana anterior)", dias_semana_opts, index=idx_sem, key=f"diasem_{gid}")

                    st.markdown("**Selecione as tabelas/comissões deste grupo:**")
                    cols_tab = st.columns(2)
                    selecionadas = []
                    tabelas_disponiveis = [t for t in todas_tabelas if t in tabelas_por_grupo[gid] or t not in tabelas_ja_usadas]
                    for i, tab in enumerate(tabelas_disponiveis):
                        checked = tab in tabelas_por_grupo[gid]
                        if cols_tab[i % 2].checkbox(tab, value=checked, key=f"tab_{gid}_{i}"):
                            selecionadas.append(tab)
                    col_s1, col_s2 = st.columns(2)
                    if col_s1.form_submit_button("💾 Salvar", use_container_width=True):
                        atualizar_grupo(gid, novo_dias, "dias" if tipo_edit=="Dias úteis após a venda" else "semana", novo_diasem)
                        salvar_tabelas_grupo(gid, selecionadas)
                        st.success("Grupo atualizado!"); st.rerun()
                    if col_s2.form_submit_button("🗑️ Excluir grupo", use_container_width=True):
                        excluir_grupo(gid)
                        st.success("Grupo excluído!"); st.rerun()

        st.divider()

        st.markdown("### 📅 Calendário de Previsão de Comissões")

        def dias_uteis_apos(data_inicio, dias):
            from datetime import timedelta
            atual = pd.Timestamp(data_inicio)
            contados = 0
            while contados < dias:
                atual += timedelta(days=1)
                if atual.weekday() < 5:
                    contados += 1
            return atual

        df_cal = preparar_dataframe_vendas()
        grupos_cal = carregar_grupos()

        if not df_cal.empty and grupos_cal:
            df_pagas_cal = df_cal[df_cal["status"] == "Pago"].copy()
            eventos_cal = {}

            dia_semana_map = {"Segunda":0,"Terca":1,"Quarta":2,"Quinta":3,"Sexta":4}

            for grupo in grupos_cal:
                gid = grupo["id"]
                gnome = grupo["nome"]
                gdias = int(grupo.get("dias_uteis") or 0)
                gtipo = grupo.get("tipo_pagamento") or "dias"
                gdiasem = grupo.get("dia_semana") or "Segunda"
                tabs_grupo = carregar_tabelas_grupo(gid)
                df_grupo = df_pagas_cal[df_pagas_cal["tabela_banco"].isin(tabs_grupo)]

                for _, row in df_grupo.iterrows():
                    data_venda = row.get("data")
                    if pd.isna(data_venda): continue
                    if gtipo == "dias":
                        data_prev = dias_uteis_apos(data_venda, gdias)
                    else:
                        from datetime import timedelta
                        alvo = dia_semana_map.get(gdiasem, 0)
                        dv = pd.Timestamp(data_venda)
                        dias_ate_seg = dv.weekday()
                        seg_atual = dv - timedelta(days=dias_ate_seg)
                        seg_prox = seg_atual + timedelta(days=7)
                        data_prev = seg_prox + timedelta(days=alvo)
                    key = str(data_prev.date())
                    valor_com = float(row.get("valor_comissao_empresa") or 0)
                    if valor_com == 0:
                        perc = calcular_percentual_empresa_venda(row.get("tabela_banco",""), float(row.get("valor",0)))
                        valor_com = float(row.get("valor",0)) * (perc/100)
                    if key not in eventos_cal:
                        eventos_cal[key] = {}
                    if gnome not in eventos_cal[key]:
                        eventos_cal[key][gnome] = 0
                    eventos_cal[key][gnome] += valor_com

            hoje = pd.Timestamp.now()
            mes_atual = hoje.month
            ano_atual = hoje.year

            meses_cal = {1:"Janeiro",2:"Fevereiro",3:"Marco",4:"Abril",5:"Maio",6:"Junho",
                        7:"Julho",8:"Agosto",9:"Setembro",10:"Outubro",11:"Novembro",12:"Dezembro"}

            col_cm1, col_cm2 = st.columns(2)
            mes_cal = col_cm1.selectbox("Mês", list(meses_cal.values()), index=mes_atual-1, key="cal_mes")
            anos_cal = sorted(df_cal["ano"].dropna().unique().astype(int).tolist(), reverse=True)
            ano_cal = col_cm2.selectbox("Ano", anos_cal if anos_cal else [ano_atual], key="cal_ano")
            mes_num_cal = [k for k,v in meses_cal.items() if v==mes_cal][0]

            import calendar
            primeiro_dia = calendar.weekday(ano_cal, mes_num_cal, 1)
            primeiro_dia = (primeiro_dia + 1) % 7
            dias_no_mes = calendar.monthrange(ano_cal, mes_num_cal)[1]

            total_mes_cal = sum(sum(g.values()) for k,g in eventos_cal.items() if k.startswith(f"{ano_cal}-{str(mes_num_cal).zfill(2)}"))
            total_7d = 0
            total_atrasado = 0
            for k, gvals in eventos_cal.items():
                d = pd.Timestamp(k)
                diff = (d.normalize() - hoje.normalize()).days
                val = sum(gvals.values())
                if diff < 0: total_atrasado += val
                elif diff <= 7: total_7d += val

            k1, k2, k3 = st.columns(3)
            k1.metric("💰 Total no mês", dinheiro(total_mes_cal))
            k2.metric("⚡ Próximos 7 dias", dinheiro(total_7d))
            k3.metric("⚠️ Atrasados", dinheiro(total_atrasado))

            cores_grupos = ["#E6F1FB","#EEEDFE","#E1F5EE","#FAEEDA","#FCEBEB","#EAF3DE"]
            cores_texto  = ["#185FA5","#3C3489","#0F6E56","#854F0B","#A32D2D","#3B6D11"]
            mapa_cores = {}
            for i, g in enumerate(grupos_cal):
                mapa_cores[g["nome"]] = (cores_grupos[i % len(cores_grupos)], cores_texto[i % len(cores_texto)])

            dias_semana = ["Dom","Seg","Ter","Qua","Qui","Sex","Sáb"]
            header_html = "".join([f'<div style="text-align:center;font-size:11px;color:#64748b;padding:4px 0;">{d}</div>' for d in dias_semana])
            cells_html = ""
            for _ in range(primeiro_dia):
                cells_html += '<div></div>'
            for d in range(1, dias_no_mes+1):
                key = f"{ano_cal}-{str(mes_num_cal).zfill(2)}-{str(d).zfill(2)}"
                is_hoje = (d == hoje.day and mes_num_cal == hoje.month and ano_cal == hoje.year)
                is_weekend = (d + primeiro_dia - 1) % 7 in [0, 6]
                grupos_dia = eventos_cal.get(key, {})
                total_dia = sum(grupos_dia.values())

                border = "2px solid #378ADD" if is_hoje else "0.5px solid #e2e8f0"
                bg = "#ffffff" if grupos_dia else "#f8fafc"
                opacity = "opacity:0.5;" if is_weekend else ""

                inner = f'<div style="font-size:11px;color:#64748b;margin-bottom:3px;">{d}</div>'
                for gnome, val in grupos_dia.items():
                    bg_c, txt_c = mapa_cores.get(gnome, ("#f1f5f9","#64748b"))
                    inner += f'<div style="font-size:9px;font-weight:600;background:{bg_c};color:{txt_c};border-radius:3px;padding:1px 4px;margin-bottom:2px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{gnome[:10]}: {dinheiro(val).replace("R$ ","R$")}</div>'
                if total_dia > 0:
                    inner += f'<div style="font-size:9px;font-weight:700;color:#0f172a;border-top:0.5px solid #e2e8f0;padding-top:2px;margin-top:2px;">Total: {dinheiro(total_dia).replace("R$ ","R$")}</div>'

                cells_html += f'<div style="background:{bg};border:{border};border-radius:8px;padding:5px;min-height:70px;{opacity}">{inner}</div>'

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin-bottom:4px;">{header_html}</div>
            <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;">{cells_html}</div>
            """, unsafe_allow_html=True)

        elif not grupos_cal:
            st.info("Crie grupos de bancos acima para ver o calendário.")

        st.divider()
        st.markdown("### ⚙️ Regras de Comissao")

        with st.expander("📎 Configurar quais produtos pedem anexo de documento"):
            st.caption("Marque os produtos que devem exibir a seção de anexo de documentos (contracheque, comprovante, etc.) no Nova Venda. Assim que você criar um produto novo aqui embaixo, ele aparece nesta lista para você marcar.")
            produtos_com_doc_cfg = carregar_produtos_requer_documento()
            for produto_cfg in todas_tabelas:
                marcado_atual = produto_cfg in produtos_com_doc_cfg
                novo_valor = st.checkbox(produto_cfg, value=marcado_atual, key=f"cfg_doc_{produto_cfg}")
                if novo_valor != marcado_atual:
                    sucesso_toggle = alternar_produto_requer_documento(produto_cfg, novo_valor)
                    if not sucesso_toggle:
                        st.error(f"⚠️ Não consegui salvar essa marcação para '{produto_cfg}'. Verifique se a tabela 'produtos_requer_documento' existe no Supabase e se o RLS permite INSERT/DELETE.")
                    else:
                        st.rerun()

        with st.expander("➕ Adicionar nova comissão", expanded=False):
            with st.form("nova_regra_rapida", clear_on_submit=True):
                col_nova1, col_nova2, col_nova3, col_nova4 = st.columns([3, 1.3, 1.3, 1])

                produto_novo = col_nova1.text_input(
                    "Tabela/Banco",
                    placeholder="Ex: 3RN CAPITAL - FGL 23 (36X)"
                )

                valor_minimo_novo = col_nova2.number_input(
                    "Valor mínimo",
                    min_value=0.0,
                    step=1000.0,
                    value=0.0
                )

                percentual_empresa_novo = col_nova3.number_input(
                    "% Empresa",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.01,
                    value=0.0,
                    format="%.2f"
                )

                ativo_novo = col_nova4.checkbox("Ativo", value=True)

                salvar_nova = st.form_submit_button(
                    "➕ Adicionar comissão",
                    use_container_width=True
                )

                if salvar_nova:
                    nome_novo = str(produto_novo or "").strip().upper()

                    if not nome_novo:
                        st.error("Digite o nome da Tabela/Banco.")
                    else:
                        supabase.table("regras_comissao").insert({
                            "produto": nome_novo,
                            "valor_minimo": valor_minimo_novo,
                            "percentual_empresa": percentual_empresa_novo,
                            "percentual_vendedor": 0,
                            "ativo": ativo_novo
                        }).execute()

                        st.success("Comissão adicionada!")
                        st.rerun()

        regras = supabase.table("regras_comissao").select("*").order("produto").order("valor_minimo").execute()
        df_regras = pd.DataFrame(regras.data)

        if df_regras.empty:
            st.warning("Nenhuma regra cadastrada.")
        else:
            st.markdown("**Editar tabelas rapidamente:**")
            st.caption("Edite direto na tabela: Tabela/Banco, Valor Mínimo, % Empresa e Ativo.")

            df_edit = df_regras[["id","produto","valor_minimo","percentual_empresa","ativo"]].copy()
            df_edit = df_edit.rename(columns={
                "produto": "Tabela/Banco",
                "valor_minimo": "Valor Minimo",
                "percentual_empresa": "% Empresa",
                "ativo": "Ativo"
            })

            editado = st.data_editor(
                df_edit,
                use_container_width=True,
                hide_index=True,
                disabled=["id"],
                column_config={
                    "Tabela/Banco": st.column_config.TextColumn(
                        "Tabela/Banco",
                        help="Edite o nome da tabela/banco aqui",
                        required=True
                    ),
                    "Valor Minimo": st.column_config.NumberColumn(
                        "Valor Minimo",
                        help="Valor mínimo para essa regra. Normalmente pode ficar 0.",
                        min_value=0.0,
                        step=1000.0,
                        format="%.2f"
                    ),
                    "% Empresa": st.column_config.NumberColumn(
                        "% Empresa",
                        help="Edite o percentual da empresa aqui. Ex: 5.05",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.01,
                        format="%.2f"
                    ),
                    "Ativo": st.column_config.CheckboxColumn(
                        "Ativo",
                        help="Desmarque para inativar"
                    )
                }
            )

            col_salvar_tab, col_info_tab = st.columns([1.2, 2.8])

            with col_salvar_tab:
                salvar_tabela = st.button(
                    "💾 Salvar alterações da tabela",
                    use_container_width=True,
                    key="btn_salvar_tabela_comissao"
                )

            with col_info_tab:
                st.caption("Dica: após editar uma célula, clique em Salvar alterações da tabela.")

            if salvar_tabela:
                for _, row in editado.iterrows():
                    nome_tabela = str(row["Tabela/Banco"] or "").strip().upper()

                    try:
                        percentual_empresa_edit = float(row["% Empresa"] or 0)
                    except Exception:
                        percentual_empresa_edit = converter_valor_brasileiro(row["% Empresa"])

                    try:
                        valor_minimo_edit = float(row["Valor Minimo"] or 0)
                    except Exception:
                        valor_minimo_edit = converter_valor_brasileiro(row["Valor Minimo"])

                    if not nome_tabela:
                        st.error("Existe uma linha sem nome de Tabela/Banco. Corrija antes de salvar.")
                        st.stop()

                    supabase.table("regras_comissao").update({
                        "produto": nome_tabela,
                        "valor_minimo": valor_minimo_edit,
                        "percentual_empresa": percentual_empresa_edit,
                        "ativo": bool(row["Ativo"])
                    }).eq("id", int(row["id"])).execute()

                st.success("Alterações salvas!")
                st.rerun()

            st.divider()

            with st.expander("🗑️ Excluir comissão", expanded=False):
                regra_id_excluir = st.selectbox(
                    "Selecionar comissão para excluir",
                    df_regras["id"].tolist(),
                    format_func=lambda x: df_regras[df_regras["id"]==x].iloc[0]["produto"],
                    key="regra_id_excluir_rapido"
                )

                confirmar_excluir_regra = st.checkbox(
                    "Confirmo que quero excluir esta comissão",
                    key="confirmar_excluir_regra_rapido"
                )

                if st.button("🗑️ Excluir comissão selecionada", use_container_width=True, key="btn_excluir_regra_rapido"):
                    if not confirmar_excluir_regra:
                        st.error("Marque a confirmação antes de excluir.")
                    else:
                        supabase.table("regras_comissao").delete().eq("id", int(regra_id_excluir)).execute()
                        st.success("Comissão excluída!")
                        st.rerun()


    elif menu == "🏢 Custos":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Custos Operacionais</span>', unsafe_allow_html=True)

        def carregar_custos():
            try:
                res = supabase.table("custos_operacionais").select("*").order("categoria").order("id").execute()
                return res.data or []
            except Exception: return []

        def salvar_custo(nome, categoria, valor):
            try:
                supabase.table("custos_operacionais").insert({"nome":nome,"categoria":categoria,"valor":valor,"mes":datetime.now().month,"ano":datetime.now().year}).execute()
                return True
            except Exception: return False

        def excluir_custo(cid):
            try:
                supabase.table("custos_operacionais").delete().eq("id",int(cid)).execute()
                return True
            except Exception: return False

        df_c = preparar_dataframe_vendas()
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        df_c = df_c[(df_c["mes_num"]==mes_atual)&(df_c["ano"]==ano_atual)]
        comissao_mes = df_c[df_c["status"]=="Pago"]["valor_comissao_empresa"].fillna(0).sum()
        if comissao_mes==0:
            comissao_mes = df_c[df_c["status"]=="Pago"]["valor"].fillna(0).sum()*0.038
        custos = carregar_custos()
        total_custos = sum(float(c.get("valor",0)) for c in custos)
        resultado = comissao_mes - total_custos
        taxa_media = 3.8
        vol_necessario = total_custos/(taxa_media/100) if taxa_media>0 else 0
        pct_cobertura = min(int((comissao_mes/total_custos*100)) if total_custos>0 else 0, 100)
        col_k1,col_k2,col_k3,col_k4 = st.columns(4)
        col_k1.metric("💸 Total custos", dinheiro(total_custos))
        col_k2.metric("💰 Comissao atual", dinheiro(comissao_mes))
        col_k3.metric("🎯 Vol. necessario", f"R$ {round(vol_necessario/1000)}k")
        col_k4.metric("📊 Resultado", dinheiro(resultado), delta=f"{pct_cobertura}% coberto")
        bar_color = "#22c55e" if pct_cobertura>=100 else "#0ea5e9" if pct_cobertura>=70 else "#ef4444"
        st.markdown(f"""
        <div style="background:#ffffff;border:1.5px solid rgba(14,165,233,0.25);border-radius:14px;padding:16px 20px;margin:10px 0 20px;">
            <div style="display:flex;justify-content:space-between;font-size:12px;color:#64748b;margin-bottom:8px;"><span>Cobertura dos custos</span><span style="font-weight:700;color:{'#16a34a' if pct_cobertura>=100 else '#0ea5e9' if pct_cobertura>=70 else '#dc2626'};">{pct_cobertura}%</span></div>
            <div style="background:#f1f5f9;border-radius:999px;height:12px;overflow:hidden;">
                <div style="width:{pct_cobertura}%;height:100%;background:{bar_color};border-radius:999px;"></div>
            </div>
            <div style="font-size:11px;color:#94a3b8;margin-top:5px;">{"Superavit: "+dinheiro(resultado) if resultado>=0 else "Faltam: "+dinheiro(abs(resultado))}</div>
        </div>
        """, unsafe_allow_html=True)
        col_left,col_right = st.columns([1.6,1])
        with col_left:
            with st.form("form_novo_custo", clear_on_submit=True):
                col_n,col_cat,col_v,col_q = st.columns([2,1.5,1,0.8])
                nome_c = col_n.text_input("Descricao", placeholder="Ex: Salario minimo")
                cat_c = col_cat.selectbox("Categoria", ["Pessoal","DP","Estrutura","Marketing","Outros"])
                val_c = col_v.number_input("Valor (R$)", min_value=0.0, step=100.0)
                qtd_c = col_q.number_input("Qtd", min_value=1, max_value=20, step=1, value=1)
                if st.form_submit_button("➕ Adicionar custo", use_container_width=True):
                    if nome_c and val_c>0:
                        nome_final = f"{nome_c} (x{qtd_c})" if qtd_c>1 else nome_c
                        if salvar_custo(nome_final, cat_c, val_c*qtd_c): st.success(f"Adicionado: {dinheiro(val_c*qtd_c)}"); st.rerun()
                    else: st.error("Preencha descricao e valor.")
            if custos:
                cat_atual = None
                for c in custos:
                    cat = c.get("categoria","Outros")
                    cat_label = "DP — Depart. Pessoal" if cat=="DP" else cat
                    if cat != cat_atual:
                        cat_atual = cat
                        st.markdown(f'<div style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.10em;padding:8px 0 4px;">{cat_label}</div>', unsafe_allow_html=True)
                    col_desc,col_val,col_edit,col_del = st.columns([3,1.5,0.4,0.4])
                    col_desc.markdown(f'<div style="padding:8px 0;font-size:14px;color:#0f172a;">{c.get("nome","")}</div>', unsafe_allow_html=True)
                    col_val.markdown(f'<div style="padding:8px 0;font-size:14px;font-weight:700;color:#dc2626;">{dinheiro(c.get("valor",0))}</div>', unsafe_allow_html=True)
                    if col_edit.button("✏️", key=f"edit_custo_{c['id']}"):
                        st.session_state[f"editando_custo_{c['id']}"] = True
                    if col_del.button("✕", key=f"del_custo_{c['id']}"):
                        excluir_custo(c["id"]); st.rerun()
                    if st.session_state.get(f"editando_custo_{c['id']}"):
                        with st.form(f"form_edit_custo_{c['id']}"):
                            ec1,ec2,ec3 = st.columns([2,1.5,1])
                            novo_nome = ec1.text_input("Descricao", value=c.get("nome",""), key=f"en_{c['id']}")
                            nova_cat = ec2.selectbox("Categoria", ["Pessoal","DP","Estrutura","Marketing","Outros"],
                                index=["Pessoal","DP","Estrutura","Marketing","Outros"].index(c.get("categoria","Outros")) if c.get("categoria","Outros") in ["Pessoal","DP","Estrutura","Marketing","Outros"] else 0,
                                key=f"ec_{c['id']}")
                            novo_val = ec3.number_input("Valor", value=float(c.get("valor",0)), step=100.0, key=f"ev_{c['id']}")
                            cs1,cs2 = st.columns(2)
                            if cs1.form_submit_button("💾 Salvar"):
                                try:
                                    supabase.table("custos_operacionais").update({"nome":novo_nome,"categoria":nova_cat,"valor":novo_val}).eq("id",int(c["id"])).execute()
                                    st.session_state[f"editando_custo_{c['id']}"] = False
                                    st.success("Custo atualizado!"); st.rerun()
                                except Exception as e: st.error(f"Erro: {e}")
                            if cs2.form_submit_button("Cancelar"):
                                st.session_state[f"editando_custo_{c['id']}"] = False; st.rerun()
            else:
                st.info("Nenhum custo cadastrado ainda.")
        with col_right:
            if custos:
                cats_total = {}
                for c in custos:
                    cat = c.get("categoria","Outros")
                    cats_total[cat] = cats_total.get(cat,0)+float(c.get("valor",0))
                cores = {"Pessoal":"#0ea5e9","DP":"#6366f1","Estrutura":"#1d9e75","Marketing":"#ba7517","Outros":"#888780"}
                for cat,val in sorted(cats_total.items(), key=lambda x: -x[1]):
                    pct = int((val/total_custos*100)) if total_custos>0 else 0
                    cor = cores.get(cat,"#0ea5e9")
                    st.markdown(f"""<div style="margin-bottom:12px;"><div style="display:flex;justify-content:space-between;font-size:13px;margin-bottom:4px;"><span style="color:#0f172a;">{cat}</span><span style="color:#64748b;">{dinheiro(val)} ({pct}%)</span></div><div style="background:#f1f5f9;border-radius:999px;height:8px;overflow:hidden;"><div style="width:{pct}%;height:100%;background:{cor};border-radius:999px;"></div></div></div>""", unsafe_allow_html=True)
                st.divider()
                st.markdown(f'<div style="font-size:12px;color:#64748b;">Volume break-even</div><div style="font-size:20px;font-weight:800;color:#0f172a;">{dinheiro(vol_necessario)}</div><div style="font-size:12px;color:#94a3b8;">a taxa {taxa_media}%</div><div style="font-size:12px;color:#64748b;margin-top:8px;">Por vendedora (2)</div><div style="font-size:18px;font-weight:700;color:#0ea5e9;">{dinheiro(vol_necessario/2)}</div>', unsafe_allow_html=True)
            else:
                st.info("Adicione custos para ver a distribuicao.")

    elif menu == "📑 Consulta FGTS":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">Consulta FGTS — Saque Aniversário</span>', unsafe_allow_html=True)
        st.caption("Consulta o saldo de FGTS (Saque Aniversário) via API V8 Digital, provider BMS.")

        if "fgts_flags" not in st.session_state:
            st.session_state.fgts_flags = {}

        def fgts_buscar_rodada_ativa():
            try:
                res = supabase.table("fgts_rodadas").select("*").in_("status", ["em_andamento","pausando","cancelando"]).order("id", desc=True).limit(1).execute()
                return res.data[0] if res.data else None
            except Exception:
                return None

        def fgts_buscar_rodadas_pausadas():
            try:
                res = supabase.table("fgts_rodadas").select("*").in_("status", ["pausada", "erro_autenticacao"]).order("id", desc=True).execute()
                return res.data or []
            except Exception:
                return []

        def fgts_buscar_historico(limite=15):
            try:
                res = supabase.table("fgts_rodadas").select("*").order("id", desc=True).limit(limite).execute()
                return res.data or []
            except Exception:
                return []

        def fgts_buscar_resultados(rodada_id):
            try:
                res = supabase.table("fgts_resultados").select("*").eq("rodada_id", rodada_id).execute()
                return res.data or []
            except Exception:
                return []

        def fgts_buscar_credenciais(somente_ativas=False):
            try:
                q = supabase.table("fgts_credenciais").select("*").order("id")
                if somente_ativas:
                    q = q.eq("ativo", True)
                res = q.execute()
                return res.data or []
            except Exception:
                return []

        def fgts_formatar_tempo(segundos):
            if segundos is None:
                return "—"
            segundos = float(segundos)
            if segundos < 60:
                return f"{segundos:.0f}s"
            minutos = int(segundos // 60)
            seg_resto = int(segundos % 60)
            if minutos < 60:
                return f"{minutos}min {seg_resto}s"
            horas = int(minutos // 60)
            min_resto = int(minutos % 60)
            return f"{horas}h {min_resto}min"

        def fgts_calcular_tempo_medio(resultados_rod):
            tempos = [float(r.get("tempo_segundos")) for r in resultados_rod if r.get("tempo_segundos") is not None]
            if not tempos:
                return None
            return sum(tempos) / len(tempos)

        def fgts_exportar_excel(resultados_rod, nome_arquivo, key_botao):
            df_res = pd.DataFrame(resultados_rod)
            mapa_status_label = {
                "success": "✅ Sucesso",
                "fail": "❌ Falha",
                "nao_autorizado": "🚫 Não autorizado",
                "saldo_insuficiente": "⚠️ Saldo insuficiente",
                "operacao_em_andamento": "🔄 Operação em andamento",
                "erro_tecnico": "⚠️ Erro técnico",
            }
            df_res["status_label"] = df_res["status"].map(lambda s: mapa_status_label.get(s, s))
            colunas_exibir = ["cpf","provider","status_label","saldo_disponivel","periodos","observacao","tempo_segundos","processado_em"]
            colunas_exibir = [c for c in colunas_exibir if c in df_res.columns]
            df_visao_fgts = df_res[colunas_exibir].rename(columns={
                "cpf":"CPF","provider":"Provider","status_label":"Status",
                "saldo_disponivel":"Saldo disponível","periodos":"Períodos",
                "observacao":"Observação","tempo_segundos":"Tempo (s)","processado_em":"Processado em"
            })
            st.dataframe(df_visao_fgts, use_container_width=True, hide_index=True)

            buf_fgts = io.BytesIO()
            with pd.ExcelWriter(buf_fgts, engine="openpyxl") as writer:
                df_visao_fgts.to_excel(writer, index=False, sheet_name="Resultados FGTS")
            buf_fgts.seek(0)
            st.download_button(
                label="📥 Exportar resultado (Excel)",
                data=buf_fgts,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                key=key_botao
            )

        with st.expander("🔑 Gerenciar credenciais V8 (logins para rodar em paralelo)"):
            st.caption("Cadastre quantos logins V8 quiser. Ao iniciar uma consulta, você escolhe quais ficam ativos para dividir os CPFs entre eles e processar em paralelo.")

            with st.form("form_nova_credencial_fgts", clear_on_submit=True):
                col_cred1, col_cred2, col_cred3 = st.columns([1.3,1.5,1.5])
                apelido_cred = col_cred1.text_input("Apelido", placeholder="Ex: Tamara, João...")
                username_cred = col_cred2.text_input("E-mail (login V8)")
                password_cred = col_cred3.text_input("Senha (login V8)", type="password")
                if st.form_submit_button("➕ Adicionar credencial", use_container_width=True):
                    if not username_cred.strip() or not password_cred.strip():
                        st.error("Preencha e-mail e senha.")
                    else:
                        supabase.table("fgts_credenciais").insert({
                            "apelido": apelido_cred.strip() or username_cred.strip(),
                            "username": username_cred.strip(),
                            "password": password_cred,
                            "ativo": True,
                        }).execute()
                        st.success("Credencial adicionada!")
                        st.rerun()

            credenciais_existentes = fgts_buscar_credenciais()
            if not credenciais_existentes:
                st.info("Nenhuma credencial cadastrada ainda. Adicione pelo menos uma para iniciar consultas.")
            else:
                st.markdown("**Credenciais cadastradas:**")
                for cred in credenciais_existentes:
                    col_v1, col_v2, col_v3 = st.columns([3,1,1])
                    with col_v1:
                        status_ativo = "🟢 Ativa" if cred.get("ativo") else "⚪ Inativa"
                        st.markdown(f"**{cred.get('apelido','')}** — {cred.get('username','')} — {status_ativo}")
                    with col_v2:
                        if st.button("🔁 Ativar/Desativar", key=f"toggle_cred_{cred['id']}"):
                            supabase.table("fgts_credenciais").update({"ativo": not cred.get("ativo")}).eq("id", cred["id"]).execute()
                            st.rerun()
                    with col_v3:
                        if st.button("🗑️ Remover", key=f"del_cred_{cred['id']}"):
                            supabase.table("fgts_credenciais").delete().eq("id", cred["id"]).execute()
                            st.rerun()

        st.divider()

        rodada_ativa = fgts_buscar_rodada_ativa()
        rodadas_pausadas = fgts_buscar_rodadas_pausadas()

        if rodada_ativa and rodada_ativa.get("status") == "em_andamento":
            resultado_watchdog_aba = fgts_checar_e_religar_rodada_ativa()
            if resultado_watchdog_aba:
                st.session_state.fgts_flags[rodada_ativa["id"]] = _fgts_flags_globais.get(rodada_ativa["id"])
                st.warning(f"⚠️ {resultado_watchdog_aba}")
                time.sleep(1)
                st.rerun()

        if rodada_ativa:
            rid = rodada_ativa["id"]
            status_rid = rodada_ativa.get("status","em_andamento")
            total = int(rodada_ativa.get("total_cpfs") or 0)
            processados = int(rodada_ativa.get("processados") or 0)
            pct = int((processados/total*100)) if total > 0 else 0
            cred_usadas_txt = rodada_ativa.get("credenciais_usadas") or ""

            if status_rid == "pausando":
                st.warning(f"⏸️ Rodada #{rid} — pausando... (finalizando o(s) CPF(s) atual(is))")
            elif status_rid == "cancelando":
                st.warning(f"🛑 Rodada #{rid} — cancelando... (finalizando o(s) CPF(s) atual(is))")
            else:
                st.info(f"⏳ Rodada #{rid} em andamento — iniciada em {str(rodada_ativa.get('iniciado_em',''))[:16]}")

            if cred_usadas_txt:
                st.caption(f"🔑 Processando em paralelo com: {cred_usadas_txt}")

            cred_com_erro_txt = rodada_ativa.get("credenciais_com_erro") or ""
            if cred_com_erro_txt:
                st.error(f"⚠️ Credencial(is) com erro de autenticação nesta rodada: {cred_com_erro_txt}. As demais credenciais continuam processando normalmente — corrija/troque essa credencial e retome depois para reaproveitar a fatia dela.")
                detalhe_erro_txt = rodada_ativa.get("detalhe_erro_autenticacao") or ""
                if detalhe_erro_txt:
                    with st.expander("Ver detalhe técnico do erro"):
                        st.code(detalhe_erro_txt)

            st.progress(min(pct,100)/100, text=f"{processados} de {total} — {pct}%")

            resultados_atuais = fgts_buscar_resultados(rid)
            tempo_medio = fgts_calcular_tempo_medio(resultados_atuais)

            col_t1, col_t2, col_t3 = st.columns(3)
            col_t1.metric("⏱️ Tempo médio por CPF", fgts_formatar_tempo(tempo_medio) if tempo_medio else "Calculando...")
            if tempo_medio and total > processados:
                n_cred_ativa = max(len(cred_usadas_txt.split(",")), 1) if cred_usadas_txt else 1
                restante_estimado = (tempo_medio * (total - processados)) / n_cred_ativa
                col_t2.metric("⏳ Estimativa restante", fgts_formatar_tempo(restante_estimado))
            else:
                col_t2.metric("⏳ Estimativa restante", "—")
            tempo_decorrido = None
            if rodada_ativa.get("iniciado_em"):
                try:
                    inicio_dt = pd.to_datetime(rodada_ativa.get("iniciado_em"))
                    tempo_decorrido = (pd.Timestamp.now() - inicio_dt).total_seconds()
                except Exception:
                    pass
            col_t3.metric("🕐 Tempo decorrido", fgts_formatar_tempo(tempo_decorrido) if tempo_decorrido else "—")

            col_r1, col_r2, col_r3 = st.columns([2,1,1])
            with col_r1:
                st.caption("Você pode navegar para outras abas; a consulta continua em segundo plano.")
            with col_r2:
                if st.button("⏸️ Pausar", use_container_width=True, key=f"pausar_{rid}", disabled=(status_rid!="em_andamento")):
                    flag = st.session_state.fgts_flags.get(rid)
                    if flag is not None:
                        flag["parar"] = "pausar"
                    supabase.table("fgts_rodadas").update({"status": "pausando"}).eq("id", rid).execute()
                    st.info("Pausa solicitada — vai parar após o(s) CPF(s) atual(is) e liberar a exportação do parcial.")
                    time.sleep(1)
                    st.rerun()
            with col_r3:
                if st.button("🛑 Cancelar", use_container_width=True, key=f"cancelar_{rid}", disabled=(status_rid!="em_andamento")):
                    flag = st.session_state.fgts_flags.get(rid)
                    if flag is not None:
                        flag["parar"] = "cancelar"
                    supabase.table("fgts_rodadas").update({"status": "cancelando"}).eq("id", rid).execute()
                    st.warning("Cancelamento solicitado.")
                    time.sleep(1)
                    st.rerun()

            if st.button("🔄 Atualizar progresso", use_container_width=True, key=f"refresh_{rid}"):
                st.rerun()

            st.caption("Se o botão Pausar/Cancelar não tiver efeito em poucos segundos (ex: app reiniciou e a thread não existe mais), force pelo botão abaixo.")
            if st.button("⚠️ Forçar parada (rodada travada)", key=f"forcar_{rid}"):
                supabase.table("fgts_rodadas").update({
                    "status": "pausada"
                }).eq("id", rid).execute()
                st.success("Rodada marcada como pausada. Você já pode exportar o parcial ou retomar.")
                time.sleep(1)
                st.rerun()

        elif rodadas_pausadas:
            st.markdown("### ⏸️ Rodadas pausadas")
            st.caption("Exporte o que já foi consultado ou retome de onde parou.")

            credenciais_ativas_disponiveis = fgts_buscar_credenciais(somente_ativas=True)

            for rod_p in rodadas_pausadas:
                rid_p = rod_p["id"]
                status_rod_p = rod_p.get("status", "pausada")
                total_p = int(rod_p.get("total_cpfs") or 0)
                proc_p = int(rod_p.get("processados") or 0)
                pct_p = int((proc_p/total_p*100)) if total_p > 0 else 0

                with st.container(border=True):
                    if status_rod_p == "erro_autenticacao":
                        st.markdown(f"**Rodada #{rid_p}** — ❌ parou por erro de autenticação, com {proc_p}/{total_p} CPF(s) processados ({pct_p}%)")
                        st.caption("Causa provável: a credencial usada fez login manual em outro lugar (site/app da V8) enquanto a rodada rodava, ou a senha mudou. Evite logar manualmente com a mesma conta enquanto uma rodada estiver ativa.")
                    else:
                        st.markdown(f"**Rodada #{rid_p}** — pausada com {proc_p}/{total_p} CPF(s) processados ({pct_p}%)")

                    resultados_parciais = fgts_buscar_resultados(rid_p)
                    tempo_medio_p = fgts_calcular_tempo_medio(resultados_parciais)
                    if tempo_medio_p:
                        st.caption(f"⏱️ Tempo médio por CPF até aqui: {fgts_formatar_tempo(tempo_medio_p)}")

                    if credenciais_ativas_disponiveis:
                        nomes_cred_retomar = st.multiselect(
                            "Credenciais para retomar (divide os CPFs restantes entre elas)",
                            options=[c["id"] for c in credenciais_ativas_disponiveis],
                            default=[credenciais_ativas_disponiveis[0]["id"]],
                            format_func=lambda cid: next((c["apelido"] for c in credenciais_ativas_disponiveis if c["id"]==cid), str(cid)),
                            key=f"cred_retomar_{rid_p}"
                        )
                    else:
                        nomes_cred_retomar = []
                        st.warning("Nenhuma credencial ativa cadastrada. Cadastre uma acima para poder retomar.")

                    col_p1, col_p2, col_p3 = st.columns([1.3, 1.3, 1])
                    with col_p1:
                        if st.button("▶️ Retomar rodada", use_container_width=True, key=f"retomar_{rid_p}", disabled=(len(nomes_cred_retomar)==0)):
                            cpfs_lista_str = rod_p.get("cpfs_lista") or ""
                            cpfs_originais = [c for c in cpfs_lista_str.split(",") if c]

                            if not cpfs_originais:
                                st.error("Não encontrei a lista original de CPFs desta rodada para retomar.")
                            else:
                                credenciais_selecionadas = [c for c in credenciais_ativas_disponiveis if c["id"] in nomes_cred_retomar]

                                flag = {"parar": False}
                                st.session_state.fgts_flags[rid_p] = flag

                                supabase.table("fgts_rodadas").update({
                                    "status": "em_andamento",
                                    "credenciais_usadas": ", ".join(c["apelido"] for c in credenciais_selecionadas),
                                    "ultimo_processamento_em": str(datetime.now()),
                                }).eq("id", rid_p).execute()

                                fgts_iniciar_threads(cpfs_originais, rid_p, credenciais_selecionadas, flag)

                                st.success(f"Rodada #{rid_p} retomada com {len(credenciais_selecionadas)} credencial(is)!")
                                time.sleep(1)
                                st.rerun()

                    with col_p2:
                        if resultados_parciais:
                            st.caption(f"{len(resultados_parciais)} resultado(s) disponível(eis) para exportar abaixo ⬇️")
                        else:
                            st.caption("Nenhum resultado salvo ainda nesta rodada.")

                    with col_p3:
                        confirmar_descarte = st.checkbox("Confirmo", key=f"confirma_descarte_{rid_p}", help="Marque para habilitar o descarte definitivo desta rodada")
                        if st.button("🗑️ Descartar", use_container_width=True, key=f"descartar_{rid_p}", disabled=not confirmar_descarte):
                            supabase.table("fgts_rodadas").update({
                                "status": "cancelada",
                                "finalizado_em": str(datetime.now()),
                            }).eq("id", rid_p).execute()
                            st.success(f"Rodada #{rid_p} descartada. Os resultados já consultados continuam disponíveis no histórico.")
                            time.sleep(1)
                            st.rerun()

                    if resultados_parciais:
                        with st.expander(f"📋 Ver/exportar resultados parciais da rodada #{rid_p}"):
                            fgts_exportar_excel(resultados_parciais, f"fgts_rodada_{rid_p}_parcial.xlsx", f"export_parcial_{rid_p}")

            st.divider()

            qtd_erro_auth = sum(1 for r in rodadas_pausadas if r.get("status") == "erro_autenticacao")
            if qtd_erro_auth > 1:
                confirmar_limpar_todas = st.checkbox(f"Confirmo que quero descartar as {qtd_erro_auth} rodada(s) com erro de autenticação de uma vez", key="confirma_limpar_todas_erro")
                if st.button(f"🗑️ Descartar todas as {qtd_erro_auth} rodadas com erro de autenticação", use_container_width=True, disabled=not confirmar_limpar_todas):
                    for rod_erro in rodadas_pausadas:
                        if rod_erro.get("status") == "erro_autenticacao":
                            supabase.table("fgts_rodadas").update({
                                "status": "cancelada",
                                "finalizado_em": str(datetime.now()),
                            }).eq("id", rod_erro["id"]).execute()
                    st.success(f"{qtd_erro_auth} rodada(s) descartada(s).")
                    time.sleep(1)
                    st.rerun()
                st.divider()

            if st.button("➕ Iniciar nova rodada (sem retomar)", use_container_width=True):
                st.session_state["fgts_forcar_nova"] = True
                st.rerun()

        if not rodada_ativa and (not rodadas_pausadas or st.session_state.get("fgts_forcar_nova")):
            st.markdown("### ▶️ Nova consulta")

            credenciais_ativas = fgts_buscar_credenciais(somente_ativas=True)

            if not credenciais_ativas:
                st.warning("⚠️ Cadastre pelo menos uma credencial V8 ativa (acima, em 'Gerenciar credenciais V8') antes de iniciar uma consulta.")
            else:
                credenciais_escolhidas_ids = st.multiselect(
                    "Quais credenciais usar nesta rodada? (cada uma processa uma fatia dos CPFs, em paralelo)",
                    options=[c["id"] for c in credenciais_ativas],
                    default=[credenciais_ativas[0]["id"]],
                    format_func=lambda cid: next((c["apelido"] for c in credenciais_ativas if c["id"]==cid), str(cid)),
                    key="fgts_cred_nova_rodada"
                )

                modo_entrada = st.radio("Como deseja informar os CPFs?", ["Colar lista de CPFs", "Subir arquivo .csv"], horizontal=True, key="fgts_modo_entrada")

                cpfs_para_processar = []

                if modo_entrada == "Colar lista de CPFs":
                    texto_cpfs = st.text_area("Cole os CPFs (um por linha)", height=180, placeholder="12345678900\n98765432100\n...", key="fgts_texto_cpfs")
                    if texto_cpfs.strip():
                        linhas = [l.strip() for l in texto_cpfs.splitlines() if l.strip()]
                        for l in linhas:
                            c = limpar_documento(l)
                            if len(c) == 11:
                                cpfs_para_processar.append(c)
                else:
                    arquivo_csv = st.file_uploader("Selecione o arquivo .csv com os CPFs", type=["csv"], key="fgts_upload_csv")
                    if arquivo_csv is not None:
                        try:
                            df_up = pd.read_csv(arquivo_csv, dtype=str)
                            coluna_cpf = None
                            for nome_col in ["cpf","CPF","documentNumber","documento","Documento"]:
                                if nome_col in df_up.columns:
                                    coluna_cpf = nome_col
                                    break
                            if coluna_cpf is None:
                                st.error(f"Não encontrei coluna de CPF no arquivo. Colunas disponíveis: {list(df_up.columns)}")
                            else:
                                for v in df_up[coluna_cpf].dropna():
                                    c = limpar_documento(v)
                                    if len(c) == 11:
                                        cpfs_para_processar.append(c)
                        except Exception as e:
                            st.error(f"Erro ao ler o arquivo: {e}")

                cpfs_para_processar = list(dict.fromkeys(cpfs_para_processar))

                if cpfs_para_processar:
                    n_sel = max(len(credenciais_escolhidas_ids), 1)
                    st.success(f"✅ {len(cpfs_para_processar)} CPF(s) válido(s) detectado(s) — serão divididos entre {n_sel} credencial(is).")

                if st.button("🚀 Iniciar Consulta", use_container_width=True, disabled=(len(cpfs_para_processar)==0 or len(credenciais_escolhidas_ids)==0)):
                    try:
                        credenciais_selecionadas = [c for c in credenciais_ativas if c["id"] in credenciais_escolhidas_ids]

                        nova_rodada = supabase.table("fgts_rodadas").insert({
                            "total_cpfs": len(cpfs_para_processar),
                            "processados": 0,
                            "status": "em_andamento",
                            "usuario": st.session_state.get("nome", st.session_state.get("usuario","")),
                            "cpfs_lista": ",".join(cpfs_para_processar),
                            "credenciais_usadas": ", ".join(c["apelido"] for c in credenciais_selecionadas),
                            "ultimo_processamento_em": str(datetime.now()),
                        }).execute()
                        rodada_id_nova = nova_rodada.data[0]["id"]

                        flag = {"parar": False}
                        st.session_state.fgts_flags[rodada_id_nova] = flag

                        fgts_iniciar_threads(cpfs_para_processar, rodada_id_nova, credenciais_selecionadas, flag)

                        st.session_state["fgts_forcar_nova"] = False
                        st.success(f"Rodada #{rodada_id_nova} iniciada! Processando {len(cpfs_para_processar)} CPF(s) com {len(credenciais_selecionadas)} credencial(is) em paralelo.")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao iniciar rodada: {e}")

        st.divider()

        st.markdown("### 🕓 Histórico de rodadas")
        historico = fgts_buscar_historico(15)

        if not historico:
            st.info("Nenhuma rodada de consulta realizada ainda.")
        else:
            badges_status = {
                "em_andamento": ("⏳ Em andamento", "#fef9c3", "#92400e"),
                "pausando": ("⏸️ Pausando...", "#fef3c7", "#92400e"),
                "pausada": ("⏸️ Pausada", "#e0f2fe", "#075985"),
                "cancelando": ("🛑 Cancelando...", "#fee2e2", "#991b1b"),
                "concluida": ("✅ Concluída", "#dcfce7", "#166534"),
                "cancelada": ("🛑 Cancelada", "#fee2e2", "#991b1b"),
                "erro_autenticacao": ("❌ Erro de autenticação", "#fee2e2", "#991b1b"),
            }

            for rod in historico:
                rid = rod["id"]
                status_rod = rod.get("status","em_andamento")
                label_status, bg_status, txt_status = badges_status.get(status_rod, (status_rod, "#f1f5f9", "#64748b"))
                total_r = int(rod.get("total_cpfs") or 0)
                proc_r = int(rod.get("processados") or 0)
                iniciado = str(rod.get("iniciado_em",""))[:16]
                finalizado = str(rod.get("finalizado_em") or "")[:16]
                tempo_total_r = rod.get("tempo_total_segundos")

                with st.expander(f"Rodada #{rid} — {iniciado} — {proc_r}/{total_r} CPF(s) — {label_status}"):
                    st.markdown(f'''<span style="background:{bg_status};color:{txt_status};padding:4px 12px;border-radius:8px;font-size:12px;font-weight:700;">{label_status}</span>''', unsafe_allow_html=True)
                    st.caption(f"Iniciada em: {iniciado}" + (f" | Finalizada em: {finalizado}" if finalizado else ""))
                    st.caption(f"Usuário: {rod.get('usuario','')}" + (f" | Credenciais: {rod.get('credenciais_usadas','')}" if rod.get('credenciais_usadas') else ""))
                    if rod.get("credenciais_com_erro"):
                        st.warning(f"⚠️ Credencial(is) que tiveram erro de autenticação durante esta rodada: {rod.get('credenciais_com_erro')}")
                        if rod.get("detalhe_erro_autenticacao"):
                            with st.expander("Ver detalhe técnico do erro"):
                                st.code(rod.get("detalhe_erro_autenticacao"))

                    resultados_rod = fgts_buscar_resultados(rid)

                    if not resultados_rod:
                        st.info("Nenhum resultado registrado ainda para esta rodada.")
                    else:
                        tempo_medio_hist = fgts_calcular_tempo_medio(resultados_rod)
                        col_h1, col_h2 = st.columns(2)
                        col_h1.metric("⏱️ Tempo médio por CPF", fgts_formatar_tempo(tempo_medio_hist) if tempo_medio_hist else "—")
                        if tempo_total_r:
                            col_h2.metric("🏁 Tempo total da rodada", fgts_formatar_tempo(tempo_total_r))
                        else:
                            col_h2.metric("🏁 Tempo total da rodada", "—")

                        df_res = pd.DataFrame(resultados_rod)

                        mapa_status_label = {
                            "success": "✅ Sucesso",
                            "fail": "❌ Falha",
                            "nao_autorizado": "🚫 Não autorizado",
                            "saldo_insuficiente": "⚠️ Saldo insuficiente",
                            "operacao_em_andamento": "🔄 Operação em andamento",
                            "erro_tecnico": "⚠️ Erro técnico",
                        }
                        df_res["status_label"] = df_res["status"].map(lambda s: mapa_status_label.get(s, s))

                        contagem = df_res["status_label"].value_counts()
                        cols_resumo = st.columns(min(len(contagem), 5) or 1)
                        for i, (lbl, qtd) in enumerate(contagem.items()):
                            cols_resumo[i % len(cols_resumo)].metric(lbl, qtd)

                        colunas_exibir = ["cpf","provider","status_label","saldo_disponivel","periodos","observacao","tempo_segundos","processado_em"]
                        colunas_exibir = [c for c in colunas_exibir if c in df_res.columns]
                        df_visao_fgts = df_res[colunas_exibir].rename(columns={
                            "cpf":"CPF","provider":"Provider","status_label":"Status",
                            "saldo_disponivel":"Saldo disponível","periodos":"Períodos",
                            "observacao":"Observação","tempo_segundos":"Tempo (s)","processado_em":"Processado em"
                        })
                        st.dataframe(df_visao_fgts, use_container_width=True, hide_index=True)

                        buf_fgts = io.BytesIO()
                        with pd.ExcelWriter(buf_fgts, engine="openpyxl") as writer:
                            df_visao_fgts.to_excel(writer, index=False, sheet_name="Resultados FGTS")
                        buf_fgts.seek(0)
                        st.download_button(
                            label="📥 Exportar resultado (Excel)",
                            data=buf_fgts,
                            file_name=f"fgts_rodada_{rid}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True,
                            key=f"export_fgts_{rid}"
                        )

    elif menu == "🏦 CLT Lote":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">CLT Lote — Consulta de Margem Soma BP2</span>', unsafe_allow_html=True)
        st.caption("Consulta margem/saldo em lote (produto privado CLT) via API Soma BP2.")

        with st.expander("🔑 Gerenciar credencial Soma BP2"):
            st.caption("Cadastre o Client ID/Secret gerados no painel da Soma. Só a credencial marcada como ativa é usada nas consultas.")

            with st.form("form_nova_credencial_soma", clear_on_submit=True):
                col_cs1, col_cs2, col_cs3 = st.columns([1.3, 1.8, 1.8])
                apelido_cred_soma = col_cs1.text_input("Apelido", placeholder="Ex: Principal")
                client_id_cred_soma = col_cs2.text_input("Client ID")
                client_secret_cred_soma = col_cs3.text_input("Client Secret", type="password")
                if st.form_submit_button("➕ Adicionar credencial", use_container_width=True):
                    if not client_id_cred_soma.strip() or not client_secret_cred_soma.strip():
                        st.error("Preencha Client ID e Client Secret.")
                    else:
                        supabase.table("soma_credenciais").insert({
                            "apelido": apelido_cred_soma.strip() or client_id_cred_soma.strip(),
                            "client_id": client_id_cred_soma.strip(),
                            "client_secret": client_secret_cred_soma.strip(),
                            "ativo": True,
                        }).execute()
                        st.success("Credencial adicionada e ativada!")
                        st.rerun()

            credenciais_soma_existentes = soma_buscar_credenciais()
            if not credenciais_soma_existentes:
                st.info("Nenhuma credencial cadastrada ainda. Adicione uma acima para poder consultar.")
            else:
                st.markdown("**Credenciais cadastradas:**")
                for cred_soma in credenciais_soma_existentes:
                    col_cv1, col_cv2, col_cv3 = st.columns([3, 1, 1])
                    with col_cv1:
                        status_ativo_soma = "🟢 Ativa" if cred_soma.get("ativo") else "⚪ Inativa"
                        st.markdown(f"**{cred_soma.get('apelido','')}** — `{cred_soma.get('client_id','')}` — {status_ativo_soma}")
                    with col_cv2:
                        if st.button("✅ Tornar ativa", key=f"ativar_cred_soma_{cred_soma['id']}", disabled=bool(cred_soma.get("ativo"))):
                            supabase.table("soma_credenciais").update({"ativo": False}).neq("id", cred_soma["id"]).execute()
                            supabase.table("soma_credenciais").update({"ativo": True}).eq("id", cred_soma["id"]).execute()
                            st.rerun()
                    with col_cv3:
                        if st.button("🗑️ Remover", key=f"del_cred_soma_{cred_soma['id']}"):
                            supabase.table("soma_credenciais").delete().eq("id", cred_soma["id"]).execute()
                            st.rerun()

        credencial_soma_ativa = soma_buscar_credencial_ativa()
        if not credencial_soma_ativa:
            st.warning("⚠️ Nenhuma credencial Soma BP2 ativa. Cadastre uma acima antes de iniciar consultas.")

        if "soma_lote_flags" not in st.session_state:
            st.session_state.soma_lote_flags = {}

        rodada_ativa_soma = soma_lote_buscar_rodada_ativa()
        rodadas_pausadas_soma = soma_lote_buscar_rodadas_pausadas()

        if rodada_ativa_soma:
            rid_s = rodada_ativa_soma["id"]
            status_rid_s = rodada_ativa_soma.get("status", "em_andamento")
            total_s = int(rodada_ativa_soma.get("total_cpfs") or 0)
            processados_s = int(rodada_ativa_soma.get("processados") or 0)
            pct_s = int((processados_s / total_s * 100)) if total_s > 0 else 0

            if status_rid_s == "pausando":
                st.warning(f"⏸️ Rodada #{rid_s} — pausando...")
            elif status_rid_s == "cancelando":
                st.warning(f"🛑 Rodada #{rid_s} — cancelando...")
            else:
                st.info(f"⏳ Rodada #{rid_s} em andamento — bancarizadora {rodada_ativa_soma.get('bancarizadora','')}")

            st.progress(min(pct_s, 100) / 100, text=f"{processados_s} de {total_s} — {pct_s}%")

            col_rs1, col_rs2, col_rs3 = st.columns([2, 1, 1])
            with col_rs1:
                st.caption("Você pode navegar para outras abas; a consulta continua em segundo plano.")
            with col_rs2:
                if st.button("⏸️ Pausar", use_container_width=True, key=f"pausar_soma_{rid_s}", disabled=(status_rid_s != "em_andamento")):
                    flag_s = st.session_state.soma_lote_flags.get(rid_s)
                    if flag_s is not None:
                        flag_s["parar"] = "pausar"
                    supabase.table("soma_lote_rodadas").update({"status": "pausando"}).eq("id", rid_s).execute()
                    time.sleep(1)
                    st.rerun()
            with col_rs3:
                if st.button("🛑 Cancelar", use_container_width=True, key=f"cancelar_soma_{rid_s}", disabled=(status_rid_s != "em_andamento")):
                    flag_s = st.session_state.soma_lote_flags.get(rid_s)
                    if flag_s is not None:
                        flag_s["parar"] = "cancelar"
                    supabase.table("soma_lote_rodadas").update({"status": "cancelando"}).eq("id", rid_s).execute()
                    time.sleep(1)
                    st.rerun()

            if st.button("🔄 Atualizar progresso", use_container_width=True, key=f"refresh_soma_{rid_s}"):
                st.rerun()

            st.caption("Se Pausar/Cancelar não fizer efeito (ex: app reiniciou), force pelo botão abaixo.")
            if st.button("⚠️ Forçar parada (rodada travada)", key=f"forcar_soma_{rid_s}"):
                supabase.table("soma_lote_rodadas").update({"status": "pausada"}).eq("id", rid_s).execute()
                st.success("Rodada marcada como pausada.")
                time.sleep(1)
                st.rerun()

        elif rodadas_pausadas_soma:
            st.markdown("### ⏸️ Rodadas pausadas")
            for rod_p_s in rodadas_pausadas_soma:
                rid_p_s = rod_p_s["id"]
                total_p_s = int(rod_p_s.get("total_cpfs") or 0)
                proc_p_s = int(rod_p_s.get("processados") or 0)
                pct_p_s = int((proc_p_s / total_p_s * 100)) if total_p_s > 0 else 0

                with st.container(border=True):
                    st.markdown(f"**Rodada #{rid_p_s}** — pausada com {proc_p_s}/{total_p_s} CPF(s) processados ({pct_p_s}%)")
                    resultados_parciais_s = soma_lote_buscar_resultados(rid_p_s)

                    col_ps1, col_ps2, col_ps3 = st.columns([1.3, 1.3, 1])
                    with col_ps1:
                        if st.button("▶️ Retomar rodada", use_container_width=True, key=f"retomar_soma_{rid_p_s}"):
                            cpfs_lista_str_s = rod_p_s.get("cpfs_lista") or ""
                            try:
                                cpfs_originais_s = _json_soma.loads(cpfs_lista_str_s) if cpfs_lista_str_s else []
                            except Exception:
                                cpfs_originais_s = []
                            if not cpfs_originais_s:
                                st.error("Não encontrei a lista original de CPFs desta rodada.")
                            else:
                                flag_s = {"parar": False}
                                st.session_state.soma_lote_flags[rid_p_s] = flag_s
                                supabase.table("soma_lote_rodadas").update({
                                    "status": "em_andamento",
                                    "ultimo_processamento_em": str(datetime.now()),
                                }).eq("id", rid_p_s).execute()
                                soma_lote_iniciar_threads(cpfs_originais_s, rid_p_s, rod_p_s.get("bancarizadora", "UY3"), flag_s)
                                st.success(f"Rodada #{rid_p_s} retomada!")
                                time.sleep(1)
                                st.rerun()
                    with col_ps2:
                        if resultados_parciais_s:
                            st.caption(f"{len(resultados_parciais_s)} resultado(s) disponível(eis) para exportar abaixo ⬇️")
                        else:
                            st.caption("Nenhum resultado salvo ainda.")
                    with col_ps3:
                        confirmar_descarte_s = st.checkbox("Confirmo", key=f"confirma_descarte_soma_{rid_p_s}")
                        if st.button("🗑️ Descartar", use_container_width=True, key=f"descartar_soma_{rid_p_s}", disabled=not confirmar_descarte_s):
                            supabase.table("soma_lote_rodadas").update({
                                "status": "cancelada", "finalizado_em": str(datetime.now()),
                            }).eq("id", rid_p_s).execute()
                            st.success(f"Rodada #{rid_p_s} descartada.")
                            time.sleep(1)
                            st.rerun()

                    if resultados_parciais_s:
                        with st.expander(f"📋 Ver/exportar resultados parciais da rodada #{rid_p_s}"):
                            df_parcial_s = pd.DataFrame(resultados_parciais_s)
                            st.dataframe(df_parcial_s, use_container_width=True, hide_index=True)
                            buf_parcial_s = io.BytesIO()
                            with pd.ExcelWriter(buf_parcial_s, engine="openpyxl") as writer:
                                df_parcial_s.drop(columns=["resposta_completa"], errors="ignore").to_excel(writer, index=False, sheet_name="Resultados")
                            buf_parcial_s.seek(0)
                            st.download_button("📥 Exportar resultado (Excel)", data=buf_parcial_s,
                                file_name=f"soma_clt_lote_{rid_p_s}_parcial.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                use_container_width=True, key=f"export_parcial_soma_{rid_p_s}")

            st.divider()
            if st.button("➕ Iniciar nova rodada (sem retomar)", use_container_width=True, key="soma_forcar_nova"):
                st.session_state["soma_lote_forcar_nova"] = True
                st.rerun()

        if not rodada_ativa_soma and (not rodadas_pausadas_soma or st.session_state.get("soma_lote_forcar_nova")):
            st.markdown("### ▶️ Nova consulta em lote")

            bancarizadora_nova_s = st.selectbox("Bancarizadora", ["UY3", "CELCOIN"], key="soma_bancarizadora_nova")

            st.caption("A Soma exige nome e celular junto com o CPF (mínimo 3 caracteres no nome, 10 dígitos no celular).")

            modo_entrada_soma = st.radio(
                "Como deseja informar os dados?",
                ["Subir arquivo .csv", "Colar lista"],
                horizontal=True, key="soma_modo_entrada"
            )

            cpfs_soma_processar = []
            linhas_com_erro_soma = []

            if modo_entrada_soma == "Subir arquivo .csv":
                st.caption("O arquivo precisa ter colunas de CPF, nome e celular (os nomes das colunas podem variar, ex: 'cpf', 'nome', 'celular'/'telefone').")
                arquivo_csv_soma = st.file_uploader("Selecione o arquivo .csv", type=["csv"], key="soma_upload_csv")

                if arquivo_csv_soma is not None:
                    try:
                        df_up_soma = pd.read_csv(arquivo_csv_soma, dtype=str, sep=None, engine="python")
                        df_up_soma.columns = [str(c).strip().lower() for c in df_up_soma.columns]

                        col_cpf_soma = next((c for c in ["cpf", "documento", "documentnumber"] if c in df_up_soma.columns), None)
                        col_nome_soma = next((c for c in ["nome", "cliente", "name"] if c in df_up_soma.columns), None)
                        col_celular_soma = next((c for c in ["celular", "telefone", "phone", "fone"] if c in df_up_soma.columns), None)

                        faltando = [nome_col for nome_col, val in
                                    [("CPF", col_cpf_soma), ("nome", col_nome_soma), ("celular", col_celular_soma)]
                                    if val is None]

                        if faltando:
                            st.error(f"Não encontrei coluna(s) de {', '.join(faltando)} no arquivo. Colunas disponíveis: {list(df_up_soma.columns)}")
                        else:
                            for num_linha, row in df_up_soma.reset_index().iterrows():
                                cpf_l = limpar_documento(row.get(col_cpf_soma, ""))
                                nome_l = str(row.get(col_nome_soma, "") or "").strip()
                                celular_l = limpar_documento(row.get(col_celular_soma, ""))

                                if len(cpf_l) != 11:
                                    linhas_com_erro_soma.append(f"Linha {num_linha + 2}: CPF inválido ({cpf_l})")
                                    continue
                                if len(nome_l) < 3:
                                    linhas_com_erro_soma.append(f"Linha {num_linha + 2}: nome muito curto")
                                    continue
                                if len(celular_l) < 10:
                                    linhas_com_erro_soma.append(f"Linha {num_linha + 2}: celular deve ter no mínimo 10 dígitos")
                                    continue
                                cpfs_soma_processar.append({"cpf": cpf_l, "nome": nome_l, "celular": celular_l})
                    except Exception as e:
                        st.error(f"Erro ao ler o arquivo: {e}")
            else:
                texto_cpfs_soma = st.text_area(
                    "Cole um por linha, no formato CPF;NOME;CELULAR", height=180,
                    placeholder="12345678900;JOAO DA SILVA;11999999999\n98765432100;MARIA SOUZA;21988887777\n...",
                    key="soma_texto_cpfs"
                )

                if texto_cpfs_soma.strip():
                    for num_linha, linha in enumerate(texto_cpfs_soma.splitlines(), start=1):
                        linha = linha.strip()
                        if not linha:
                            continue
                        partes = linha.split(";")
                        if len(partes) < 3:
                            linhas_com_erro_soma.append(f"Linha {num_linha}: faltam campos (esperado CPF;NOME;CELULAR)")
                            continue
                        cpf_l, nome_l, celular_l = partes[0].strip(), partes[1].strip(), partes[2].strip()
                        cpf_l = limpar_documento(cpf_l)
                        celular_l = limpar_documento(celular_l)
                        if len(cpf_l) != 11:
                            linhas_com_erro_soma.append(f"Linha {num_linha}: CPF inválido ({cpf_l})")
                            continue
                        if len(nome_l) < 3:
                            linhas_com_erro_soma.append(f"Linha {num_linha}: nome muito curto")
                            continue
                        if len(celular_l) < 10:
                            linhas_com_erro_soma.append(f"Linha {num_linha}: celular deve ter no mínimo 10 dígitos")
                            continue
                        cpfs_soma_processar.append({"cpf": cpf_l, "nome": nome_l, "celular": celular_l})

            # remove duplicados por CPF mantendo a primeira ocorrência
            vistos_cpf_soma = set()
            cpfs_soma_processar_dedup = []
            for reg in cpfs_soma_processar:
                if reg["cpf"] not in vistos_cpf_soma:
                    vistos_cpf_soma.add(reg["cpf"])
                    cpfs_soma_processar_dedup.append(reg)
            cpfs_soma_processar = cpfs_soma_processar_dedup

            if linhas_com_erro_soma:
                st.error("Corrija essas linhas antes de continuar:\n" + "\n".join(linhas_com_erro_soma))

            if cpfs_soma_processar:
                st.success(f"✅ {len(cpfs_soma_processar)} registro(s) válido(s) detectado(s).")

            if st.button("🚀 Iniciar Consulta em Lote", use_container_width=True,
                         disabled=(len(cpfs_soma_processar) == 0 or not credencial_soma_ativa or bool(linhas_com_erro_soma))):
                try:
                    nova_rodada_soma = supabase.table("soma_lote_rodadas").insert({
                        "total_cpfs": len(cpfs_soma_processar),
                        "processados": 0,
                        "status": "em_andamento",
                        "bancarizadora": bancarizadora_nova_s,
                        "usuario": st.session_state.get("nome", st.session_state.get("usuario", "")),
                        "cpfs_lista": _json_soma.dumps(cpfs_soma_processar),
                        "ultimo_processamento_em": str(datetime.now()),
                    }).execute()
                    rodada_id_nova_soma = nova_rodada_soma.data[0]["id"]

                    flag_nova_s = {"parar": False}
                    st.session_state.soma_lote_flags[rodada_id_nova_soma] = flag_nova_s
                    soma_lote_iniciar_threads(cpfs_soma_processar, rodada_id_nova_soma, bancarizadora_nova_s, flag_nova_s)

                    st.session_state["soma_lote_forcar_nova"] = False
                    st.success(f"Rodada #{rodada_id_nova_soma} iniciada! Processando {len(cpfs_soma_processar)} CPF(s).")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao iniciar rodada: {e}")

        st.divider()
        st.markdown("### 🕓 Histórico de rodadas")
        historico_soma = soma_lote_buscar_historico(15)

        if not historico_soma:
            st.info("Nenhuma rodada de consulta realizada ainda.")
        else:
            badges_status_soma = {
                "em_andamento": ("⏳ Em andamento", "#fef9c3", "#92400e"),
                "pausando": ("⏸️ Pausando...", "#fef3c7", "#92400e"),
                "pausada": ("⏸️ Pausada", "#e0f2fe", "#075985"),
                "cancelando": ("🛑 Cancelando...", "#fee2e2", "#991b1b"),
                "concluida": ("✅ Concluída", "#dcfce7", "#166534"),
                "cancelada": ("🛑 Cancelada", "#fee2e2", "#991b1b"),
            }
            for rod_s in historico_soma:
                rid_h_s = rod_s["id"]
                status_rod_s = rod_s.get("status", "em_andamento")
                label_status_s, bg_status_s, txt_status_s = badges_status_soma.get(status_rod_s, (status_rod_s, "#f1f5f9", "#64748b"))
                total_r_s = int(rod_s.get("total_cpfs") or 0)
                proc_r_s = int(rod_s.get("processados") or 0)
                iniciado_s = str(rod_s.get("iniciado_em", ""))[:16]

                with st.expander(f"Rodada #{rid_h_s} — {iniciado_s} — {proc_r_s}/{total_r_s} CPF(s) — {label_status_s} — {rod_s.get('bancarizadora','')}"):
                    st.markdown(f'''<span style="background:{bg_status_s};color:{txt_status_s};padding:4px 12px;border-radius:8px;font-size:12px;font-weight:700;">{label_status_s}</span>''', unsafe_allow_html=True)
                    st.caption(f"Usuário: {rod_s.get('usuario','')} | Bancarizadora: {rod_s.get('bancarizadora','')}")

                    resultados_rod_s = soma_lote_buscar_resultados(rid_h_s)
                    if not resultados_rod_s:
                        st.info("Nenhum resultado registrado ainda para esta rodada.")
                    else:
                        df_res_s = pd.DataFrame(resultados_rod_s)
                        colunas_exibir_s = ["cpf", "bancarizadora", "status", "status_soma", "margem_disponivel", "margem_bruta", "salario_bruto", "salario_liquido", "empregador", "mensagem", "tempo_segundos"]
                        colunas_exibir_s = [c for c in colunas_exibir_s if c in df_res_s.columns]
                        df_visao_s = df_res_s[colunas_exibir_s].rename(columns={
                            "cpf": "CPF", "bancarizadora": "Bancarizadora", "status": "Status",
                            "status_soma": "Status Soma", "margem_disponivel": "Margem Disponível",
                            "margem_bruta": "Margem Bruta", "salario_bruto": "Salário Bruto",
                            "salario_liquido": "Salário Líquido", "empregador": "Empregador",
                            "mensagem": "Mensagem", "tempo_segundos": "Tempo (s)"
                        })
                        st.dataframe(df_visao_s, use_container_width=True, hide_index=True)

                        buf_hist_s = io.BytesIO()
                        with pd.ExcelWriter(buf_hist_s, engine="openpyxl") as writer:
                            df_visao_s.to_excel(writer, index=False, sheet_name="Resultados")
                        buf_hist_s.seek(0)
                        st.download_button(
                            label="📥 Exportar resultado (Excel)", data=buf_hist_s,
                            file_name=f"soma_clt_lote_{rid_h_s}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"export_soma_{rid_h_s}"
                        )

    elif menu == "🌐 CLT Multi-Bancos":
        st.markdown('<span style="font-size:20px;font-weight:900;color:#0f172a;font-family:Orbitron,sans-serif;">CLT Multi-Bancos — Consulta simultânea</span>', unsafe_allow_html=True)
        st.caption("Consulta margem/saldo em vários bancos de uma vez (Soma BP2 e V8 Digital), para o produto privado CLT.")

        with st.expander("🔑 Gerenciar credencial V8 (Crédito Privado CLT)"):
            st.caption("Login e senha da sua conta V8 Digital (mesmo sistema do FGTS, mas essa credencial fica separada para o produto CLT).")

            with st.form("form_nova_credencial_v8_clt", clear_on_submit=True):
                col_v8c1, col_v8c2, col_v8c3 = st.columns([1.3, 1.8, 1.8])
                apelido_cred_v8c = col_v8c1.text_input("Apelido", placeholder="Ex: Principal", key="apelido_v8clt")
                usuario_cred_v8c = col_v8c2.text_input("E-mail (login V8)", key="usuario_v8clt")
                senha_cred_v8c = col_v8c3.text_input("Senha (login V8)", type="password", key="senha_v8clt")
                if st.form_submit_button("➕ Adicionar credencial", use_container_width=True):
                    if not usuario_cred_v8c.strip() or not senha_cred_v8c.strip():
                        st.error("Preencha e-mail e senha.")
                    else:
                        supabase.table("v8_clt_credenciais").insert({
                            "apelido": apelido_cred_v8c.strip() or usuario_cred_v8c.strip(),
                            "username": usuario_cred_v8c.strip(),
                            "password": senha_cred_v8c,
                            "ativo": True,
                        }).execute()
                        st.success("Credencial adicionada e ativada!")
                        st.rerun()

            credenciais_v8clt_existentes = v8_clt_buscar_credenciais()
            if not credenciais_v8clt_existentes:
                st.info("Nenhuma credencial V8 (CLT) cadastrada ainda.")
            else:
                st.markdown("**Credenciais cadastradas:**")
                for cred_v8c in credenciais_v8clt_existentes:
                    col_v8v1, col_v8v2, col_v8v3 = st.columns([3, 1, 1])
                    with col_v8v1:
                        status_ativo_v8c = "🟢 Ativa" if cred_v8c.get("ativo") else "⚪ Inativa"
                        st.markdown(f"**{cred_v8c.get('apelido','')}** — {cred_v8c.get('username','')} — {status_ativo_v8c}")
                    with col_v8v2:
                        if st.button("✅ Tornar ativa", key=f"ativar_v8clt_{cred_v8c['id']}", disabled=bool(cred_v8c.get("ativo"))):
                            supabase.table("v8_clt_credenciais").update({"ativo": False}).neq("id", cred_v8c["id"]).execute()
                            supabase.table("v8_clt_credenciais").update({"ativo": True}).eq("id", cred_v8c["id"]).execute()
                            st.rerun()
                    with col_v8v3:
                        if st.button("🗑️ Remover", key=f"del_v8clt_{cred_v8c['id']}"):
                            supabase.table("v8_clt_credenciais").delete().eq("id", cred_v8c["id"]).execute()
                            st.rerun()

        st.caption("A credencial da Soma continua sendo gerenciada na aba '🏦 CLT Lote'.")

        credencial_soma_ativa_mb = soma_buscar_credencial_ativa()
        credencial_v8clt_ativa = v8_clt_buscar_credencial_ativa()

        col_status1, col_status2 = st.columns(2)
        col_status1.markdown("🟢 Soma: credencial ativa" if credencial_soma_ativa_mb else "🔴 Soma: sem credencial ativa")
        col_status2.markdown("🟢 V8: credencial ativa" if credencial_v8clt_ativa else "🔴 V8: sem credencial ativa")

        if "clt_mb_flags" not in st.session_state:
            st.session_state.clt_mb_flags = {}

        rodada_ativa_mb = clt_mb_buscar_rodada_ativa()
        rodadas_pausadas_mb = clt_mb_buscar_rodadas_pausadas()

        if rodada_ativa_mb:
            rid_mb = rodada_ativa_mb["id"]
            status_rid_mb = rodada_ativa_mb.get("status", "em_andamento")
            total_mb = int(rodada_ativa_mb.get("total_cpfs") or 0)
            processados_mb = int(rodada_ativa_mb.get("processados") or 0)
            pct_mb = int((processados_mb / total_mb * 100)) if total_mb > 0 else 0

            if status_rid_mb == "pausando":
                st.warning(f"⏸️ Rodada #{rid_mb} — pausando...")
            elif status_rid_mb == "cancelando":
                st.warning(f"🛑 Rodada #{rid_mb} — cancelando...")
            else:
                st.info(f"⏳ Rodada #{rid_mb} em andamento — bancos: {rodada_ativa_mb.get('bancos','')}")

            st.progress(min(pct_mb, 100) / 100, text=f"{processados_mb} de {total_mb} — {pct_mb}% (cada CPF conta 1x por banco consultado)")

            col_rmb1, col_rmb2, col_rmb3 = st.columns([2, 1, 1])
            with col_rmb1:
                st.caption("Você pode navegar para outras abas; a consulta continua em segundo plano.")
            with col_rmb2:
                if st.button("⏸️ Pausar", use_container_width=True, key=f"pausar_mb_{rid_mb}", disabled=(status_rid_mb != "em_andamento")):
                    flag_mb = st.session_state.clt_mb_flags.get(rid_mb)
                    if flag_mb is not None:
                        flag_mb["parar"] = "pausar"
                    supabase.table("clt_multibanco_rodadas").update({"status": "pausando"}).eq("id", rid_mb).execute()
                    time.sleep(1)
                    st.rerun()
            with col_rmb3:
                if st.button("🛑 Cancelar", use_container_width=True, key=f"cancelar_mb_{rid_mb}", disabled=(status_rid_mb != "em_andamento")):
                    flag_mb = st.session_state.clt_mb_flags.get(rid_mb)
                    if flag_mb is not None:
                        flag_mb["parar"] = "cancelar"
                    supabase.table("clt_multibanco_rodadas").update({"status": "cancelando"}).eq("id", rid_mb).execute()
                    time.sleep(1)
                    st.rerun()

            if st.button("🔄 Atualizar progresso", use_container_width=True, key=f"refresh_mb_{rid_mb}"):
                st.rerun()

            st.caption("Se Pausar/Cancelar não fizer efeito (ex: app reiniciou), force pelo botão abaixo.")
            if st.button("⚠️ Forçar parada (rodada travada)", key=f"forcar_mb_{rid_mb}"):
                supabase.table("clt_multibanco_rodadas").update({"status": "pausada"}).eq("id", rid_mb).execute()
                st.success("Rodada marcada como pausada.")
                time.sleep(1)
                st.rerun()

        elif rodadas_pausadas_mb:
            st.markdown("### ⏸️ Rodadas pausadas")
            for rod_p_mb in rodadas_pausadas_mb:
                rid_p_mb = rod_p_mb["id"]
                total_p_mb = int(rod_p_mb.get("total_cpfs") or 0)
                proc_p_mb = int(rod_p_mb.get("processados") or 0)
                pct_p_mb = int((proc_p_mb / total_p_mb * 100)) if total_p_mb > 0 else 0

                with st.container(border=True):
                    st.markdown(f"**Rodada #{rid_p_mb}** — pausada com {proc_p_mb}/{total_p_mb} ({pct_p_mb}%) — bancos: {rod_p_mb.get('bancos','')}")
                    resultados_parciais_mb = clt_mb_buscar_resultados(rid_p_mb)

                    col_pmb1, col_pmb2, col_pmb3 = st.columns([1.3, 1.3, 1])
                    with col_pmb1:
                        if st.button("▶️ Retomar rodada", use_container_width=True, key=f"retomar_mb_{rid_p_mb}"):
                            registros_str_mb = rod_p_mb.get("registros_lista") or ""
                            try:
                                registros_originais_mb = _json_soma.loads(registros_str_mb) if registros_str_mb else []
                            except Exception:
                                registros_originais_mb = []
                            bancos_originais_mb = [b for b in (rod_p_mb.get("bancos") or "").split(",") if b]
                            if not registros_originais_mb or not bancos_originais_mb:
                                st.error("Não encontrei os dados originais desta rodada.")
                            else:
                                flag_mb_novo = {"parar": False}
                                st.session_state.clt_mb_flags[rid_p_mb] = flag_mb_novo
                                supabase.table("clt_multibanco_rodadas").update({
                                    "status": "em_andamento",
                                    "ultimo_processamento_em": str(datetime.now()),
                                }).eq("id", rid_p_mb).execute()
                                clt_mb_iniciar_threads(registros_originais_mb, rid_p_mb, bancos_originais_mb, flag_mb_novo)
                                st.success(f"Rodada #{rid_p_mb} retomada!")
                                time.sleep(1)
                                st.rerun()
                    with col_pmb2:
                        if resultados_parciais_mb:
                            st.caption(f"{len(resultados_parciais_mb)} resultado(s) disponível(eis) para exportar abaixo ⬇️")
                        else:
                            st.caption("Nenhum resultado salvo ainda.")
                    with col_pmb3:
                        confirmar_descarte_mb = st.checkbox("Confirmo", key=f"confirma_descarte_mb_{rid_p_mb}")
                        if st.button("🗑️ Descartar", use_container_width=True, key=f"descartar_mb_{rid_p_mb}", disabled=not confirmar_descarte_mb):
                            supabase.table("clt_multibanco_rodadas").update({
                                "status": "cancelada", "finalizado_em": str(datetime.now()),
                            }).eq("id", rid_p_mb).execute()
                            st.success(f"Rodada #{rid_p_mb} descartada.")
                            time.sleep(1)
                            st.rerun()

                    if resultados_parciais_mb:
                        with st.expander(f"📋 Ver/exportar resultados parciais da rodada #{rid_p_mb}"):
                            df_parcial_mb = pd.DataFrame(resultados_parciais_mb)
                            st.dataframe(df_parcial_mb, use_container_width=True, hide_index=True)

            st.divider()
            if st.button("➕ Iniciar nova rodada (sem retomar)", use_container_width=True, key="mb_forcar_nova"):
                st.session_state["clt_mb_forcar_nova"] = True
                st.rerun()

        if not rodada_ativa_mb and (not rodadas_pausadas_mb or st.session_state.get("clt_mb_forcar_nova")):
            st.markdown("### ▶️ Nova consulta multi-bancos")

            bancos_selecionados_mb = st.multiselect(
                "Quais bancos consultar?", ["SOMA", "V8"], default=["SOMA", "V8"], key="mb_bancos_selecionados"
            )

            inferir_genero_mb = False
            if "V8" in bancos_selecionados_mb:
                inferir_genero_mb = st.checkbox(
                    "🤖 Inferir gênero automaticamente pelo primeiro nome quando a coluna 'genero' estiver vazia (estimativa, não garantida)",
                    value=False, key="mb_inferir_genero"
                )

            st.caption(
                "CSV único com colunas: cpf, nome, celular (sempre obrigatórias). "
                "genero ('male' ou 'female') é obrigatório se a V8 estiver selecionada — "
                "marque a opção acima para tentar preencher automaticamente quando faltar. "
                "data_nascimento e email são opcionais — se a V8 exigir algum deles, o erro aparece na coluna Mensagem."
            )

            arquivo_csv_mb = st.file_uploader("Selecione o arquivo .csv", type=["csv"], key="mb_upload_csv")

            registros_mb_processar = []
            linhas_com_erro_mb = []

            if arquivo_csv_mb is not None:
                try:
                    df_up_mb = pd.read_csv(arquivo_csv_mb, dtype=str, sep=None, engine="python")
                    df_up_mb.columns = [str(c).strip().lower() for c in df_up_mb.columns]

                    col_cpf_mb = next((c for c in ["cpf", "documento", "documentnumber"] if c in df_up_mb.columns), None)
                    col_nome_mb = next((c for c in ["nome", "cliente", "name"] if c in df_up_mb.columns), None)
                    col_celular_mb = next((c for c in ["celular", "telefone", "phone", "fone"] if c in df_up_mb.columns), None)
                    col_datanasc_mb = next((c for c in ["data_nascimento", "datanascimento", "nascimento"] if c in df_up_mb.columns), None)
                    col_genero_mb = next((c for c in ["genero", "gênero", "sexo"] if c in df_up_mb.columns), None)
                    col_email_mb = next((c for c in ["email", "e-mail"] if c in df_up_mb.columns), None)

                    faltando_mb = [n for n, v in [("CPF", col_cpf_mb), ("nome", col_nome_mb), ("celular", col_celular_mb)] if v is None]
                    precisa_genero_v8_mb = "V8" in bancos_selecionados_mb
                    if precisa_genero_v8_mb and col_genero_mb is None and not inferir_genero_mb:
                        faltando_mb.append("genero")

                    if faltando_mb:
                        st.error(f"Não encontrei coluna(s) de {', '.join(faltando_mb)} no arquivo. Colunas disponíveis: {list(df_up_mb.columns)}")
                        if precisa_genero_v8_mb and "genero" in faltando_mb:
                            st.caption("A V8 exige o campo 'genero' ('male' ou 'female') — sem ele, a consulta na V8 falha com erro de validação. Marque a opção de inferir automaticamente acima, ou adicione a coluna.")
                    else:
                        qtd_genero_inferido_mb = 0
                        for num_linha, row in df_up_mb.reset_index().iterrows():
                            cpf_l = limpar_documento(row.get(col_cpf_mb, ""))
                            nome_l = str(row.get(col_nome_mb, "") or "").strip()
                            celular_l = limpar_documento(row.get(col_celular_mb, ""))
                            data_nasc_l = str(row.get(col_datanasc_mb, "") or "").strip() if col_datanasc_mb else ""
                            genero_l = str(row.get(col_genero_mb, "") or "").strip().lower() if col_genero_mb else ""
                            email_l = str(row.get(col_email_mb, "") or "").strip() if col_email_mb else ""

                            if len(cpf_l) != 11:
                                linhas_com_erro_mb.append(f"Linha {num_linha + 2}: CPF inválido ({cpf_l})")
                                continue
                            if len(nome_l) < 3:
                                linhas_com_erro_mb.append(f"Linha {num_linha + 2}: nome muito curto")
                                continue
                            if len(celular_l) < 10:
                                linhas_com_erro_mb.append(f"Linha {num_linha + 2}: celular deve ter no mínimo 10 dígitos")
                                continue

                            if precisa_genero_v8_mb and genero_l not in ("male", "female"):
                                if inferir_genero_mb:
                                    genero_l = inferir_genero_por_nome(nome_l)
                                    qtd_genero_inferido_mb += 1
                                if genero_l not in ("male", "female"):
                                    linhas_com_erro_mb.append(f"Linha {num_linha + 2}: genero deve ser 'male' ou 'female' (obrigatório para V8)")
                                    continue

                            registros_mb_processar.append({
                                "cpf": cpf_l, "nome": nome_l, "celular": celular_l,
                                "data_nascimento": data_nasc_l, "genero": genero_l, "email": email_l,
                            })
                except Exception as e:
                    st.error(f"Erro ao ler o arquivo: {e}")

            if linhas_com_erro_mb:
                st.error("Corrija essas linhas antes de continuar:\n" + "\n".join(linhas_com_erro_mb))

            if registros_mb_processar:
                st.success(f"✅ {len(registros_mb_processar)} registro(s) válido(s) — {len(registros_mb_processar) * max(len(bancos_selecionados_mb),1)} consulta(s) no total.")
                if inferir_genero_mb and qtd_genero_inferido_mb > 0:
                    st.info(f"🤖 {qtd_genero_inferido_mb} registro(s) tiveram o gênero estimado automaticamente pelo nome (não é garantido — revise se for crítico).")

            credenciais_ok_mb = (
                ("SOMA" not in bancos_selecionados_mb or credencial_soma_ativa_mb) and
                ("V8" not in bancos_selecionados_mb or credencial_v8clt_ativa)
            )
            if not credenciais_ok_mb:
                st.warning("⚠️ Cadastre a(s) credencial(is) dos bancos selecionados antes de iniciar.")

            if st.button("🚀 Iniciar Consulta Multi-Bancos", use_container_width=True,
                         disabled=(len(registros_mb_processar) == 0 or len(bancos_selecionados_mb) == 0
                                   or bool(linhas_com_erro_mb) or not credenciais_ok_mb)):
                try:
                    nova_rodada_mb = supabase.table("clt_multibanco_rodadas").insert({
                        "total_cpfs": len(registros_mb_processar) * len(bancos_selecionados_mb),
                        "processados": 0,
                        "status": "em_andamento",
                        "bancos": ",".join(bancos_selecionados_mb),
                        "usuario": st.session_state.get("nome", st.session_state.get("usuario", "")),
                        "registros_lista": _json_soma.dumps(registros_mb_processar),
                        "ultimo_processamento_em": str(datetime.now()),
                    }).execute()
                    rodada_id_nova_mb = nova_rodada_mb.data[0]["id"]

                    flag_nova_mb = {"parar": False}
                    st.session_state.clt_mb_flags[rodada_id_nova_mb] = flag_nova_mb
                    clt_mb_iniciar_threads(registros_mb_processar, rodada_id_nova_mb, bancos_selecionados_mb, flag_nova_mb)

                    st.session_state["clt_mb_forcar_nova"] = False
                    st.success(f"Rodada #{rodada_id_nova_mb} iniciada!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao iniciar rodada: {e}")

        st.divider()
        st.markdown("### 🕓 Histórico de rodadas")
        historico_mb = clt_mb_buscar_historico(15)

        if not historico_mb:
            st.info("Nenhuma rodada de consulta realizada ainda.")
        else:
            badges_status_mb = {
                "em_andamento": ("⏳ Em andamento", "#fef9c3", "#92400e"),
                "pausando": ("⏸️ Pausando...", "#fef3c7", "#92400e"),
                "pausada": ("⏸️ Pausada", "#e0f2fe", "#075985"),
                "cancelando": ("🛑 Cancelando...", "#fee2e2", "#991b1b"),
                "concluida": ("✅ Concluída", "#dcfce7", "#166534"),
                "cancelada": ("🛑 Cancelada", "#fee2e2", "#991b1b"),
            }
            for rod_mb in historico_mb:
                rid_h_mb = rod_mb["id"]
                status_rod_mb = rod_mb.get("status", "em_andamento")
                label_status_mb, bg_status_mb, txt_status_mb = badges_status_mb.get(status_rod_mb, (status_rod_mb, "#f1f5f9", "#64748b"))
                total_r_mb = int(rod_mb.get("total_cpfs") or 0)
                proc_r_mb = int(rod_mb.get("processados") or 0)
                iniciado_mb = str(rod_mb.get("iniciado_em", ""))[:16]

                with st.expander(f"Rodada #{rid_h_mb} — {iniciado_mb} — {proc_r_mb}/{total_r_mb} — {label_status_mb} — {rod_mb.get('bancos','')}"):
                    st.markdown(f'''<span style="background:{bg_status_mb};color:{txt_status_mb};padding:4px 12px;border-radius:8px;font-size:12px;font-weight:700;">{label_status_mb}</span>''', unsafe_allow_html=True)
                    st.caption(f"Usuário: {rod_mb.get('usuario','')} | Bancos: {rod_mb.get('bancos','')}")

                    resultados_rod_mb = clt_mb_buscar_resultados(rid_h_mb)
                    if not resultados_rod_mb:
                        st.info("Nenhum resultado registrado ainda para esta rodada.")
                    else:
                        df_res_mb = pd.DataFrame(resultados_rod_mb)

                        # ── Uma linha por CPF, colunas de Status e Margem por banco ──
                        try:
                            bancos_presentes_mb = sorted(df_res_mb["banco"].dropna().unique().tolist())
                            df_wide_mb = df_res_mb[["cpf", "nome"]].drop_duplicates(subset=["cpf"]) if "nome" in df_res_mb.columns else df_res_mb[["cpf"]].drop_duplicates()
                            df_wide_mb = df_wide_mb.rename(columns={"cpf": "CPF"})

                            for banco_col in bancos_presentes_mb:
                                sub = df_res_mb[df_res_mb["banco"] == banco_col].set_index("cpf")
                                df_wide_mb[f"{banco_col} - Status"] = df_wide_mb["CPF"].map(sub["status"])
                                if "margem_disponivel" in sub.columns:
                                    df_wide_mb[f"{banco_col} - Margem"] = df_wide_mb["CPF"].map(sub["margem_disponivel"])

                            st.dataframe(df_wide_mb, use_container_width=True, hide_index=True)
                        except Exception as e_pivot:
                            st.caption(f"Não consegui montar a tabela por banco ({e_pivot}) — veja o detalhado abaixo.")

                        with st.expander("📋 Ver detalhado (com mensagens de erro)"):
                            colunas_exibir_mb = ["cpf", "banco", "status", "margem_disponivel", "mensagem", "tempo_segundos"]
                            colunas_exibir_mb = [c for c in colunas_exibir_mb if c in df_res_mb.columns]
                            df_visao_mb = df_res_mb[colunas_exibir_mb].rename(columns={
                                "cpf": "CPF", "banco": "Banco", "status": "Status",
                                "margem_disponivel": "Margem Disponível", "mensagem": "Mensagem",
                                "tempo_segundos": "Tempo (s)"
                            })
                            st.dataframe(df_visao_mb, use_container_width=True, hide_index=True)

                        buf_hist_mb = io.BytesIO()
                        with pd.ExcelWriter(buf_hist_mb, engine="openpyxl") as writer:
                            df_wide_mb.to_excel(writer, index=False, sheet_name="Resumo por CPF")
                            df_visao_mb.to_excel(writer, index=False, sheet_name="Detalhado")
                        buf_hist_mb.seek(0)
                        st.download_button(
                            label="📥 Exportar resultado (Excel)", data=buf_hist_mb,
                            file_name=f"clt_multibanco_{rid_h_mb}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key=f"export_mb_{rid_h_mb}"
                        )
