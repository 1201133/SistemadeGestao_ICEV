# 🚀 GUIA DE DEPLOY - STREAMLIT CLOUD

Este arquivo cobre apenas o deploy. Para configuração de segurança e geração de hashes, use [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md).

## 📋 Pré-requisitos

✅ Repositório GitHub público ou privado  
✅ Arquivo `.env` com suas credenciais locais  
✅ Banco de dados vazio no repositório (dados sensíveis protegidos)  
✅ Testes automatizados executados localmente  

---

## 🌐 PASSO 1: Preparar o Repositório

### ✅ Verificar Arquivos Protegidos

```bash
# Verificar o que está sendo ignorado
git status

# ❌ NÃO deve aparecer:
# - .env
# - .streamlit/secrets.toml
# - dizimos_ofertas_BACKUP.db
# - __pycache__/
```

### ✅ Arquivos que DEVEM Estar no Repositório

```
✅ app.py
✅ auth.py
✅ config.py (com suporte a st.secrets)
✅ database.py
✅ mobile_config.py
✅ utils.py
✅ notifications.py
✅ requirements.txt
✅ dizimos_ofertas.db (vazio)
✅ modules/ (todos os .py)
✅ README.md
✅ .gitignore
```

---

## ☁️ PASSO 2: Deploy no Streamlit Cloud

### 1. Acessar Streamlit Cloud

🌐 **URL:** https://share.streamlit.io/

### 2. Fazer Login

- Clique em **Sign in**
- Use sua conta GitHub
- Autorize o acesso ao Streamlit

### 3. Criar Novo App

- Clique em **New app**
- Selecione:
  - **Repository:** `ROBSONAUGUSTODIAS/DizimosOfertas`
  - **Branch:** `main`
  - **Main file path:** `app.py`
- Clique em **Deploy!**

---

## 🔐 PASSO 3: Configurar Secrets (CRÍTICO!)

### ⚠️ ATENÇÃO: Sem esta configuração, o app NÃO funcionará!

1. **No painel do Streamlit Cloud:**
   - Vá em **Settings** (engrenagem) → **Secrets**

2. **Cole o conteúdo do arquivo `.env`** no formato TOML:

```toml
# ========================================
# CONFIGURAÇÃO DE SECRETS - STREAMLIT CLOUD
# ========================================

[passwords]
USER_ADMIN_HASH = "$2b$12$SUA_HASH_ADMIN_AQUI"
USER_DIACONO01_HASH = "$2b$12$SUA_HASH_DIACONO01_AQUI"
USER_DIACONO02_HASH = "$2b$12$SUA_HASH_DIACONO02_AQUI"
USER_DIACONO03_HASH = "$2b$12$SUA_HASH_DIACONO03_AQUI"

[pix]
PIX_CHAVE = "sua_chave_pix_aqui"
PIX_BENEFICIARIO = "Nome da Igreja"
```

Também é aceito configurar esses mesmos hashes como chaves no topo (sem seção), mas o formato com `[passwords]` é o recomendado para organização.

### 📝 Como Obter os Hashes?

**Opção 1: Do arquivo `.env` local:**
```bash
cat .env
```

**Opção 2: Gerar novos hashes:** use o procedimento descrito em [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md)

3. **Clique em Save**

---

## ✅ PASSO 4: Configurações Adicionais (Opcional)

### Configurações Avançadas

No painel **Settings** → **Advanced settings**:

```
Python version: 3.11
```

### Configurar Domínio Customizado (Opcional)

1. Settings → **General**
2. Em **App URL**, você pode customizar:
   - `dizimos-ofertas.streamlit.app` (exemplo)

---

## 🧪 PASSO 5: Testar o Deploy

Antes do push para deploy, execute localmente:

```bash
python3 -m unittest tests.test_authorization_scope tests.test_auth_session -v
```

### 1. Aguardar Deploy

- O Streamlit Cloud vai instalar as dependências
- Tempo estimado: 2-5 minutos
- Você verá os logs em tempo real

### 2. Testar Login

Acesse a URL do app e tente fazer login com um usuário configurado nos Secrets.

### 3. Testar Funcionalidades

✅ **Visualizar:** Métricas e tabelas  
✅ **Registrar:** Novo lançamento  
✅ **Editar:** Admin com escopo global; não-admin apenas nos próprios registros  
✅ **Mobile:** Testar no celular  

---

## 🔧 PASSO 6: Gerenciar Banco de Dados

### ⚠️ Banco de Dados SQLite no Streamlit Cloud

**IMPORTANTE:** O Streamlit Cloud usa sistema de arquivos **efêmero**!

- ❌ Dados são **perdidos** quando o app reinicia
- ❌ Cada sessão tem seu próprio banco
- ❌ Não é adequado para produção com dados reais

### 🎯 Soluções para Persistência de Dados:

#### Opção 1: PostgreSQL (Recomendado)
```bash
# Usar banco PostgreSQL remoto (Supabase, Render, etc)
pip install psycopg2-binary
```

#### Opção 2: Google Sheets
```bash
# Usar Google Sheets como banco de dados
pip install gspread oauth2client
```

#### Opção 3: Firebase/Firestore
```bash
# Usar Firebase Firestore
pip install firebase-admin
```

#### Opção 4: Turso/LibSQL (SQLite na nuvem)
```bash
# SQLite compatível hospedado
pip install libsql-client
```

### 📝 Para Testes/Demo (SQLite Atual)

- ✅ Funciona para demonstração
- ✅ Bom para protótipos
- ❌ Dados não persistem entre deploys

---

## 🛠️ TROUBLESHOOTING

### Erro: "Missing Secrets"

**Problema:** Secrets não configurados

**Solução:**
1. Settings → Secrets
2. Cole o conteúdo do `.env` no formato TOML
3. Save e aguarde restart

### Erro: "ModuleNotFoundError"

**Problema:** Dependência faltando

**Solução:**
1. Verificar `requirements.txt` tem todas as dependências
2. Fazer commit e push
3. App reinicia automaticamente

### Erro: Login Não Funciona

**Problema:** Hash de senha incorreto

**Solução:**
1. Gere um novo hash seguindo [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md)
2. Atualizar em Settings → Secrets
3. Testar novamente

### App Fica Reiniciando

**Problema:** Erro no código ou secrets

**Solução:**
1. Ver logs em **Manage app** → **Logs**
2. Corrigir erro
3. Fazer commit e push

---

## Checklist Final

Antes de considerar o deploy concluído, confirme:

- [ ] `.env` permanece fora do repositório
- [ ] Secrets foram salvos no Streamlit Cloud
- [ ] login foi testado no app publicado
- [ ] bancos locais não contêm dados reais versionados
- [ ] notificações SMTP foram revisadas antes de ativar

## Pós-Deploy

- atualizações de código: `git add`, `git commit`, `git push`
- atualização de secrets: `Settings → Secrets` e salvar
- monitoramento básico: `Manage app → Logs`

Para troubleshooting detalhado de login, use [TROUBLESHOOTING_LOGIN.md](TROUBLESHOOTING_LOGIN.md). Para segurança, use [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md).
