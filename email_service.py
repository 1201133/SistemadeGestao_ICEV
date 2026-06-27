"""Serviços compartilhados de envio de e-mail via SMTP."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Tuple
import smtplib

from config import (
    SMTP_ENABLED,
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)


def enviar_email_html(destinatarios: List[str], assunto: str, html: str, texto_plano: str) -> Tuple[bool, str]:
    """Envia um e-mail em HTML com texto alternativo usando a configuração SMTP da aplicação."""
    if not SMTP_ENABLED:
        return False, "Envio de e-mail desativado. Configure SMTP_ENABLED=true no .env."

    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        return False, "Configuração SMTP incompleta. Verifique SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD e SMTP_FROM_EMAIL."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg["To"] = ", ".join(destinatarios)

    msg.attach(MIMEText(texto_plano, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, destinatarios, msg.as_string())
        return True, f"E-mail enviado para {len(destinatarios)} destinatário(s)."
    except Exception as e:
        return False, f"Falha ao enviar e-mail: {e}"