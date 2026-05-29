"""
Página de Calendário de Eventos.
"""
import smtplib
from datetime import date, datetime, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Tuple

import streamlit as st

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
from database_calendario import (
    atualizar_evento,
    criar_evento,
    excluir_evento,
    listar_eventos,
)
from database_membros import obter_membros
from notifications import validar_email

try:
    from streamlit_calendar import calendar
    CALENDAR_WIDGET_DISPONIVEL = True
except Exception:
    CALENDAR_WIDGET_DISPONIVEL = False


def _parse_emails(raw: str) -> Tuple[List[str], List[str]]:
    if not raw:
        return [], []

    candidatos = []
    for pedaco in raw.replace(";", ",").replace("\n", ",").split(","):
        email = pedaco.strip()
        if email:
            candidatos.append(email)

    validos = []
    invalidos = []
    for email in candidatos:
        if validar_email(email):
            validos.append(email)
        else:
            invalidos.append(email)

    return list(dict.fromkeys(validos)), list(dict.fromkeys(invalidos))


def _obter_emails_membros() -> List[str]:
    membros = obter_membros()
    emails = []
    for m in membros:
        email = (m["email"] or "").strip() if "email" in m.keys() else ""
        if email and validar_email(email):
            emails.append(email)
    return list(dict.fromkeys(emails))


def _evento_db_para_fullcalendar(row) -> dict:
    inicio = row["inicio"]
    fim = row["fim"]
    all_day = bool(row["dia_todo"])

    evento = {
        "id": str(row["id"]),
        "title": row["titulo"],
        "start": inicio,
        "allDay": all_day,
        "backgroundColor": row["cor"] or "#1b7ebd",
        "borderColor": row["cor"] or "#1b7ebd",
        "extendedProps": {
            "descricao": row["descricao"] or "",
            "local": row["local"] or "",
            "criado_por": row["criado_por"] or "",
        },
    }

    if fim:
        evento["end"] = fim

    return evento


def _formatar_agenda_html(eventos: list, data_inicio: date, data_fim: date) -> str:
    itens = []
    for e in eventos:
        inicio_dt = datetime.fromisoformat(e["inicio"])
        dia_todo = bool(e["dia_todo"])
        data_txt = inicio_dt.strftime("%d/%m/%Y")
        hora_txt = "Dia todo" if dia_todo else inicio_dt.strftime("%H:%M")
        local_txt = e["local"] or "Não informado"
        desc_txt = e["descricao"] or "Sem descrição"
        itens.append(
            f"""
            <tr>
              <td style='padding:10px;border-bottom:1px solid #e6eef5;'>{data_txt}</td>
              <td style='padding:10px;border-bottom:1px solid #e6eef5;'>{hora_txt}</td>
              <td style='padding:10px;border-bottom:1px solid #e6eef5;'><strong>{e['titulo']}</strong></td>
              <td style='padding:10px;border-bottom:1px solid #e6eef5;'>{local_txt}</td>
              <td style='padding:10px;border-bottom:1px solid #e6eef5;'>{desc_txt}</td>
            </tr>
            """
        )

    linhas = "\n".join(itens) if itens else "<tr><td colspan='5' style='padding:12px;'>Nenhum evento no período selecionado.</td></tr>"

    return f"""
    <html>
      <body style="font-family:Segoe UI,Tahoma,sans-serif;background:#f6f9fc;padding:16px;color:#22313f;">
        <div style="max-width:860px;margin:0 auto;background:#fff;border:1px solid #dde6f0;border-radius:12px;overflow:hidden;">
          <div style="background:linear-gradient(120deg,#12355b,#1b7ebd);padding:20px;color:#fff;">
            <h2 style="margin:0;">Agenda de Eventos</h2>
            <p style="margin:8px 0 0 0;opacity:.92;">Período: {data_inicio.strftime('%d/%m/%Y')} até {data_fim.strftime('%d/%m/%Y')}</p>
          </div>
          <div style="padding:18px;">
            <table width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;font-size:14px;">
              <thead>
                <tr style="background:#f0f6fb;">
                  <th align="left" style="padding:10px;">Data</th>
                  <th align="left" style="padding:10px;">Hora</th>
                  <th align="left" style="padding:10px;">Título</th>
                  <th align="left" style="padding:10px;">Local</th>
                  <th align="left" style="padding:10px;">Descrição</th>
                </tr>
              </thead>
              <tbody>
                {linhas}
              </tbody>
            </table>
          </div>
        </div>
      </body>
    </html>
    """


def _enviar_agenda_por_email(destinatarios: List[str], assunto: str, html: str) -> Tuple[bool, str]:
    if not SMTP_ENABLED:
        return False, "Envio de e-mail desativado. Configure SMTP_ENABLED=true no .env."

    if not all([SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM_EMAIL]):
        return False, "Configuração SMTP incompleta. Verifique SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD e SMTP_FROM_EMAIL."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    msg["To"] = ", ".join(destinatarios)

    texto = "Agenda de eventos da igreja. Abra em HTML para melhor visualização."
    msg.attach(MIMEText(texto, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            if SMTP_USE_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM_EMAIL, destinatarios, msg.as_string())
        return True, f"Agenda enviada para {len(destinatarios)} destinatário(s)."
    except Exception as e:
        return False, f"Falha ao enviar agenda por e-mail: {e}"


def exibir_pagina_calendario() -> None:
    st.title("📅 Calendário de Eventos")
    usuario = st.session_state.get("usuario", "sistema")
    nivel = st.session_state.get("nivel", "visualizador")
    if nivel == "admin":
        st.caption("Consulte eventos no calendário, crie novos eventos e envie a agenda por e-mail.")
    else:
        st.caption("Consulte e gerencie apenas os eventos criados por voce.")

    abas = st.tabs(["📆 Calendário", "➕ Criar Evento", "📨 Enviar Agenda"])

    eventos_db = listar_eventos(limit=500, criado_por=None if nivel == "admin" else usuario)

    with abas[0]:
        st.subheader("Consulta de eventos")

        eventos_fc = [_evento_db_para_fullcalendar(r) for r in eventos_db]

        if CALENDAR_WIDGET_DISPONIVEL:
            options = {
                "initialView": "dayGridMonth",
                "height": 680,
                "locale": "pt-br",
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek",
                },
                "buttonText": {
                    "today": "Hoje",
                    "month": "Mês",
                    "week": "Semana",
                    "day": "Dia",
                    "list": "Lista",
                },
                "eventDisplay": "block",
                "eventTimeFormat": {"hour": "2-digit", "minute": "2-digit", "hour12": False},
                "slotMinTime": "06:00:00",
                "slotMaxTime": "23:00:00",
            }

            custom_css = """
            :root {
              --fc-border-color: #d8e3ef;
              --fc-today-bg-color: rgba(27, 126, 189, 0.10);
              --fc-page-bg-color: #ffffff;
            }
            .fc .fc-toolbar-title {
              font-size: 1.15rem;
              color: #12355b;
            }
            """

            state = calendar(
                events=eventos_fc,
                options=options,
                custom_css=custom_css,
                key="calendario_eventos_widget",
            )

            if state and isinstance(state, dict) and state.get("eventClick"):
                evento_clicado = state["eventClick"].get("event", {})
                st.info(f"Evento selecionado: {evento_clicado.get('title', '')}")
        else:
            st.warning(
                "Widget FullCalendar indisponível. Instale 'streamlit-calendar' para visualização completa."
            )

        if eventos_db:
            st.markdown("### Próximos eventos")
            for row in sorted(eventos_db, key=lambda x: x["inicio"])[:10]:
                ini = datetime.fromisoformat(row["inicio"])
                data_txt = ini.strftime("%d/%m/%Y")
                hora_txt = "Dia todo" if row["dia_todo"] else ini.strftime("%H:%M")
                st.write(f"- **{data_txt} {hora_txt}** · {row['titulo']} ({row['local'] or 'Local não informado'})")
        else:
            st.info("Nenhum evento cadastrado ainda.")

    with abas[1]:
        st.subheader("Novo evento")

        with st.form("form_criar_evento"):
            titulo = st.text_input("Título do evento")
            descricao = st.text_area("Descrição")
            local = st.text_input("Local")
            dia_todo = st.checkbox("Evento para o dia todo", value=False)
            cor = st.color_picker("Cor do evento", value="#1b7ebd")

            col_a, col_b = st.columns(2)
            with col_a:
                data_inicio = st.date_input("Data de início", value=date.today(), format="DD/MM/YYYY")
                hora_inicio = st.time_input("Hora de início", value=time(19, 0), disabled=dia_todo)

            with col_b:
                data_fim = st.date_input("Data de término", value=data_inicio, format="DD/MM/YYYY")
                hora_fim = st.time_input("Hora de término", value=time(21, 0), disabled=dia_todo)

            salvar_evento = st.form_submit_button("💾 Salvar evento", width="stretch")

        if salvar_evento:
            if not titulo.strip():
                st.error("Informe o título do evento.")
            else:
                if dia_todo:
                    inicio_iso = datetime.combine(data_inicio, time.min).isoformat()
                    fim_iso = datetime.combine(data_fim, time.min).isoformat()
                else:
                    inicio_dt = datetime.combine(data_inicio, hora_inicio)
                    fim_dt = datetime.combine(data_fim, hora_fim)
                    if fim_dt < inicio_dt:
                        st.error("Data/hora de término não pode ser menor que início.")
                        return
                    inicio_iso = inicio_dt.isoformat()
                    fim_iso = fim_dt.isoformat()

                novo_id = criar_evento(
                    titulo=titulo,
                    descricao=descricao,
                    local=local,
                    inicio_iso=inicio_iso,
                    fim_iso=fim_iso,
                    dia_todo=dia_todo,
                    cor=cor,
                    criado_por=st.session_state.get("usuario", "sistema"),
                )
                if novo_id:
                    st.success(f"Evento criado com sucesso! ID: {novo_id}")
                    st.rerun()
                else:
                    st.error("Não foi possível criar o evento.")

        st.markdown("### Gerenciar eventos")
        if not eventos_db:
            st.info("Cadastre um evento para habilitar edição e exclusão.")
        else:
            opcoes = [
                f"#{r['id']} · {r['titulo']} · {datetime.fromisoformat(r['inicio']).strftime('%d/%m/%Y %H:%M')}"
                for r in eventos_db
            ]
            idx = st.selectbox("Selecione um evento", options=list(range(len(opcoes))), format_func=lambda i: opcoes[i])
            evento = eventos_db[idx]

            with st.form(f"form_editar_evento_{evento['id']}"):
                t2 = st.text_input("Título", value=evento["titulo"], key=f"evento_titulo_{evento['id']}")
                d2 = st.text_area("Descrição", value=evento["descricao"] or "")
                l2 = st.text_input("Local", value=evento["local"] or "", key=f"evento_local_{evento['id']}")
                a2 = st.checkbox("Dia todo", value=bool(evento["dia_todo"]))
                c2 = st.color_picker("Cor", value=evento["cor"] or "#1b7ebd")

                ini_dt = datetime.fromisoformat(evento["inicio"])
                fim_dt = datetime.fromisoformat(evento["fim"]) if evento["fim"] else ini_dt

                ca, cb = st.columns(2)
                with ca:
                    di2 = st.date_input("Data início", value=ini_dt.date(), format="DD/MM/YYYY", key=f"di_{evento['id']}")
                    hi2 = st.time_input("Hora início", value=ini_dt.time(), key=f"hi_{evento['id']}", disabled=a2)
                with cb:
                    df2 = st.date_input("Data fim", value=fim_dt.date(), format="DD/MM/YYYY", key=f"df_{evento['id']}")
                    hf2 = st.time_input("Hora fim", value=fim_dt.time(), key=f"hf_{evento['id']}", disabled=a2)

                col_editar, col_excluir = st.columns(2)
                with col_editar:
                    atualizar_btn = st.form_submit_button("✏️ Atualizar", width="stretch")
                with col_excluir:
                    excluir_btn = st.form_submit_button("🗑️ Excluir", width="stretch")

            if atualizar_btn:
                if a2:
                    ini2 = datetime.combine(di2, time.min)
                    fim2 = datetime.combine(df2, time.min)
                else:
                    ini2 = datetime.combine(di2, hi2)
                    fim2 = datetime.combine(df2, hf2)

                if fim2 < ini2:
                    st.error("Data/hora de término não pode ser menor que início.")
                else:
                    ok = atualizar_evento(
                        evento_id=int(evento["id"]),
                        titulo=t2,
                        descricao=d2,
                        local=l2,
                        inicio_iso=ini2.isoformat(),
                        fim_iso=fim2.isoformat(),
                        dia_todo=a2,
                        cor=c2,
                        criado_por=None if nivel == "admin" else usuario,
                    )
                    if ok:
                        st.success("Evento atualizado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Falha ao atualizar evento ou permissão insuficiente.")

            if excluir_btn:
                ok = excluir_evento(int(evento["id"]), None if nivel == "admin" else usuario)
                if ok:
                    st.success("Evento excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("Falha ao excluir evento ou permissão insuficiente.")

    with abas[2]:
        st.subheader("Enviar agenda por e-mail")

        if not eventos_db:
            st.info("Não há eventos cadastrados para enviar.")
        else:
            col_i, col_f = st.columns(2)
            with col_i:
                de = st.date_input("Período inicial", value=date.today(), format="DD/MM/YYYY")
            with col_f:
                ate = st.date_input("Período final", value=date.today(), format="DD/MM/YYYY")

            if ate < de:
                st.warning("Período final deve ser maior ou igual ao inicial.")
                return

            inicio_limite = datetime.combine(de, time.min)
            fim_limite = datetime.combine(ate, time.max)
            eventos_periodo = [
                e for e in eventos_db
                if datetime.fromisoformat(e["inicio"]) <= fim_limite
                and datetime.fromisoformat(e["fim"] or e["inicio"]) >= inicio_limite
            ]

            st.write(f"Eventos no período: **{len(eventos_periodo)}**")

            usar_emails_membros = st.checkbox("Usar e-mails dos membros", value=False)
            emails_membros_selecionados = []
            if usar_emails_membros:
                emails_membros = _obter_emails_membros()
                if emails_membros:
                    emails_membros_selecionados = st.multiselect(
                        "Selecione os membros destinatários",
                        options=emails_membros,
                        default=emails_membros,
                    )
                else:
                    st.info("Não há e-mails válidos cadastrados nos membros.")

            destinatarios_raw = st.text_area(
                "Destinatários adicionais (vírgula, ponto e vírgula ou linha)",
                placeholder="email1@dominio.com; email2@dominio.com",
                height=90,
            )

            assunto = st.text_input(
                "Assunto do e-mail",
                value=f"Agenda da igreja · {de.strftime('%d/%m/%Y')} a {ate.strftime('%d/%m/%Y')}",
            )

            if st.button("📨 Enviar agenda por e-mail", width="stretch"):
                texto_dest = destinatarios_raw
                if emails_membros_selecionados:
                    texto_dest = ", ".join(emails_membros_selecionados + [destinatarios_raw])

                validos, invalidos = _parse_emails(texto_dest)

                if invalidos:
                    st.warning(f"E-mails inválidos ignorados: {', '.join(invalidos)}")

                if not validos:
                    st.error("Informe ao menos um destinatário válido.")
                else:
                    html = _formatar_agenda_html(eventos_periodo, de, ate)
                    ok, msg = _enviar_agenda_por_email(validos, assunto, html)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
