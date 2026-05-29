"""
Módulo de Autenticação e Autorização.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
import bcrypt
from config import USUARIOS_HASHES, NIVEIS_ACESSO, NOMES_USUARIOS


LIMITE_TENTATIVAS_LOGIN = 5
MINUTOS_BLOQUEIO_LOGIN = 15
MINUTOS_EXPIRACAO_SESSAO = 30


def verificar_senha_hash(senha: str, hash_armazenado: str) -> bool:
    """
    Verifica se a senha corresponde ao hash armazenado
    
    Args:
        senha: Senha em texto plano fornecida pelo usuário
        hash_armazenado: Hash bcrypt armazenado no sistema
    
    Returns:
        True se a senha está correta, False caso contrário
    """
    try:
        if not hash_armazenado:
            return False
            
        # Converte senha e hash para bytes
        senha_bytes = senha.encode('utf-8')
        hash_bytes = hash_armazenado.encode('utf-8')
        
        # Verifica se a senha corresponde ao hash
        return bcrypt.checkpw(senha_bytes, hash_bytes)
    except Exception as e:
        print(f"Erro ao verificar senha: {e}")
        return False


def verificar_login(usuario: str, senha: str) -> Optional[Dict[str, str]]:
    """
    Verifica as credenciais do usuário usando hash bcrypt
    
    Args:
        usuario: Nome de usuário
        senha: Senha do usuário em texto plano
    
    Returns:
        Dict com informações do usuário se válido, None caso contrário
    """
    # Verifica se o usuário existe
    if usuario not in USUARIOS_HASHES:
        return None
    
    # Obtém o hash armazenado
    hash_armazenado = USUARIOS_HASHES[usuario]
    
    # Verifica se o hash existe (pode estar None se não configurado)
    if not hash_armazenado:
        print(f"⚠️ Hash não configurado para o usuário: {usuario}")
        return None
    
    # Verifica a senha
    if verificar_senha_hash(senha, hash_armazenado):
        return {
            "usuario": usuario,
            "nome": NOMES_USUARIOS.get(usuario, usuario),
            "nivel": NIVEIS_ACESSO.get(usuario, "diacono")
        }
    
    return None


def login_esta_bloqueado(bloqueado_ate: Optional[datetime], agora: Optional[datetime] = None) -> bool:
    """Retorna True quando o login ainda está dentro da janela de bloqueio."""
    if not bloqueado_ate:
        return False
    agora = agora or datetime.now()
    return agora < bloqueado_ate


def minutos_restantes_bloqueio(bloqueado_ate: Optional[datetime], agora: Optional[datetime] = None) -> int:
    """Retorna os minutos restantes de bloqueio, arredondando para cima."""
    if not bloqueado_ate:
        return 0
    agora = agora or datetime.now()
    if agora >= bloqueado_ate:
        return 0
    return int((bloqueado_ate - agora).total_seconds() // 60) + 1


def registrar_falha_login(tentativas_atuais: int, agora: Optional[datetime] = None) -> Dict[str, Optional[datetime]]:
    """Atualiza o estado de tentativas após uma falha de autenticação."""
    agora = agora or datetime.now()
    tentativas = tentativas_atuais + 1
    bloqueado_ate = None
    if tentativas >= LIMITE_TENTATIVAS_LOGIN:
        bloqueado_ate = agora + timedelta(minutes=MINUTOS_BLOQUEIO_LOGIN)
    return {
        "tentativas": tentativas,
        "bloqueado_ate": bloqueado_ate,
    }


def sessao_expirada(ultima_atividade: Optional[str], agora: Optional[datetime] = None) -> bool:
    """Retorna True se a sessao deve expirar por inatividade."""
    if not ultima_atividade:
        return False
    agora = agora or datetime.now()
    try:
        ultimo_acesso = datetime.fromisoformat(ultima_atividade)
    except ValueError:
        return False
    return (agora - ultimo_acesso) > timedelta(minutes=MINUTOS_EXPIRACAO_SESSAO)
