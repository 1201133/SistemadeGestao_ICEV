# 🚀 Como Executar a Aplicação

Guia passo a passo para executar o Sistema de Gestão de Dízimos e Ofertas.

---

## 📋 Pré-requisitos

Antes de executar, certifique-se de ter instalado:

- ✅ **Python 3.8 ou superior**
  - Verificar versão: `python --version`
  - Download: https://www.python.org/downloads/

- ✅ **pip** (gerenciador de pacotes Python)
  - Geralmente vem com Python
  - Verificar: `pip --version`

---

## ⚡ Início Rápido (3 passos)

### 1️⃣ Instalar Dependências

Abra o terminal/PowerShell na pasta do projeto e execute:

```bash
pip install -r requirements.txt
```

**O que será instalado:**
- `streamlit` - Framework web
- `pandas` - Manipulação de dados
- `streamlit-option-menu` - Menu lateral
- `Pillow` - Processamento de imagens

### 2️⃣ Executar o Sistema

```bash
D:/PROTOTIPO/DizimosOfertas/.venv/Scripts/Activate.ps1
streamlit run app.py
```

### 3️⃣ Acessar no Navegador

O navegador abrirá automaticamente em:
```
http://localhost:8501
```

Se não abrir automaticamente, copie e cole o link no navegador.

---

## 🔐 Login no Sistema

Use um usuário previamente configurado no ambiente:

| Usuário | Senha | Nível de Acesso |
|---------|-------|-----------------|
| `admin` | Configurada no `.env` ou `secrets.toml` | Administrador com escopo global |
| `diacono01` | Configurada no `.env` ou `secrets.toml` | Diácono com módulos liberados pelo admin |
| `diacono02` | Configurada no `.env` ou `secrets.toml` | Diácono com módulos liberados pelo admin |
| `diacono03` | Configurada no `.env` ou `secrets.toml` | Diácono com módulos liberados pelo admin |

**Recomendação de Segurança:** Defina hashes fortes no `.env` ou no `secrets.toml` antes do uso em produção e nunca publique credenciais em texto plano.

---

## 💻 Comandos Detalhados

### Windows (PowerShell/CMD):

```powershell
# Navegar até a pasta do projeto
cd D:\PROTOTIPO\DizimosOfertas

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py

# OU com porta específica
streamlit run app.py --server.port=8000

# OU usando módulo python
python -m streamlit run app.py
```

### Linux/Mac (Terminal):

```bash
# Navegar até a pasta do projeto
cd /caminho/para/DizimosOfertas

# Ativar ambiente virtual, se estiver usando um
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py

# OU com porta específica
streamlit run app.py --server.port=8000
```

### Usando Ambiente Virtual (Recomendado):

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
## Windows:
venv\Scripts\activate

## Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run app.py
```

---

## 🎯 Usando o Sistema

### 1. Visualizar Lançamentos

- Faça login
- Menu lateral → **"Visualizar"**
- Veja todos os lançamentos registrados
- Resumo financeiro com gráficos

### 2. Registrar Nova Contribuição

- Menu lateral → **"Registrar"** para usuários com esse módulo liberado
- Preencha os dados:
  - Nome do contribuinte
  - Valor da contribuição
  - Tipo de pagamento
  - Categoria (Dízimo/Oferta/Visitante)
  - Celular (opcional)
  - Email (opcional)
- Clique em **"Registrar Lançamento"**

### 3. Editar/Excluir Lançamentos

- Menu lateral → **"Editar"** para usuários com esse módulo liberado
- Selecione o lançamento
- Clique em **"Atualizar"** ou **"Excluir"**

Observação: o usuário `admin` pode editar ou excluir qualquer lançamento. Usuários não-admin editam e excluem apenas registros criados por eles.

---

## 🛠️ Solução de Problemas

### ❌ "streamlit: comando não encontrado"

**Problema:** Streamlit não está instalado ou não está no PATH.

**Solução:**
```bash
# Instalar streamlit
pip install streamlit

# OU usar módulo python
python -m streamlit run app.py
```

---

### ❌ "ModuleNotFoundError: No module named 'streamlit'"

**Problema:** Dependências não instaladas.

**Solução:**
```bash
pip install -r requirements.txt
```

---

### ❌ "Port 8501 is already in use"

**Problema:** Porta já está sendo usada.

**Solução 1 - Usar outra porta:**
```bash
streamlit run app.py --server.port=8502
```

**Solução 2 - Fechar processo na porta:**
```powershell
# Windows
netstat -ano | findstr :8501
taskkill /PID <numero_do_pid> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

---

### ❌ Banco de dados corrompido

**Problema:** Erros ao acessar/salvar dados.

**Solução - Recriar banco:**
```bash
# ATENÇÃO: Isso apaga todos os dados!

# Windows (PowerShell)
Remove-Item -Force dizimos_ofertas.db

# Linux/Mac
rm dizimos_ofertas.db

# Reiniciar aplicação
streamlit run app.py
```

O banco será recriado automaticamente vazio.

---

### ❌ Logo não aparece

**Problema:** Arquivo de imagem não encontrado.

**Solução:**
1. Verifique se existe: `imagem/igrejadechomai.jpg`
2. Se não existir, o sistema mostra texto "MINISTÉRIO DECHONAI"
3. Adicione sua logo neste caminho

---

## ⚙️ Configurações Avançadas

### Alterar Porta do Servidor

```bash
streamlit run app.py --server.port=8000
```

### Permitir Acesso Externo (Rede Local)

```bash
streamlit run app.py --server.address=0.0.0.0
```

Acesse de outro dispositivo na mesma rede:
```
http://IP_DO_SERVIDOR:8501
```

Para descobrir seu IP:
```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

### Executar em Background (Servidor)

**Linux/Mac:**
```bash
nohup streamlit run app.py &
```

**Windows (usando PowerShell):**
```powershell
Start-Process -NoNewWindow streamlit run app.py
```

---

## 📊 Estrutura do Banco de Dados

O sistema cria automaticamente o arquivo `dizimos_ofertas.db` (SQLite) com a seguinte estrutura:

```sql
CREATE TABLE lancamentos (
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
);
```

**Localização:** Raiz do projeto (`DizimosOfertas/dizimos_ofertas.db`)

---

## 🔄 Atualizar o Sistema

### Atualizar Dependências:

```bash
pip install --upgrade -r requirements.txt
```

### Atualizar apenas Streamlit:

```bash
pip install --upgrade streamlit
```

### Verificar Versões Instaladas:

```bash
pip list
```

---

## 📦 Deploy em Produção

### Opção 1: Streamlit Cloud (Gratuito)

1. Faça upload do projeto no GitHub
2. Acesse: https://streamlit.io/cloud
3. Conecte seu repositório
4. Deploy automático!

**Vantagens:**
- ✅ Gratuito
- ✅ HTTPS automático
- ✅ Sempre online
- ✅ Fácil atualização

### Opção 2: Servidor Próprio

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar com nohup (Linux)
nohup streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &

# Configurar proxy reverso (Nginx)
# Habilitar HTTPS com Let's Encrypt
```

### Opção 3: Docker

Crie `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Execute:
```bash
docker build -t dizimos-ofertas .
docker run -p 8501:8501 dizimos-ofertas
```

---

## 📝 Checklist de Primeira Execução

- [ ] Python 3.8+ instalado
- [ ] Navegou até a pasta do projeto
- [ ] Executou `pip install -r requirements.txt`
- [ ] Executou `streamlit run app.py`
- [ ] Acessou http://localhost:8501
- [ ] Fez login com um usuário configurado no ambiente
- [ ] Testou registrar uma contribuição

---

## 🆘 Precisa de Ajuda?

### Documentação do Projeto:
- **README.md** - Visão geral do sistema
- **GUIA_SEGURANCA.md** - Configuração de segurança e credenciais

### Documentação Streamlit:
- https://docs.streamlit.io

### Logs do Sistema:
Os logs aparecem no terminal onde você executou o comando.

---

## ✅ Pronto!

Seu sistema está rodando em: **http://localhost:8501**

**Próximos Passos:**
1. ✅ Faça login
2. ✅ Registre uma contribuição de teste
3. ✅ Altere senhas padrão para mais segurança
4. ✅ Adicione o logo da sua igreja em `imagem/`

---

**Desenvolvido para o Ministério Dechonai**  
*Sistema de Gestão de Dízimos e Ofertas*
