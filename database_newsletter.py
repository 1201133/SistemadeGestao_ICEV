"""
Módulo de persistência da Newsletter/Comunicados.
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from config import DATABASE_NAME


@contextmanager
def get_db_connection():
    """Context manager para gerenciar conexões com o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_newsletter_table():
    """Cria a tabela de newsletters/comunicados caso não exista."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS newsletters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                data_evento TEXT NOT NULL,
                resumo TEXT,
                conteudo TEXT NOT NULL,
                assunto_email TEXT,
                publicado INTEGER DEFAULT 1,
                email_enviado INTEGER DEFAULT 0,
                criado_por TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def criar_newsletter(
    titulo: str,
    data_evento: str,
    resumo: str,
    conteudo: str,
    assunto_email: str,
    criado_por: str,
    publicado: bool = True,
) -> Optional[int]:
    """Insere um comunicado e retorna o ID criado."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO newsletters
                (titulo, data_evento, resumo, conteudo, assunto_email, publicado, criado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    titulo.strip(),
                    data_evento,
                    resumo.strip() if resumo else None,
                    conteudo.strip(),
                    assunto_email.strip() if assunto_email else None,
                    int(bool(publicado)),
                    criado_por,
                ),
            )
            conn.commit()
            return int(cursor.lastrowid)
    except Exception as e:
        print(f"Erro ao criar newsletter: {e}")
        return None


def listar_newsletters(limit: int = 100, criado_por: Optional[str] = None) -> List[sqlite3.Row]:
    """Lista os comunicados mais recentes."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if criado_por:
            cursor.execute(
                """
                SELECT id, titulo, data_evento, resumo, conteudo, assunto_email,
                       publicado, email_enviado, criado_por, created_at, updated_at
                FROM newsletters
                WHERE criado_por = ?
                ORDER BY data_evento DESC, id DESC
                LIMIT ?
                """,
                (criado_por, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, titulo, data_evento, resumo, conteudo, assunto_email,
                       publicado, email_enviado, criado_por, created_at, updated_at
                FROM newsletters
                ORDER BY data_evento DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
        return cursor.fetchall()


def obter_newsletter_por_id(newsletter_id: int) -> Optional[sqlite3.Row]:
    """Retorna um comunicado pelo ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, titulo, data_evento, resumo, conteudo, assunto_email,
                   publicado, email_enviado, criado_por, created_at, updated_at
            FROM newsletters
            WHERE id = ?
            """,
            (newsletter_id,),
        )
        return cursor.fetchone()


def marcar_email_enviado(newsletter_id: int) -> bool:
    """Marca o comunicado como enviado por e-mail."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE newsletters
                SET email_enviado = 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (newsletter_id,),
            )
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao marcar e-mail como enviado: {e}")
        return False


def atualizar_newsletter(
    newsletter_id: int,
    titulo: str,
    data_evento: str,
    resumo: str,
    conteudo: str,
    assunto_email: str,
    publicado: bool,
    criado_por: Optional[str] = None,
) -> bool:
    """Atualiza os dados de um comunicado existente."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if criado_por:
                cursor.execute(
                    """
                    UPDATE newsletters
                    SET titulo = ?,
                        data_evento = ?,
                        resumo = ?,
                        conteudo = ?,
                        assunto_email = ?,
                        publicado = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND criado_por = ?
                    """,
                    (
                        titulo.strip(),
                        data_evento,
                        resumo.strip() if resumo else None,
                        conteudo.strip(),
                        assunto_email.strip() if assunto_email else None,
                        int(bool(publicado)),
                        newsletter_id,
                        criado_por,
                    ),
                )
            else:
                cursor.execute(
                    """
                    UPDATE newsletters
                    SET titulo = ?,
                        data_evento = ?,
                        resumo = ?,
                        conteudo = ?,
                        assunto_email = ?,
                        publicado = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        titulo.strip(),
                        data_evento,
                        resumo.strip() if resumo else None,
                        conteudo.strip(),
                        assunto_email.strip() if assunto_email else None,
                        int(bool(publicado)),
                        newsletter_id,
                    ),
                )
            conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar newsletter: {e}")
        return False


def excluir_newsletter(newsletter_id: int, criado_por: Optional[str] = None) -> bool:
    """Exclui um comunicado pelo ID."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if criado_por:
                cursor.execute("DELETE FROM newsletters WHERE id = ? AND criado_por = ?", (newsletter_id, criado_por))
            else:
                cursor.execute("DELETE FROM newsletters WHERE id = ?", (newsletter_id,))
            conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir newsletter: {e}")
        return False