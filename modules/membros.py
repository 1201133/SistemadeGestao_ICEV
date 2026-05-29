"""
Página de Cadastro de Membros
Permite criar, visualizar, editar e excluir membros
Com busca automática de CEP e máscara de telefone
Otimizado para Desktop e Mobile
"""
import streamlit as st
import unicodedata
from datetime import datetime
from database_membros import (
    adicionar_membro,
    obter_membros,
    obter_membro_por_id,
    atualizar_membro,
    excluir_membro,
    validar_cep
)
from mobile_config import detectar_mobile


def formatar_telefone_input(telefone: str) -> str:
    """
    Formata telefone enquanto digita para padrão (XX) XXXXX-XXXX
    
    Args:
        telefone: Telefone parcial ou completo
    
    Returns:
        Telefone formatado
    """
    numeros = ''.join(filter(str.isdigit, telefone))
    
    if len(numeros) <= 2:
        return numeros
    elif len(numeros) <= 7:
        return f"({numeros[:2]}) {numeros[2:]}"
    else:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:11]}"


def validar_telefone(telefone: str) -> tuple:
    """
    Valida formato de telefone brasileiro
    
    Args:
        telefone: Número de telefone
    
    Returns:
        (valido: bool, mensagem: str)
    """
    if not telefone:
        return True, ""
    
    numeros = ''.join(filter(str.isdigit, telefone))
    
    if len(numeros) != 11:
        return False, "Telefone deve conter 11 dígitos (DDD + 9 dígitos)."
    
    if numeros[2] != '9':
        return False, "Número deve ser de celular (iniciar com 9)."
    
    return True, ""


def validar_email(email: str) -> bool:
    """Valida formato de e-mail"""
    if not email:
        return True
    
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_data_nascimento(data_str: str) -> tuple:
    """
    Valida data de nascimento
    
    Args:
        data_str: Data no formato YYYY-MM-DD
    
    Returns:
        (valido: bool, mensagem: str)
    """
    try:
        data_nasc = datetime.strptime(data_str, "%Y-%m-%d")
        hoje = datetime.now()
        idade = (hoje - data_nasc).days // 365
        
        if idade < 0 or idade > 150:
            return False, "Data de nascimento inválida."
        
        return True, ""
    except ValueError:
        return False, "Formato de data inválido."


def _chave(modo: str, campo: str) -> str:
    if modo == "criar":
        gen = st.session_state.get("membro_criar_form_gen", 0)
        return f"membro_{modo}_{gen}_{campo}"
    return f"membro_{modo}_{campo}"


def formatar_cep_input(cep: str) -> str:
    """Formata CEP para 00000-000."""
    numeros = ''.join(filter(str.isdigit, cep))[:8]
    if len(numeros) <= 5:
        return numeros
    return f"{numeros[:5]}-{numeros[5:]}"


def _inicializar_estado_membro(modo: str, membro=None):
    """Inicializa session_state para o formulário de membro."""
    cep_inicial = membro["cep"] if membro and membro["cep"] else ""
    cep_inicial = formatar_cep_input(cep_inicial)
    campos = {
        "logradouro": membro["logradouro"] if membro and membro["logradouro"] else "",
        "bairro":     membro["bairro"]     if membro and membro["bairro"]     else "",
        "cidade":     membro["cidade"]     if membro and membro["cidade"]     else "",
        "estado":     membro["estado"]     if membro and membro["estado"]     else "",
        "cep_input": cep_inicial,
        "cep_input_raw": cep_inicial,
        "cep_status": "",  # mensagem de status da busca
    }
    for campo, valor in campos.items():
        chave = _chave(modo, campo)
        if chave not in st.session_state:
            st.session_state[chave] = valor


def _preencher_cep(modo: str):
    """Callback: ao digitar o CEP, consulta ViaCEP e preenche endereço."""
    chave_cep_raw = _chave(modo, "cep_input_raw")
    chave_cep = _chave(modo, "cep_input")
    cep_digitado = st.session_state.get(chave_cep_raw, "")
    st.session_state[chave_cep] = formatar_cep_input(cep_digitado)
    numeros = "".join(filter(str.isdigit, cep_digitado))

    if not numeros:
        st.session_state[_chave(modo, "cep_status")] = ""
        return

    if len(numeros) != 8:
        st.session_state[_chave(modo, "cep_status")] = "⚠️ CEP deve conter 8 dígitos"
        return

    # Limpa campos e status antes de nova busca
    for campo in ("logradouro", "bairro", "cidade", "estado"):
        st.session_state[_chave(modo, campo)] = ""
    for campo in ("logradouro_field", "bairro_field", "cidade_field", "estado_field"):
        st.session_state[_chave(modo, campo)] = ""
    st.session_state[_chave(modo, "complemento")] = ""
    st.session_state[_chave(modo, "cep_status")] = ""

    st.session_state[_chave(modo, "cep_status")] = "🔍 Buscando..."

    valido, resultado = validar_cep(numeros)
    if valido:
        dados = resultado
        logradouro = dados.get("logradouro", "")
        bairro = dados.get("bairro", "")
        cidade = dados.get("localidade", "")
        estado = dados.get("uf", "")
        complemento = dados.get("complemento", "")

        st.session_state[_chave(modo, "logradouro")] = logradouro
        st.session_state[_chave(modo, "bairro")] = bairro
        st.session_state[_chave(modo, "cidade")] = cidade
        st.session_state[_chave(modo, "estado")] = estado

        # Atualiza também as keys dos widgets exibidos no formulário.
        st.session_state[_chave(modo, "logradouro_field")] = logradouro
        st.session_state[_chave(modo, "bairro_field")] = bairro
        st.session_state[_chave(modo, "cidade_field")] = cidade
        st.session_state[_chave(modo, "estado_field")] = estado
        st.session_state[_chave(modo, "complemento")] = complemento
        st.session_state[_chave(modo, "cep_status")] = "✅ Endereço encontrado!"
    else:
        st.session_state[_chave(modo, "cep_status")] = f"⚠️ {resultado}"


def exibir_formulario_membro(membro=None, modo="criar"):
    """
    Exibe o formulário de cadastro/edição de membro.
    O CEP é consultado automaticamente na API ViaCEP ao ser digitado.
    """
    config = detectar_mobile()

    _inicializar_estado_membro(modo, membro)

    if modo == "criar":
        st.subheader("➕ Novo Membro")
    else:
        st.subheader("✏️ Editar Membro")

    st.markdown("#### 📋 Dados Pessoais")

    col_nome = st.text_input(
        "Nome Completo *",
        value=membro["nome"] if membro else "",
        max_chars=100,
        placeholder="Digite o nome completo",
        key=_chave(modo, "nome")
    )

    col_data_nasc = st.date_input(
        "Data de Nascimento *",
        value=datetime.strptime(membro["data_nascimento"], "%Y-%m-%d") if membro else datetime(1990, 1, 1),
        min_value=datetime(1950, 1, 1),
        max_value=datetime(2050, 12, 31),
        format="DD/MM/YYYY",
        help="Data de nascimento do membro",
        key=_chave(modo, "data_nasc")
    )

    st.markdown("---")
    st.markdown("#### 📞 Contato")

    col_telefone = st.text_input(
        "Telefone",
        value=membro["telefone"] if membro else "",
        max_chars=15,
        placeholder="(11) 99999-9999",
        help="Telefone com DDD",
        key=_chave(modo, "telefone")
    )

    col_email = st.text_input(
        "E-mail",
        value=membro["email"] if membro else "",
        max_chars=100,
        placeholder="exemplo@email.com",
        key=_chave(modo, "email")
    )

    st.markdown("---")
    st.markdown("#### 🏠 Endereço")

    with st.container():
        st.text_input(
            "CEP",
            max_chars=9,
            placeholder="00000-000",
            help="Digite o CEP — o endereço será preenchido automaticamente",
            key=_chave(modo, "cep_input_raw"),
            on_change=_preencher_cep,
            args=(modo,)
        )

        if st.button("🔎 Buscar CEP", key=_chave(modo, "btn_buscar_cep"), width="stretch"):
            _preencher_cep(modo)

        status = st.session_state.get(_chave(modo, "cep_status"), "")
        if status:
            if "✅" in status:
                st.success(status)
            elif "⚠️" in status:
                st.warning(status)

    col_complemento = st.text_input(
        "Complemento",
        value=membro["complemento"] if membro else "",
        max_chars=50,
        placeholder="Apto, Sala, etc.",
        key=_chave(modo, "complemento")
    )

    logradouro_val = st.session_state.get(_chave(modo, "logradouro"), membro["logradouro"] if membro and membro["logradouro"] else "")
    col_logradouro, col_numero = st.columns([3, 1])
    with col_logradouro:
        col_logradouro = st.text_input(
            "Logradouro",
            value=logradouro_val,
            max_chars=100,
            placeholder="Rua, Avenida, etc.",
            key=_chave(modo, "logradouro_field")
        )
    with col_numero:
        numero = st.text_input(
            "Número *",
            value=membro["numero"] if membro else "",
            max_chars=10,
            placeholder="123",
            key=_chave(modo, "numero")
        )

    col_bairro_v, col_cidade_v, col_estado_v = st.columns([2, 2, 1])

    bairro_val  = st.session_state.get(_chave(modo, "bairro"),  membro["bairro"]  if membro and membro["bairro"]  else "")
    cidade_val  = st.session_state.get(_chave(modo, "cidade"),  membro["cidade"]  if membro and membro["cidade"]  else "")
    estado_val  = st.session_state.get(_chave(modo, "estado"),  membro["estado"]  if membro and membro["estado"]  else "")

    with col_bairro_v:
        bairro = st.text_input("Bairro", value=bairro_val, max_chars=50, key=_chave(modo, "bairro_field"))
    with col_cidade_v:
        cidade = st.text_input("Cidade", value=cidade_val, max_chars=50, key=_chave(modo, "cidade_field"))
    with col_estado_v:
        estado = st.text_input("UF",     value=estado_val, max_chars=2,  key=_chave(modo, "estado_field"))

    st.markdown("---")

    col_btn1, col_btn2 = st.columns(config["botoes"])

    with col_btn1:
        submit_btn = st.button(
            "✅ Salvar" if modo == "criar" else "✅ Atualizar",
            type="primary",
            width="stretch",
            key=_chave(modo, "btn_salvar")
        )

    with col_btn2:
        if modo == "editar":
            cancelar_btn = st.button("❌ Cancelar", width="stretch", key=_chave(modo, "btn_cancelar"))
        else:
            cancelar_btn = st.button("🔄 Limpar", width="stretch", key=_chave(modo, "btn_limpar"))

    if submit_btn:
        nome_val     = st.session_state.get(_chave(modo, "nome"), "")
        telefone_val = st.session_state.get(_chave(modo, "telefone"), "")
        email_val    = st.session_state.get(_chave(modo, "email"), "")
        cep_val      = st.session_state.get(_chave(modo, "cep_input"), st.session_state.get(_chave(modo, "cep_input_raw"), ""))
        numero_val   = st.session_state.get(_chave(modo, "numero"), "")
        compl_val    = st.session_state.get(_chave(modo, "complemento"), "")
        logr_val     = st.session_state.get(_chave(modo, "logradouro_field"), "")
        bairro_val2  = st.session_state.get(_chave(modo, "bairro_field"), "")
        cidade_val2  = st.session_state.get(_chave(modo, "cidade_field"), "")
        estado_val2  = st.session_state.get(_chave(modo, "estado_field"), "")
        data_val     = st.session_state.get(_chave(modo, "data_nasc"), None)

        if not nome_val.strip():
            st.error("❌ O nome é obrigatório.")
            return None

        # Verifica duplicidade de nome + sobrenome (apenas ao criar)
        if modo == "criar":
            def _normalizar(texto: str) -> str:
                """Remove acentos e converte para minúsculas."""
                return unicodedata.normalize("NFD", texto)\
                    .encode("ascii", "ignore")\
                    .decode("ascii")\
                    .lower()\
                    .strip()

            partes_novo = nome_val.strip().split()
            nome_norm   = _normalizar(partes_novo[0])
            sobrenome_norm = _normalizar(partes_novo[-1]) if len(partes_novo) > 1 else ""

            for m in obter_membros():
                partes_m = m["nome"].strip().split()
                nome_m_norm      = _normalizar(partes_m[0])
                sobrenome_m_norm = _normalizar(partes_m[-1]) if len(partes_m) > 1 else ""

                if nome_norm == nome_m_norm and sobrenome_norm == sobrenome_m_norm:
                    st.warning(
                        f"⚠️ Este membro já possui cadastro: **{m['nome']}**. "
                        "Verifique a lista de membros antes de continuar."
                    )
                    return None

        if not numero_val.strip():
            st.error("❌ O número do endereço é obrigatório.")
            return None

        data_str = data_val.strftime("%Y-%m-%d") if data_val else ""
        valido, msg = validar_data_nascimento(data_str)
        if not valido:
            st.error(f"❌ {msg}")
            return None

        if telefone_val.strip():
            valido_tel, msg_tel = validar_telefone(telefone_val)
            if not valido_tel:
                st.error(f"❌ {msg_tel}")
                return None

        if email_val.strip() and not validar_email(email_val):
            st.error("❌ E-mail inválido.")
            return None

        cep_limpo = "".join(filter(str.isdigit, cep_val)) or None

        return {
            "nome":           nome_val.strip(),
            "data_nascimento": data_str,
            "telefone":       telefone_val.strip() or None,
            "email":          email_val.strip() or None,
            "cep":            cep_limpo,
            "numero":         numero_val.strip(),
            "complemento":    compl_val.strip() or None,
            "logradouro":     logr_val.strip() or None,
            "bairro":         bairro_val2.strip() or None,
            "cidade":         cidade_val2.strip() or None,
            "estado":         estado_val2.strip() or None,
        }

    if cancelar_btn and modo == "editar":
        st.session_state["membro_editando"] = None
        st.rerun()

    if cancelar_btn and modo == "criar":
        # Incrementa a geração do formulário: todas as chaves mudam,
        # forçando Streamlit a recriar cada widget com o valor padrão.
        st.session_state["membro_criar_form_gen"] = (
            st.session_state.get("membro_criar_form_gen", 0) + 1
        )
        st.rerun()

    return None


def exibir_lista_membros():
    """Exibe a lista de membros cadastrados"""
    st.subheader("📋 Membros Cadastrados")
    
    membros = obter_membros()
    
    if not membros:
        st.info("ℹ️ Nenhum membro cadastrado ainda.")
        return
    
    st.caption(f"Total: {len(membros)} membro(s)")
    
    for membro in membros:
        with st.expander(f"👤 {membro['nome']}"):
            col_info1, col_info2 = st.columns(2)
            
            with col_info1:
                st.write(f"**📅 Nascimento:** {datetime.strptime(membro['data_nascimento'], '%Y-%m-%d').strftime('%d/%m/%Y')}")
                if membro['telefone']:
                    st.write(f"**📞 Telefone:** {membro['telefone']}")
                if membro['email']:
                    st.write(f"**📧 E-mail:** {membro['email']}")
            
            with col_info2:
                if membro['logradouro']:
                    endereco = f"{membro['logradouro']}, {membro['numero']}"
                    if membro['complemento']:
                        endereco += f" - {membro['complemento']}"
                    endereco += f"\n{membro['bairro']} - {membro['cidade']}/{membro['estado']}"
                    if membro['cep']:
                        endereco += f"\nCEP: {membro['cep'][:5]}-{membro['cep'][5:]}"
                    st.write(f"**🏠 Endereço:**\n{endereco}")
            
            st.markdown("---")
            
            col_btn_edit, col_btn_delete = st.columns(2)
            
            with col_btn_edit:
                if st.button("✏️ Editar", key=f"edit_{membro['id']}", width="stretch"):
                    st.session_state["membro_editando"] = membro['id']
                    st.rerun()
            
            with col_btn_delete:
                if st.button("🗑️ Excluir", key=f"delete_{membro['id']}", width="stretch"):
                    st.session_state["membro_excluindo"] = membro['id']
                    st.rerun()


def exibir_confirmacao_exclusao():
    """Exibe confirmação de exclusão de membro"""
    id_membro = st.session_state.get("membro_excluindo")
    
    if not id_membro:
        return
    
    membro = obter_membro_por_id(id_membro)
    
    if not membro:
        st.session_state["membro_excluindo"] = None
        st.rerun()
        return
    
    st.warning(f"⚠️ Deseja excluir o membro **{membro['nome']}**?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirmar Exclusão", type="primary", width="stretch", key="btn_confirmar_exclusao"):
            if excluir_membro(id_membro):
                st.session_state["membro_excluindo"] = None
                st.session_state["exclusao_sucesso"] = True
                st.rerun()
            else:
                st.error("❌ Erro ao excluir membro.")
    
    with col2:
        if st.button("❌ Cancelar", width="stretch", key="btn_cancelar_exclusao"):
            st.session_state["membro_excluindo"] = None
            st.rerun()


def exibir_pagina_membros():
    """
    Exibe a página principal de cadastro de membros
    """
    st.title("👥 Cadastro de Membros")
    
    if "membro_editando" not in st.session_state:
        st.session_state["membro_editando"] = None
    
    if "membro_excluindo" not in st.session_state:
        st.session_state["membro_excluindo"] = None

    if st.session_state.pop("exclusao_sucesso", False):
        st.success("✅ Membro excluído com sucesso!")
    
    if st.session_state["membro_excluindo"]:
        exibir_confirmacao_exclusao()
        st.markdown("---")
        exibir_lista_membros()
        return
    
    if st.session_state["membro_editando"]:
        membro = obter_membro_por_id(st.session_state["membro_editando"])
        dados = exibir_formulario_membro(membro, modo="editar")
        
        if dados:
            if atualizar_membro(st.session_state["membro_editando"], **dados):
                st.success("✅ Membro atualizado com sucesso!")
                st.session_state["membro_editando"] = None
                st.rerun()
            else:
                st.error("❌ Erro ao atualizar membro.")
        
        st.markdown("---")
    else:
        dados = exibir_formulario_membro(modo="criar")
        
        if dados:
            if adicionar_membro(**dados):
                st.success("✅ Membro cadastrado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Erro ao cadastrar membro.")
        
        st.markdown("---")
    
    exibir_lista_membros()

