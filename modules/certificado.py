"""
Página de Certificado
Exibe os certificados e permite baixar em PDF A4 (210 x 297 mm).
"""

import io
import os
import unicodedata

import streamlit as st
from PIL import Image, ImageFilter
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def _obter_modelos_certificado() -> list[dict[str, str]]:
    """Retorna os modelos de certificado disponiveis para visualizacao e download."""
    return [
        {
            "nome": "Certificado de Batismo",
            "arquivo": "Certificado-Batismo-ICVEV.png",
            "prefixo_pdf": "certificado_batismo",
        },
        {
            "nome": "Certificado de Apresentação de Crianças",
            "arquivo": "Certificado-Criancas-ICEV.png",
            "prefixo_pdf": "certificado_apresentacao_criancas",
        },
        {
            "nome": "Certificado de Apresentação Diácono",
            "arquivo": "Certificado-de-Diacono-ICEV.png",
            "prefixo_pdf": "certificado_diacono",
        },
    ]


def _obter_caminho_certificado(nome_arquivo: str) -> str:
    """Retorna o caminho absoluto da imagem do certificado."""
    raiz_projeto = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pasta_imagem = os.path.join(raiz_projeto, "imagem")

    def _normalizar(texto: str) -> str:
        texto = unicodedata.normalize("NFKD", texto)
        texto = "".join(c for c in texto if not unicodedata.combining(c))
        return texto.lower()

    # Caminho direto quando o arquivo exato existe.
    caminho_exato = os.path.join(pasta_imagem, nome_arquivo)
    if os.path.exists(caminho_exato):
        return caminho_exato

    # Fallback inteligente por categoria para lidar com variacoes de nomes.
    try:
        arquivos_png = [f for f in os.listdir(pasta_imagem) if f.lower().endswith(".png")]
    except Exception:
        arquivos_png = []

    nome_normalizado = _normalizar(nome_arquivo)

    if "batismo" in nome_normalizado:
        for candidato in arquivos_png:
            n = _normalizar(candidato)
            if "certificado" in n and "batismo" in n:
                return os.path.join(pasta_imagem, candidato)

    if "criancas" in nome_normalizado:
        for candidato in arquivos_png:
            n = _normalizar(candidato)
            if "certificado" in n and "criancas" in n:
                return os.path.join(pasta_imagem, candidato)

    if "diacono" in nome_normalizado:
        for candidato in arquivos_png:
            n = _normalizar(candidato)
            if "certificado" in n and "diacono" in n:
                return os.path.join(pasta_imagem, candidato)

    if nome_arquivo == "Certificado-Batismo-ICVEV.png":
        candidatos = [
            "Certificado-Batismo-ICVEV.png",
            "certificado-Batismo-ICVEV.png",
            "Certificado-Batismo-ICEV.png",
            "Certificado-Batismo-Dechomai.png",
        ]
        for candidato in candidatos:
            caminho_candidato = os.path.join(pasta_imagem, candidato)
            if os.path.exists(caminho_candidato):
                return caminho_candidato

    if nome_arquivo == "Certificado-Criancas-ICEV.png":
        candidatos = [
            "Certificado-Criancas-ICEV.png",
            "certificado-de-apresentacao-de-criancas-ICVEV.png",
            "Certificado-de-Apresentacao-de-Criancas-ICVEV.png",
            "certificado-de-Apresentacao-de-Criancas-ICVEV.png",
            "Certificado-de-Apresentaçao-de-Criancas-Dechomai.png",
            "Certificado-de-Apresentacao-de-Criancas-Dechomai.png",
        ]
        for candidato in candidatos:
            caminho_candidato = os.path.join(pasta_imagem, candidato)
            if os.path.exists(caminho_candidato):
                return caminho_candidato

    if nome_arquivo == "certificado-de-apresentacao-de-criancas-ICVEV.png":
        candidatos = [
            "Certificado-Criancas-ICEV.png",
            "certificado-de-apresentacao-de-criancas-ICVEV.png",
            "Certificado-de-Apresentacao-de-Criancas-ICVEV.png",
            "certificado-de-Apresentacao-de-Criancas-ICVEV.png",
            "Certificado-de-Apresentaçao-de-Criancas-Dechomai.png",
            "Certificado-de-Apresentacao-de-Criancas-Dechomai.png",
        ]
        for candidato in candidatos:
            caminho_candidato = os.path.join(pasta_imagem, candidato)
            if os.path.exists(caminho_candidato):
                return caminho_candidato

    return caminho_exato


def _preparar_imagem_alta_resolucao(caminho_imagem: str) -> Image.Image:
    """Prepara a imagem para melhor definição em tela e impressão."""
    largura_a4_px_300dpi = 2480
    altura_a4_px_300dpi = 3508

    imagem_pil = Image.open(caminho_imagem).convert("RGB")

    # Mantem o certificado em orientacao vertical.
    if imagem_pil.width > imagem_pil.height:
        imagem_pil = imagem_pil.rotate(90, expand=True)

    # Eleva a resolução de referencia para impressão A4 em 300 DPI quando necessário.
    escala = max(1.0, min(
        largura_a4_px_300dpi / imagem_pil.width,
        altura_a4_px_300dpi / imagem_pil.height,
    ))
    if escala > 1.0:
        novo_tamanho = (
            int(round(imagem_pil.width * escala)),
            int(round(imagem_pil.height * escala)),
        )
        imagem_pil = imagem_pil.resize(novo_tamanho, Image.Resampling.LANCZOS)

    # Realca levemente contornos para impressão sem exagero.
    imagem_pil = imagem_pil.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130, threshold=3))
    return imagem_pil


def _preparar_imagem_compacta(caminho_imagem: str) -> Image.Image:
    """Prepara a imagem para um PDF menor, mantendo boa legibilidade."""
    largura_a4_px_150dpi = 1240
    altura_a4_px_150dpi = 1754

    imagem_pil = Image.open(caminho_imagem).convert("RGB")

    # Mantem o certificado em orientacao vertical.
    if imagem_pil.width > imagem_pil.height:
        imagem_pil = imagem_pil.rotate(90, expand=True)

    # Reduz para referencia de 150 DPI, ajudando a diminuir o tamanho final.
    escala = min(
        largura_a4_px_150dpi / imagem_pil.width,
        altura_a4_px_150dpi / imagem_pil.height,
    )
    if escala < 1.0:
        novo_tamanho = (
            int(round(imagem_pil.width * escala)),
            int(round(imagem_pil.height * escala)),
        )
        imagem_pil = imagem_pil.resize(novo_tamanho, Image.Resampling.LANCZOS)

    return imagem_pil


def _gerar_pdf_a4_com_imagem(imagem_pil: Image.Image) -> bytes:
    """Gera um PDF A4 vertical (210 x 297 mm) otimizado para impressão."""
    largura_a4 = 210 * mm
    altura_a4 = 297 * mm

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=(largura_a4, altura_a4))
    pdf.setPageCompression(1)

    imagem = ImageReader(imagem_pil)
    largura_img, altura_img = imagem.getSize()

    # Ajusta para caber no A4 vertical sem cortar conteúdo.
    escala = min(largura_a4 / largura_img, altura_a4 / altura_img)
    largura_final = largura_img * escala
    altura_final = altura_img * escala

    pos_x = (largura_a4 - largura_final) / 2
    pos_y = (altura_a4 - altura_final) / 2

    pdf.drawImage(
        imagem,
        pos_x,
        pos_y,
        width=largura_final,
        height=altura_final,
        preserveAspectRatio=True,
        mask="auto",
    )
    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer.getvalue()


def exibir_pagina_certificado():
    """Renderiza a tela de certificado no menu."""
    st.title("📜 Certificado")
    st.markdown("Visualização e download de certificados em PDF A4 (210 x 297 mm).")

    modelos = _obter_modelos_certificado()
    nomes_modelos = [modelo["nome"] for modelo in modelos]
    nome_selecionado = st.selectbox("Modelo de certificado", nomes_modelos)
    modelo_escolhido = next(modelo for modelo in modelos if modelo["nome"] == nome_selecionado)

    caminho_certificado = _obter_caminho_certificado(modelo_escolhido["arquivo"])

    if not os.path.exists(caminho_certificado):
        st.error("Arquivo de certificado não encontrado na pasta imagem.")
        st.info(f"Caminho esperado: imagem/{modelo_escolhido['arquivo']}")
        return

    imagem_alta = _preparar_imagem_alta_resolucao(caminho_certificado)
    st.image(imagem_alta, caption=modelo_escolhido["nome"], width="stretch")

    st.markdown("### Download do PDF")
    st.caption("Escolha entre máxima qualidade para impressão ou arquivo compacto.")

    col_alta, col_compacta = st.columns(2)

    with col_alta:
        pdf_alta = _gerar_pdf_a4_com_imagem(imagem_alta)
        st.download_button(
            label="⬇️ Alta qualidade (300 DPI)",
            data=pdf_alta,
            file_name=f"{modelo_escolhido['prefixo_pdf']}_a4_alta_300dpi.pdf",
            mime="application/pdf",
            width="stretch",
        )

    with col_compacta:
        imagem_compacta = _preparar_imagem_compacta(caminho_certificado)
        pdf_compacto = _gerar_pdf_a4_com_imagem(imagem_compacta)
        st.download_button(
            label="⬇️ Compacto (150 DPI)",
            data=pdf_compacto,
            file_name=f"{modelo_escolhido['prefixo_pdf']}_a4_compacto_150dpi.pdf",
            mime="application/pdf",
            width="stretch",
        )