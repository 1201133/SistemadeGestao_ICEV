"""
Sistema de Gestão de Dízimos e Ofertas
Arquitetura Modular com Separação de Responsabilidades
Otimizado para Desktop e Mobile
"""
import streamlit as st
from streamlit_option_menu import option_menu
from datetime import date, datetime
import os
from typing import Callable
from PIL import Image

# Importações dos módulos personalizados
from config import PAGE_TITLE, PAGE_ICON, LAYOUT, FAVICON_PATH, USUARIOS_HASHES
from database import init_db
from auth import (
    verificar_login,
    login_esta_bloqueado,
    minutos_restantes_bloqueio,
    registrar_falha_login,
    sessao_expirada,
)
from utils import display_logo, exibir_usuario_info
from modules.visualizar import exibir_pagina_visualizar
from modules.registrar import exibir_pagina_registrar
from modules.editar import exibir_pagina_editar
from modules.membros import exibir_pagina_membros
from modules.duvidas import exibir_pagina_duvidas
from modules.aniversariantes import exibir_pagina_aniversariantes
from modules.certificado import exibir_pagina_certificado
from modules.permissoes import exibir_painel_permissoes
from modules.newsletter import exibir_pagina_newsletter
from modules.calendario import exibir_pagina_calendario
from mobile_config import aplicar_css_mobile
from permissions import usuario_tem_permissao
from database_financas import listar_contas

# Import seguro do módulo de finanças para não derrubar o app inteiro
# caso alguma dependência opcional não esteja disponível no ambiente.
FINANCAS_DISPONIVEL = False
FINANCAS_IMPORT_ERROR = ""


def _exibir_pagina_financas_indisponivel():
    """Fallback quando o módulo de finanças não puder ser importado."""
    st.error("❌ O módulo Gestão de Finanças está indisponível neste ambiente.")
    if FINANCAS_IMPORT_ERROR:
        st.caption(f"Detalhe técnico: {FINANCAS_IMPORT_ERROR}")


exibir_pagina_financas: Callable[[], None] = _exibir_pagina_financas_indisponivel

try:
    from modules.financas import exibir_pagina_financas as _exibir_pagina_financas
    exibir_pagina_financas = _exibir_pagina_financas
    FINANCAS_DISPONIVEL = True
except ImportError as exc:
    FINANCAS_IMPORT_ERROR = str(exc)
except Exception as exc:
    FINANCAS_IMPORT_ERROR = f"Falha ao carregar modulo de financas: {exc}"


def _saldo_pendente_conta(conta: tuple) -> float:
    """Calcula o saldo pendente da conta considerando parcelamento."""
    valor_total = float(conta[3])
    status = conta[6]
    num_parcelas = int(conta[8]) if conta[8] else 1
    parcelas_pagas = int(conta[9]) if conta[9] else 0

    if status == "Pago":
        return 0.0

    valor_parcela = valor_total / num_parcelas if num_parcelas > 0 else valor_total
    valor_pago = valor_parcela * parcelas_pagas
    return max(0.0, valor_total - valor_pago)


def _formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def exibir_alertas_financeiros(usuario: str, nivel: str):
    """Exibe alertas de contas próximas do vencimento e vencidas."""
    if not usuario_tem_permissao(usuario, "financas"):
        return

    try:
        contas = listar_contas(usuario, nivel)
    except Exception:
        return

    hoje = date.today()
    contas_vencidas = []
    contas_vencer = []

    for conta in contas:
        status = conta[6]
        if status == "Pago":
            continue

        try:
            data_venc = datetime.strptime(conta[2], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue

        dias = (data_venc - hoje).days
        saldo = _saldo_pendente_conta(conta)
        if saldo <= 0:
            continue

        if dias < 0:
            contas_vencidas.append((conta, abs(dias), saldo))
        elif dias <= 7:
            contas_vencer.append((conta, dias, saldo))

    if contas_vencidas:
        total_vencido = sum(item[2] for item in contas_vencidas)
        qtd = len(contas_vencidas)
        mais_antiga = max(item[1] for item in contas_vencidas)
        st.error(
            "🚨 Alerta crítico de finanças: "
            f"{qtd} conta(s) vencida(s), total pendente de {_formatar_brl(total_vencido)}. "
            f"Há conta em atraso há {mais_antiga} dia(s). "
            "Priorize a regularização para evitar juros e bloqueios de serviço."
        )

    if contas_vencer:
        total_a_vencer = sum(item[2] for item in contas_vencer)
        qtd = len(contas_vencer)
        menor_prazo = min(item[1] for item in contas_vencer)
        prazo_txt = "hoje" if menor_prazo == 0 else f"em {menor_prazo} dia(s)"
        st.warning(
            "⚠️ Atenção financeira: "
            f"{qtd} conta(s) vencem nos próximos 7 dias, somando {_formatar_brl(total_a_vencer)}. "
            f"Próximo vencimento {prazo_txt}. "
            "Organize o caixa para manter os pagamentos em dia."
        )


def exibir_tela_login():
    """Exibe a tela de login - otimizado para mobile"""
    # Proteção básica contra tentativa excessiva de login por sessão
    if "login_tentativas" not in st.session_state:
        st.session_state["login_tentativas"] = 0
    if "login_bloqueado_ate" not in st.session_state:
        st.session_state["login_bloqueado_ate"] = None

    # Centralizar conteúdo em mobile
    _, col2, _ = st.columns([1, 6, 1])
    
    with col2:
        # ── Logo Ministério Dehomai ──────────────────────────────────────
        logo_candidates = [
            "./imagem/imagen-ICEV-Login.png",
            "./imagem/imagem-ICEV-Login.png",
            "./imagem/logo-login.png",
        ]
        logo_login = next((path for path in logo_candidates if os.path.exists(path)), None)
        if logo_login and os.path.exists(logo_login):
            c1, c2, c3 = st.columns([1.5, 1, 1.5])
            with c2:
                st.image(logo_login, width="stretch")
        else:
            st.title("🔐 Login")

        # Verifica se hashes de usuário foram carregados via variáveis/secret store.
        if not any(USUARIOS_HASHES.values()):
            st.error("⚠️ **ERRO DE CONFIGURAÇÃO**")
            st.warning("""
            Os **hashes de usuários não foram carregados** neste ambiente.
            
            **Solução:**
            1. Se estiver no **Streamlit Community Cloud**: abra https://share.streamlit.io/ → **Manage app** → **Settings** → **Secrets**
            2. Configure os hashes no bloco `[passwords]` **ou** como chaves no topo:
               `USER_ADMIN_HASH`, `USER_DIACONO01_HASH`, `USER_DIACONO02_HASH`, `USER_DIACONO03_HASH`
            3. Se estiver local, configure o arquivo `.env` com essas mesmas chaves
            """)
            st.info("📖 Veja o guia completo: TROUBLESHOOTING_LOGIN.md")
        
        st.markdown("---")
        
        with st.form("login_form"):
            usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            
            st.markdown("""
            <style>
            .stFormSubmitButton button {
                width: 100%;
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            </style>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("🔐 Entrar", type="primary")
            
            if submitted:
                bloqueado_ate = st.session_state.get("login_bloqueado_ate")
                agora = datetime.now()
                if login_esta_bloqueado(bloqueado_ate, agora):
                    restante = minutos_restantes_bloqueio(bloqueado_ate, agora)
                    st.error(f"❌ Muitas tentativas inválidas. Tente novamente em {restante} minuto(s).")
                    return

                usuario_info = verificar_login(usuario, senha)
                if usuario_info:
                    st.session_state["login_tentativas"] = 0
                    st.session_state["login_bloqueado_ate"] = None
                    st.session_state["usuario"] = usuario_info["usuario"]
                    st.session_state["nome"] = usuario_info["nome"]
                    st.session_state["nivel"] = usuario_info["nivel"]
                    st.session_state["ultima_atividade"] = datetime.now().isoformat()
                    st.success(f"✅ Bem-vindo, {usuario_info['nome']}!")
                    st.rerun()
                else:
                    estado_falha = registrar_falha_login(st.session_state["login_tentativas"], agora)
                    st.session_state["login_tentativas"] = estado_falha["tentativas"]
                    if estado_falha["bloqueado_ate"]:
                        st.session_state["login_bloqueado_ate"] = estado_falha["bloqueado_ate"]
                        st.error("❌ Muitas tentativas inválidas. Acesso bloqueado por 15 minutos.")
                        return
                    st.error("❌ Credenciais inválidas. Tente novamente.")


def configurar_menu():
    """Configura o menu lateral com base nas permissões do usuário"""
    usuario = st.session_state["usuario"]
    nivel   = st.session_state["nivel"]

    opcoes_menu = []
    icons = []

    # Cada módulo aparece no menu somente se o usuário tiver permissão
    if usuario_tem_permissao(usuario, "visualizar"):
        opcoes_menu.append("Visualizar")
        icons.append("list")

    if usuario_tem_permissao(usuario, "registrar"):
        opcoes_menu.append("Registrar")
        icons.append("plus-circle")

    if usuario_tem_permissao(usuario, "editar"):
        opcoes_menu.append("Editar")
        icons.append("pencil-square")

    if usuario_tem_permissao(usuario, "membros"):
        opcoes_menu.append("Cadastro de Membros")
        icons.append("people")

    if usuario_tem_permissao(usuario, "aniversariantes"):
        opcoes_menu.append("Aniversariantes")
        icons.append("balloon-heart")

    if usuario_tem_permissao(usuario, "certificado"):
        opcoes_menu.append("Certificado")
        icons.append("award")

    if usuario_tem_permissao(usuario, "newsletter"):
        opcoes_menu.append("Newsletter")
        icons.append("envelope-paper")

    if usuario_tem_permissao(usuario, "calendario"):
        opcoes_menu.append("Calendário")
        icons.append("calendar-event")

    if usuario_tem_permissao(usuario, "financas") and FINANCAS_DISPONIVEL:
        opcoes_menu.append("Gestão de Finanças")
        icons.append("cash-coin")

    # Painel de permissões — exclusivo para admin
    if nivel == "admin":
        opcoes_menu.append("Permissões")
        icons.append("shield-lock")

    # Dúvidas está sempre disponível para todos
    opcoes_menu.append("Dúvidas")
    icons.append("question-circle")
    
    with st.sidebar:
        display_logo()
        if usuario_tem_permissao(usuario, "financas") and not FINANCAS_DISPONIVEL:
            st.warning("Modulo de financas indisponivel neste ambiente.")
        escolha = option_menu(
            "Menu",
            opcoes_menu,
            icons=icons,
            menu_icon="menu-app",
            default_index=0
        )
        if nivel != "admin" and any(
            usuario_tem_permissao(usuario, modulo)
            for modulo in ("editar", "newsletter", "calendario")
        ):
            st.caption(
                "Nos modulos de edicao, newsletter e calendario, voce gerencia apenas os itens criados por voce."
            )
    
    return escolha


def exibir_pagina_principal():
    """Exibe a página principal após o login"""
    # Exibir informações do usuário no topo
    exibir_usuario_info()

    # Alertas financeiros globais (vencidas e a vencer)
    exibir_alertas_financeiros(
        st.session_state["usuario"],
        st.session_state["nivel"],
    )
    
    # Configurar menu lateral
    escolha = configurar_menu()
    
    # Renderizar página selecionada
    usuario = st.session_state["usuario"]
    nivel   = st.session_state["nivel"]

    if escolha == "Visualizar" and usuario_tem_permissao(usuario, "visualizar"):
        exibir_pagina_visualizar()

    elif escolha == "Registrar" and usuario_tem_permissao(usuario, "registrar"):
        exibir_pagina_registrar()

    elif escolha == "Cadastro de Membros" and usuario_tem_permissao(usuario, "membros"):
        exibir_pagina_membros()

    elif escolha == "Aniversariantes" and usuario_tem_permissao(usuario, "aniversariantes"):
        exibir_pagina_aniversariantes()

    elif escolha == "Certificado" and usuario_tem_permissao(usuario, "certificado"):
        exibir_pagina_certificado()

    elif escolha == "Newsletter" and usuario_tem_permissao(usuario, "newsletter"):
        exibir_pagina_newsletter()

    elif escolha == "Calendário" and usuario_tem_permissao(usuario, "calendario"):
        exibir_pagina_calendario()

    elif escolha == "Editar" and usuario_tem_permissao(usuario, "editar"):
        exibir_pagina_editar()

    elif escolha == "Gestão de Finanças" and usuario_tem_permissao(usuario, "financas"):
        exibir_pagina_financas()

    elif escolha == "Permissões" and nivel == "admin":
        exibir_painel_permissoes()

    elif escolha == "Dúvidas":
        exibir_pagina_duvidas()


def main():
    """Função principal da aplicação"""
    page_icon = PAGE_ICON
    if FAVICON_PATH and os.path.exists(FAVICON_PATH):
        try:
            page_icon = Image.open(FAVICON_PATH)
        except Exception:
            page_icon = PAGE_ICON

    # Configuração da página - layout centered para melhor mobile
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=page_icon,
        layout=LAYOUT,
        initial_sidebar_state="collapsed"  # Sidebar fechada em mobile por padrão
    )
    
    # Aplicar CSS responsivo para mobile
    aplicar_css_mobile()
    
    # Inicializar banco de dados apenas uma vez por sessão para evitar lock em reruns
    if not st.session_state.get("db_initialized", False):
        init_db()
        st.session_state["db_initialized"] = True
    
    # Verificar estado de autenticação
    if "usuario" not in st.session_state:
        exibir_tela_login()
    else:
        # Expiração básica de sessão por inatividade
        agora = datetime.now()
        ultima_atividade = st.session_state.get("ultima_atividade")
        if sessao_expirada(ultima_atividade, agora):
            st.session_state.clear()
            st.warning("⚠️ Sessão expirada por inatividade. Faça login novamente.")
            st.rerun()

        st.session_state["ultima_atividade"] = agora.isoformat()
        exibir_pagina_principal()


if __name__ == "__main__":
    main()

