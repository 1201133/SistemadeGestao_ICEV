"""
Módulo de Configurações do Sistema
"""
import os

# Tenta importar streamlit para uso de secrets (Streamlit Community Cloud)
try:
    import streamlit as st
except (ImportError, FileNotFoundError, Exception):
    st = None

# Carrega variáveis de ambiente do arquivo .env (desenvolvimento local)
# Mesmo com Streamlit secrets habilitado, manter o .env como fallback.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_secret(key, section=None):
    """
    Obtém valores secretos de forma flexível:
    - Streamlit Cloud: usa st.secrets
    - Desenvolvimento local: usa .env
    """
    if st is not None:
        try:
            if section:
                # Suporta formato TOML com seção, ex.: [passwords]
                if section in st.secrets and key in st.secrets[section]:
                    return st.secrets[section][key]
            # Suporta chave no topo do secrets, sem seção
            if key in st.secrets:
                return st.secrets[key]
        except Exception as e:
            print(f"Erro ao acessar secret {key}: {e}")

    # Fallback para variáveis de ambiente (.env)
    value = os.getenv(key)
    if value:
        return value
    return None

# ============================================
# CONFIGURAÇÃO DE USUÁRIOS E ACESSOS
# ============================================

# ATENÇÃO: As senhas agora são armazenadas como hashes bcrypt
# Gere novos hashes bcrypt antes de atualizar o .env ou os Secrets
# 
# Desenvolvimento local: configure no arquivo .env
# Streamlit Cloud: configure em Settings → Secrets

USUARIOS_HASHES = {
    "admin": get_secret('USER_ADMIN_HASH', 'passwords') or get_secret('USER_ADMIN_HASH'),
    "diacono01": get_secret('USER_DIACONO01_HASH', 'passwords') or get_secret('USER_DIACONO01_HASH'),
    "diacono02": get_secret('USER_DIACONO02_HASH', 'passwords') or get_secret('USER_DIACONO02_HASH'),
    "diacono03": get_secret('USER_DIACONO03_HASH', 'passwords') or get_secret('USER_DIACONO03_HASH')
}

NIVEIS_ACESSO = {
    "admin": "admin",
    "diacono01": "diacono",
    "diacono02": "diacono",
    "diacono03": "diacono"
}

NOMES_USUARIOS = {
    "admin": "Administrador",
    "diacono01": "Diácono01",
    "diacono02": "Diácono02",
    "diacono03": "Diácono03"
}

# ============================================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================================

# Permite sobrescrever caminho do banco via variável de ambiente.
_db_from_env = os.getenv("DATABASE_NAME")

if _db_from_env:
    DATABASE_NAME = _db_from_env
else:
    # Em Windows acessando projeto por \\wsl$, SQLite pode falhar com lock.
    # Nesse caso, usa um caminho local no AppData para escrita confiável.
    if os.name == "nt" and os.getcwd().startswith("\\\\wsl$\\"):
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            db_dir = os.path.join(local_appdata, "DizimosOfertas")
            os.makedirs(db_dir, exist_ok=True)
            DATABASE_NAME = os.path.join(db_dir, "dizimos_ofertas.db")
        else:
            DATABASE_NAME = "dizimos_ofertas.db"
    else:
        DATABASE_NAME = "dizimos_ofertas.db"

# ============================================
# CONFIGURAÇÕES DA APLICAÇÃO
# ============================================

PAGE_TITLE = "Dízimos e Ofertas"
PAGE_ICON = "💰"
LAYOUT = "wide"

_logo_candidates = [
    "./imagem/imagem-ICEV-Logo.png",
    "./imagem/imagem-ICEV-Login.png",
    "./imagem/imagem-ICVE-Login.png",
    "./imagem/imagem-ICEV-logo.png",
    "./imagem/logo-login.png",
    "./imagem/igrejadechomai.jpg",
]
LOGO_PATH = next((path for path in _logo_candidates if os.path.exists(path)), "./imagem/igrejadechomai.jpg")
FAVICON_PATH = LOGO_PATH

# ============================================
# CATEGORIAS E TIPOS
# ============================================

TIPOS_PAGAMENTO = ["Dinheiro", "Cartão", "Transferência", "Cheque", "Pix"]
CATEGORIAS = ["Dízimo", "Oferta", "Visitante"]

# ============================================
# OPERADORAS DE CELULAR
# ============================================

OPERADORAS = [
    "Vivo",
    "Claro",
    "TIM",
    "Oi",
    "Algar",
    "Nextel",
    "Sercomtel",
    "Outra"
]


# ============================================
# CONFIGURAÇÕES DE EMAIL (NEWSLETTER)
# ============================================

def str_to_bool(value, default=False):
    """Converte string para booleano com fallback seguro."""
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "t", "yes", "y", "on"}


SMTP_ENABLED = str_to_bool(get_secret("SMTP_ENABLED"), default=False)
SMTP_HOST = get_secret("SMTP_HOST") or get_secret("SMTP_HOST", "smtp")
SMTP_PORT = int((get_secret("SMTP_PORT") or get_secret("SMTP_PORT", "smtp") or 587))
SMTP_USER = get_secret("SMTP_USER") or get_secret("SMTP_USER", "smtp")
SMTP_PASSWORD = get_secret("SMTP_PASSWORD") or get_secret("SMTP_PASSWORD", "smtp")
SMTP_FROM_NAME = (get_secret("SMTP_FROM_NAME") or get_secret("SMTP_FROM_NAME", "smtp") or "Sistema de Dízimos e Ofertas")
SMTP_FROM_EMAIL = (get_secret("SMTP_FROM_EMAIL") or get_secret("SMTP_FROM_EMAIL", "smtp") or SMTP_USER)
SMTP_USE_TLS = str_to_bool(get_secret("SMTP_USE_TLS") or get_secret("SMTP_USE_TLS", "smtp"), default=True)

if get_secret("SMTP_ENABLED") is not None:
    SMTP_ENABLED = str_to_bool(get_secret("SMTP_ENABLED"), default=False)
else:
    SMTP_ENABLED = str_to_bool(get_secret("SMTP_ENABLED", "smtp"), default=False)


# ============================================
# CONFIGURAÇÕES RAPIDAPI (CORRETOR ORTOGRÁFICO)
# ============================================

JSPELL_API_URL = get_secret("JSPELL_API_URL") or "https://jspell-checker.p.rapidapi.com/check"
JSPELL_API_HOST = get_secret("JSPELL_API_HOST") or "jspell-checker.p.rapidapi.com"
JSPELL_API_KEY = get_secret("JSPELL_API_KEY") or get_secret("RAPIDAPI_KEY")
JSPELL_TIMEOUT_SECONDS = int(get_secret("JSPELL_TIMEOUT_SECONDS") or 20)

