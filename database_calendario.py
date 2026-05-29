"""
CRUD para eventos do calendário.
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional

from config import DATABASE_NAME


@contextmanager
def _get_conn():
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_calendario_table() -> None:
    """Cria a tabela de eventos do calendário, se necessário."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS eventos_calendario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descricao TEXT,
                local TEXT,
                inicio TEXT NOT NULL,
                fim TEXT,
                dia_todo INTEGER DEFAULT 0,
                cor TEXT DEFAULT '#1b7ebd',
                criado_por TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def criar_evento(
    titulo: str,
    descricao: str,
    local: str,
    inicio_iso: str,
    fim_iso: Optional[str],
    dia_todo: bool,
    cor: str,
    criado_por: str,
) -> Optional[int]:
    """Insere um novo evento e retorna o ID."""
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO eventos_calendario
                (titulo, descricao, local, inicio, fim, dia_todo, cor, criado_por)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    titulo.strip(),
                    (descricao or "").strip(),
                    (local or "").strip(),
                    inicio_iso,
                    fim_iso,
                    int(bool(dia_todo)),
                    cor or "#1b7ebd",
                    criado_por,
                ),
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao criar evento: {e}")
        return None


def listar_eventos(limit: int = 300, criado_por: Optional[str] = None) -> List[sqlite3.Row]:
    """Lista eventos mais recentes."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        if criado_por:
            cursor.execute(
                """
                SELECT id, titulo, descricao, local, inicio, fim, dia_todo, cor, criado_por, created_at, updated_at
                FROM eventos_calendario
                WHERE criado_por = ?
                ORDER BY inicio DESC, id DESC
                LIMIT ?
                """,
                (criado_por, limit),
            )
        else:
            cursor.execute(
                """
                SELECT id, titulo, descricao, local, inicio, fim, dia_todo, cor, criado_por, created_at, updated_at
                FROM eventos_calendario
                ORDER BY inicio DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
        return cursor.fetchall()


def obter_evento_por_id(evento_id: int) -> Optional[sqlite3.Row]:
    """Busca um evento por ID."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, titulo, descricao, local, inicio, fim, dia_todo, cor, criado_por, created_at, updated_at
            FROM eventos_calendario
            WHERE id = ?
            """,
            (evento_id,),
        )
        return cursor.fetchone()


def atualizar_evento(
    evento_id: int,
    titulo: str,
    descricao: str,
    local: str,
    inicio_iso: str,
    fim_iso: Optional[str],
    dia_todo: bool,
    cor: str,
    criado_por: Optional[str] = None,
) -> bool:
    """Atualiza dados do evento."""
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            if criado_por:
                cursor.execute(
                    """
                    UPDATE eventos_calendario
                    SET
                        titulo = ?,
                        descricao = ?,
                        local = ?,
                        inicio = ?,
                        fim = ?,
                        dia_todo = ?,
                        cor = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND criado_por = ?
                    """,
                    (
                        titulo.strip(),
                        (descricao or "").strip(),
                        (local or "").strip(),
                        inicio_iso,
                        fim_iso,
                        int(bool(dia_todo)),
                        cor or "#1b7ebd",
                        evento_id,
                        criado_por,
                    ),
                )
            else:
                cursor.execute(
                    """
                    UPDATE eventos_calendario
                    SET
                        titulo = ?,
                        descricao = ?,
                        local = ?,
                        inicio = ?,
                        fim = ?,
                        dia_todo = ?,
                        cor = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        titulo.strip(),
                        (descricao or "").strip(),
                        (local or "").strip(),
                        inicio_iso,
                        fim_iso,
                        int(bool(dia_todo)),
                        cor or "#1b7ebd",
                        evento_id,
                    ),
                )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar evento {evento_id}: {e}")
        return False


def excluir_evento(evento_id: int, criado_por: Optional[str] = None) -> bool:
    """Exclui evento por ID."""
    try:
        with _get_conn() as conn:
            cursor = conn.cursor()
            if criado_por:
                cursor.execute("DELETE FROM eventos_calendario WHERE id = ? AND criado_por = ?", (evento_id, criado_por))
            else:
                cursor.execute("DELETE FROM eventos_calendario WHERE id = ?", (evento_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir evento {evento_id}: {e}")
        return False
