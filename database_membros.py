"""
Módulo de Gerenciamento do Cadastro de Membros
"""
import sqlite3
import requests
from contextlib import contextmanager
from typing import List, Tuple, Optional
from config import DATABASE_NAME


@contextmanager
def get_db_connection():
    """Context manager para gerenciar conexões com o banco de dados"""
    conn = sqlite3.connect(DATABASE_NAME, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_membros_table():
    """
    Inicializa a tabela de membros no banco de dados
    
    Tabela membros:
    - id: Identificador único auto-incrementado
    - nome: Nome completo do membro
    - data_nascimento: Data de nascimento
    - cep: Código de Endereçamento Postal
    - numero: Número do endereço
    - complemento: Complemento do endereço (opcional)
    - logradouro: Nome da rua/avenida
    - bairro: Bairro
    - cidade: Cidade
    - estado: Estado (UF)
    - email: Endereço de e-mail
    - telefone: Número de telefone
    - created_at: Data/hora de criação do registro
    - updated_at: Data/hora da última atualização
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS membros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_nascimento TEXT NOT NULL,
                cep TEXT,
                numero TEXT,
                complemento TEXT,
                logradouro TEXT,
                bairro TEXT,
                cidade TEXT,
                estado TEXT,
                email TEXT,
                telefone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()


def validar_cep(cep: str) -> Tuple[bool, object]:
    """
    Valida e consulta um CEP na API ViaCEP.

    Args:
        cep: CEP com ou sem máscara

    Returns:
        (True, dados_json) quando encontrado
        (False, mensagem_erro) quando inválido ou não encontrado
    """
    cep = ''.join(filter(str.isdigit, cep))

    if len(cep) != 8:
        return False, "CEP deve conter 8 dígitos"

    url = f"https://viacep.com.br/ws/{cep}/json/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'erro' in data:
            return False, "CEP não encontrado"

        return True, data
    except requests.RequestException:
        return False, "Erro ao consultar CEP"
    except ValueError:
        return False, "Resposta inválida da API"


def buscar_cep(cep: str) -> Optional[dict]:
    """
    Busca endereço pelo CEP usando a API ViaCEP
    
    Args:
        cep: CEP com 8 dígitos
    
    Returns:
        Dicionário com dados do endereço ou None se não encontrado
    """
    valido, resultado = validar_cep(cep)

    if not valido:
        return None

    data = resultado
    return {
        'logradouro': data.get('logradouro', ''),
        'bairro': data.get('bairro', ''),
        'cidade': data.get('localidade', ''),
        'estado': data.get('uf', ''),
        'complemento': data.get('complemento', '')
    }


def adicionar_membro(
    nome: str,
    data_nascimento: str,
    email: str = None,
    telefone: str = None,
    cep: str = None,
    numero: str = None,
    complemento: str = None,
    logradouro: str = None,
    bairro: str = None,
    cidade: str = None,
    estado: str = None
) -> bool:
    """
    Adiciona um novo membro ao banco de dados
    
    Args:
        nome: Nome completo do membro
        data_nascimento: Data de nascimento (YYYY-MM-DD)
        email: Endereço de e-mail (opcional)
        telefone: Número de telefone (opcional)
        cep: CEP (opcional)
        numero: Número do endereço (opcional)
        complemento: Complemento (opcional)
        logradouro: Logradouro (opcional)
        bairro: Bairro (opcional)
        cidade: Cidade (opcional)
        estado: Estado/UF (opcional)
    
    Returns:
        True se adicionado com sucesso, False caso contrário
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO membros 
                (nome, data_nascimento, email, telefone, cep, numero, complemento, 
                 logradouro, bairro, cidade, estado) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nome.strip(),
                data_nascimento,
                email.strip() if email else None,
                telefone.strip() if telefone else None,
                cep.replace('-', '') if cep else None,
                numero.strip() if numero else None,
                complemento.strip() if complemento else None,
                logradouro.strip() if logradouro else None,
                bairro.strip() if bairro else None,
                cidade.strip() if cidade else None,
                estado.strip() if estado else None
            ))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao adicionar membro: {e}")
        return False


def obter_membros() -> List[Tuple]:
    """
    Obtém todos os membros do banco de dados
    
    Returns:
        Lista de tuplas com os dados dos membros
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, data_nascimento, email, telefone, 
                   cep, numero, complemento, logradouro, bairro, cidade, estado,
                   created_at, updated_at
            FROM membros 
            ORDER BY nome ASC
        ''')
        return cursor.fetchall()


def obter_membro_por_id(id_membro: int) -> Optional[Tuple]:
    """
    Obtém um membro específico pelo ID
    
    Args:
        id_membro: ID do membro
    
    Returns:
        Tupla com os dados do membro ou None se não encontrado
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, data_nascimento, email, telefone, 
                   cep, numero, complemento, logradouro, bairro, cidade, estado,
                   created_at, updated_at
            FROM membros 
            WHERE id = ?
        ''', (id_membro,))
        return cursor.fetchone()


def obter_membros_por_nome(termo: str) -> List[Tuple]:
    """
    Busca membros pelo nome (busca parcial)
    
    Args:
        termo: Termo de busca
    
    Returns:
        Lista de tuplas com os dados dos membros encontrados
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, data_nascimento, email, telefone, 
                   cep, numero, complemento, logradouro, bairro, cidade, estado,
                   created_at, updated_at
            FROM membros 
            WHERE nome LIKE ?
            ORDER BY nome ASC
        ''', (f"%{termo}%",))
        return cursor.fetchall()


def atualizar_membro(
    id_membro: int,
    nome: str,
    data_nascimento: str,
    email: str = None,
    telefone: str = None,
    cep: str = None,
    numero: str = None,
    complemento: str = None,
    logradouro: str = None,
    bairro: str = None,
    cidade: str = None,
    estado: str = None
) -> bool:
    """
    Atualiza um membro existente
    
    Args:
        id_membro: ID do membro a ser atualizado
        nome: Nome completo do membro
        data_nascimento: Data de nascimento (YYYY-MM-DD)
        email: Endereço de e-mail (opcional)
        telefone: Número de telefone (opcional)
        cep: CEP (opcional)
        numero: Número do endereço (opcional)
        complemento: Complemento (opcional)
        logradouro: Logradouro (opcional)
        bairro: Bairro (opcional)
        cidade: Cidade (opcional)
        estado: Estado/UF (opcional)
    
    Returns:
        True se atualizado com sucesso, False caso contrário
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE membros 
                SET nome = ?, data_nascimento = ?, email = ?, telefone = ?,
                    cep = ?, numero = ?, complemento = ?, logradouro = ?,
                    bairro = ?, cidade = ?, estado = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                nome.strip(),
                data_nascimento,
                email.strip() if email else None,
                telefone.strip() if telefone else None,
                cep.replace('-', '') if cep else None,
                numero.strip() if numero else None,
                complemento.strip() if complemento else None,
                logradouro.strip() if logradouro else None,
                bairro.strip() if bairro else None,
                cidade.strip() if cidade else None,
                estado.strip() if estado else None,
                id_membro
            ))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao atualizar membro: {e}")
        return False


def excluir_membro(id_membro: int) -> bool:
    """
    Exclui um membro do banco de dados
    
    Args:
        id_membro: ID do membro a ser excluído
    
    Returns:
        True se excluído com sucesso, False caso contrário
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM membros WHERE id = ?', (id_membro,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao excluir membro: {e}")
        return False
