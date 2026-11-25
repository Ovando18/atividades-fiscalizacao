"""Geração do PDF — Folha de Atividades de Viagem de Fiscalização (Crea-MS / DFI)."""

from __future__ import annotations

import io
import os
from datetime import date, datetime
from zoneinfo import ZoneInfo
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Flowable,
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

AZUL_ESCURO = colors.HexColor("#003366")
AZUL_MEDIO = colors.HexColor("#005A9C")
VERDE = colors.HexColor("#00843D")
CINZA_CLARO = colors.HexColor("#F4F6F9")
CINZA_LINHA = colors.HexColor("#C9D1DC")
CINZA_TEXTO = colors.HexColor("#5A6472")

FUSO_MS = ZoneInfo("America/Campo_Grande")  # horário oficial de Mato Grosso do Sul


def agora_ms() -> datetime:
    return datetime.now(FUSO_MS)


_BASE = os.path.dirname(os.path.abspath(__file__))


def localizar_logo() -> str | None:
    """Procura logo_crea_ms.(png|jpg|jpeg|webp) na raiz do projeto."""
    for ext in ("png", "jpg", "jpeg", "webp", "PNG", "JPG", "JPEG"):
        caminho = os.path.join(_BASE, f"logo_crea_ms.{ext}")
        if os.path.exists(caminho):
            return caminho
    return None


LOGO_PADRAO = localizar_logo()


def fmt_data(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _st(name, **kw) -> ParagraphStyle:
    base = dict(fontName="Helvetica", fontSize=9, leading=11.5, textColor=colors.black)
    base.update(kw)
    return ParagraphStyle(name, **base)


ST_TITULO = _st("titulo", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=AZUL_ESCURO)
ST_SUB = _st("sub", fontName="Helvetica-Bold", fontSize=9, leading=11.5, textColor=AZUL_MEDIO)
ST_SECAO = _st("secao", fontName="Helvetica-Bold", fontSize=9.5, leading=12, textColor=colors.white)
ST_ROTULO = _st("rotulo", fontName="Helvetica-Bold", fontSize=8.5, textColor=AZUL_ESCURO)
ST_VALOR = _st("valor", fontSize=9)
ST_CEL = _st("cel", fontSize=8.8, leading=10.5)
ST_CEL_C = _st("celc", fontSize=8.8, leading=10.5, alignment=TA_CENTER)
ST_HEAD = _st("head", fontName="Helvetica-Bold", fontSize=8.3, leading=10, textColor=colors.white, alignment=TA_CENTER)
ST_HEAD_L = _st("headl", fontName="Helvetica-Bold", fontSize=8.3, leading=10, textColor=colors.white, alignment=TA_LEFT)
ST_OBS = _st("obs", fontSize=9, leading=12)
ST_ASS = _st("ass", fontSize=8.5, leading=10.5, alignment=TA_CENTER)
ST_ASS_B = _st("assb", fontName="Helvetica-Bold", fontSize=8.5, leading=10.5, alignment=TA_CENTER, textColor=AZUL_ESCURO)
ST_LOGO_TXT = _st("logotxt", fontName="Helvetica-Bold", fontSize=17, leading=19, textColor=AZUL_ESCURO)
ST_LOGO_SUB = _st("logosub", fontSize=6.5, leading=8, textColor=CINZA_TEXTO)


class CaixaSelecao(Flowable):
    """Quadradinho vazio para o fiscal marcar em campo."""

    def __init__(self, tamanho=4.2 * mm):
        super().__init__()
        self.tamanho = tamanho
        self.width = self.height = tamanho

    def draw(self):
        self.canv.setStrokeColor(AZUL_ESCURO)
        self.canv.setLineWidth(0.9)
        self.canv.rect(0, 0, self.tamanho, self.tamanho, stroke=1, fill=0)


class LinhaPautada(Flowable):
    """Linha tracejada de apoio para anotação manuscrita."""

    def __init__(self, largura):
        super().__init__()
        self.width, self.height = largura, 1

    def draw(self):
        self.canv.setStrokeColor(CINZA_LINHA)
        self.canv.setDash(1, 2)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, -6, self.width, -6)


def _bloco_logo(logo_path: str | None):
    """Logo em imagem, ou fallback tipográfico 'CREA-MS'."""
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image(logo_path)
            ratio = img.imageWidth / float(img.imageHeight)
            h = 17 * mm
            w = min(h * ratio, 58 * mm)
            return Image(logo_path, width=w, height=w / ratio)
        except Exception:
            pass
    t = Table(
        [[Paragraph("CREA-MS", ST_LOGO_TXT)], [Paragraph("Departamento de Fiscalização", ST_LOGO_SUB)]],
        colWidths=[40 * mm],
    )
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEBELOW", (0, 0), (0, 0), 1.6, VERDE),
    ]))
    return t


def _faixa_secao(texto: str, largura: float) -> Table:
    t = Table([[Paragraph(texto, ST_SECAO)]], colWidths=[largura])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL_ESCURO),
        ("LINEBELOW", (0, 0), (-1, -1), 2, VERDE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def gerar_pdf(
    agente: str,
    microrregiao: str | None,
    municipios: list[str],
    data_inicio: date,
    data_fim: date,
    atividades: list[str],
    observacoes: str = "",
    logo_path: str | None = None,
    emitido_em: datetime | None = None,
) -> bytes:
    """Gera a Folha de Atividades e devolve os bytes do PDF."""
    emitido_em = emitido_em or agora_ms()
    logo_path = logo_path or localizar_logo()
    buffer = io.BytesIO()
    margem = 14 * mm
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=margem, rightMargin=margem, topMargin=12 * mm, bottomMargin=16 * mm,
        title="Folha de Atividades de Viagem - Crea-MS",
        author="Crea-MS - Departamento de Fiscalização",
        subject=f"Fiscalização - {agente}",
    )
    largura = A4[0] - 2 * margem
    story = []

    # ---------------- Cabeçalho ----------------
    titulo = [
        Paragraph("CONSELHO REGIONAL DE ENGENHARIA E AGRONOMIA DE MATO GROSSO DO SUL — CREA-MS", ST_TITULO),
        Spacer(1, 2),
        Paragraph("DEPARTAMENTO DE FISCALIZAÇÃO (DFI) — FOLHA DE ATIVIDADES DE VIAGEM", ST_SUB),
    ]
    logo = _bloco_logo(logo_path)
    col_logo = max(46 * mm, getattr(logo, "drawWidth", 0) + 5 * mm)
    cab = Table([[logo, titulo]], colWidths=[col_logo, largura - col_logo])
    cab.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, 0), 2.2, AZUL_ESCURO),
    ]))
    story += [cab, Spacer(1, 1.2 * mm)]
    faixa = Table([[""]], colWidths=[largura], rowHeights=[1.3 * mm])
    faixa.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), VERDE)]))
    story += [faixa, Spacer(1, 5 * mm)]

    # ---------------- Identificação ----------------
    dias = (data_fim - data_inicio).days + 1
    micro_txt = f"Microrregião {microrregiao}" if microrregiao else "Avulsa / Especial"
    munis_txt = ", ".join(m.upper() for m in municipios) if municipios else "—"
    periodo_txt = (
        f"<b>{fmt_data(data_inicio)}</b> a <b>{fmt_data(data_fim)}</b> "
        f"&nbsp;({dias} dia{'s' if dias != 1 else ''})"
    )
    linhas_id = [
        ("Agente de Fiscalização", f"<b>{escape(agente.upper())}</b>"),
        ("Microrregião", escape(micro_txt)),
        ("Localidades (Municípios)", escape(munis_txt)),
        ("Período da Fiscalização", periodo_txt),
    ]
    story.append(_faixa_secao("1. IDENTIFICAÇÃO DA VIAGEM", largura))
    tid = Table(
        [[Paragraph(r, ST_ROTULO), Paragraph(v, ST_VALOR)] for r, v in linhas_id],
        colWidths=[48 * mm, largura - 48 * mm],
    )
    tid.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), CINZA_CLARO),
        ("GRID", (0, 0), (-1, -1), 0.5, CINZA_LINHA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [tid, Spacer(1, 6 * mm)]

    # ---------------- Atividades ----------------
    story.append(_faixa_secao(f"2. ATIVIDADES A FISCALIZAR ({len(atividades)})", largura))
    col_w = [13 * mm, 72 * mm, 25 * mm, largura - 110 * mm]
    dados = [[
        Paragraph("ITEM", ST_HEAD),
        Paragraph("ATIVIDADE / EMPREENDIMENTO A FISCALIZAR", ST_HEAD_L),
        Paragraph("VERIFICADO", ST_HEAD),
        Paragraph("OBSERVAÇÕES DE CAMPO", ST_HEAD_L),
    ]]
    for i, atv in enumerate(atividades, 1):
        dados.append([Paragraph(f"{i:02d}", ST_CEL_C), Paragraph(escape(atv), ST_CEL), CaixaSelecao(), LinhaPautada(col_w[3] - 12)])
    tat = Table(dados, colWidths=col_w, repeatRows=1,
                rowHeights=[None] + [11 * mm] * len(atividades))
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL_MEDIO),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (2, 1), (2, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.8, AZUL_ESCURO),
        ("INNERGRID", (0, 0), (-1, -1), 0.4, CINZA_LINHA),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
    ]
    for r in range(1, len(dados)):
        if r % 2 == 0:
            estilo.append(("BACKGROUND", (0, r), (2, r), CINZA_CLARO))
    tat.setStyle(TableStyle(estilo))
    story += [tat, Spacer(1, 6 * mm)]

    # ---------------- Observações gerais ----------------
    if observacoes and observacoes.strip():
        txt = escape(observacoes.strip()).replace("\n", "<br/>")
        tobs = Table([[Paragraph(txt, ST_OBS)]], colWidths=[largura])
        tobs.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, CINZA_LINHA),
            ("LINEBEFORE", (0, 0), (0, -1), 3, VERDE),
            ("BACKGROUND", (0, 0), (-1, -1), CINZA_CLARO),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(KeepTogether([
            _faixa_secao("3. OBSERVAÇÕES GERAIS / DIRETRIZES DA VIAGEM", largura),
            tobs, Spacer(1, 6 * mm),
        ]))

    # ---------------- Assinaturas ----------------
    meia = (largura - 14 * mm) / 2
    ass = Table(
        [
            ["", "", ""],
            [Paragraph(escape(agente.upper()), ST_ASS_B), "", Paragraph("GERENTE DO DFI", ST_ASS_B)],
            [Paragraph("Agente de Fiscalização", ST_ASS), "",
             Paragraph("Gerente do Departamento de Fiscalização", ST_ASS)],
        ],
        colWidths=[meia, 14 * mm, meia], rowHeights=[16 * mm, None, None],
    )
    ass.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (0, 0), 0.8, colors.black),
        ("LINEBELOW", (2, 0), (2, 0), 0.8, colors.black),
        ("TOPPADDING", (0, 1), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 0),
    ]))
    story.append(KeepTogether([Spacer(1, 4 * mm), ass]))

    # ---------------- Rodapé de página ----------------
    emissao_txt = f"Documento emitido em {emitido_em.strftime('%d/%m/%Y às %H:%M')}"

    def rodape(canvas, doc_):
        canvas.saveState()
        y = 9 * mm
        canvas.setStrokeColor(AZUL_ESCURO)
        canvas.setLineWidth(0.6)
        canvas.line(margem, y + 4 * mm, A4[0] - margem, y + 4 * mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(CINZA_TEXTO)
        canvas.drawString(margem, y, f"Crea-MS · Departamento de Fiscalização (DFI) · {emissao_txt}")
        canvas.drawRightString(A4[0] - margem, y, f"Página {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    return buffer.getvalue()
