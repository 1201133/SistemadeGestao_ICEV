# 🔐 Guia de Segurança - Login e Senha

## ⚠️ IMPORTANTE - Leia Antes de Publicar

Este documento explica como o sistema de autenticação seguro funciona e como configurá-lo corretamente antes de publicar no Streamlit Cloud.

Este é o guia principal de segurança do projeto. Os demais documentos de suporte devem apontar para este arquivo para evitar instruções divergentes.

## 🎯 O Que Foi Implementado

### 1. **Hash de Senhas com Bcrypt**
- ✅ Senhas nunca são armazenadas em texto plano
- ✅ Utiliza algoritmo bcrypt com salt automático
- ✅ Proteção contra força bruta e rainbow tables
- ✅ Impossível recuperar a senha original a partir do hash

### 2. **Variáveis de Ambiente**
- ✅ Credenciais armazenadas em arquivo `.env`
- ✅ Arquivo `.env` no `.gitignore` (não vai para o GitHub)
- ✅ Código-fonte não contém senhas
- ✅ Compatível com Streamlit Cloud Secrets

### 3. **Arquivos de Configuração**
- `.env` - Arquivo com credenciais reais (NÃO compartilhar)
- `.env.example` - Modelo sem dados sensíveis (pode compartilhar)
- `.gitignore` - Protege `.env` de ser enviado ao GitHub

## 🚀 Como Usar Localmente

### Passo 1: Instalar Dependências
```bash
pip install -r requirements.txt
```

### Passo 2: Configurar Senhas (Primeira Vez)

O arquivo `.env` deve conter hashes bcrypt próprios para cada usuário.

**Para criar um hash manualmente:**

1. Abra um terminal Python:
```bash
python
```

2. Gere um hash bcrypt:
```python
import bcrypt
bcrypt.hashpw("MinhaSenhaForte@123".encode(), bcrypt.gensalt()).decode()
```

3. Copie o resultado e adicione ao `.env`:
```env
USER_ADMIN_HASH=$2b$12$abc123...xyz789
```

4. Repita o processo para cada usuário necessário

### Passo 3: Executar a Aplicação
```bash
streamlit run app.py
```

## 🌐 Como Publicar no Streamlit Cloud

### ⚠️ ATENÇÃO: NÃO Envie o Arquivo .env para o GitHub!

O arquivo `.gitignore` já está configurado para proteger o `.env`, mas verifique:

```bash
# Ver o que será enviado ao git
git status

# O .env NÃO deve aparecer na lista!
# Se aparecer, adicione ao .gitignore
```

### Configurar Secrets no Streamlit Cloud

1. **Faça Push do Código para o GitHub** (sem o .env)
```bash
git add .
git commit -m "Sistema com autenticação segura"
git push origin main
```

2. **No Streamlit Cloud:**
   - Acesse: https://share.streamlit.io
   - Selecione seu app
   - Clique em **⚙️ Settings**
   - Vá em **Secrets**
   - Cole o conteúdo do seu arquivo `.env`:

```toml
USER_ADMIN_HASH = "$2b$12$seu_hash_completo_aqui"
USER_DIACONO01_HASH = "$2b$12$seu_hash_completo_aqui"
USER_DIACONO02_HASH = "$2b$12$seu_hash_completo_aqui"

WHATSAPP_ENABLED = "false"
```

3. **Salve e Reinicie o App**

## 🔒 Boas Práticas de Segurança

### ✅ Senhas Fortes

**O que é uma senha forte?**
- Mínimo 12 caracteres
- Letras maiúsculas: A-Z
- Letras minúsculas: a-z
- Números: 0-9
- Símbolos: !@#$%^&*

**Exemplos de senhas fortes:**
- `Igreja@Segura#2026!`
- `Diacono$Forte123@`
- `Admin&Protegido2026#`

**❌ Evite:**
- Senhas curtas (menos de 8 caracteres)
- Palavras do dicionário
- Informações pessoais (nome, data de nascimento)
- Sequências óbvias (123456, abcdef)
- Senha igual para todos os usuários

### 🛡️ Gerenciamento de Usuários

**Localização:** [config.py](config.py)

```python
# Adicionar novo usuário
USUARIOS_HASHES = {
    "admin": os.getenv('USER_ADMIN_HASH'),
    "diacono01": os.getenv('USER_DIACONO01_HASH'),
    "diacono02": os.getenv('USER_DIACONO02_HASH'),
    "diacono03": os.getenv('USER_DIACONO03_HASH'),
    "novousuario": os.getenv('USER_NOVOUSUARIO_HASH'),  # ← Adicione aqui
}

NIVEIS_ACESSO = {
    "admin": "admin",
    "diacono01": "diacono",
    "diacono02": "diacono",
    "diacono03": "diacono",
    "novousuario": "diacono",  # ← Defina nivel conforme o perfil adotado no sistema
}

NOMES_USUARIOS = {
    "admin": "Administrador",
    "diacono01": "Diácono01",
    "diacono02": "Diácono02",
    "diacono03": "Diácono03",
    "novousuario": "Nome Completo",  # ← Adicione nome
}
```

**Passos para adicionar usuário:**

1. Edite `config.py` conforme acima
2. Gere o hash da senha com bcrypt em um terminal Python
3. Adicione ao `.env`:
```env
USER_NOVOUSUARIO_HASH=$2b$12$hash_gerado
```
4. Reinicie a aplicação

### 📋 Níveis de Acesso

| Nível | Permissões |
|-------|-----------|
| **admin** | Acesso global ao sistema, gerenciamento de permissoes e administracao de todos os registros |
| **diacono** | Acesso apenas aos modulos liberados pelo admin; nos modulos sensiveis, atua apenas sobre os itens criados por ele |

Observacao: neste projeto, o acesso fino por funcionalidade e controlado pelo modulo [permissions.py](permissions.py), e nao por niveis intermediarios como `editor` ou `visualizador`.

## 🔍 Verificação de Segurança

### Checklist antes de publicar:

- [ ] Arquivo `.env` no `.gitignore`
- [ ] `.env` NÃO enviado para o GitHub
- [ ] Senhas fortes configuradas
- [ ] Hashes únicos para cada usuário
- [ ] Secrets configurados no Streamlit Cloud
- [ ] Testado localmente antes de publicar
- [ ] `python3 -m unittest tests.test_authorization_scope tests.test_auth_session -v` executado com sucesso

### Comandos de verificação:

```bash
# Verificar se .env está ignorado
git check-ignore .env
# Deve retornar: .env

# Ver arquivos que serão enviados
git status
# .env NÃO deve aparecer!

# Testar login local
streamlit run app.py
# Tente fazer login com as credenciais configuradas
```

## 🆘 Solução de Problemas

### ❌ "Hash não configurado para o usuário"

**Causa:** Falta o hash no arquivo `.env`

**Solução:**
1. Verifique se o arquivo `.env` existe
2. Confirme se a variável está definida:
```env
USER_ADMIN_HASH=$2b$12$...
```
3. Reinicie o Streamlit

### ❌ "Credenciais inválidas"

**Causas possíveis:**
1. Senha digitada incorretamente
2. Hash não corresponde à senha
3. Arquivo `.env` não carregado

**Solução:**
1. Confirme a senha correta
2. Gere novo hash com bcrypt em um terminal Python
3. Atualize o `.env`
4. Reinicie o Streamlit

### ❌ "ModuleNotFoundError: No module named 'bcrypt'"

**Causa:** Biblioteca não instalada

**Solução:**
```bash
pip install -r requirements.txt
```

### ❌ No Streamlit Cloud: Login não funciona

**Causa:** Secrets não configurados

**Solução:**
1. Acesse Settings → Secrets no Streamlit Cloud
2. Cole o conteúdo do `.env`
3. Salve e reinicie o app

## 📚 Arquivos Importantes

| Arquivo | Descrição | Compartilhar? |
|---------|-----------|---------------|
| `.env` | Credenciais reais | ❌ NUNCA |
| `.env.example` | Modelo sem dados sensíveis | ✅ SIM |
| `.gitignore` | Proteção de arquivos | ✅ SIM |
| `config.py` | Configuração do sistema | ✅ SIM |
| `auth.py` | Lógica de autenticação | ✅ SIM |
| `GUIA_SEGURANCA.md` | Guia principal de segurança | ✅ SIM |

## 📖 Documentação Adicional

- [README.md](README.md) - Documentação completa do sistema
- [DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md) - Passo a passo de deploy
- [TROUBLESHOOTING_LOGIN.md](TROUBLESHOOTING_LOGIN.md) - Diagnóstico de login
- [bcrypt documentation](https://github.com/pyca/bcrypt/) - Biblioteca bcrypt
- [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management) - Gerenciamento de secrets

## 📞 Suporte

Se tiver dúvidas ou problemas:

1. Consulte [README.md](README.md) para visão geral do projeto
2. Verifique os erros no terminal/logs
3. Execute os comandos de verificação acima
4. Revise o checklist de segurança

---

**🔐 Lembre-se: A segurança da aplicação depende de senhas fortes e proteção adequada das credenciais!**
