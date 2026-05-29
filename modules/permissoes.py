"""
Painel de Gerenciamento de Permissões dos Diáconos

Exclusivo para o usuário admin.
Permite ativar/desativar cada módulo do sistema para cada diácono.
"""

import streamlit as st

from permissions import (
    MODULOS_SISTEMA,
    USUARIOS_DIACONO,
    get_permissoes_usuario,
    salvar_permissoes_usuario,
)
from config import NOMES_USUARIOS


def exibir_painel_permissoes():
    """Renderiza o painel completo de gerenciamento de permissões."""

    st.title("🔐 Gerenciar Permissões dos Diáconos")
    st.markdown(
        "Configure abaixo quais funcionalidades cada diácono pode acessar. "
        "As alterações têm efeito imediato após salvar."
    )
    st.info(
        "Nos módulos de edição, newsletter e calendário, o acesso concedido ao diácono "
        "permite operar apenas sobre conteúdos criados pelo próprio usuário. "
        "O usuário admin mantém administração global.",
        icon="ℹ️",
    )
    st.markdown("---")

    # ── Uma aba por diácono ──────────────────────────────────────────────────
    nomes_abas = [NOMES_USUARIOS.get(u, u) for u in USUARIOS_DIACONO]
    tabs = st.tabs(nomes_abas)

    for tab, usuario in zip(tabs, USUARIOS_DIACONO):
        with tab:
            nome_exibicao = NOMES_USUARIOS.get(usuario, usuario)
            st.subheader(f"Permissões — {nome_exibicao}")
            st.caption(f"Usuário de login: `{usuario}`")
            st.markdown("")

            # Carrega permissões atuais do banco
            perms_atuais = get_permissoes_usuario(usuario)

            # Exibe um checkbox por módulo
            novas_perms = {}
            for modulo, info in MODULOS_SISTEMA.items():
                col_icone, col_check = st.columns([1, 11])
                with col_icone:
                    # Exibe o ícone do módulo como texto grande
                    st.markdown(
                        f"<div style='font-size:1.6rem;margin-top:4px'>{info['icon']}</div>",
                        unsafe_allow_html=True,
                    )
                with col_check:
                    novas_perms[modulo] = st.checkbox(
                        f"**{info['label']}**",
                        value=perms_atuais.get(modulo, False),
                        help=info["descricao"],
                        key=f"perm_{usuario}_{modulo}",
                    )

            st.markdown("")

            # Resumo visual do estado atual
            habilitados = [
                MODULOS_SISTEMA[m]["label"]
                for m, v in novas_perms.items()
                if v
            ]
            if habilitados:
                st.info(
                    "**Módulos habilitados:** " + " · ".join(habilitados),
                    icon="✅",
                )
            else:
                st.warning(
                    f"{nome_exibicao} não terá acesso a nenhum módulo.",
                    icon="⚠️",
                )

            st.markdown("")

            # Botão de salvar — chave única por diácono
            if st.button(
                f"💾 Salvar permissões de {nome_exibicao}",
                key=f"btn_salvar_{usuario}",
                type="primary",
                width="stretch",
            ):
                ok = salvar_permissoes_usuario(usuario, novas_perms)
                if ok:
                    st.success("Permissões salvas com sucesso!", icon="✅")
                else:
                    st.error("❌ Erro ao salvar permissões. Tente novamente.")
