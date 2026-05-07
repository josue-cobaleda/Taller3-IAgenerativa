"""
Render de mensajes y bloques de chat:
- mensajes de usuario / agente con st.chat_message
- bloques: text, tool-call (con expander), label-card, order-card, error-card
- typing indicator
"""

import json
import html
import streamlit as st

from components.cards import render_label_card, render_order_card, render_error_card


TOOL_ICON_SVG = {
    "kb": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>',
    "order": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><path d="M3.3 7 12 12l8.7-5"/><path d="M12 22V12"/></svg>',
    "check": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 12l2 2 4-4"/><path d="M12 22c5.5-3 8-6 8-12V5l-8-3-8 3v5c0 6 2.5 9 8 12z"/></svg>',
    "label": '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 7h2v10H7zM12 7h1v10h-1zM16 7h2v10h-2z"/></svg>',
}

STATUS_LABEL = {"ok": "Éxito", "err": "Error", "run": "Ejecutando"}


# ---------------------------------------------------------------------------
# Tool-call trace
# ---------------------------------------------------------------------------
def render_tool_call(block: dict) -> None:
    """Renderiza un bloque tool: badge, función, status, params + resultado."""
    badge = block.get("badge", "kb")
    status = block.get("status", "ok")
    fn = block.get("fn", "tool")

    # Header
    st.markdown(
        f"""
        <div class="em-tool-call">
            <div class="em-tool-head">
                <div class="em-tool-badge {badge}">{TOOL_ICON_SVG.get(badge, "")}</div>
                <div style="flex:1; line-height:1.25;">
                    <div>
                        <span class="em-tool-fn">{html.escape(fn)}()</span>
                        <span class="em-tool-status {status}">{STATUS_LABEL[status]}</span>
                    </div>
                    <div class="em-tool-sub">{html.escape(block.get("sub", ""))}</div>
                </div>
            </div>
            <div class="em-tool-section">
                <div class="em-tool-section-label">Parámetros</div>
                <pre class="em-tool-code">{html.escape(json.dumps(block.get("params", {}),
                                                                  indent=2, ensure_ascii=False))}</pre>
            </div>
            <div class="em-tool-section">
                <div class="em-tool-section-label">Resultado</div>
                <pre class="em-tool-code">{html.escape(json.dumps(block.get("result", {}),
                                                                  indent=2, ensure_ascii=False))}</pre>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Block dispatcher
# ---------------------------------------------------------------------------
def render_block(block: dict) -> None:
    """Despacha el render correcto según el tipo de bloque del agente."""
    btype = block.get("type")
    if btype == "text":
        st.markdown(block["html"])
    elif btype == "tool":
        render_tool_call(block)
    elif btype == "label-card":
        render_label_card(block)
    elif btype == "order-card":
        render_order_card(block)
    elif btype == "error-card":
        render_error_card(block)


# ---------------------------------------------------------------------------
# Message render
# ---------------------------------------------------------------------------
def render_message(msg: dict) -> None:
    """Renderiza un mensaje completo dentro de st.chat_message."""
    role = msg["role"]
    avatar = "🌿" if role == "agent" else "🧑"
    chat_role = "assistant" if role == "agent" else "user"

    with st.chat_message(chat_role, avatar=avatar):
        if role == "user":
            # Soporta markdown en el contenido del usuario
            st.markdown(msg["content"])
        else:
            # El contenido del agente es una lista de bloques
            for block in msg["content"]:
                render_block(block)


# ---------------------------------------------------------------------------
# Typing indicator
# ---------------------------------------------------------------------------
def render_typing_indicator() -> None:
    """Muestra el indicador 'EcoAgent escribiendo…' mientras el agente piensa."""
    with st.chat_message("assistant", avatar="🌿"):
        st.markdown(
            '<div class="em-typing"><span></span><span></span><span></span></div>',
            unsafe_allow_html=True,
        )
