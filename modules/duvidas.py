"""
Página de Dúvidas — Versionamento e Tecnologias
"""
import streamlit as st


def exibir_pagina_duvidas():
    st.title("❓ Dúvidas e Informações")

    # ── Versionamento ─────────────────────────────────────────────────────────
    st.markdown("## 📋 Versionamento")
    st.markdown("""
| Versão | Data | Descrição |
|--------|------|-----------|
| 1.0.0  | Mar/2026 | Versão inicial — registro de dízimos e ofertas |
| 1.1.0  | Mar/2026 | Módulo de Cadastro de Membros |
| 1.2.0  | Mai/2026 | Busca automática de CEP via ViaCEP, ajustes de segurança e correções de UX |
| 1.3.0  | Mai/2026 | Módulo de Aniversariantes |
| 1.4.0  | Mai/2026 | Módulo de Permissões e controle de acesso por perfil |
| 1.7.0  | Mai/2026 | Módulo de Calendário de Eventos e Newsletter (envio de comunicados) |
| 1.8.0  | Mai/2026 | Módulo de Certificados (download em PDF) |
| 1.9.0  | Mai/2026 | Novo módulo de Gestão de Finanças (Contas a Pagar, Extrato/Caixa, Resumo e exportação Excel) |
""")

    st.markdown("---")

    # ── Tecnologias utilizadas ─────────────────────────────────────────────────
    st.markdown("## 🛠️ Tecnologias Utilizadas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🐍 Linguagem")
        st.markdown("""
- **Python 3.10+**  
  Linguagem principal da aplicação.
""")

        st.markdown("### 🖥️ Interface")
        st.markdown("""
- **Streamlit ≥ 1.28**  
  Framework de interface web para Python.
- **streamlit-option-menu ≥ 0.3.6**  
  Menu lateral com ícones.
""")

        st.markdown("### 🔐 Segurança")
        st.markdown("""
- **bcrypt ≥ 4.0**  
  Hash seguro de senhas dos usuários.
- **python-dotenv ≥ 1.0**  
  Gerenciamento de variáveis de ambiente (.env).
""")

    with col2:
        st.markdown("### 🗄️ Banco de Dados")
        st.markdown("""
- **SQLite** (via módulo nativo `sqlite3`)  
  Armazenamento local dos lançamentos e membros.
""")

        st.markdown("### 📦 Utilitários")
        st.markdown("""
- **pandas ≥ 2.0**  
  Manipulação e exportação de dados tabulares.
- **openpyxl ≥ 3.1**  
  Exportação de relatórios em formato Excel (.xlsx).
- **Pillow ≥ 10.0**  
  Exibição e processamento de imagens (logo).
- **requests ≥ 2.31**  
  Consulta de CEP via API ViaCEP.
""")

        st.markdown("### 🌐 APIs Externas")
        st.markdown("""
- **ViaCEP** (`viacep.com.br`)  
  Consulta e preenchimento automático de endereço pelo CEP.
""")

    st.markdown("---")

    # ── Contato / Suporte ──────────────────────────────────────────────────────
    st.markdown("## 💬 Suporte")
    st.info(
        "Em caso de dúvidas ou problemas, entre em contato com o administrador do sistema."
    )

    st.markdown("---")

    # ── Créditos ───────────────────────────────────────────────────────────────
    st.markdown("## 👨‍💻 Desenvolvimento")
    st.info(
        "Desenvolvido por **Robson Augusto Dias** · "
        "Utilizando **LLM Copilot** como assistente de desenvolvimento"
    )
