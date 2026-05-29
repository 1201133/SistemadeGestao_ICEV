# Sistema de GestÃ£o de DÃ­zimos e Ofertas

Sistema web desenvolvido em Python com Streamlit para gerenciamento de dÃ­zimos, ofertas e contribuiÃ§Ãµes de uma igreja.

## DocumentaÃ§Ã£o

- **[ðŸ” GUIA DE SEGURANÃ‡A](GUIA_SEGURANCA.md)** - Guia completo de configuraÃ§Ã£o e uso do sistema seguro
- **[ðŸš€ DEPLOY STREAMLIT](DEPLOY_STREAMLIT.md)** - Passo a passo de deploy e configuraÃ§Ã£o de secrets
- **[ðŸ› ï¸ TROUBLESHOOTING LOGIN](TROUBLESHOOTING_LOGIN.md)** - DiagnÃ³stico de autenticaÃ§Ã£o e login

## Funcionalidades

### GestÃ£o de LanÃ§amentos
- **AutenticaÃ§Ã£o de UsuÃ¡rios**: Sistema de login com diferentes nÃ­veis de acesso
- **Registro de LanÃ§amentos**: Cadastro completo de dÃ­zimos, ofertas e contribuiÃ§Ãµes
- **Cadastro de Contatos**: Telefone/celular e Email opcionais
- **VisualizaÃ§Ã£o**: Consulta de lanÃ§amentos com histÃ³rico completo ou Ãºltimos 30 dias
- **EdiÃ§Ã£o e ExclusÃ£o**: Admin gerencia todos os registros; demais usuÃ¡rios autorizados gerenciam apenas os prÃ³prios
- **RelatÃ³rios**: Totais por dia, mÃªs e categoria
- **GrÃ¡ficos**: VisualizaÃ§Ã£o de distribuiÃ§Ã£o de entradas

## SeguranÃ§a e AutenticaÃ§Ã£o

O projeto usa autenticaÃ§Ã£o com hashes bcrypt e configuraÃ§Ã£o por `.env` ou `Settings â†’ Secrets` no Streamlit Cloud. O fluxo detalhado de criaÃ§Ã£o de hashes, configuraÃ§Ã£o de usuÃ¡rios e publicaÃ§Ã£o segura foi centralizado nos documentos abaixo:

- [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md) para configuraÃ§Ã£o completa de seguranÃ§a
- [DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md) para deploy e configuraÃ§Ã£o de secrets
- [TROUBLESHOOTING_LOGIN.md](TROUBLESHOOTING_LOGIN.md) para diagnÃ³stico de login

Resumo rÃ¡pido:

- senhas nÃ£o ficam no cÃ³digo-fonte
- `.env` deve permanecer fora do Git
- cada usuÃ¡rio precisa ter seu prÃ³prio hash bcrypt
- o Streamlit Cloud deve receber os hashes em `Settings â†’ Secrets`

## âœ… Testes Automatizados

O projeto possui uma suÃ­te inicial com `unittest` para proteger a regra de escopo por usuÃ¡rio nos mÃ³dulos sensÃ­veis.

Execute com:

```bash
python3 -m unittest tests.test_authorization_scope tests.test_auth_session -v
```

Cobertura atual:

- lanÃ§amentos: admin vÃª tudo; nÃ£o-admin atua apenas nos prÃ³prios registros
- newsletter: admin gerencia todos; nÃ£o-admin gerencia apenas comunicados prÃ³prios
- calendÃ¡rio: admin gerencia todos; nÃ£o-admin gerencia apenas eventos prÃ³prios
- autenticaÃ§Ã£o: validaÃ§Ã£o de hash, login vÃ¡lido e falhas por usuÃ¡rio inexistente ou sem hash
- sessÃ£o: bloqueio apÃ³s tentativas invÃ¡lidas e expiraÃ§Ã£o por inatividade

RecomendaÃ§Ã£o: rode essa suÃ­te antes de publicar alteraÃ§Ãµes relacionadas a permissÃµes, CRUD ou autenticaÃ§Ã£o.

## ðŸ“± Responsividade Mobile

### Sistema Otimizado para Celular e Tablet

A aplicaÃ§Ã£o foi **totalmente otimizada** para proporcionar uma excelente experiÃªncia em dispositivos mÃ³veis:

#### âœ… Recursos Mobile
- **Layout Responsivo**: Colunas que empilham verticalmente em telas pequenas
- **BotÃµes Touch-Friendly**: Tamanho mÃ­nimo de 44px para fÃ¡cil toque
- **Inputs Otimizados**: Font-size 16px+ previne zoom automÃ¡tico (iOS/Android)
- **Tabelas com Scroll**: Scroll horizontal suave para visualizar todas as colunas
- **Sidebar ColapsÃ¡vel**: Fechada por padrÃ£o em mobile para mÃ¡ximo espaÃ§o
- **CSS Customizado**: Mais de 200 linhas de CSS otimizado para mobile
- **MÃ©tricas Empilhadas**: Cards financeiros empilham verticalmente
- **FormulÃ¡rios Adaptivos**: Campos se reorganizam para telas pequenas

#### ðŸ“Š Breakpoint Mobile
```css
@media (max-width: 768px) {
  /* Todas as otimizaÃ§Ãµes sÃ£o aplicadas */
}
```

#### ðŸ§ª Como Testar no Celular

**OpÃ§Ã£o 1: DevTools do Navegador (RÃ¡pido)**
1. Execute: `streamlit run app.py`
2. Abra F12 (DevTools)
3. Clique no Ã­cone de celular ðŸ“±
4. Selecione: iPhone, Samsung ou iPad
5. Teste a navegaÃ§Ã£o!

**OpÃ§Ã£o 2: Dispositivo Real**
1. Execute: `streamlit run app.py --server.address=0.0.0.0`
2. Descubra seu IP: `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)
3. No celular: `http://SEU_IP:8501`

**ðŸ“– ExecuÃ§Ã£o em rede local:** veja [COMO_EXECUTAR.md](COMO_EXECUTAR.md)

#### ðŸ“‹ Checklist Mobile Aprovado
- âœ… Login centralizado e responsivo
- âœ… MÃ©tricas financeiras empilhadas
- âœ… Tabelas com scroll horizontal
- âœ… FormulÃ¡rios otimizados para toque
- âœ… BotÃµes grandes (44px+)
- âœ… GrÃ¡ficos ocupam largura total
- âœ… Logo responsiva
- âœ… Sidebar colapsÃ¡vel
- âœ… Zero zoom automÃ¡tico em inputs

## ðŸ—ï¸ Arquitetura

O projeto segue uma arquitetura modular com separaÃ§Ã£o de responsabilidades:

```
DizimosOfertas/
â”œâ”€â”€ app.py                  # AplicaÃ§Ã£o principal
â”œâ”€â”€ config.py               # ConfiguraÃ§Ãµes e constantes
â”œâ”€â”€ database.py             # Gerenciamento do banco de dados
â”œâ”€â”€ auth.py                 # AutenticaÃ§Ã£o e autorizaÃ§Ã£o
â”œâ”€â”€ utils.py                # FunÃ§Ãµes utilitÃ¡rias
â”œâ”€â”€ modules/                # MÃ³dulos da aplicaÃ§Ã£o
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ visualizar.py       # MÃ³dulo de visualizaÃ§Ã£o
â”‚   â”œâ”€â”€ registrar.py        # MÃ³dulo de registro
â”‚   â””â”€â”€ editar.py           # MÃ³dulo de ediÃ§Ã£o
â”œâ”€â”€ imagem/                 # Recursos de imagem
â”œâ”€â”€ requirements.txt        # DependÃªncias
â”œâ”€â”€ .env.example            # Exemplo de configuraÃ§Ã£o (NOVO)
â””â”€â”€ README.md              # Este arquivo
```

## ðŸ“± IntegraÃ§Ã£o WhatsApp - Guia Completo

### âš ï¸ REGRA IMPORTANTE: WhatsApp apenas para PIX

**O sistema envia confirmaÃ§Ã£o via WhatsApp SOMENTE quando o tipo de pagamento for PIX.**

**Por quÃª?**
- ðŸ¦ **Rastreabilidade**: Pagamentos PIX sÃ£o instantÃ¢neos e confirmados automaticamente
- âš¡ **Agilidade**: PIX cai na hora, permitindo confirmaÃ§Ã£o imediata ao contribuinte
- âœ… **AutomaÃ§Ã£o**: Ideal para notificaÃ§Ãµes automÃ¡ticas em tempo real
- ðŸ“Š **Controle**: Facilita a gestÃ£o de contribuiÃ§Ãµes digitais

**Outros tipos de pagamento** (Dinheiro, CartÃ£o, TransferÃªncia, Cheque):
- âœ… SÃ£o registrados normalmente no sistema
- âŒ NÃƒO recebem confirmaÃ§Ã£o automÃ¡tica via WhatsApp
- â„¹ï¸ Mensagem informativa Ã© exibida ao contribuinte

### O que Ã© necessÃ¡rio?


### Passo a Passo para ConfiguraÃ§Ã£o


2. Clique em "Sign up" e preencha seus dados
3. Confirme seu email
4. VocÃª receberÃ¡ crÃ©ditos gratuitos para testes (cerca de $15 USD)

#### 2ï¸âƒ£ Configurar WhatsApp Sandbox

O WhatsApp Sandbox permite testar gratuitamente antes de configurar um nÃºmero oficial:

2. VocÃª verÃ¡ um cÃ³digo do tipo: `join <palavra-cÃ³digo>`
4. Exemplo: Se aparecer `join happy-cat`, envie: `join happy-cat` para `+1 415 523 8886`
5. VocÃª receberÃ¡ uma confirmaÃ§Ã£o no WhatsApp

#### 3ï¸âƒ£ Obter Credenciais


1. Copie o **Account SID** (comeÃ§a com AC...)
2. Copie o **Auth Token** (clique em "Show" para visualizar)

#### 4ï¸âƒ£ Configurar no Sistema

**MÃ©todo 1: Arquivo .env (Recomendado)**

1. Copie o arquivo `.env.example` e renomeie para `.env`
2. Edite o arquivo `.env` e preencha:

```env
WHATSAPP_ENABLED=true
```

**MÃ©todo 2: Direto no config.py**

Edite o arquivo `config.py` e substitua:

```python
WHATSAPP_ENABLED = True
```

#### 5ï¸âƒ£ Testar o Sistema

1. Instale as dependÃªncias:
```bash
pip install -r requirements.txt
```

2. Execute o sistema:
```bash
streamlit run app.py
```

3. FaÃ§a login e registre uma nova contribuiÃ§Ã£o
4. **IMPORTANTE**: Selecione **"Pix"** como tipo de pagamento
5. Marque a opÃ§Ã£o "ðŸ“² Enviar confirmaÃ§Ã£o via WhatsApp" (sÃ³ aparece para PIX)
6. Preencha um nÃºmero de celular vÃ¡lido
7. Clique em "Registrar"
8. O WhatsApp serÃ¡ enviado automaticamente!

### Como Funciona o Envio de WhatsApp?

#### Fluxo TÃ©cnico:

```
1. UsuÃ¡rio preenche formulÃ¡rio de cadastro
   â”œâ”€â”€ Nome do contribuinte
   â”œâ”€â”€ Valor da contribuiÃ§Ã£o
   â”œâ”€â”€ Tipo de pagamento: **PIX** (obrigatÃ³rio para WhatsApp)
   â”œâ”€â”€ Celular (obrigatÃ³rio)
   â””â”€â”€ Email (opcional)
   
2. Sistema valida o tipo de pagamento
   â”œâ”€â”€ Se tipo == "Pix":
   â”‚   â”œâ”€â”€ Checkbox WhatsApp Ã© exibido
   â”‚   â””â”€â”€ UsuÃ¡rio pode marcar para enviar
   â””â”€â”€ Se tipo != "Pix":
       â””â”€â”€ Mensagem informativa: "WhatsApp disponÃ­vel apenas para PIX"

3. Sistema valida o nÃºmero de celular
   â”œâ”€â”€ Verifica formato brasileiro (11 dÃ­gitos)
   â”œâ”€â”€ Valida DDD
   â””â”€â”€ Confirma que Ã© celular (inicia com 9)
   
4. Dados sÃ£o salvos no banco SQLite
   
5. Se WhatsApp estiver habilitado E tipo == "Pix":
   â”œâ”€â”€ Sistema formata nÃºmero para padrÃ£o internacional
   â”‚   Exemplo: (11) 98765-4321 â†’ whatsapp:+5511987654321
   â”‚
   â”œâ”€â”€ Monta mensagem personalizada:
   â”‚   ðŸ™ *MinistÃ©rio Dechonai*
   â”‚   OlÃ¡ JoÃ£o!
   â”‚   âœ… Sua contribuiÃ§Ã£o foi registrada com sucesso:
   â”‚   â€¢ Categoria: DÃ­zimo
   â”‚   â€¢ Valor: R$ 100,00
   â”‚   â€¢ Data: 07/02/2026
   â”‚
   â”‚
   â””â”€â”€ Retorna confirmaÃ§Ã£o ou erro
```

#### CÃ³digo Comentado (`whatsapp_service.py`):

```python
def enviar_confirmacao_contribuicao(telefone, nome, valor, categoria, data):
    """
    Envia mensagem WhatsApp de confirmaÃ§Ã£o
    
    Processo:
    1. Valida se serviÃ§o estÃ¡ habilitado
    2. Formata nÃºmero brasileiro â†’ internacional
    3. Cria mensagem personalizada
    5. Retorna status
    """
    
    # 1. Formatar nÃºmero
    numero_formatado = formatar_numero_whatsapp(telefone)
    # Input: "(11) 98765-4321"
    # Output: "whatsapp:+5511987654321"
    
    # 2. Montar mensagem
    mensagem = f"""
    ðŸ™ *MinistÃ©rio Dechonai*
    OlÃ¡ {nome}!
    âœ… Sua contribuiÃ§Ã£o foi registrada:
    â€¢ Categoria: {categoria}
    â€¢ Valor: R$ {valor:.2f}
    â€¢ Data: {data}
    """
    
    message = client.messages.create(
        body=mensagem,
        to=numero_formatado
    )
    
    # 4. Retornar sucesso
    return True, f"Enviado! SID: {message.sid}"
```

### ValidaÃ§Ã£o de Telefone

O sistema valida automaticamente:

âœ… **Formato aceito**: `(11) 98765-4321` ou `11987654321`
âœ… **Requisitos**: 
- 11 dÃ­gitos (DDD + nÃºmero)
- Terceiro dÃ­gito deve ser 9 (celular)
- DDD vÃ¡lido (11-99)

âŒ **Rejeitados**:
- Telefone fixo (sem o 9)
- Menos de 11 dÃ­gitos
- Formato invÃ¡lido

### Custos e Limites

#### Conta Gratuita (Trial):
- **CrÃ©dito inicial**: ~$15 USD
- **Custo por mensagem**: ~$0.005 USD
- **Limite**: ~3.000 mensagens com crÃ©dito inicial
- **RestriÃ§Ã£o**: Apenas nÃºmeros verificados no Sandbox

#### Conta Paga:
- **Plano prÃ©-pago**: Sem mensalidade, paga por uso
- **Custo Brasil**: ~$0.012 USD por mensagem
- **WhatsApp Business**: NÃºmero oficial da igreja
- **Sem restriÃ§Ãµes**: Envia para qualquer nÃºmero

### Troubleshooting (SoluÃ§Ã£o de Problemas)

#### ðŸ”´ "ServiÃ§o WhatsApp nÃ£o habilitado"
- Verifique se `WHATSAPP_ENABLED=true` no `.env`
- Confirme se as credenciais estÃ£o corretas

- Verifique Account SID e Auth Token

#### ðŸ”´ "Recipient not opted in"
- O nÃºmero nÃ£o confirmou no Sandbox

#### ðŸ”´ "Invalid phone number"
- Verifique formato do telefone
- Use padrÃ£o brasileiro: 55 + DDD + nÃºmero

### Upgrade para ProduÃ§Ã£o

Para uso profissional com nÃºmero prÃ³prio:

1. **Ativar WhatsApp Business API**:
   - Seguir processo de aprovaÃ§Ã£o do Facebook

2. **Obter NÃºmero Dedicado**:
   - Ou conectar nÃºmero existente

3. **Templates Aprovados**:
   - Submeter templates de mensagem
   - Aguardar aprovaÃ§Ã£o do WhatsApp

## ðŸ“¦ MÃ³dulos do Sistema

### ðŸ“Œ AtualizaÃ§Ã£o importante

As rotinas de envio de mensagens (WhatsApp/SMS/Email) foram removidas da aplicaÃ§Ã£o para manter foco no registro e consulta de lanÃ§amentos.

#### 1. `config.py` - ConfiguraÃ§Ãµes
Centraliza todas as configuraÃ§Ãµes do sistema:
- UsuÃ¡rios e nÃ­veis de acesso
- Tipos de pagamento e categorias
- Operadoras de celular

#### 2. `database.py` - Banco de Dados
Gerencia todas as operaÃ§Ãµes com o banco SQLite:
- `init_db()`: Inicializa o banco com schema atualizado
- `adicionar_lancamento()`: Adiciona novo lanÃ§amento com contatos
- `obter_lancamentos()`: Busca lanÃ§amentos com filtros
- `atualizar_lancamento()`: Atualiza lanÃ§amento incluindo contatos
- `excluir_lancamento()`: Remove lanÃ§amento
- `obter_lancamento_por_id()`: Busca lanÃ§amento especÃ­fico

#### 3. `auth.py` - AutenticaÃ§Ã£o
Sistema de autenticaÃ§Ã£o e seguranÃ§a de sessÃ£o:
- `verificar_login()`: Valida credenciais
- `login_esta_bloqueado()`: Verifica bloqueio temporÃ¡rio de login
- `registrar_falha_login()`: Calcula tentativas e janela de bloqueio
- `sessao_expirada()`: Verifica expiraÃ§Ã£o por inatividade

#### 4. `permissions.py` - PermissÃµes por mÃ³dulo
Controle de acesso por usuÃ¡rio e mÃ³dulo:
- `usuario_tem_permissao()`: Verifica acesso ao mÃ³dulo
- `get_permissoes_usuario()`: Carrega permissÃµes salvas
- `salvar_permissoes_usuario()`: Persiste permissÃµes do usuÃ¡rio

#### 5. `utils.py` - UtilitÃ¡rios
FunÃ§Ãµes auxiliares do sistema:
- `display_logo()`: Exibe logo da igreja
- `formatar_valor()`: Formata valores monetÃ¡rios
- `formatar_data()`: Formata datas
- `validar_nome()`: Valida nomes de contribuintes
- `validar_valor()`: Valida valores numÃ©ricos
- `calcular_totais()`: Calcula estatÃ­sticas financeiras
- `exibir_usuario_info()`: Exibe informaÃ§Ãµes do usuÃ¡rio logado

#### 5. `notifications.py` - ValidaÃ§Ãµes de Contato
ResponsÃ¡vel por validaÃ§Ãµes utilitÃ¡rias de email e celular usadas na ediÃ§Ã£o de lanÃ§amentos.

**FunÃ§Ãµes de ValidaÃ§Ã£o:**
- `validar_email()`: Valida formato de email
- `validar_celular()`: Valida DDD e nÃºmero de celular
- `formatar_telefone()`: Formata para padrÃ£o internacional

**FunÃ§Ãµes de Envio:**
- `enviar_email()`: Envia email HTML personalizado
  - Template responsivo
  - Dados da contribuiÃ§Ã£o
  - VersÃ­culo bÃ­blico
  - ConexÃ£o SMTP configurÃ¡vel
  
- `enviar_sms()`: Envia SMS de confirmaÃ§Ã£o
  - Mensagem otimizada (160 caracteres)
  - FormataÃ§Ã£o de nÃºmero internacional
  
- `enviar_notificacoes()`: Envia ambas notificaÃ§Ãµes
  - Gerencia email e SMS em conjunto
  - Retorna status de cada envio
  - Tratamento de erros individual

## Como Executar

O passo a passo completo de instalaÃ§Ã£o, configuraÃ§Ã£o do ambiente, execuÃ§Ã£o local e troubleshooting foi movido para [COMO_EXECUTAR.md](COMO_EXECUTAR.md).

Resumo rÃ¡pido:

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Antes do primeiro login, configure os hashes de usuÃ¡rio no `.env` ou no `secrets.toml`, conforme descrito em [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md).

## ðŸ‘¥ UsuÃ¡rios e NÃ­veis de Acesso

- **admin**: acesso global e gerenciamento de permissÃµes
- **diacono**: acesso apenas aos mÃ³dulos liberados pelo admin, com escopo restrito nos mÃ³dulos sensÃ­veis

Os usuÃ¡rios e nomes exibidos sÃ£o definidos em [config.py](config.py). A configuraÃ§Ã£o de hashes e a inclusÃ£o de novos usuÃ¡rios estÃ£o descritas em [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md).

## ðŸ“Š Banco de Dados

O sistema utiliza SQLite para armazenamento local dos dados. O banco de dados Ã© criado automaticamente na primeira execuÃ§Ã£o.

### Estrutura da Tabela `lancamentos`:
- `id`: Identificador Ãºnico (auto-incremento)
- `data`: Data do lanÃ§amento (YYYY-MM-DD)
- `nome`: Nome completo do contribuinte
- `valor`: Valor da contribuiÃ§Ã£o (REAL)
- `tipo`: Tipo de pagamento (Dinheiro, CartÃ£o, TransferÃªncia, Cheque, Pix)
- `categoria`: Categoria (DÃ­zimo, Oferta, Visitante)
- `usuario`: UsuÃ¡rio que registrou o lanÃ§amento
- **`email`**: Email do contribuinte (OPCIONAL - NOVO)
- **`codigo_area`**: DDD do celular (OPCIONAL - NOVO)
- **`celular`**: NÃºmero do celular (OPCIONAL - NOVO)
- **`operadora`**: Operadora do celular (OPCIONAL - NOVO)
- `created_at`: Timestamp de criaÃ§Ã£o automÃ¡tica

### OperaÃ§Ãµes DisponÃ­veis:

**Inserir LanÃ§amento:**
```python
adicionar_lancamento(
    data="2026-02-07",
    nome="JoÃ£o Silva",
    valor=100.00,
    tipo="Pix",
    categoria="DÃ­zimo",
    usuario="admin",
    email="joao@email.com",  # Opcional
    codigo_area="11",         # Opcional
    celular="999999999",      # Opcional
    operadora="Vivo"          # Opcional
)
```

**Buscar LanÃ§amentos:**
```python
# Admin vÃª todos
lancamentos = obter_lancamentos()

# UsuÃ¡rio comum vÃª apenas os seus
lancamentos = obter_lancamentos("usuario123", "diacono")
```

**Atualizar LanÃ§amento:**
```python
atualizar_lancamento(
    id_lancamento=1,
    data="2026-02-07",
    nome="JoÃ£o Silva Atualizado",
    valor=150.00,
    tipo="Dinheiro",
    categoria="Oferta",
    email="novo@email.com",
    codigo_area="21",
    celular="988888888",
    operadora="Claro"
)
```

## ðŸ“§ Sistema de NotificaÃ§Ãµes - Detalhes TÃ©cnicos

### Fluxo de Envio

1. **UsuÃ¡rio preenche formulÃ¡rio** de registro com dados opcionais de contato
2. **Sistema valida** email e celular
3. **LanÃ§amento Ã© salvo** no banco de dados
4. **NotificaÃ§Ãµes sÃ£o enviadas** (se habilitadas e dados vÃ¡lidos)
5. **Feedback visual** para o usuÃ¡rio sobre status do envio

### ValidaÃ§Ãµes Implementadas

#### Email:
- Verifica presenÃ§a de `@` e `.`
- Formato bÃ¡sico de email vÃ¡lido

#### Celular:
- DDD deve ter 2 dÃ­gitos
- Celular deve ter 8 ou 9 dÃ­gitos
- Remove caracteres nÃ£o numÃ©ricos automaticamente

### Templates de Mensagens

#### Email HTML
```html
Template responsivo com:
- CabeÃ§alho personalizado
- Dados da contribuiÃ§Ã£o em destaque
- VersÃ­culo bÃ­blico (2 CorÃ­ntios 9:7)
- RodapÃ© informativo
```

#### SMS Texto
```
OlÃ¡ {nome}! Agradecemos sua contribuiÃ§Ã£o de R$ {valor} 
({categoria}). Que Deus abenÃ§oe! - MinistÃ©rio Dechonai
```

### Modo SimulaÃ§Ã£o

Por padrÃ£o, o sistema opera em **modo simulaÃ§Ã£o** (para desenvolvimento/testes):
- Mensagens sÃ£o impressas no console
- Nenhum email/SMS real Ã© enviado
- Retorna sucesso para testes

Para **ativar envios reais**, edite `notifications.py`:

1. **Email** - Descomente as linhas:
```python
servidor = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
servidor.starttls()
servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
servidor.send_message(mensagem)
servidor.quit()
```

2. **SMS** - Descomente as linhas:
```python
message = client.messages.create(
    body=mensagem_sms,
    to=numero_completo
)
```

## ðŸ’¡ Exemplos de Uso

### Registrar ContribuiÃ§Ã£o com NotificaÃ§Ãµes

1. FaÃ§a login como `admin` ou `tesoureiro`
2. VÃ¡ em **"Registrar"**
3. Preencha os dados bÃ¡sicos:
   - Data
   - Nome completo
   - Valor
   - Tipo de pagamento
   - Categoria
4. Preencha os dados de contato (opcional):
   - Email
   - DDD + Celular
   - Operadora
5. Marque as opÃ§Ãµes de notificaÃ§Ã£o desejadas
6. Clique em **"Registrar LanÃ§amento"**
7. Sistema envia notificaÃ§Ãµes e exibe confirmaÃ§Ã£o

### Visualizar LanÃ§amentos com Contatos

1. VÃ¡ em **"Visualizar"**
2. Veja a tabela com colunas adicionais:
   - Email
   - Celular formatado: (DDD) NÃšMERO
3. Confira resumo financeiro atualizado

### Editar InformaÃ§Ãµes de Contato

1. Login como usuÃ¡rio com acesso ao mÃ³dulo **Editar**
2. VÃ¡ em **"Editar"**
3. Selecione o lanÃ§amento
4. Atualize email ou celular
5. Salve as alteraÃ§Ãµes

ObservaÃ§Ã£o: o usuÃ¡rio `admin` pode editar qualquer lanÃ§amento; outros usuÃ¡rios sÃ³ podem alterar registros criados por eles.

## ðŸ”’ SeguranÃ§a

Para operaÃ§Ã£o segura em produÃ§Ã£o:

- use hashes bcrypt e secrets fora do repositÃ³rio
- publique a aplicaÃ§Ã£o atrÃ¡s de HTTPS
- trate banco SQLite apenas como opÃ§Ã£o local ou de demonstraÃ§Ã£o

Para o checklist completo, consulte [GUIA_SEGURANCA.md](GUIA_SEGURANCA.md).

## ðŸ› ï¸ Tecnologias Utilizadas

### Core
- **Python 3.8+**: Linguagem base
- **Streamlit 1.28+**: Framework web interativo
- **SQLite**: Banco de dados relacional embutido
- **Pandas 2.0+**: AnÃ¡lise e manipulaÃ§Ã£o de dados

### UI/UX
- **Streamlit Option Menu**: Menu lateral customizado
- **Pillow 10.0+**: Processamento de imagens (logo)

### NotificaÃ§Ãµes (Opcional)
- **smtplib**: Envio de emails (biblioteca padrÃ£o Python)
- **email.mime**: CriaÃ§Ã£o de mensagens HTML

## ðŸ“ Melhorias Futuras

### Funcionalidades
- [ ] ExportaÃ§Ã£o de relatÃ³rios (PDF, Excel, CSV)
- [ ] Filtros avanÃ§ados de busca e data
- [ ] Dashboard com grÃ¡ficos interativos
- [ ] RelatÃ³rios mensais/anuais automatizados
- [ ] Sistema de metas de arrecadaÃ§Ã£o
- [ ] Categorias personalizÃ¡veis

### NotificaÃ§Ãµes
- [ ] Templates de email customizÃ¡veis
- [ ] Agendamento de envio de relatÃ³rios
- [ ] NotificaÃ§Ãµes push (PWA)
- [ ] Reavaliar integrações de mensagens no futuro
- [ ] ConfirmaÃ§Ã£o de recebimento

### Infraestrutura
- [ ] Backup automÃ¡tico em nuvem
- [ ] MigraÃ§Ã£o para PostgreSQL
- [ ] Deploy em cloud (AWS, Azure, Heroku)
- [ ] ContainerizaÃ§Ã£o (Docker)
- [ ] CI/CD pipeline
- [ ] Modo escuro/claro

### SeguranÃ§a
- [ ] AutenticaÃ§Ã£o com OAuth2
- [ ] Rate limiting
- [ ] Logs de auditoria completos
- [ ] Criptografia de dados sensÃ­veis
- [ ] Compliance com LGPD

## ðŸ› SoluÃ§Ã£o de Problemas

Os problemas mais comuns de login e configuraÃ§Ã£o estÃ£o documentados em [TROUBLESHOOTING_LOGIN.md](TROUBLESHOOTING_LOGIN.md). Para execuÃ§Ã£o local e ajustes de ambiente, use [COMO_EXECUTAR.md](COMO_EXECUTAR.md).

## ðŸ“ž Suporte e Contato

Para dÃºvidas ou sugestÃµes sobre o sistema:

- **Igreja**: MinistÃ©rio Dechonai
- **Desenvolvedor**: Sistema desenvolvido em Python/Streamlit
- **VersÃ£o**: 2.0 (com Sistema de NotificaÃ§Ãµes)
- **Ãšltima AtualizaÃ§Ã£o**: Fevereiro 2026

## ðŸ“„ LicenÃ§a

Este projeto Ã© de cÃ³digo aberto e estÃ¡ disponÃ­vel para uso e modificaÃ§Ã£o.

**Uso Livre** para:
- Igrejas e organizaÃ§Ãµes religiosas
- Estudos e aprendizado
- ModificaÃ§Ã£o e customizaÃ§Ã£o

**RecomendaÃ§Ãµes**:
- Manter crÃ©ditos aos desenvolvedores
- Compartilhar melhorias com a comunidade
- Usar de acordo com princÃ­pios Ã©ticos e cristÃ£os

## âœ¨ CrÃ©ditos

Desenvolvido para o **MinistÃ©rio Dechonai**

**Features desenvolvidas**:
- âœ… Sistema de autenticaÃ§Ã£o multi-nÃ­vel
- âœ… GestÃ£o completa de lanÃ§amentos
- âœ… RelatÃ³rios financeiros automÃ¡ticos
- âœ… **Sistema de notificaÃ§Ãµes Email/SMS (NOVO)**
- âœ… **Cadastro de contatos (NOVO)**
- âœ… **ValidaÃ§Ãµes de email e celular (NOVO)**
- âœ… Arquitetura modular e escalÃ¡vel
- âœ… Interface intuitiva e responsiva

---

**"Cada um dÃª conforme determinou em seu coraÃ§Ã£o, nÃ£o com pesar ou por obrigaÃ§Ã£o, pois Deus ama quem dÃ¡ com alegria." - 2 CorÃ­ntios 9:7**

---

## ðŸš€ Quick Start

```bash
# 1. Instalar dependÃªncias
pip install -r requirements.txt

# 2. Configurar hashes no .env ou secrets.toml
# Veja GUIA_SEGURANCA.md

# 3. Executar aplicaÃ§Ã£o
python -m streamlit run app.py

# 4. Acessar no navegador
# http://localhost:8501

# 5. Fazer login com um usuÃ¡rio configurado no ambiente
```

**Pronto! Sistema funcionando! ðŸŽ‰**

Este projeto Ã© de cÃ³digo aberto e estÃ¡ disponÃ­vel para uso e modificaÃ§Ã£o.

## âœ¨ Autor

Desenvolvido para o MinistÃ©rio Dechonai

