"""
Módulo de Gerenciamento do Banco de Dados
"""
import sqlite3
from contextlib import contextmanager
from typing import List, Tuple, Optional
from config import DATABASE_NAME
from database_membros import init_membros_table
from database_newsletter import init_newsletter_table
from database_calendario import init_calendario_table
from database_financas import init_financas_tables
from permissions import init_permissions_table


@contextmanager
def get_db_connection():
    """Context manager para gerenciar conexões com o banco de dados"""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Inicializa o banco de dados criando as tabelas necessárias
    
    Tabela lancamentos:
    - id: Identificador único auto-incrementado
    - data: Data do lançamento
    - nome: Nome do contribuinte
    - valor: Valor da contribuição
    - tipo: Tipo de pagamento (Dinheiro, Cartão, etc)
    - categoria: Categoria da contribuição (Dízimo, Oferta, Visitante)
    - usuario: Usuário que registrou o lançamento
    - email: Email do contribuinte (opcional)
    - codigo_area: Código de área do celular (opcional)
    - celular: Número do celular (opcional)
    - operadora: Operadora do celular (opcional)
    - created_at: Data/hora de criação do registro
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                nome TEXT NOT NULL,
                valor REAL NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                usuario TEXT NOT NULL,
                email TEXT,
                codigo_area TEXT,
                celular TEXT,
                operadora TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    
    init_membros_table()
    init_newsletter_table()
    init_calendario_table()
    init_financas_tables()
    init_permissions_table()


def adicionar_lancamento(data: str, nome: str, valor: float, tipo: str, 
                        categoria: str, usuario: str, email: str = None,
                        telefone: str = None, codigo_area: str = None, 
                        celular: str = None, operadora: str = None) -> bool:
    """
    Adiciona um novo lançamento ao banco de dados
    
    Args:
        data: Data do lançamento no formato YYYY-MM-DD
        nome: Nome do contribuinte
        valor: Valor da contribuição
        tipo: Tipo de pagamento
        categoria: Categoria da contribuição
        usuario: Usuário que está registrando
        email: Email do contribuinte (opcional)
        telefone: Telefone completo formatado (opcional, prioridade)
        codigo_area: Código de área do celular (compatibilidade)
        celular: Número do celular sem DDD (compatibilidade)
        operadora: Operadora do celular (compatibilidade)
    
    Returns:
        True se adicionado com sucesso, False caso contrário
    """
    try:
        # Se telefone completo não foi fornecido, usa codigo_area + celular
        if not codigo_area and telefone:
            # Extrai DDD do telefone formatado
            numeros = ''.join(filter(str.isdigit, telefone))
            if len(numeros) >= 11:
                codigo_area = numeros[:2]
                celular = numeros[2:]
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO lancamentos 
                (data, nome, valor, tipo, categoria, usuario, email, codigo_area, celular, operadora) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data, nome, valor, tipo, categoria, usuario, email, codigo_area, celular, operadora))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar lançamento: {e}")
        return False


def obter_lancamentos(usuario: Optional[str] = None, nivel_acesso: str = "diacono") -> List[Tuple]:
    """
    Obtém lançamentos do banco de dados com base no usuário e nível de acesso.
    
    Args:
        usuario: Nome de usuário para filtrar (opcional)
        nivel_acesso: Nível do usuário. `admin` vê todos; demais níveis filtram por `usuario`.
    
    Returns:
        Lista de tuplas com os dados dos lançamentos
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if usuario and nivel_acesso != "admin":
            cursor.execute('''
                SELECT id, data, nome, valor, tipo, categoria, email, codigo_area, celular, operadora
                FROM lancamentos 
                WHERE usuario = ? 
                ORDER BY data DESC, id DESC
            ''', (usuario,))
        else:
            cursor.execute('''
                SELECT id, data, nome, valor, tipo, categoria, usuario, email, codigo_area, celular, operadora
                FROM lancamentos 
                ORDER BY data DESC, id DESC
            ''')
        
        return cursor.fetchall()


def atualizar_lancamento(id_lancamento: int, data: str, nome: str, 
                        valor: float, tipo: str, categoria: str,
                        email: str = None, codigo_area: str = None,
                        celular: str = None, operadora: str = None,
                        usuario: str = None) -> bool:
    """
    Atualiza um lançamento existente
    
    Args:
        id_lancamento: ID do lançamento a ser atualizado
        data: Nova data do lançamento
        nome: Novo nome do contribuinte
        valor: Novo valor da contribuição
        tipo: Novo tipo de pagamento
        categoria: Nova categoria
        email: Novo email (opcional)
        codigo_area: Novo código de área (opcional)
        celular: Novo número de celular (opcional)
        operadora: Nova operadora (opcional)
    
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if usuario:
                cursor.execute('''
                    UPDATE lancamentos 
                    SET data = ?, nome = ?, valor = ?, tipo = ?, categoria = ?,
                        email = ?, codigo_area = ?, celular = ?, operadora = ?
                    WHERE id = ? AND usuario = ?
                ''', (data, nome, valor, tipo, categoria, email, codigo_area, celular, operadora, id_lancamento, usuario))
            else:
                cursor.execute('''
                    UPDATE lancamentos 
                    SET data = ?, nome = ?, valor = ?, tipo = ?, categoria = ?,
                        email = ?, codigo_area = ?, celular = ?, operadora = ?
                    WHERE id = ?
                ''', (data, nome, valor, tipo, categoria, email, codigo_area, celular, operadora, id_lancamento))
            conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar lançamento: {e}")
        return False


def excluir_lancamento(id_lancamento: int, usuario: str = None) -> bool:
    """Exclui um lançamento do banco de dados"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            if usuario:
                cursor.execute('DELETE FROM lancamentos WHERE id = ? AND usuario = ?', (id_lancamento, usuario))
            else:
                cursor.execute('DELETE FROM lancamentos WHERE id = ?', (id_lancamento,))
            conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao excluir lançamento: {e}")
        return False


def obter_lancamento_por_id(id_lancamento: int) -> Optional[Tuple]:
    """
    Obtém um lançamento específico pelo ID
    
    Args:
        id_lancamento: ID do lançamento
    
    Returns:
        Tupla com os dados do lançamento ou None se não encontrado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, data, nome, valor, tipo, categoria, usuario, email, codigo_area, celular, operadora
            FROM lancamentos 
            WHERE id = ?
        ''', (id_lancamento,))
        return cursor.fetchone()
