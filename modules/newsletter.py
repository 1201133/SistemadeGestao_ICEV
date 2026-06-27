"""
Página de Newsletter e Comunicados.
"""
import base64
import io
from datetime import date, datetime
from typing import List, Tuple

import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage, Paragraph, SimpleDocTemplate, Spacer

# Importa pyspellchecker com fallback (não é obrigatório)
try:
    from spellchecker import SpellChecker
    SPELLCHECKER_DISPONIVEL = True
    SPELLCHECKER_PT = SpellChecker(language="pt")
except ImportError:
    SPELLCHECKER_DISPONIVEL = False

from config import (
    JSPELL_API_HOST,
    JSPELL_API_KEY,
    JSPELL_API_URL,
    JSPELL_TIMEOUT_SECONDS,
)
from email_service import enviar_email_html
from database_newsletter import (
    criar_newsletter,
    atualizar_newsletter,
    excluir_newsletter,
    listar_newsletters,
    marcar_email_enviado,
)
from database_membros import obter_membros
from notifications import validar_email


def _parse_emails(raw: str) -> Tuple[List[str], List[str]]:
    """Transforma entrada em lista de e-mails válidos e inválidos."""
    if not raw:
        return [], []

    candidatos = []
    for pedaco in raw.replace(";", ",").replace("\n", ",").split(","):
        email = pedaco.strip()
        if email:
            candidatos.append(email)

    # Remove duplicados preservando ordem
    unicos = list(dict.fromkeys(candidatos))
    validos = [e for e in unicos if validar_email(e)]
    invalidos = [e for e in unicos if not validar_email(e)]
    return validos, invalidos


def _obter_emails_membros() -> List[str]:
    """Busca e-mails válidos do cadastro de membros."""
    membros = obter_membros()
    emails = []
    for m in membros:
        email = (m["email"] or "").strip() if "email" in m.keys() else ""
        if email and validar_email(email):
            emails.append(email)
    return list(dict.fromkeys(emails))


def _extrair_texto_corrigido(payload) -> str:
    """Tenta localizar o texto corrigido em diferentes formatos de resposta da API."""
    if isinstance(payload, str):
        return payload

    if isinstance(payload, dict):
        chaves_prioritarias = [
            "correctedText",
            "corrected_text",
            "textCorrected",
            "text",
            "result",
            "output",
            "message",
        ]
        for chave in chaves_prioritarias:
            valor = payload.get(chave)
            if isinstance(valor, str) and valor.strip():
                return valor

        for valor in payload.values():
            extraido = _extrair_texto_corrigido(valor)
            if extraido:
                return extraido

    if isinstance(payload, list):
        for item in payload:
            extraido = _extrair_texto_corrigido(item)
            if extraido:
                return extraido

    return ""


def _corrigir_com_spellchecker_local(texto: str) -> Tuple[str, str]:
    """Corrige ortografia usando pyspellchecker local (sem chave de API)."""
    if not SPELLCHECKER_DISPONIVEL:
        return texto, "Corretor local não disponível (instale com: pip install pyspellchecker)"

    if not texto.strip():
        return texto, ""

    try:
        palavras = texto.split()
        misspelled = SPELLCHECKER_PT.unknown(palavras)

        if not misspelled:
            return texto, ""  # Sem erros

        # Corrige as palavras erradas com a sugestão mais provável
        texto_corrigido = texto
        for palavra_errada in misspelled:
            if len(palavra_errada) > 1:
                sugestoes = SPELLCHECKER_PT.candidates(palavra_errada)
                if sugestoes:
                    melhor_sugestao = SPELLCHECKER_PT.correction(palavra_errada)
                    if melhor_sugestao and melhor_sugestao != palavra_errada:
                        # Substitui a palavra preservando maiúsculas no início se houver
                        texto_corrigido = texto_corrigido.replace(
                            palavra_errada, melhor_sugestao, 1
                        )

        return texto_corrigido, ""
    except Exception as e:
        return texto, f"Erro ao corrigir com spellchecker local: {str(e)[:100]}"


def _corrigir_texto_com_api(texto: str) -> Tuple[str, str]:
    """Corrige ortografia usando a API jspell-checker da RapidAPI com fallback para local."""
    if not texto.strip():
        return texto, ""

    # Se há chave de API, tenta usar primeiro
    if JSPELL_API_KEY:
        headers = {
            "Content-Type": "application/json",
            "x-rapidapi-host": JSPELL_API_HOST,
            "x-rapidapi-key": JSPELL_API_KEY,
        }

        payloads = [
            {"language": "pt-BR", "text": texto},
            {"language": "pt", "text": texto},
            {"text": texto},
        ]

        for body in payloads:
            try:
                response = requests.post(
                    JSPELL_API_URL,
                    json=body,
                    headers=headers,
                    timeout=JSPELL_TIMEOUT_SECONDS,
                )
                if response.status_code < 400:
                    data = response.json()
                    texto_corrigido = _extrair_texto_corrigido(data)
                    if texto_corrigido and texto_corrigido != "You are not subscribed to this API.":
                        return texto_corrigido, ""
            except (requests.RequestException, ValueError):
                pass

    # Fallback: usa corretor local se disponível
    if SPELLCHECKER_DISPONIVEL:
        return _corrigir_com_spellchecker_local(texto)

    # Se nada funcionar, retorna texto original
    return texto, "Sem acesso à API e sem corretor local disponível"


def _corrigir_texto_com_api_antigo(texto: str) -> Tuple[str, str]:
    """Versão anterior mantida apenas para compatibilidade."""
    return _corrigir_texto_com_api(texto)


def _processar_upload_imagem(uploaded_file) -> Tuple[bytes, str, str]:
    """Valida upload de imagem e retorna bytes, mime type e nome."""
    if not uploaded_file:
        return b"", "", ""

    imagem_bytes = uploaded_file.getvalue()
    if not imagem_bytes:
        return b"", "", ""

    if len(imagem_bytes) > 5 * 1024 * 1024:
        raise ValueError("A imagem deve ter no máximo 5 MB.")

    imagem_mime = (uploaded_file.type or "").lower()
    if not imagem_mime.startswith("image/"):
        raise ValueError("Arquivo inválido. Envie um arquivo de imagem.")

    imagem_nome = uploaded_file.name or "imagem-comunicado"
    return imagem_bytes, imagem_mime, imagem_nome


def _gerar_html_email(
    titulo: str,
    data_evento: str,
    conteudo: str,
    imagem_bytes: bytes = b"",
    imagem_mime: str = "",
    imagem_nome: str = "",
) -> str:
    """Cria template HTML estilizado para envio da newsletter."""
    data_fmt = datetime.strptime(data_evento, "%Y-%m-%d").strftime("%d/%m/%Y")
    conteudo_html = "<br>".join(
        linha.strip() for linha in conteudo.splitlines() if linha.strip()
    )
    imagem_html = ""
    if imagem_bytes:
        mime = imagem_mime or "image/jpeg"
        nome_seguro = (imagem_nome or "imagem-comunicado").replace('"', "")
        imagem_b64 = base64.b64encode(imagem_bytes).decode("ascii")
        imagem_html = f"""
                    <div style="margin:0 0 18px 0;text-align:center;">
                      <img src="data:{mime};base64,{imagem_b64}" alt="{nome_seguro}" style="max-width:100%;height:auto;border-radius:10px;border:1px solid #d9e9f8;" />
                    </div>
        """

    return f"""
    <html>
      <body style="margin:0;padding:0;background:#f4f7fb;font-family:Segoe UI,Tahoma,sans-serif;color:#24323f;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:24px 12px;">
          <tr>
            <td align="center">
              <table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #d9e4f2;">
                <tr>
                  <td style="background:linear-gradient(120deg,#134074,#1b7ebd);padding:26px 28px;color:#ffffff;">
                    <p style="margin:0;font-size:12px;letter-spacing:1px;text-transform:uppercase;opacity:.9;">Comunicado Oficial</p>
                    <h1 style="margin:8px 0 0 0;font-size:28px;line-height:1.2;">{titulo}</h1>
                  </td>
                </tr>
                <tr>
                  <td style="padding:26px 28px;">
                    <p style="margin:0 0 8px 0;font-size:14px;color:#4f6273;"><strong>Data do evento:</strong> {data_fmt}</p>
                                        {imagem_html}
                    <div style="padding:18px;background:#f7fbff;border:1px solid #d9e9f8;border-radius:10px;font-size:15px;line-height:1.65;color:#22313f;">
                      {conteudo_html}
                    </div>
                    <p style="margin:22px 0 0 0;font-size:13px;color:#5c6f80;">Este e-mail foi enviado automaticamente pelo sistema de Dízimos e Ofertas.</p>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </body>
    </html>
    """


def _enviar_email_newsletter(destinatarios: List[str], assunto: str, html: str) -> Tuple[bool, str]:
    """Envia a newsletter usando o serviço SMTP compartilhado."""
    texto_plano = "Comunicado da igreja. Visualize este e-mail em modo HTML para melhor experiência."
    return enviar_email_html(destinatarios, assunto, html, texto_plano)


def _gerar_pdf_newsletter(
    titulo: str,
    data_evento: str,
    conteudo: str,
    imagem_bytes: bytes = b"",
) -> bytes:
    """Gera PDF da newsletter para download."""
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
        "TituloNewsletter",
        parent=styles["Heading1"],
        fontSize=20,
        textColor=colors.HexColor("#12355b"),
        spaceAfter=10,
    )
    estilo_data = ParagraphStyle(
        "DataEvento",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#3d5366"),
        spaceAfter=8,
    )
    estilo_texto = ParagraphStyle(
        "TextoConteudo",
        parent=styles["Normal"],
        fontSize=11,
        leading=17,
        textColor=colors.HexColor("#1e2a36"),
    )

    data_fmt = datetime.strptime(data_evento, "%Y-%m-%d").strftime("%d/%m/%Y")
    linhas_conteudo = [linha.strip() for linha in conteudo.splitlines() if linha.strip()]

    blocos = [
        Paragraph("Newsletter e Comunicados", estilo_data),
        Paragraph(titulo, estilo_titulo),
        Paragraph(f"Data do Evento: <b>{data_fmt}</b>", estilo_data),
    ]

    if imagem_bytes:
        try:
            imagem_pdf = RLImage(io.BytesIO(imagem_bytes))
            max_largura = doc.width
            max_altura = 12 * cm

            if imagem_pdf.drawWidth > max_largura:
                fator = max_largura / float(imagem_pdf.drawWidth)
                imagem_pdf.drawWidth = max_largura
                imagem_pdf.drawHeight = imagem_pdf.drawHeight * fator

            if imagem_pdf.drawHeight > max_altura:
                fator = max_altura / float(imagem_pdf.drawHeight)
                imagem_pdf.drawHeight = max_altura
                imagem_pdf.drawWidth = imagem_pdf.drawWidth * fator

            blocos.append(Spacer(1, 0.2 * cm))
            blocos.append(imagem_pdf)
            blocos.append(Spacer(1, 0.35 * cm))
        except Exception:
            blocos.append(Paragraph("Imagem não pôde ser renderizada no PDF.", estilo_data))

    for linha in linhas_conteudo:
        bloco_seguro = (
            linha.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        blocos.append(Paragraph(bloco_seguro, estilo_texto))
        blocos.append(Spacer(1, 0.18 * cm))

    blocos.append(Spacer(1, 0.6 * cm))
    blocos.append(
        Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            estilo_data,
        )
    )

    doc.build(blocos)
    return buffer.getvalue()


def _habilitar_spellcheck_nativo() -> None:
    """Ativa spellcheck do navegador (pt-BR) nos campos de texto da página."""
    st.html(
        """
        <div style="display:none"></div>
        <script>
            (function () {
                const applySpellcheck = () => {
                    const campos = window.parent.document.querySelectorAll("textarea, input[type='text']");
                    campos.forEach((el) => {
                        el.setAttribute("spellcheck", "true");
                        el.setAttribute("lang", "pt-BR");
                        el.setAttribute("autocapitalize", "sentences");
                        el.setAttribute("autocomplete", "on");
                    });
                };

                applySpellcheck();
                if (!window.__newsletterSpellcheckInterval) {
                    window.__newsletterSpellcheckInterval = setInterval(applySpellcheck, 1200);
                }
            })();
        </script>
        """,
        unsafe_allow_javascript=True,
        )


def exibir_pagina_newsletter():
    """Renderiza a página de newsletter."""
    st.title("📰 Newsletter e Comunicados")
    usuario = st.session_state.get("usuario", "sistema")
    nivel = st.session_state.get("nivel", "visualizador")
    if nivel == "admin":
        st.caption("Crie, publique, envie por e-mail e disponibilize comunicados em PDF.")
    else:
        st.caption("Crie, publique e gerencie apenas os comunicados criados por voce.")
    _habilitar_spellcheck_nativo()

    aba_criar, aba_historico = st.tabs(["✍️ Criar e Publicar", "📚 Histórico"])

    with aba_criar:
        mensagem_newsletter = st.session_state.pop("newsletter_flash", None)
        if mensagem_newsletter:
            tipo_mensagem = mensagem_newsletter.get("tipo", "info")
            texto_mensagem = mensagem_newsletter.get("texto", "")
            if tipo_mensagem == "success":
                st.success(texto_mensagem)
            elif tipo_mensagem == "warning":
                st.warning(texto_mensagem)
            elif tipo_mensagem == "error":
                st.error(texto_mensagem)
            else:
                st.info(texto_mensagem)

        # Estado do formulário para permitir limpeza automática após publicar
        if "newsletter_reset_form" not in st.session_state:
            st.session_state["newsletter_reset_form"] = False
        if "newsletter_form_version" not in st.session_state:
            st.session_state["newsletter_form_version"] = 0

        if st.session_state["newsletter_reset_form"]:
            st.session_state["newsletter_titulo_input"] = ""
            st.session_state["newsletter_data_input"] = date.today()
            st.session_state["newsletter_conteudo_input"] = ""
            st.session_state["newsletter_enviar_email_input"] = False
            st.session_state["newsletter_assunto_email_input"] = ""
            st.session_state["newsletter_usa_emails_membros_input"] = False
            st.session_state["newsletter_destinatarios_input"] = ""
            st.session_state["newsletter_publicado_input"] = True
            st.session_state["newsletter_form_version"] += 1
            st.session_state["newsletter_reset_form"] = False

        if "newsletter_data_input" not in st.session_state:
            st.session_state["newsletter_data_input"] = date.today()
        if "newsletter_enviar_email_input" not in st.session_state:
            st.session_state["newsletter_enviar_email_input"] = False
        if "newsletter_usa_emails_membros_input" not in st.session_state:
            st.session_state["newsletter_usa_emails_membros_input"] = False
        if "newsletter_publicado_input" not in st.session_state:
            st.session_state["newsletter_publicado_input"] = True

        with st.form("form_newsletter"):
            st.subheader("Novo comunicado")

            titulo = st.text_input(
                "Título do comunicado",
                placeholder="Ex.: Encontro de Casais e Jantar Comunitário",
                key="newsletter_titulo_input",
            )
            data_evento = st.date_input(
                "Data do evento",
                format="DD/MM/YYYY",
                key="newsletter_data_input",
            )

            imagem_upload = st.file_uploader(
                "Imagem do comunicado (opcional)",
                type=["png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff"],
                help="Formatos aceitos: PNG, JPG, JPEG, WEBP, GIF, BMP, TIF e TIFF. Máximo de 5 MB.",
                key=f"newsletter_imagem_input_{st.session_state['newsletter_form_version']}",
            )
            if imagem_upload:
                st.image(imagem_upload, caption="Pré-visualização da imagem", width="stretch")

            conteudo = st.text_area(
                "Mensagem completa",
                placeholder="Descreva todos os detalhes do evento, horários, local e orientações.",
                height=220,
                key="newsletter_conteudo_input",
            )

            st.markdown("### ✉️ Opções de e-mail")
            enviar_email = st.checkbox(
                "Enviar por e-mail após publicar",
                key="newsletter_enviar_email_input",
            )
            assunto_email = st.text_input(
                "Assunto do e-mail",
                placeholder="Ex.: Comunicado oficial - Evento da semana",
                key="newsletter_assunto_email_input",
            )
            usar_emails_membros = st.checkbox(
                "Usar e-mails cadastrados dos membros",
                key="newsletter_usa_emails_membros_input",
            )

            emails_membros_selecionados = []
            if usar_emails_membros:
                emails_membros = _obter_emails_membros()
                if emails_membros:
                    emails_membros_selecionados = st.multiselect(
                        "Selecione os membros que receberão o comunicado",
                        options=emails_membros,
                        default=emails_membros,
                        key="newsletter_emails_membros_selecionados",
                    )
                else:
                    st.info("Não há e-mails válidos cadastrados em membros.")

            destinatarios_raw = st.text_area(
                "Destinatários (separe por vírgula, ponto e vírgula ou linha)",
                placeholder="membro1@email.com; membro2@email.com",
                height=90,
                key="newsletter_destinatarios_input",
            )

            publicado = st.checkbox(
                "Publicar imediatamente",
                key="newsletter_publicado_input",
            )
            submitted = st.form_submit_button("🚀 Publicar comunicado", width="stretch")

        # Processar botão "Publicar comunicado"
        if submitted:
            if not titulo.strip():
                st.error("Informe o título do comunicado.")
                return

            if not conteudo.strip():
                st.error("Informe a mensagem completa do comunicado.")
                return

            try:
                imagem_bytes, imagem_mime, imagem_nome = _processar_upload_imagem(imagem_upload)
            except ValueError as e:
                st.error(str(e))
                return

            texto_combinado_destinatarios = destinatarios_raw
            if emails_membros_selecionados:
                texto_combinado_destinatarios = ", ".join(emails_membros_selecionados + [destinatarios_raw])

            validos, invalidos = _parse_emails(texto_combinado_destinatarios)
            if enviar_email and not validos:
                st.error("Para enviar e-mail, informe ao menos um destinatário válido.")
                return

            if invalidos:
                st.warning(f"Alguns e-mails foram ignorados por formato inválido: {', '.join(invalidos)}")

            assunto_final = assunto_email.strip() or f"Comunicado: {titulo.strip()}"

            newsletter_id = criar_newsletter(
                titulo=titulo,
                data_evento=data_evento.strftime("%Y-%m-%d"),
                resumo="",
                conteudo=conteudo,
                assunto_email=assunto_final,
                criado_por=st.session_state.get("usuario", "sistema"),
                publicado=publicado,
            )

            if not newsletter_id:
                st.error("Não foi possível salvar o comunicado.")
                return

            msg_sucesso = f"Comunicado publicado com sucesso. ID: {newsletter_id}"
            falha_envio_email = False
            mensagem_falha_email = ""

            if enviar_email:
                html = _gerar_html_email(
                    titulo=titulo,
                    data_evento=data_evento.strftime("%Y-%m-%d"),
                    conteudo=conteudo,
                    imagem_bytes=imagem_bytes,
                    imagem_mime=imagem_mime,
                    imagem_nome=imagem_nome,
                )
                ok, msg = _enviar_email_newsletter(validos, assunto_final, html)
                if ok:
                    marcar_email_enviado(newsletter_id)
                    msg_sucesso = f"{msg_sucesso} {msg}"
                else:
                    falha_envio_email = True
                    mensagem_falha_email = msg

            pdf_bytes = _gerar_pdf_newsletter(
                titulo=titulo,
                data_evento=data_evento.strftime("%Y-%m-%d"),
                conteudo=conteudo,
                imagem_bytes=imagem_bytes,
            )
            st.session_state["newsletter_pdf_ultimo"] = pdf_bytes
            st.session_state["newsletter_pdf_nome"] = f"newsletter_{newsletter_id}.pdf"
            if falha_envio_email:
                st.session_state["newsletter_flash"] = {
                    "tipo": "warning",
                    "texto": f"{msg_sucesso} O comunicado foi salvo, mas o e-mail não foi enviado. Detalhe: {mensagem_falha_email}",
                }
            else:
                st.session_state["newsletter_reset_form"] = True
                st.session_state["newsletter_flash"] = {
                    "tipo": "success",
                    "texto": f"{msg_sucesso} Campos limpos para nova publicação.",
                }
            st.rerun()

        if st.session_state.get("newsletter_pdf_ultimo"):
            st.markdown("---")
            st.markdown("#### Último PDF gerado")
            baixou_pdf = st.download_button(
                label="⬇️ Baixar PDF do último comunicado publicado",
                data=st.session_state["newsletter_pdf_ultimo"],
                file_name=st.session_state.get("newsletter_pdf_nome", "newsletter_publicado.pdf"),
                mime="application/pdf",
                key="download_ultimo_pdf_publicado",
                width="stretch",
            )
            if baixou_pdf:
                st.session_state.pop("newsletter_pdf_ultimo", None)
                st.session_state.pop("newsletter_pdf_nome", None)
                st.rerun()

    with aba_historico:
        st.subheader("Comunicados recentes")
        newsletters = listar_newsletters(limit=100, criado_por=None if nivel == "admin" else usuario)

        if not newsletters:
            st.info("Nenhum comunicado publicado até o momento.")
            return

        for row in newsletters:
            data_fmt = datetime.strptime(row["data_evento"], "%Y-%m-%d").strftime("%d/%m/%Y")
            status_publicacao = "Publicado" if row["publicado"] else "Rascunho"
            status_email = "E-mail enviado" if row["email_enviado"] else "E-mail pendente"

            with st.expander(f"{row['titulo']} • {data_fmt}"):
                st.markdown(f"**Status:** {status_publicacao} | {status_email}")
                if row["resumo"]:
                    st.markdown(f"**Resumo:** {row['resumo']}")
                st.markdown("**Mensagem:**")
                st.write(row["conteudo"])

                with st.form(f"editar_news_{row['id']}"):
                    st.markdown("#### Editar comunicado")
                    titulo_edit = st.text_input("Título", value=row["titulo"], key=f"news_titulo_edit_{row['id']}")
                    data_edit = st.date_input(
                        "Data do evento",
                        value=datetime.strptime(row["data_evento"], "%Y-%m-%d").date(),
                        format="DD/MM/YYYY",
                        key=f"data_edit_{row['id']}",
                    )
                    resumo_edit = st.text_area(
                        "Resumo",
                        value=row["resumo"] or "",
                        key=f"resumo_edit_{row['id']}",
                        height=80,
                    )
                    conteudo_edit = st.text_area(
                        "Mensagem",
                        value=row["conteudo"],
                        key=f"conteudo_edit_{row['id']}",
                        height=180,
                    )
                    assunto_edit = st.text_input(
                        "Assunto de e-mail",
                        value=row["assunto_email"] or f"Comunicado: {row['titulo']}",
                        key=f"assunto_edit_{row['id']}",
                    )
                    publicado_edit = st.checkbox(
                        "Publicado",
                        value=bool(row["publicado"]),
                        key=f"publicado_edit_{row['id']}",
                    )
                    salvar_edit = st.form_submit_button("💾 Salvar alterações", width="stretch")

                if salvar_edit:
                    if not titulo_edit.strip() or not conteudo_edit.strip():
                        st.error("Título e mensagem são obrigatórios para salvar.")
                    else:
                        ok = atualizar_newsletter(
                            newsletter_id=int(row["id"]),
                            titulo=titulo_edit,
                            data_evento=data_edit.strftime("%Y-%m-%d"),
                            resumo=resumo_edit,
                            conteudo=conteudo_edit,
                            assunto_email=assunto_edit,
                            publicado=publicado_edit,
                            criado_por=None if nivel == "admin" else usuario,
                        )
                        if ok:
                            st.success("Comunicado atualizado com sucesso.")
                            st.rerun()
                        else:
                            st.error("Não foi possível atualizar o comunicado ou a permissão é insuficiente.")

                pdf_bytes = _gerar_pdf_newsletter(
                    titulo=row["titulo"],
                    data_evento=row["data_evento"],
                    conteudo=row["conteudo"],
                )
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"newsletter_{row['id']}.pdf",
                    mime="application/pdf",
                    key=f"pdf_news_{row['id']}",
                    width="stretch",
                )

                st.markdown("#### Reenviar por e-mail")
                destinatarios_reenvio = st.text_area(
                    "Destinatários",
                    key=f"dest_{row['id']}",
                    placeholder="email1@dominio.com, email2@dominio.com",
                    height=80,
                )
                if st.button("✉️ Reenviar agora", key=f"reenviar_{row['id']}", width="stretch"):
                    validos, invalidos = _parse_emails(destinatarios_reenvio)
                    if not validos:
                        st.error("Informe destinatários válidos para reenviar.")
                    else:
                        if invalidos:
                            st.warning(f"E-mails ignorados: {', '.join(invalidos)}")

                        assunto = row["assunto_email"] or f"Comunicado: {row['titulo']}"
                        html = _gerar_html_email(
                            titulo=row["titulo"],
                            data_evento=row["data_evento"],
                            conteudo=row["conteudo"],
                        )
                        ok, msg = _enviar_email_newsletter(validos, assunto, html)
                        if ok:
                            marcar_email_enviado(int(row["id"]))
                            st.success(msg)
                        else:
                            st.error(msg)

                st.markdown("#### Excluir comunicado")
                confirmar_exclusao = st.checkbox(
                    "Confirmo que desejo excluir este comunicado",
                    key=f"confirm_del_{row['id']}",
                )
                if st.button(
                    "🗑️ Excluir comunicado",
                    key=f"delete_{row['id']}",
                    width="stretch",
                    disabled=not confirmar_exclusao,
                ):
                    ok = excluir_newsletter(int(row["id"]), None if nivel == "admin" else usuario)
                    if ok:
                        st.success("Comunicado excluído com sucesso.")
                        st.rerun()
                    else:
                        st.error("Não foi possível excluir o comunicado ou a permissão é insuficiente.")