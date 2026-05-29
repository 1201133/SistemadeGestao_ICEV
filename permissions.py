"""
Módulo de Gerenciamento de Permissões por Usuário

Permite ao admin configurar quais funcionalidades cada diácono pode acessar.
As permissões são armazenadas no mesmo banco SQLite da aplicação.
"""

import sqlite3
from contextlib import contextmanager

from config import DATABASE_NAME

# ─────────────────────────────────────────────────────────────────────────────
# Catálogo de módulos controláveis do sistema
# ─────────────────────────────────────────────────────────────────────────────

MODULOS_SISTEMA = {
    "visualizar": {
        "label": "Visualizar",
        "icon": "👁️",
        "descricao": "Visualizar lançamentos de dízimos e ofertas",
        "menu_icon": "list",
    },
    "registrar": {
        "label": "Registrar",
        "icon": "➕",
        "descricao": "Registrar novos lançamentos",
        "menu_icon": "plus-circle",
    },
    "membros": {
        "label": "Cadastro de Membros",
        "icon": "👥",
        "descricao": "Gerenciar cadastro de membros da igreja",
        "menu_icon": "people",
    },
    "aniversariantes": {
        "label": "Aniversariantes",
        "icon": "🎂",
        "descricao": "Visualizar e exportar lista de aniversariantes",
        "menu_icon": "balloon-heart",
    },
    "certificado": {
        "label": "Certificado",
        "icon": "📜",
        "descricao": "Visualizar certificado e baixar em PDF A4",
        "menu_icon": "award",
    },
    "newsletter": {
        "label": "Newsletter",
        "icon": "📰",
        "descricao": "Criar comunicados e gerenciar os próprios envios; admin pode administrar todos",
        "menu_icon": "envelope-paper",
    },
    "calendario": {
        "label": "Calendário",
        "icon": "📅",
        "descricao": "Consultar e criar eventos próprios; admin pode administrar todos e enviar agenda global",
        "menu_icon": "calendar-event",
    },
    "editar": {
        "label": "Editar Lançamentos",
        "icon": "✏️",
        "descricao": "Editar e excluir lançamentos próprios; admin pode administrar todos",
        "menu_icon": "pencil-square",
    },
    "financas": {
        "label": "Gestão de Finanças",
        "icon": "💰",
        "descricao": "Controle de contas a pagar, extrato bancário e projeção de caixa",
        "menu_icon": "cash-coin",
    },
}

# Usuários cujas permissões são gerenciadas pelo admin
USUARIOS_DIACONO = ["diacono01", "diacono02", "diacono03"]


# ─────────────────────────────────────────────────────────────────────────────
# Conexão interna
# ─────────────────────────────────────────────────────────────────────────────

@contextmanager
def _get_conn():
    """Context manager de conexão isolado para este módulo."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Inicialização da tabela
# ─────────────────────────────────────────────────────────────────────────────

def init_permissions_table():
    """
    Cria a tabela 'permissoes_usuarios' caso não exista e popula
    com entradas padrão (desabilitadas) para todos os diáconos.
    Usa INSERT OR IGNORE para não sobrescrever configurações já salvas.
    """
    with _get_conn() as conn:
        cursor = conn.cursor()

        # Cria tabela com chave primária composta (usuario, modulo)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissoes_usuarios (
                usuario TEXT NOT NULL,
                modulo  TEXT NOT NULL,
                ativo   INTEGER DEFAULT 0,
                PRIMARY KEY (usuario, modulo)
            )
        ''')
        conn.commit()

        # Garante que cada diácono possui uma linha para cada módulo
        for usuario in USUARIOS_DIACONO:
            for modulo in MODULOS_SISTEMA:
                cursor.execute(
                    "INSERT OR IGNORE INTO permissoes_usuarios (usuario, modulo, ativo) VALUES (?, ?, 0)",
                    (usuario, modulo),
                )
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# Consultas e atualizações
# ─────────────────────────────────────────────────────────────────────────────

def usuario_tem_permissao(usuario: str, modulo: str) -> bool:
    """
    Verifica se um usuário pode acessar um módulo específico.

    Regras:
    - nivel == "admin"  → acesso total sem consultar o banco
    - nivel == "diacono" → consulta a tabela permissoes_usuarios
    - qualquer outro nivel → acesso negado
    """
    # Importação local para evitar dependência circular no nível de módulo
    from config import NIVEIS_ACESSO

    nivel = NIVEIS_ACESSO.get(usuario, "")

    # Administrador tem acesso irrestrito a tudo
    if nivel == "admin":
        return True

    # Para diáconos, consulta o banco
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT ativo FROM permissoes_usuarios WHERE usuario = ? AND modulo = ?",
            (usuario, modulo),
        )
        row = cursor.fetchone()
        return bool(row and row[0])


def get_permissoes_usuario(usuario: str) -> dict:
    """
    Retorna um dicionário {modulo: bool} com todas as permissões
    salvas para o usuário informado.
    Módulos ainda não cadastrados na tabela são retornados como False.
    """
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT modulo, ativo FROM permissoes_usuarios WHERE usuario = ?",
            (usuario,),
        )
        rows = cursor.fetchall()

    # Constrói o dict garantindo que todos os módulos aparecem
    resultado = {modulo: False for modulo in MODULOS_SISTEMA}
    for modulo, ativo in rows:
        resultado[modulo] = bool(ativo)
    return resultado


def salvar_permissoes_usuario(usuario: str, permissoes: dict) -> bool:
    """
    Persiste o dicionário {modulo: bool} no banco.
    Usa UPSERT (INSERT … ON CONFLICT DO UPDATE) para atualizar ou inserir.

    Retorna True em caso de sucesso, False se ocorrer erro.
    """
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            for modulo, ativo in permissoes.items():
                cursor.execute(
                    """
                    INSERT INTO permissoes_usuarios (usuario, modulo, ativo)
                    VALUES (?, ?, ?)
                    ON CONFLICT(usuario, modulo) DO UPDATE SET ativo = excluded.ativo
                    """,
                    (usuario, modulo, int(bool(ativo))),
                )
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao salvar permissões de {usuario}: {e}")
        return False
