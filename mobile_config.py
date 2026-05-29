"""
CSS e Configurações Responsivas para Mobile
"""
import streamlit as st


def aplicar_css_mobile():
    """
    Aplica CSS customizado para melhorar a experiência mobile
    """
    st.markdown("""
    <style>
    /* ========================================
       CONFIGURAÇÕES GERAIS MOBILE
       ======================================== */
    
    /* Remover padding extra em mobile */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        /* Título principal menor em mobile */
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        h4 {
            font-size: 1rem !important;
        }
    }
    
    /* ========================================
       SIDEBAR MOBILE
       ======================================== */
    
    @media (max-width: 768px) {
        /* Sidebar mais compacta */
        [data-testid="stSidebar"] {
            min-width: 200px !important;
        }
        
        /* Logo ajustada ao container da sidebar */
        [data-testid="stSidebar"] img {
            width: 100% !important;
            max-width: 300px !important;
            height: auto !important;
            margin: 0 auto !important;
            display: block !important;
        }
    }
    
    /* ========================================
       FORMULÁRIOS E INPUTS
       ======================================== */
    
    /* Inputs maiores para toque em mobile */
    @media (max-width: 768px) {
        input, select, textarea {
            font-size: 16px !important;
            min-height: 44px !important;
        }
        
        button {
            min-height: 44px !important;
            font-size: 16px !important;
        }
        
        /* Botões mais espaçados */
        .stButton button {
            width: 100% !important;
            margin: 0.5rem 0 !important;
        }
    }
    
    /* ========================================
       MÉTRICAS E CARDS
       ======================================== */
    
    /* Métricas responsivas */
    @media (max-width: 768px) {
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
        }
        
        /* Cards de métrica com espaçamento */
        [data-testid="metric-container"] {
            padding: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
    }
    
    /* ========================================
       TABELAS E DATAFRAMES
       ======================================== */
    
    /* Tabelas com scroll horizontal suave */
    @media (max-width: 768px) {
        [data-testid="stDataFrame"] {
            font-size: 12px !important;
        }
        
        /* Melhor visualização de tabelas */
        .dataframe {
            font-size: 11px !important;
        }
        
        .dataframe th {
            font-size: 11px !important;
            padding: 4px !important;
        }
        
        .dataframe td {
            font-size: 11px !important;
            padding: 4px !important;
        }
    }
    
    /* ========================================
       INFORMAÇÕES E ALERTAS
       ======================================== */
    
    /* Info boxes responsivas */
    @media (max-width: 768px) {
        .stAlert {
            font-size: 0.9rem !important;
            padding: 0.75rem !important;
        }
    }
    
    /* ========================================
       COLUNAS RESPONSIVAS
       ======================================== */
    
    /* Forçar colunas a empilhar em mobile */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
        }
    }
    
    /* ========================================
       EXPANDERS E CONTAINERS
       ======================================== */
    
    @media (max-width: 768px) {
        .streamlit-expanderHeader {
            font-size: 0.95rem !important;
        }
        
        .streamlit-expanderContent {
            font-size: 0.9rem !important;
        }
    }
    
    /* ========================================
       GRÁFICOS
       ======================================== */
    
    /* Gráficos responsivos */
    @media (max-width: 768px) {
        [data-testid="stVegaLiteChart"] {
            width: 100% !important;
        }
    }
    
    /* ========================================
       LOGIN E USUARIO INFO
       ======================================== */
    
    /* Área de usuário compacta em mobile */
    @media (max-width: 768px) {
        .user-info {
            font-size: 0.85rem !important;
            text-align: right !important;
        }
        
        .user-info button {
            font-size: 0.85rem !important;
            padding: 0.25rem 0.75rem !important;
        }
    }
    
    /* ========================================
       MELHORIAS GERAIS DE UX MOBILE
       ======================================== */
    
    /* Remover zoom em inputs (iOS) */
    input[type="text"],
    input[type="number"],
    input[type="email"],
    input[type="password"],
    select,
    textarea {
        font-size: 16px !important;
    }
    
    /* Links e botões mais fáceis de tocar */
    a, button {
        padding: 0.5rem !important;
        margin: 0.25rem 0 !important;
    }
    
    /* Scroll suave */
    html {
        scroll-behavior: smooth;
    }
    
    /* ========================================
       FORM SUBMIT BUTTONS
       ======================================== */
    
    @media (max-width: 768px) {
        .stFormSubmitButton button {
            width: 100% !important;
            min-height: 50px !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
        }
    }
    
    /* ========================================
       SELECTBOX E MULTISELECT
       ======================================== */
    
    @media (max-width: 768px) {
        [data-baseweb="select"] {
            font-size: 16px !important;
        }
    }
    
    /* ========================================
       DATE INPUT
       ======================================== */
    
    @media (max-width: 768px) {
        [data-baseweb="input"] {
            font-size: 16px !important;
        }
    }
    
    /* ========================================
       DIVIDERS
       ======================================== */
    
    @media (max-width: 768px) {
        hr {
            margin: 1rem 0 !important;
        }
    }
    
    /* ========================================
       CHECKBOX E RADIO
       ======================================== */
    
    @media (max-width: 768px) {
        [data-testid="stCheckbox"] label {
            font-size: 16px !important;
        }
        
        [data-testid="stRadio"] label {
            font-size: 16px !important;
        }
    }
    
    </style>
    """, unsafe_allow_html=True)


def detectar_mobile():
    """
    Detecta se o dispositivo é mobile baseado na largura da tela
    Retorna configuração de colunas apropriada
    """
    # Esta é uma aproximação - Streamlit não tem detecção nativa de mobile
    # Retorna configurações que funcionam bem tanto em desktop quanto mobile
    return {
        "metricas_principais": [1, 1, 1],  # 3 colunas que colapsam em mobile via CSS
        "form_dupla": [1, 1],  # 2 colunas que colapsam
        "form_tripla": [1, 2, 2],  # 3 colunas
        "botoes": [1, 1],  # 2 botões
        "usuario_info": [3, 1],  # Título e info do usuário
        "logo_width": 120,  # Largura da logo
    }
