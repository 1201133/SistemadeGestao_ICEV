"""
Módulo de Funções Utilitárias
"""
import streamlit as st
from PIL import Image
from datetime import datetime
from typing import List, Tuple
from config import LOGO_PATH
from mobile_config import detectar_mobile


def display_logo():
    """Exibe o logo da igreja ou um texto alternativo - responsivo para mobile"""
    config = detectar_mobile()
    
    try:
        logo = Image.open(LOGO_PATH)
        # Exibe com largura total da sidebar para melhor enquadramento visual
        st.image(logo, width="stretch")
    except:
        st.markdown("""
        <style>
            .logo {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                text-align: center;
                margin: 10px 0;
                padding: 10px;
            }
            @media (max-width: 768px) {
                .logo {
                    font-size: 12px;
                }
            }
        </style>
        <div class="logo">🕊 MINISTÉRIO DECHONAI</div>
        """, unsafe_allow_html=True)


def formatar_valor(valor: float) -> str:
    """Formata um valor numérico para moeda brasileira"""
    return f"R$ {valor:.2f}"


def formatar_data(data_str: str, formato_entrada: str = "%Y-%m-%d", 
                  formato_saida: str = "%d/%m/%Y") -> str:
    """Formata uma data de um formato para outro"""
    try:
        data_obj = datetime.strptime(data_str, formato_entrada)
        return data_obj.strftime(formato_saida)
    except:
        return data_str


def validar_nome(nome: str) -> bool:
    """Valida se o nome é válido"""
    return len(nome.strip()) >= 2


def validar_valor(valor: float) -> bool:
    """Valida se o valor é válido"""
    return valor > 0


def calcular_totais(lancamentos: List[Tuple]) -> dict:
    """
    Calcula os totais financeiros dos lançamentos
    
    Args:
        lancamentos: Lista de tuplas com os dados dos lançamentos
    
    Returns:
        Dicionário com os totais calculados
    
    Nota: A função ajusta dinamicamente os índices baseado no número de campos
    """
    hoje = datetime.today().strftime("%Y-%m-%d")
    mes_atual_str = datetime.today().strftime("%Y-%m")
    
    # Descobrir se temos a coluna usuario (admin) ou não
    # Se o primeiro lançamento tem mais de 10 campos, inclui usuario
    tem_usuario = len(lancamentos[0]) > 10 if lancamentos else False
    
    # Índices dos campos principais (sempre presentes)
    idx_data = 1
    idx_valor = 3
    idx_categoria = 5
    
    total_geral = sum(l[idx_valor] for l in lancamentos)
    
    lancamentos_hoje = [l for l in lancamentos if l[idx_data] == hoje]
    lancamentos_mes_atual = [l for l in lancamentos if l[idx_data].startswith(mes_atual_str)]
    
    total_dia = sum(l[idx_valor] for l in lancamentos_hoje)
    total_mes = sum(l[idx_valor] for l in lancamentos_mes_atual)
    
    total_dizimo_geral = sum(l[idx_valor] for l in lancamentos if l[idx_categoria] == "Dízimo")
    total_oferta_geral = sum(l[idx_valor] for l in lancamentos if l[idx_categoria] == "Oferta")
    total_visitante_geral = sum(l[idx_valor] for l in lancamentos if l[idx_categoria] == "Visitante")
    
    total_dizimo_mes = sum(l[idx_valor] for l in lancamentos_mes_atual if l[idx_categoria] == "Dízimo")
    total_oferta_mes = sum(l[idx_valor] for l in lancamentos_mes_atual if l[idx_categoria] == "Oferta")
    total_visitante_mes = sum(l[idx_valor] for l in lancamentos_mes_atual if l[idx_categoria] == "Visitante")
    
    return {
        "total_geral": total_geral,
        "total_dia": total_dia,
        "total_mes": total_mes,
        "total_dizimo_geral": total_dizimo_geral,
        "total_oferta_geral": total_oferta_geral,
        "total_visitante_geral": total_visitante_geral,
        "total_dizimo_mes": total_dizimo_mes,
        "total_oferta_mes": total_oferta_mes,
        "total_visitante_mes": total_visitante_mes
    }


def exibir_usuario_info():
    """Exibe informações do usuário logado no topo da página - responsivo"""
    config = detectar_mobile()
    
    # Layout responsivo que empilha em mobile
    col_title, col_user_info = st.columns(config["usuario_info"])
    
    with col_title:
        st.title("💰 Dízimos e Ofertas")
    
    with col_user_info:
        # Informações compactas do usuário
        st.markdown("""
        <style>
        .user-box {
            background-color: #f0f2f6;
            padding: 0.75rem;
            border-radius: 0.5rem;
            text-align: right;
        }
        .user-box p {
            margin: 0;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        .user-box strong {
            color: #1f77b4;
        }
        @media (max-width: 768px) {
            .user-box {
                text-align: center;
                margin-top: 0.5rem;
            }
            .user-box p {
                font-size: 0.8rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="user-box">
            <p><strong>{st.session_state['nome']}</strong></p>
            <p>🔑 {st.session_state['nivel'].capitalize()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Sair", width="stretch"):
            st.session_state.clear()
            st.rerun()
