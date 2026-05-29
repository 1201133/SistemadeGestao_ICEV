"""
Página de Edição de Lançamentos.
Admin vê todos os lançamentos; demais usuários veem apenas os próprios.
"""
import streamlit as st
from datetime import datetime
from database import obter_lancamentos, atualizar_lancamento, excluir_lancamento
from config import TIPOS_PAGAMENTO, CATEGORIAS, OPERADORAS
from utils import validar_nome, validar_valor, formatar_valor
from notifications import validar_email, validar_celular
from mobile_config import detectar_mobile


def exibir_pagina_editar():
    """
    Exibe a página de edição de lançamentos.
    Admin pode editar todos os registros; demais usuários, apenas os próprios.
    Layout responsivo para mobile
    """
    config = detectar_mobile()
    usuario = st.session_state["usuario"]
    nivel = st.session_state["nivel"]
    
    st.subheader("✏️ Editar Lançamentos")
    if nivel != "admin":
        st.info("Voce pode editar e excluir apenas os lancamentos criados por voce.")
    
    lancamentos = obter_lancamentos(usuario, nivel)
    
    if lancamentos:
        # Criar lista de opções para seleção
        lancamentos_para_edicao = {
            f"ID: {l[0]} - {l[2]} - {formatar_valor(l[3])} - {l[1]}": l[0] 
            for l in lancamentos
        }
        
        selected = st.selectbox(
            "Selecione um lançamento para editar", 
            options=list(lancamentos_para_edicao.keys())
        )
        
        id_selecionado = lancamentos_para_edicao[selected]
        
        # Encontrar o lançamento selecionado
        lancamento_selecionado = None
        for l in lancamentos:
            if l[0] == id_selecionado:
                lancamento_selecionado = l
                break
        
        if not lancamento_selecionado:
            st.error("❌ Lançamento não encontrado.")
            return
        
        # Formulário de edição
        with st.form("editar_form"):
            # ============================================
            # SEÇÃO: DADOS DO LANÇAMENTO
            # ============================================
            st.markdown("#### 📋 Dados do Lançamento")
            
            data = st.date_input(
                "Data", 
                value=datetime.strptime(lancamento_selecionado[1], "%Y-%m-%d")
            )
            
            nome = st.text_input("Nome Completo", value=lancamento_selecionado[2], key=f"editar_nome_{id_selecionado}")
            
            valor = st.number_input(
                "Valor (R$)", 
                value=float(lancamento_selecionado[3]), 
                min_value=0.01, 
                step=0.01, 
                format="%.2f"
            )
            
            # Tipo de pagamento
            try:
                index_tipo = TIPOS_PAGAMENTO.index(lancamento_selecionado[4])
            except ValueError:
                index_tipo = 0
            
            tipo = st.selectbox("Tipo de Pagamento", TIPOS_PAGAMENTO, index=index_tipo)
            
            # Categoria
            try:
                index_categoria = CATEGORIAS.index(lancamento_selecionado[5])
            except ValueError:
                index_categoria = 0
            
            categoria = st.selectbox("Categoria", CATEGORIAS, index=index_categoria)
            
            # ============================================
            # SEÇÃO: DADOS DE CONTATO
            # ============================================
            st.markdown("---")
            st.markdown("#### 📞 Dados de Contato")
            
            # Email (índice 7 no resultado)
            email_atual = lancamento_selecionado[7] if len(lancamento_selecionado) > 7 else ""
            email = st.text_input(
                "Email",
                value=email_atual if email_atual else "",
                max_chars=100,
                placeholder="exemplo@email.com",
                key=f"editar_email_{id_selecionado}"
            )
            
            # Celular em colunas - responsivo
            st.markdown("**Celular**")
            col1, col2, col3 = st.columns(config["form_tripla"])
            
            # Código de área (índice 8)
            codigo_area_atual = lancamento_selecionado[8] if len(lancamento_selecionado) > 8 else ""
            with col1:
                codigo_area = st.text_input(
                    "DDD",
                    value=codigo_area_atual if codigo_area_atual else "",
                    max_chars=2,
                    placeholder="11",
                    label_visibility="collapsed",
                    key=f"editar_codigo_area_{id_selecionado}"
                )
                st.caption("DDD")
            
            # Celular (índice 9)
            celular_atual = lancamento_selecionado[9] if len(lancamento_selecionado) > 9 else ""
            with col2:
                celular = st.text_input(
                    "Número",
                    value=celular_atual if celular_atual else "",
                    max_chars=10,
                    placeholder="999999999",
                    label_visibility="collapsed",
                    key=f"editar_celular_{id_selecionado}"
                )
                st.caption("Número")
            
            # Operadora (índice 10)
            operadora_atual = lancamento_selecionado[10] if len(lancamento_selecionado) > 10 else ""
            try:
                index_operadora = OPERADORAS.index(operadora_atual) if operadora_atual else 0
            except ValueError:
                index_operadora = 0
            
            with col3:
                operadora = st.selectbox(
                    "Operadora", 
                    OPERADORAS, 
                    index=index_operadora,
                    label_visibility="collapsed"
                )
                st.caption("Operadora")
            
            # ============================================
            # BOTÕES DE AÇÃO
            # ============================================
            st.markdown("---")
            
            # Botões em colunas que empilham em mobile
            col_btn1, col_btn2 = st.columns(config["botoes"])
            
            with col_btn1:
                atualizar_btn = st.form_submit_button(
                    "✅ Atualizar", 
                    type="primary",
                    width="stretch"
                )
            
            with col_btn2:
                excluir_btn = st.form_submit_button(
                    "🗑️ Excluir", 
                    type="secondary",
                    width="stretch"
                )

            confirmar_exclusao = st.checkbox(
                "Confirmo a exclusão permanente deste lançamento",
                value=False
            )
            
            # ============================================
            # PROCESSAMENTO DAS AÇÕES
            # ============================================
            if atualizar_btn:
                # Validações
                if not validar_nome(nome):
                    st.error("❌ O nome deve ter pelo menos 2 caracteres.")
                    return
                
                if not validar_valor(valor):
                    st.error("❌ O valor deve ser maior que zero.")
                    return
                
                # Validar email se fornecido
                email_valido = None
                if email.strip():
                    if validar_email(email.strip()):
                        email_valido = email.strip()
                    else:
                        st.error("❌ Email inválido.")
                        return
                
                # Validar celular se fornecido
                celular_valido = None
                codigo_area_valido = None
                operadora_valida = None
                
                if codigo_area.strip() and celular.strip():
                    if validar_celular(codigo_area.strip(), celular.strip()):
                        codigo_area_valido = codigo_area.strip()
                        celular_valido = celular.strip()
                        operadora_valida = operadora
                    else:
                        st.error("❌ Celular inválido.")
                        return
                
                # Atualizar lançamento
                sucesso = atualizar_lancamento(
                    id_selecionado,
                    data.strftime("%Y-%m-%d"),
                    nome.strip(),
                    float(valor),
                    tipo,
                    categoria,
                    email=email_valido,
                    codigo_area=codigo_area_valido,
                    celular=celular_valido,
                    operadora=operadora_valida,
                    usuario=None if nivel == "admin" else usuario,
                )
                
                if sucesso:
                    st.success("✅ Lançamento atualizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar lançamento ou permissão insuficiente.")
            
            if excluir_btn:
                if not confirmar_exclusao:
                    st.warning("⚠️ Marque a confirmação de exclusão para continuar.")
                    return

                sucesso = excluir_lancamento(id_selecionado, None if nivel == "admin" else usuario)
                
                if sucesso:
                    st.success("✅ Lançamento excluído com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao excluir lançamento ou permissão insuficiente.")
    else:
        st.info("ℹ️ Nenhum lançamento disponível para edição")
