"""
Módulo de validações de contato
"""
import re


def validar_email(email: str) -> bool:
    """
    Valida se o formato do email é válido
    
    Args:
        email: Endereço de email a ser validado
    
    Returns:
        True se válido, False caso contrário
    """
    if not email:
        return False

    email = email.strip()
    if len(email) > 254:
        return False

    # Validação simples e segura para formato comum de email
    padrao = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return re.match(padrao, email) is not None


def validar_celular(codigo_area: str, celular: str) -> bool:
    """
    Valida se o código de área e celular são válidos
    
    Args:
        codigo_area: Código de área (DDD)
        celular: Número do celular
    
    Returns:
        True se válido, False caso contrário
    """
    if not codigo_area or not celular:
        return False
    
    # Remover caracteres não numéricos
    codigo_area = ''.join(filter(str.isdigit, codigo_area))
    celular = ''.join(filter(str.isdigit, celular))
    
    # Validar comprimento
    if len(codigo_area) != 2:
        return False
    
    if len(celular) not in [8, 9]:  # Aceita celular com 8 ou 9 dígitos
        return False
    
    return True


