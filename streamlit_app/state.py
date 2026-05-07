"""
Inicialización y helpers de st.session_state.

Estructura de una conversación:
    {
        "id": str,
        "title": str,
        "messages": list[Message],
    }

Estructura de un Message:
    {
        "role": "user" | "agent",
        "author": str,
        "content": str | list[Block],   # str para user, lista de bloques para agent
    }

Estructura de un Block (mensaje del agente):
    {"type": "text",        "html": str}
    {"type": "tool",        "fn": str, "badge": str, "sub": str,
                            "status": "ok"|"err"|"run", "params": dict, "result": dict}
    {"type": "label-card",  "tracking": str, "carrier": str, "cost": str,
                            "expires": str, "refund": str}
    {"type": "order-card",  "id": str, "name": str, "status": str, "status_kind": str}
    {"type": "error-card",  "title": str, "msg": str}
"""

import uuid
import streamlit as st


# ---------------------------------------------------------------------------
# Conversación de bienvenida (demo)
# ---------------------------------------------------------------------------
WELCOME_CONVO = {
    "id": "c1",
    "title": "Pedido EM-78421 — estado de envío",
    "messages": [
        {
            "role": "user",
            "author": "Lucía Méndez",
            "content": "Hola, ¿pueden decirme dónde está mi pedido **EM-78421**? Hace 3 días que lo espero.",
        },
        {
            "role": "agent",
            "author": "EcoAgent",
            "content": [
                {"type": "text", "html": "Claro, Lucía. Voy a revisar el estado de tu pedido en este momento."},
                {
                    "type": "tool",
                    "fn": "consultar_estado_pedido",
                    "badge": "order",
                    "sub": "Consulta a base de datos de pedidos",
                    "status": "ok",
                    "params": {"order_id": "EM-78421", "customer_id": "u_88210"},
                    "result": {
                        "order_id": "EM-78421",
                        "status": "en_transito",
                        "carrier": "EcoLogistics",
                        "tracking": "EL2026-7841-MX",
                        "estimated_delivery": "2026-05-08",
                        "items": 2,
                    },
                },
                {
                    "type": "order-card",
                    "id": "EM-78421",
                    "name": "Pack hogar reusable + 1 más",
                    "status": "En tránsito",
                    "status_kind": "transit",
                },
                {
                    "type": "text",
                    "html": "Tu pedido está **en tránsito** con EcoLogistics. La entrega estimada es el **viernes 8 de mayo**. Tracking: **EL2026-7841-MX**.",
                },
            ],
        },
    ],
}


def init_session_state() -> None:
    """Inicializa st.session_state con valores por defecto."""
    if "conversations" not in st.session_state:
        st.session_state.conversations = {WELCOME_CONVO["id"]: WELCOME_CONVO}

    if "current_id" not in st.session_state:
        st.session_state.current_id = WELCOME_CONVO["id"]


def new_conversation() -> str:
    """Crea una nueva conversación vacía y la marca como activa."""
    new_id = "c_" + uuid.uuid4().hex[:8]
    st.session_state.conversations[new_id] = {
        "id": new_id,
        "title": "Nueva conversación",
        "messages": [],
    }
    st.session_state.current_id = new_id
    return new_id


def switch_conversation(convo_id: str) -> None:
    """Cambia la conversación activa."""
    if convo_id in st.session_state.conversations:
        st.session_state.current_id = convo_id


def current_messages() -> list:
    """Retorna los mensajes de la conversación activa."""
    return st.session_state.conversations[st.session_state.current_id]["messages"]


def append_message(message: dict) -> None:
    """Agrega un mensaje a la conversación activa.
    Si es el primer mensaje del usuario, también actualiza el título de la conversación."""
    convo = st.session_state.conversations[st.session_state.current_id]
    convo["messages"].append(message)

    # Auto-titular con el primer mensaje del usuario
    if convo["title"] == "Nueva conversación" and message["role"] == "user":
        first_line = message["content"].strip().split("\n")[0][:60]
        convo["title"] = first_line or "Nueva conversación"
