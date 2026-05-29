"""
Página de Aniversariantes
Lista aniversariantes da semana e do mês com exportação em PDF.
"""
import io
from datetime import datetime, date, timedelta

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)

from database_membros import obter_membros


# ─────────────────────────────────────────────────────────────────────────────
# Helpers de data
# ─────────────────────────────────────────────────────────────────────────────

def _semana_atual():
    """Retorna (data_inicio, data_fim) da semana corrente (seg–dom)."""
    hoje = date.today()
    inicio = hoje - timedelta(days=hoje.weekday())   # segunda
    fim    = inicio + timedelta(days=6)              # domingo
    return inicio, fim


def _aniversariantes_semana(membros) -> list:
    inicio, fim = _semana_atual()
    resultado = []
    for m in membros:
        try:
            nasc = datetime.strptime(m["data_nascimento"], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        # Compara apenas mês/dia dentro do intervalo da semana
        # Considera virada de ano (semana que abrange 31/12–01/01)
        cand = nasc.replace(year=inicio.year)
        if inicio <= cand <= fim:
            resultado.append(m)
            continue
        # Tenta com o ano da data final (virada de ano)
        if inicio.year != fim.year:
            cand2 = nasc.replace(year=fim.year)
            if inicio <= cand2 <= fim:
                resultado.append(m)

    return sorted(resultado, key=lambda m: (
        datetime.strptime(m["data_nascimento"], "%Y-%m-%d").month,
        datetime.strptime(m["data_nascimento"], "%Y-%m-%d").day,
    ))


def _aniversariantes_mes(membros, mes: int) -> list:
    resultado = [
        m for m in membros
        if datetime.strptime(m["data_nascimento"], "%Y-%m-%d").month == mes
    ]
    return sorted(resultado, key=lambda m:
        datetime.strptime(m["data_nascimento"], "%Y-%m-%d").day
    )


# ─────────────────────────────────────────────────────────────────────────────
# Geração do PDF
# ─────────────────────────────────────────────────────────────────────────────

def _gerar_pdf(titulo: str, subtitulo: str, membros: list) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        "Titulo",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1a3a5c"),
        spaceAfter=4,
    )
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#555555"),
        spaceAfter=12,
    )
    estilo_rodape = ParagraphStyle(
        "Rodape",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
    )

    conteudo = []

    # Cabeçalho
    conteudo.append(Paragraph("🎂 Sistema de Gestão de Dízimos e Ofertas", estilo_titulo))
    conteudo.append(Paragraph(titulo, estilo_subtitulo))
    conteudo.append(Paragraph(subtitulo, estilo_subtitulo))
    conteudo.append(Spacer(1, 0.4 * cm))

    if not membros:
        conteudo.append(Paragraph("Nenhum aniversariante encontrado.", styles["Normal"]))
    else:
        # Tabela
        cabecalho = ["#", "Nome", "Data de Nascimento", "Idade"]
        dados = [cabecalho]

        hoje = date.today()
        for i, m in enumerate(membros, start=1):
            nasc = datetime.strptime(m["data_nascimento"], "%Y-%m-%d").date()
            idade = hoje.year - nasc.year - (
                (hoje.month, hoje.day) < (nasc.month, nasc.day)
            )
            dados.append([
                str(i),
                m["nome"],
                nasc.strftime("%d/%m/%Y"),
                f"{idade} anos",
            ])

        col_widths = [1 * cm, 9 * cm, 4 * cm, 3 * cm]

        tabela = Table(dados, colWidths=col_widths, repeatRows=1)
        tabela.setStyle(TableStyle([
            # Cabeçalho
            ("BACKGROUND",   (0, 0), (-1, 0),  colors.HexColor("#1a3a5c")),
            ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, 0),  10),
            ("ALIGN",        (0, 0), (-1, 0),  "CENTER"),
            ("BOTTOMPADDING",(0, 0), (-1, 0),  8),
            ("TOPPADDING",   (0, 0), (-1, 0),  8),
            # Linhas pares/ímpares
            *[
                ("BACKGROUND", (0, r), (-1, r),
                 colors.HexColor("#eaf0fb") if r % 2 == 0 else colors.white)
                for r in range(1, len(dados))
            ],
            # Bordas
            ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("FONTNAME",    (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",    (0, 1), (-1, -1), 9),
            ("ALIGN",       (2, 1), (3, -1),  "CENTER"),
            ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",  (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING",(0, 1), (-1, -1), 6),
        ]))

        conteudo.append(tabela)
        conteudo.append(Spacer(1, 0.5 * cm))
        conteudo.append(Paragraph(
            f"Total: {len(membros)} aniversariante(s).",
            styles["Normal"]
        ))

    conteudo.append(Spacer(1, 1 * cm))
    conteudo.append(Paragraph(
        f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        estilo_rodape
    ))

    doc.build(conteudo)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Página principal
# ─────────────────────────────────────────────────────────────────────────────

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
]


def _exibir_tabela(membros: list):
    """Exibe tabela de aniversariantes na tela."""
    if not membros:
        st.info("ℹ️ Nenhum aniversariante encontrado.")
        return

    hoje = date.today()
    linhas = []
    for m in membros:
        nasc = datetime.strptime(m["data_nascimento"], "%Y-%m-%d").date()
        idade = hoje.year - nasc.year - (
            (hoje.month, hoje.day) < (nasc.month, nasc.day)
        )
        aniversario_hoje = nasc.month == hoje.month and nasc.day == hoje.day
        nome = f"🎂 {m['nome']}" if aniversario_hoje else m["nome"]
        linhas.append({
            "Nome": nome,
            "Data de Nascimento": nasc.strftime("%d/%m/%Y"),
            "Idade": f"{idade} anos",
        })

    import pandas as pd
    df = pd.DataFrame(linhas)
    st.dataframe(df, width="stretch", hide_index=True)


def exibir_pagina_aniversariantes():
    st.title("🎂 Aniversariantes")

    membros = list(obter_membros())

    if not membros:
        st.warning("Nenhum membro cadastrado.")
        return

    aba_semana, aba_mes = st.tabs(["📅 Semana Atual", "📆 Mês"])

    # ── Aba Semana ─────────────────────────────────────────────────────────
    with aba_semana:
        inicio, fim = _semana_atual()
        st.markdown(
            f"**Período:** {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}"
        )

        lista_semana = _aniversariantes_semana(membros)

        st.markdown(f"**{len(lista_semana)} aniversariante(s) nesta semana.**")
        _exibir_tabela(lista_semana)

        pdf_semana = _gerar_pdf(
            titulo=f"Aniversariantes da Semana",
            subtitulo=f"Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}",
            membros=lista_semana,
        )
        st.download_button(
            label="⬇️ Baixar PDF — Semana",
            data=pdf_semana,
            file_name=f"aniversariantes_semana_{inicio.strftime('%d%m%Y')}.pdf",
            mime="application/pdf",
            width="stretch",
        )

    # ── Aba Mês ────────────────────────────────────────────────────────────
    with aba_mes:
        mes_atual = date.today().month
        mes_selecionado = st.selectbox(
            "Selecione o mês",
            options=range(1, 13),
            index=mes_atual - 1,
            format_func=lambda m: MESES[m - 1],
        )

        lista_mes = _aniversariantes_mes(membros, mes_selecionado)

        st.markdown(f"**{len(lista_mes)} aniversariante(s) em {MESES[mes_selecionado - 1]}.**")
        _exibir_tabela(lista_mes)

        pdf_mes = _gerar_pdf(
            titulo=f"Aniversariantes de {MESES[mes_selecionado - 1]}",
            subtitulo=f"Mês: {mes_selecionado:02d}/{date.today().year}",
            membros=lista_mes,
        )
        st.download_button(
            label=f"⬇️ Baixar PDF — {MESES[mes_selecionado - 1]}",
            data=pdf_mes,
            file_name=f"aniversariantes_{mes_selecionado:02d}_{date.today().year}.pdf",
            mime="application/pdf",
            width="stretch",
        )
