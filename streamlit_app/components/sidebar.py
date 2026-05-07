"""
Sidebar de EcoMarket: marca, nueva conversación, lista de conversaciones,
herramientas disponibles y modelo en uso.
"""

import streamlit as st
from state import new_conversation, switch_conversation


# Tools disponibles del agente (debe coincidir con agent/tools.py)
AGENT_TOOLS = [
    {
        "name": "consultar_politica_o_faq",
        "meta": "RAG · base de conocimiento",
        "icon": "📖",
    },
    {
        "name": "consultar_estado_pedido",
        "meta": "DB pedidos",
        "icon": "📦",
    },
    {
        "name": "verificar_elegibilidad_devolucion",
        "meta": "Reglas + cruce de datos",
        "icon": "🛡",
    },
    {
        "name": "generar_etiqueta_devolucion",
        "meta": "Carrier API · simulado",
        "icon": "🏷",
    },
]


def render_sidebar() -> None:
    """Renderiza la sidebar completa."""
    with st.sidebar:
        # ------- Marca -------
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:10px; padding:4px 0 14px;">
                <div style="width:32px; height:32px; border-radius:9px;
                            background: linear-gradient(160deg, var(--em-green-700), var(--em-green-900));
                            display:grid; place-items:center; color:white;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round"
                         stroke-linejoin="round">
                        <path d="M11 20A7 7 0 0 1 4 13c0-7 7-9 16-9-1 9-3 16-9 16Z"/>
                        <path d="M2 22c2-5 6-8 12-9"/>
                    </svg>
                </div>
                <div>
                    <div style="font-weight:600; font-size:15px;">EcoMarket</div>
                    <div style="font-size:11px; color:var(--em-ink-3);
                                text-transform:uppercase; letter-spacing:0.02em;">
                        Soporte IA
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ------- Nueva conversación -------
        if st.button("＋ Nueva conversación", use_container_width=True, type="secondary"):
            new_conversation()
            st.rerun()

        # ------- Lista de conversaciones recientes -------
        st.markdown('<div class="em-side-label">Recientes</div>', unsafe_allow_html=True)

        for convo_id, convo in st.session_state.conversations.items():
            is_active = convo_id == st.session_state.current_id
            label = ("● " if is_active else "○ ") + convo["title"]
            if st.button(
                label,
                key=f"convo_{convo_id}",
                use_container_width=True,
                type="primary" if is_active else "tertiary",
            ):
                switch_conversation(convo_id)
                st.rerun()

        # ------- Tools disponibles -------
        st.markdown(
            f'<div class="em-side-label">Herramientas '
            f'<span style="float:right; text-transform:none; letter-spacing:0; '
            f'color:#a8b0a5;">{len(AGENT_TOOLS)}/{len(AGENT_TOOLS)}</span></div>',
            unsafe_allow_html=True,
        )

        for tool in AGENT_TOOLS:
            st.markdown(
                f"""
                <div class="em-tool-row">
                    <div class="em-tool-icon-sm">{tool['icon']}</div>
                    <div style="flex:1; line-height:1.25;">
                        <div style="font-size:12.5px;">{tool['name']}</div>
                        <div style="font-size:10.5px; color:var(--em-ink-3);">{tool['meta']}</div>
                    </div>
                    <div class="em-status-dot" title="disponible"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ------- Modelo en uso -------
        st.markdown('<div class="em-side-label" style="margin-top:18px;">Modelo</div>',
                    unsafe_allow_html=True)
        st.markdown(
            """
            <div style="display:flex; align-items:center; gap:10px;
                        padding:8px 10px; background:var(--em-surface);
                        border:1px solid var(--em-border); border-radius:8px;">
                <div style="width:24px; height:24px; border-radius:6px;
                            background: linear-gradient(135deg, var(--em-violet-700), var(--em-blue-700));
                            color:white; display:grid; place-items:center;
                            font-size:10px; font-weight:700;">AI</div>
                <div style="flex:1;">
                    <div style="font-size:12.5px; font-weight:500;">EcoAgent v2.1</div>
                    <div style="font-size:10.5px; color:var(--em-ink-3);">claude-sonnet · LangChain</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
