"""
Render de mensajes y bloques de chat:
- mensajes de usuario / agente con st.chat_message
- bloques: text, tool-call (colapsado en expander), label-card, order-card, error-card
- typing indicator
"""

import json
import streamlit as st

from components.cards import render_label_card, render_order_card, render_error_card


STATUS_LABEL = {"ok": "Éxito", "err": "Error", "run": "Ejecutando"}


# ---------------------------------------------------------------------------
# Tool-call trace
# ---------------------------------------------------------------------------
def render_tool_call(block: dict) -> None:
    """Renderiza la traza de una tool dentro de un expander colapsado.

    Mantiene la trazabilidad exigida por el diseño (params + result) sin
    saturar visualmente el chat — el cliente final solo ve el texto natural y
    las tarjetas accionables; quien sustente puede expandir para auditar."""
    fn = block.get("fn", "tool")
    status = block.get("status", "ok")
    status_label = STATUS_LABEL.get(status, status)
    sub = block.get("sub", "")
    label = f"🔧 {fn}() — {status_label}"

    with st.expander(label, expanded=False):
        if sub:
            st.caption(sub)
        st.markdown("**Parámetros**")
        st.code(
            json.dumps(block.get("params", {}), indent=2, ensure_ascii=False),
            language="json",
        )
        st.markdown("**Resultado**")
        st.code(
            json.dumps(block.get("result", {}), indent=2, ensure_ascii=False),
            language="json",
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
