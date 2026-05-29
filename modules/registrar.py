"""
Página de Registro de Lançamentos
Permite cadastrar novos dízimos, ofertas e contribuições
Com seleção de membros cadastrados para auto-preenchimento
Otimizado para Desktop e Mobile
"""
import streamlit as st
from datetime import datetime
from database import adicionar_lancamento
from database_membros import obter_membros
from config import TIPOS_PAGAMENTO, CATEGORIAS
from utils import validar_nome, validar_valor
from mobile_config import detectar_mobile


def _chave_reg(campo: str) -> str:
    """Gera chave de widget com base na geração atual do formulário."""
    gen = st.session_state.get("reg_form_gen", 0)
    return f"reg_{gen}_{campo}"


def validar_telefone(telefone: str) -> tuple[bool, str]:
    """
    Valida formato de telefone brasileiro
    
    Args:
        telefone: Número de telefone
    
    Returns:
        (valido: bool, mensagem: str)
    
    Formatos aceitos:
    - (11) 99999-9999
    - 11999999999
    - 11 999999999
    """
    if not telefone:
        return False, "Telefone é obrigatório."
    
    # Remove caracteres não numéricos
    numeros = ''.join(filter(str.isdigit, telefone))
    
    # Valida quantidade de dígitos (DDD + 9 dígitos)
    if len(numeros) != 11:
        return False, "Telefone deve conter 11 dígitos (DDD + 9 dígitos)."
    
    # Valida se começa com dígito 9 (celular)
    if numeros[2] != '9':
        return False, "Número deve ser de celular (iniciar com 9)."
    
    return True, "Telefone válido."


def formatar_telefone(telefone: str) -> str:
    """
    Formata telefone para padrão visual
    
    Args:
        telefone: Telefone com apenas números
    
    Returns:
        String formatada: (11) 99999-9999
    """
    numeros = ''.join(filter(str.isdigit, telefone))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    return telefone


def _inicializar_estado_registro():
    """Inicializa variáveis de session_state para o formulário de registro."""
    # Apenas chaves que NÃO são vinculadas a widgets são inicializadas aqui.
    # Chaves de widgets (reg_nome_input, reg_nome_visitante, reg_sugestao_select)
    # são gerenciadas pelo próprio Streamlit e, ao limpar, devem ser deletadas
    # em vez de reatribuídas (evita StreamlitAPIException).
    defaults = {
        "reg_form_gen": 0,
        "reg_nome_confirmado": "",
        "reg_sugestoes": [],
    }
    for chave, valor in defaults.items():
        if chave not in st.session_state:
            st.session_state[chave] = valor


def exibir_pagina_registrar():
    """
    Exibe a página de registro de novos lançamentos.
    - Para Dízimo/Oferta: busca membros cadastrados com auto-preenchimento.
    - Para Visitante: campo de texto livre, sem exigir cadastro no sistema.
    """
    import time

    config = detectar_mobile()
    _inicializar_estado_registro()

    # Chaves dos widgets da geração atual do formulário.
    chave_data = _chave_reg("data")
    chave_nome_visitante = _chave_reg("nome_visitante")
    chave_nome_input = _chave_reg("nome_input")
    chave_sugestao_select = _chave_reg("sugestao_select")
    chave_valor = _chave_reg("valor")
    chave_tipo_pagamento = _chave_reg("tipo_pagamento")
    chave_categoria = _chave_reg("categoria")
    chave_telefone_input = _chave_reg("telefone_input")
    chave_email_input = _chave_reg("email_input")

    st.subheader("➕ Registrar Novo Lançamento")

    membros = obter_membros()

    st.markdown("#### 📋 Dados do Lançamento")

    data = st.date_input(
        "Data",
        value=datetime.today(),
        key=chave_data,
        format="DD/MM/YYYY",
        help="Data em que a contribuição foi realizada"
    )

    st.markdown("#### 👤 Contribuinte")

    # Lê a categoria já salva em session_state (definida no selectbox abaixo).
    # Na primeira execução ainda não existe, então assume o primeiro valor da lista.
    categoria_atual = st.session_state.get(chave_categoria, CATEGORIAS[0])

    # ── Modo Visitante: campo de texto livre ───────────────────────────────
    if categoria_atual == "Visitante":
        st.caption("ℹ️ Visitantes não precisam estar cadastrados no sistema.")
        st.text_input(
            "Nome do Visitante *",
            key=chave_nome_visitante,
            max_chars=100,
            placeholder="Digite o nome do visitante...",
            help="Informe o nome do visitante",
        )
        nome = st.session_state.get(chave_nome_visitante, "").strip()

    # ── Modo Membro: busca com auto-preenchimento ──────────────────────────
    else:
        # Callback: filtra membros ao digitar
        def buscar_membros():
            texto = st.session_state.get(chave_nome_input, "").strip()
            st.session_state.reg_nome_confirmado = ""
            st.session_state[chave_email_input] = ""
            st.session_state[chave_telefone_input] = ""
            if texto and len(texto) >= 2:
                st.session_state.reg_sugestoes = [
                    m for m in membros
                    if texto.lower() in m["nome"].lower()
                ]
            else:
                st.session_state.reg_sugestoes = []

        # Callback: ao escolher da lista de sugestões
        def confirmar_membro():
            escolha = st.session_state.get(chave_sugestao_select, "")
            if escolha and escolha != "-- Selecione --":
                for m in membros:
                    if m["nome"] == escolha:
                        st.session_state.reg_nome_confirmado = m["nome"]
                        st.session_state[chave_email_input] = m["email"] or ""
                        st.session_state[chave_telefone_input] = m["telefone"] or ""
                        st.session_state.reg_sugestoes = []
                        break

        st.text_input(
            "Nome do Membro *",
            key=chave_nome_input,
            on_change=buscar_membros,
            max_chars=100,
            placeholder="Digite para buscar membros cadastrados...",
            help="Digite pelo menos 2 letras para filtrar os membros cadastrados",
        )

        sugestoes = st.session_state.get("reg_sugestoes", [])
        if sugestoes and not st.session_state.reg_nome_confirmado:
            opcoes = ["-- Selecione --"] + [m["nome"] for m in sugestoes]
            st.selectbox(
                "Membros encontrados:",
                opcoes,
                key=chave_sugestao_select,
                on_change=confirmar_membro,
                help="Clique no nome para selecionar o membro",
            )
        elif (not sugestoes
              and st.session_state.get(chave_nome_input, "").strip()
              and not st.session_state.reg_nome_confirmado):
            st.caption("⚠️ Nenhum membro encontrado com esse nome.")

        nome = st.session_state.reg_nome_confirmado or st.session_state.get(chave_nome_input, "")

    st.markdown("---")

    valor = st.number_input(
        "Valor (R$) *",
        min_value=0.01,
        step=0.01,
        key=chave_valor,
        format="%.2f",
        help="Valor da contribuição em reais"
    )

    col1, col2 = st.columns(config["form_dupla"])
    with col1:
        tipo = st.selectbox(
            "Tipo de Pagamento *",
            TIPOS_PAGAMENTO,
            key=chave_tipo_pagamento,
            help="Forma de pagamento utilizada"
        )
    with col2:
        categoria = st.selectbox(
            "Categoria *",
            CATEGORIAS,
            key=chave_categoria,
            help="Tipo de contribuição"
        )

    st.markdown("---")

    label_telefone = "Celular (preenchido automaticamente)" if st.session_state.get(chave_telefone_input, "") else "Celular (opcional)"
    telefone = st.text_input(
        label_telefone,
        key=chave_telefone_input,
        max_chars=15,
        placeholder="(11) 99999-9999",
        help="Celular com DDD para cadastro"
    )

    label_email = "Email (preenchido automaticamente)" if st.session_state.get(chave_email_input, "") else "Email (opcional)"
    email = st.text_input(
        label_email,
        key=chave_email_input,
        max_chars=100,
        placeholder="exemplo@email.com",
        help="Email para registro"
    )

    st.markdown("---")
    if st.button("✅ Registrar Lançamento", type="primary", width="stretch"):
        with st.spinner("🔄 Processando lançamento..."):
            if not validar_nome(nome):
                st.error("❌ O nome deve ter pelo menos 2 caracteres.")
                return

            if not validar_valor(valor):
                st.error("❌ O valor deve ser maior que zero.")
                return

            telefone_formatado = None
            if telefone.strip():
                telefone_valido, msg_telefone = validar_telefone(telefone)
                if not telefone_valido:
                    st.error(f"❌ {msg_telefone}")
                    return
                telefone_formatado = formatar_telefone(telefone)

            progress_placeholder = st.empty()
            progress_placeholder.info("💾 Salvando dados no banco...")

            sucesso = adicionar_lancamento(
                data.strftime("%Y-%m-%d"),
                nome.strip(),
                float(valor),
                tipo,
                categoria,
                st.session_state["usuario"],
                email.strip() if email else None,
                telefone=telefone_formatado
            )

            if sucesso:
                progress_placeholder.empty()
                st.success("✅ Lançamento registrado com sucesso!")

                # Limpa chaves de estado não vinculadas a widgets
                st.session_state["reg_nome_confirmado"] = ""
                st.session_state["reg_sugestoes"] = []

                # Troca a geração para reconstruir o formulário limpo no próximo rerun.
                gen_atual = st.session_state.get("reg_form_gen", 0)
                prefixo_geracao_atual = f"reg_{gen_atual}_"
                for chave in list(st.session_state.keys()):
                    if chave.startswith(prefixo_geracao_atual):
                        del st.session_state[chave]
                st.session_state["reg_form_gen"] = gen_atual + 1

                time.sleep(1.5)
                st.rerun()
            else:
                progress_placeholder.empty()
                st.error("❌ Erro ao registrar lançamento. Tente novamente.")

