"""Crea-MS · DFI — Planejamento de Viagens de Fiscalização 2027.

Execute com:  streamlit run app.py
"""

from __future__ import annotations

import os
import re
import unicodedata
from datetime import date, datetime, timedelta

import streamlit as st

from dados_fiscalizacao import (
    AGENTES,
    ATIVIDADES,
    ATIVIDADES_PADRAO,
    MICRORREGIOES_2027,
    MUNICIPIOS_MS,
)
from pdf_generator import agora_ms, fmt_data, gerar_pdf, localizar_logo

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = localizar_logo()  # logo_crea_ms.png/.jpg na raiz; None -> cabeçalho tipográfico

MODO_LISTA = "Agente da lista 2027"
MODO_AVULSO = "Avulso / Força-Tarefa / Substituição"

st.set_page_config(
    page_title="Crea-MS · DFI · Folha de Atividades 2027",
    page_icon="📋",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Estilo institucional
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
:root{--azul:#003366;--azul2:#0A2E5C;--medio:#005A9C;--verde:#00843D;--cinza:#F4F6F9;}
.stApp{background:var(--cinza);}
.block-container{padding-top:3.6rem;max-width:1250px;}
h1,h2,h3{color:var(--azul)!important;}
.crea-header{display:flex;align-items:center;justify-content:space-between;gap:1rem;
  background:#fff;border-radius:10px;padding:1rem 1.4rem;border-top:6px solid var(--azul);
  box-shadow:0 1px 3px rgba(0,0,0,.06);margin-bottom:1.2rem;}
.crea-brand{font-weight:800;font-size:2rem;letter-spacing:.5px;color:var(--azul);line-height:1;}
.crea-brand span{color:var(--verde);}
.crea-dept{color:#5A6472;font-size:.9rem;margin-top:.25rem;}
.crea-title{text-align:right;}
.crea-title .t1{font-weight:800;font-size:1.35rem;color:var(--azul);}
.crea-title .t1 b{color:var(--verde);}
.crea-title .t2{font-size:.85rem;color:#5A6472;}
.step{display:flex;align-items:center;gap:.7rem;margin:1.4rem 0 .6rem;}
.step .num{background:var(--azul);color:#fff;font-weight:700;border-radius:6px;
  padding:.25rem .6rem;font-size:.95rem;border-bottom:3px solid var(--verde);}
.step .txt{font-weight:700;font-size:1.2rem;color:var(--azul);}
.card{background:#fff;border-radius:10px;padding:1rem 1.2rem;border:1px solid #E1E6EE;}
.badge{display:inline-block;background:var(--azul);color:#fff;border-radius:6px;
  padding:.15rem .55rem;font-weight:700;margin-right:.4rem;}
.badge.verde{background:var(--verde);}
.chip{display:inline-block;background:#E8F0F8;color:var(--azul);border-radius:999px;
  padding:.15rem .65rem;margin:.15rem .2rem .15rem 0;font-size:.85rem;}
.chip.extra{background:#E6F4EC;color:var(--verde);}
.resumo-row{display:flex;gap:.6rem;padding:.45rem 0;border-bottom:1px solid #EEF1F5;}
.resumo-row:last-child{border-bottom:none;}
.resumo-row .k{min-width:190px;font-weight:700;color:var(--azul);font-size:.9rem;}
.resumo-row .v{flex:1;font-size:.95rem;}
div[data-testid="stMetric"]{background:#fff;border:1px solid #E1E6EE;border-radius:10px;padding:.6rem .9rem;}
div[data-testid="stMetricValue"]{color:var(--azul);}
.stDownloadButton button{background:var(--verde)!important;border-color:var(--verde)!important;
  color:#fff!important;font-weight:700;padding:.7rem 1.2rem;}
.stDownloadButton button:hover{filter:brightness(1.08);}
</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Estado
# ---------------------------------------------------------------------------
def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", t).strip("_").lower()


def _key_atv(nome: str) -> str:
    return f"atv__{_slug(nome)}"


def _todas_atividades() -> list[str]:
    return ATIVIDADES + st.session_state.atv_custom


def _init_state():
    if "atv_custom" not in st.session_state:
        st.session_state.atv_custom = []
    for a in _todas_atividades():
        st.session_state.setdefault(_key_atv(a), a in ATIVIDADES_PADRAO)
    st.session_state.setdefault("data_inicio", agora_ms().date())
    st.session_state.setdefault("data_fim", agora_ms().date() + timedelta(days=4))


def cb_marcar_todas():
    for a in _todas_atividades():
        st.session_state[_key_atv(a)] = True


def cb_restaurar_padrao():
    for a in _todas_atividades():
        st.session_state[_key_atv(a)] = a in ATIVIDADES_PADRAO


def cb_limpar():
    for a in _todas_atividades():
        st.session_state[_key_atv(a)] = False


def cb_add_custom():
    nome = " ".join(st.session_state.get("nova_atv", "").split())
    if not nome:
        return
    existentes = {_slug(a) for a in _todas_atividades()}
    if _slug(nome) in existentes:
        st.session_state.msg_custom = ("warning", f"A atividade “{nome}” já está na lista.")
        st.session_state[_key_atv(next(a for a in _todas_atividades() if _slug(a) == _slug(nome)))] = True
    else:
        st.session_state.atv_custom.append(nome)
        st.session_state[_key_atv(nome)] = True
        st.session_state.msg_custom = ("success", f"Atividade “{nome}” adicionada e marcada.")
    st.session_state.nova_atv = ""


def cb_remover_custom(nome: str):
    st.session_state.atv_custom.remove(nome)
    st.session_state.pop(_key_atv(nome), None)


def cb_novo_formulario():
    for k in list(st.session_state.keys()):
        del st.session_state[k]


_init_state()

# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
if LOGO_PATH:
    cab = st.container(border=True)
    c_logo, c_tit = cab.columns([1, 2], vertical_alignment="center")
    with c_logo:
        st.image(LOGO_PATH, width=300)
    with c_tit:
        st.markdown(
            '<div class="crea-title"><div class="t1">Folha de Atividades de Viagem <b>2027</b></div>'
            '<div class="t2">Planejamento de Viagens de Fiscalização · Departamento de Fiscalização (DFI)</div></div>',
            unsafe_allow_html=True,
        )
else:
    st.markdown(
        """
<div class="crea-header">
  <div><div class="crea-brand">CREA<span>-</span>MS</div>
       <div class="crea-dept">Departamento de Fiscalização</div></div>
  <div class="crea-title"><div class="t1">Folha de Atividades de Viagem <b>2027</b></div>
       <div class="t2">Planejamento de Viagens de Fiscalização · DFI</div></div>
</div>""",
        unsafe_allow_html=True,
    )

with st.sidebar:
    st.markdown("### Crea-MS · DFI")
    st.caption("Regiões de Fiscalização 2027")
    st.button("🔄 Novo formulário", on_click=cb_novo_formulario, use_container_width=True,
              help="Limpa todos os campos e restaura as 4 atividades essenciais.")
    with st.expander("Microrregiões 2027", expanded=False):
        for r in MICRORREGIOES_2027:
            st.markdown(f"**{r['numero']} · {r['agente']}**  \n{', '.join(r['municipios'])}")


def etapa(num: int, titulo: str):
    st.markdown(f'<div class="step"><span class="num">ETAPA {num}</span>'
                f'<span class="txt">{titulo}</span></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# ETAPA 1 — Viagem e agente
# ---------------------------------------------------------------------------
etapa(1, "Configuração da Viagem e Agente")

with st.container(border=True):
    modo = st.radio("Modo de seleção do agente", [MODO_LISTA, MODO_AVULSO], horizontal=True, key="modo")

    agente: str = ""
    microrregiao: str | None = None
    municipios_base: list[str] = []
    municipios_extra: list[str] = []

    if modo == MODO_LISTA:
        c1, c2 = st.columns([2, 3])
        with c1:
            nome_ag = st.selectbox(
                "Agente de Fiscalização",
                list(AGENTES.keys()),
                format_func=lambda n: f"{AGENTES[n]['numero']} — {n}",
                key="agente_sel",
            )
            reg = AGENTES[nome_ag]
            agente, microrregiao = nome_ag, reg["numero"]
            st.markdown(f'<span class="badge">Microrregião {reg["numero"]}</span>'
                        f'<span class="badge verde">{len(reg["municipios"])} municípios vinculados</span>',
                        unsafe_allow_html=True)
        with c2:
            municipios_base = st.multiselect(
                "Municípios da microrregião nesta viagem (desmarque os que não serão visitados)",
                reg["municipios"], default=reg["municipios"], key=f"munis_{reg['numero']}",
            )
            restantes = [m for m in MUNICIPIOS_MS if m not in reg["municipios"]]
            municipios_extra = st.multiselect(
                "➕ Municípios avulsos extras (opcional)", restantes,
                key=f"extras_{reg['numero']}", placeholder="Buscar município de MS…",
            )
    else:
        c1, c2 = st.columns([2, 3])
        with c1:
            agente = st.text_input("Nome do Agente de Fiscalização", key="agente_avulso",
                                   placeholder="Ex.: Maria Souza").strip()
            st.markdown('<span class="badge verde">Designação Avulsa</span>', unsafe_allow_html=True)
        with c2:
            municipios_extra = st.multiselect(
                "Municípios da viagem (lista completa dos 79 municípios de MS)", MUNICIPIOS_MS,
                key="munis_avulso", placeholder="Buscar município de MS…",
            )

    municipios = municipios_base + municipios_extra

    st.markdown("**Período da viagem**")
    d1, d2, d3 = st.columns([1, 1, 1])
    with d1:
        data_inicio = st.date_input("Data de início", key="data_inicio", format="DD/MM/YYYY")
    with d2:
        data_fim = st.date_input("Data de término", key="data_fim", format="DD/MM/YYYY")
    periodo_ok = data_fim >= data_inicio
    dias = (data_fim - data_inicio).days + 1 if periodo_ok else 0
    with d3:
        st.metric("Duração da viagem", f"{dias} dia{'s' if dias != 1 else ''}" if periodo_ok else "—")
    if not periodo_ok:
        st.error("A data de término deve ser igual ou posterior à data de início.")

# ---------------------------------------------------------------------------
# ETAPA 2 — Atividades
# ---------------------------------------------------------------------------
etapa(2, "Seleção de Atividades a Fiscalizar")

with st.container(border=True):
    b1, b2, b3, _ = st.columns([1, 1.4, 1, 1.6])
    b1.button("✅ Marcar Todas", on_click=cb_marcar_todas, use_container_width=True)
    b2.button("⭐ Restaurar Padrão (4 essenciais)", on_click=cb_restaurar_padrao, use_container_width=True)
    b3.button("🧹 Limpar Seleção", on_click=cb_limpar, use_container_width=True)

    lista = _todas_atividades()
    n_cols = 4
    por_col = -(-len(lista) // n_cols)  # preenchimento por coluna (leitura alfabética)
    cols = st.columns(n_cols)
    for i, a in enumerate(lista):
        with cols[i // por_col]:
            rotulo = f"{a} ⭐" if a in ATIVIDADES_PADRAO else (f"{a} ✚" if a in st.session_state.atv_custom else a)
            st.checkbox(rotulo, key=_key_atv(a))

    st.caption("⭐ essencial (marcada por padrão) · ✚ atividade personalizada")

    st.divider()
    cc1, cc2 = st.columns([3, 1], vertical_alignment="bottom")
    with cc1:
        st.text_input("Adicionar atividade personalizada", key="nova_atv",
                      placeholder="Ex.: Torres de Transmissão")
    with cc2:
        st.button("➕ Adicionar", on_click=cb_add_custom, use_container_width=True)
    if "msg_custom" in st.session_state:
        tipo, msg = st.session_state.pop("msg_custom")
        getattr(st, tipo)(msg)
    if st.session_state.atv_custom:
        st.caption("Atividades personalizadas (clique para remover):")
        rc = st.columns(min(len(st.session_state.atv_custom), 4))
        for i, a in enumerate(list(st.session_state.atv_custom)):
            rc[i % len(rc)].button(f"✕ {a}", key=f"rm__{_slug(a)}", on_click=cb_remover_custom, args=(a,))

    observacoes = st.text_area(
        "Observações / Diretrizes da Viagem (opcional — sai no rodapé do documento)",
        key="observacoes", height=100,
        placeholder="Ex.: Priorizar obras públicas municipais e eventos agendados para o fim de semana.",
    )

atividades_sel = [a for a in _todas_atividades() if st.session_state.get(_key_atv(a))]

# ---------------------------------------------------------------------------
# ETAPA 3 — Resumo e PDF
# ---------------------------------------------------------------------------
etapa(3, "Resumo e Geração do PDF")

m1, m2, m3, m4 = st.columns([2, 1, 1, 1])
m1.metric("Agente", agente.upper() if agente else "—")
m2.metric("Microrregião", microrregiao or "Avulsa")
m3.metric("Municípios", len(municipios))
m4.metric("Atividades", len(atividades_sel))

chips_m = "".join(f'<span class="chip">{m.upper()}</span>' for m in municipios_base) + \
          "".join(f'<span class="chip extra">{m.upper()}</span>' for m in municipios_extra)
chips_a = "".join(f'<span class="chip">{a}</span>' for a in atividades_sel)
periodo_txt = (f"{fmt_data(data_inicio)} a {fmt_data(data_fim)} ({dias} dia{'s' if dias != 1 else ''})"
               if periodo_ok else "Período inválido")
st.markdown(
    f"""
<div class="card">
 <div class="resumo-row"><div class="k">Agente Fiscal</div><div class="v">{agente.upper() or '<i>não informado</i>'}</div></div>
 <div class="resumo-row"><div class="k">Microrregião</div><div class="v">{('Microrregião ' + microrregiao) if microrregiao else 'Designação Avulsa'}</div></div>
 <div class="resumo-row"><div class="k">Municípios</div><div class="v">{chips_m or '<i>nenhum selecionado</i>'}</div></div>
 <div class="resumo-row"><div class="k">Período da Viagem</div><div class="v">{periodo_txt}</div></div>
 <div class="resumo-row"><div class="k">Atividades ({len(atividades_sel)})</div><div class="v">{chips_a or '<i>nenhuma selecionada</i>'}</div></div>
</div>""",
    unsafe_allow_html=True,
)
st.write("")

pendencias = []
if not agente:
    pendencias.append("informe o nome do agente de fiscalização")
if not municipios:
    pendencias.append("selecione ao menos um município")
if not atividades_sel:
    pendencias.append("selecione ao menos uma atividade")
if not periodo_ok:
    pendencias.append("corrija o período da viagem")

if pendencias:
    st.warning("Para gerar o documento: " + "; ".join(pendencias) + ".")
else:
    pdf_bytes = gerar_pdf(
        agente=agente,
        microrregiao=microrregiao,
        municipios=municipios,
        data_inicio=data_inicio,
        data_fim=data_fim,
        atividades=atividades_sel,
        observacoes=observacoes,
        logo_path=LOGO_PATH,
        emitido_em=agora_ms(),
    )
    nome_arq = (f"Folha_Atividades_{_slug(agente).upper()}_"
                f"{data_inicio.strftime('%Y%m%d')}-{data_fim.strftime('%Y%m%d')}.pdf")
    st.download_button(
        "📄 Gerar Ordem / Folha de Atividades (PDF)",
        data=pdf_bytes,
        file_name=nome_arq,
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

st.markdown(
    "<div style='text-align:center;color:#8A94A3;font-size:.8rem;margin-top:2rem'>"
    "Crea-MS · Departamento de Fiscalização (DFI) · Regiões de Fiscalização 2027</div>",
    unsafe_allow_html=True,
)
