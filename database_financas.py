"""
Módulo de Banco de Dados — Gestão de Finanças
Tabelas: contas_a_pagar, extrato_banco
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Optional, Tuple

from config import DATABASE_NAME


@contextmanager
def get_db_connection():
    """Context manager para conexões com o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_financas_tables():
    """
    Cria as tabelas de finanças se ainda não existirem.

    contas_a_pagar:
        Registra despesas da organização, com suporte a parcelamento.

    extrato_banco:
        Registra entradas e saídas da conta bancária para compor o
        saldo disponível e a projeção de caixa.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contas_a_pagar (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                data_lancamento TEXT    NOT NULL,
                data_vencimento TEXT    NOT NULL,
                valor           REAL    NOT NULL,
                motivo          TEXT    NOT NULL,
                fornecedor      TEXT    NOT NULL,
                status          TEXT    NOT NULL DEFAULT 'A Pagar',
                forma_pagamento TEXT    NOT NULL DEFAULT 'Boleto',
                num_parcelas    INTEGER NOT NULL DEFAULT 1,
                parcelas_pagas  INTEGER NOT NULL DEFAULT 0,
                usuario         TEXT    NOT NULL,
                created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS extrato_banco (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                data        TEXT    NOT NULL,
                descricao   TEXT    NOT NULL,
                valor       REAL    NOT NULL,
                tipo        TEXT    NOT NULL DEFAULT 'Crédito',
                usuario     TEXT    NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# CONTAS A PAGAR
# ─────────────────────────────────────────────────────────────────────────────

def adicionar_conta(
    data_lancamento: str,
    data_vencimento: str,
    valor: float,
    motivo: str,
    fornecedor: str,
    status: str,
    forma_pagamento: str,
    num_parcelas: int,
    parcelas_pagas: int,
    usuario: str,
) -> bool:
    """Insere uma nova conta a pagar. Retorna True em caso de sucesso."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO contas_a_pagar
                    (data_lancamento, data_vencimento, valor, motivo,
                     fornecedor, status, forma_pagamento,
                     num_parcelas, parcelas_pagas, usuario)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data_lancamento, data_vencimento, valor, motivo,
                    fornecedor, status, forma_pagamento,
                    num_parcelas, parcelas_pagas, usuario,
                ),
            )
            conn.commit()
        return True
    except Exception as exc:
        print(f"Erro ao adicionar conta: {exc}")
        return False


def listar_contas(usuario: Optional[str] = None, nivel: str = "diacono") -> List[Tuple]:
    """
    Retorna todas as contas a pagar.
    Admin vê tudo; diacono vê apenas os próprios registros.
    """
    with get_db_connection() as conn:
        if nivel == "admin":
            rows = conn.execute(
                "SELECT * FROM contas_a_pagar ORDER BY data_vencimento ASC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM contas_a_pagar WHERE usuario = ? ORDER BY data_vencimento ASC",
                (usuario,),
            ).fetchall()
    return rows


def atualizar_conta(conta_id: int, **campos) -> bool:
    """
    Atualiza campos de uma conta a pagar.
    Aceita qualquer subconjunto dos campos editáveis.
    """
    editaveis = {
        "data_lancamento", "data_vencimento", "valor", "motivo",
        "fornecedor", "status", "forma_pagamento",
        "num_parcelas", "parcelas_pagas",
    }
    atualizacoes = {k: v for k, v in campos.items() if k in editaveis}
    if not atualizacoes:
        return False
    set_clause = ", ".join(f"{col} = ?" for col in atualizacoes)
    valores = list(atualizacoes.values()) + [conta_id]
    try:
        with get_db_connection() as conn:
            conn.execute(
                f"UPDATE contas_a_pagar SET {set_clause} WHERE id = ?",
                valores,
            )
            conn.commit()
        return True
    except Exception as exc:
        print(f"Erro ao atualizar conta: {exc}")
        return False


def excluir_conta(conta_id: int) -> bool:
    """Remove uma conta a pagar pelo ID."""
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM contas_a_pagar WHERE id = ?", (conta_id,))
            conn.commit()
        return True
    except Exception as exc:
        print(f"Erro ao excluir conta: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# EXTRATO BANCÁRIO
# ─────────────────────────────────────────────────────────────────────────────

def adicionar_extrato(
    data: str,
    descricao: str,
    valor: float,
    tipo: str,
    usuario: str,
) -> bool:
    """Insere um lançamento no extrato bancário."""
    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO extrato_banco (data, descricao, valor, tipo, usuario)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data, descricao, abs(valor), tipo, usuario),
            )
            conn.commit()
        return True
    except Exception as exc:
        print(f"Erro ao adicionar extrato: {exc}")
        return False


def listar_extrato(usuario: Optional[str] = None, nivel: str = "diacono") -> List[Tuple]:
    """Retorna lançamentos do extrato bancário."""
    with get_db_connection() as conn:
        if nivel == "admin":
            rows = conn.execute(
                "SELECT * FROM extrato_banco ORDER BY data DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM extrato_banco WHERE usuario = ? ORDER BY data DESC",
                (usuario,),
            ).fetchall()
    return rows


def excluir_extrato(extrato_id: int) -> bool:
    """Remove um lançamento do extrato."""
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM extrato_banco WHERE id = ?", (extrato_id,))
            conn.commit()
        return True
    except Exception as exc:
        print(f"Erro ao excluir extrato: {exc}")
        return False
