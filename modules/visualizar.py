"""
Página de Visualização de Lançamentos
Otimizado para visualização em Desktop e Mobile
"""
import streamlit as st
import pandas as pd
import io
from datetime import datetime
from database import obter_lancamentos
from utils import formatar_data, formatar_valor, calcular_totais
from mobile_config import detectar_mobile


def exibir_pagina_visualizar():
    """
    Exibe a página de visualização de lançamentos
    Mostra todos os dados incluindo informações de contato
    Layout responsivo para mobile
    """
    st.subheader("📊 Consulta de Lançamentos")

    todos_lancamentos = obter_lancamentos(
        st.session_state["usuario"],
        st.session_state["nivel"]
    )

    if todos_lancamentos:
        lancamentos = []
        for lanc in todos_lancamentos:
            try:
                datetime.strptime(lanc[1], "%Y-%m-%d").date()
                lancamentos.append(lanc)
            except ValueError:
                continue

        st.caption(f"Mostrando histórico completo • {len(lancamentos)} registro(s)")

        if not lancamentos:
            st.info("ℹ️ Nenhum lançamento válido encontrado para exibição.")
            return

        # Resumo Financeiro ANTES da tabela para mobile
        exibir_resumo_financeiro(lancamentos)
        
        st.markdown("---")
        st.markdown("#### 📋 Tabela de Lançamentos")
        
        # Montagem da tabela com novos campos
        columns = ["ID", "Data", "Nome", "Valor (R$)", "Tipo", "Categoria", "Usuário", "Email", "Celular"]
        
        dados = []
        for lanc in lancamentos:
            # Dados básicos (sempre presentes)
            linha = [
                lanc[0],  # ID
                formatar_data(lanc[1]),  # Data
                lanc[2],  # Nome
                formatar_valor(lanc[3]),  # Valor
                lanc[4],  # Tipo
                lanc[5],  # Categoria
            ]
            
            # Verificar se é admin (tem coluna usuario na query)
            if st.session_state["nivel"] == "admin":
                usuario = lanc[6] if len(lanc) > 6 else "-"
                email = lanc[7] if len(lanc) > 7 else None
                codigo_area = lanc[8] if len(lanc) > 8 else None
                celular = lanc[9] if len(lanc) > 9 else None
            else:
                usuario = st.session_state["usuario"]
                email = lanc[6] if len(lanc) > 6 else None
                codigo_area = lanc[7] if len(lanc) > 7 else None
                celular = lanc[8] if len(lanc) > 8 else None
            
            # Adicionar usuário
            linha.append(usuario if usuario else "-")
            
            # Adicionar email
            linha.append(email if email else "-")
            
            # Adicionar celular formatado
            if codigo_area and celular:
                celular_formatado = f"({codigo_area}) {celular}"
            else:
                celular_formatado = "-"
            
            linha.append(celular_formatado)
            dados.append(linha)
        
        df = pd.DataFrame(dados, columns=columns)
        
        # Info sobre scroll horizontal em mobile
        st.info("👉 Deslize para o lado para ver mais colunas")
        
        # Tabela com altura fixa e scroll
        st.dataframe(
            df, 
            width="stretch", 
            hide_index=True,
            height=400  # Altura fixa para melhor controle em mobile
        )

        exibir_exportacao_planilha(df)
        
    else:
        st.info("ℹ️ Nenhum lançamento registrado ainda.")


def exibir_exportacao_planilha(df):
    """Exibe ações de exportação de planilha compatível com Google Sheets."""
    st.markdown("---")
    st.markdown("#### ⬇️ Exportar Dados")

    data_arquivo = datetime.now().strftime("%d-%m-%Y")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"lancamentos_{data_arquivo}.xlsx"

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lancamentos")
    planilha_bytes = buffer.getvalue()

    st.download_button(
        label="⬇️ Baixar Planilha (Google Sheets)",
        data=planilha_bytes,
        file_name=nome_arquivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch",
        key=f"download_planilha_{timestamp}"
    )


def exibir_resumo_financeiro(lancamentos):
    """Exibe o resumo financeiro dos lançamentos - layout responsivo"""
    config = detectar_mobile()
    
    st.subheader("📈 Resumo Financeiro")
    st.markdown("---")
    
    totais = calcular_totais(lancamentos)
    
    # Exibição das métricas principais
    st.markdown("#### 💵 Totais de Entradas")
    
    # Métricas em colunas que colapsam em mobile via CSS
    col1, col2, col3 = st.columns(config["metricas_principais"])
    
    with col1:
        st.metric(
            "📅 Hoje", 
            formatar_valor(totais["total_dia"]), 
            help="Total de entradas registradas hoje"
        )
    
    mes_atual = datetime.today().strftime('%b/%Y')
    with col2:
        st.metric(
            f"📆 Mês ({mes_atual})", 
            formatar_valor(totais["total_mes"]), 
            help="Total de entradas registradas no mês atual"
        )
    
    with col3:
        st.metric(
            "📊 Total Geral", 
            formatar_valor(totais["total_geral"]), 
            help="Total de todas as entradas registradas"
        )
    
    # Detalhes por Categoria
    st.markdown("---")
    st.markdown("#### 🎯 Detalhes por Categoria (Mês Atual)")
    
    col4, col5, col6 = st.columns(config["metricas_principais"])
    
    with col4:
        st.metric("💵 Dízimos", formatar_valor(totais["total_dizimo_mes"]))
    with col5:
        st.metric("🎁 Ofertas", formatar_valor(totais["total_oferta_mes"]))
    with col6:
        st.metric("👥 Visitantes", formatar_valor(totais["total_visitante_mes"]))
    
    # Gráfico de distribuição mensal
    if any([totais["total_dizimo_mes"], totais["total_oferta_mes"], totais["total_visitante_mes"]]):
        st.markdown("---")
        st.markdown("#### 📊 Distribuição Mensal")
        chart_data = pd.DataFrame({
            'Categoria': ['Dízimo', 'Oferta', 'Visitante'],
            'Valor': [
                totais["total_dizimo_mes"], 
                totais["total_oferta_mes"], 
                totais["total_visitante_mes"]
            ]
        })
        st.bar_chart(chart_data.set_index('Categoria'), width="stretch")
    
    # Seção expansível para totais gerais
    with st.expander("📁 Ver Totais Gerais por Categoria (Acumulado)"):
        st.write(f"**Total Geral de Dízimos:** {formatar_valor(totais['total_dizimo_geral'])}")
        st.write(f"**Total Geral de Ofertas:** {formatar_valor(totais['total_oferta_geral'])}")
        st.write(f"**Total Geral de Visitantes:** {formatar_valor(totais['total_visitante_geral'])}")
