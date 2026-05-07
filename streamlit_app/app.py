"""
EcoMarket — Atención al cliente con agente de IA
================================================
Punto de entrada principal de la app Streamlit.

Estructura:
    app.py                  ← este archivo (orquesta todo)
    components/
        sidebar.py          ← logo, nueva conversación, tools, modelo
        chat.py             ← render de mensajes y tool traces
        cards.py            ← label card, order card, error card
    agent/
        tools.py            ← stubs de las 4 tools del agente
        runner.py           ← punto de inyección del agente LangChain
    styles.py               ← CSS personalizado
    state.py                ← inicialización y helpers de st.session_state

Ejecutar:
    streamlit run app.py
"""

import sys
import pathlib

# Permite que `from agent.runner import run_agent` resuelva al paquete agent/
# de la raíz del repo (el agente real), no a un stub local.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import streamlit as st

from styles import inject_css
from state import init_session_state, new_conversation, current_messages, append_message
from components.sidebar import render_sidebar
from components.chat import render_message, render_typing_indicator
from agent.runner import run_agent

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoMarket · Soporte IA",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()
init_session_state()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
render_sidebar()

# ---------------------------------------------------------------------------
# Topbar (titulo de conversación)
# ---------------------------------------------------------------------------
convo_title = st.session_state.conversations[st.session_state.current_id]["title"]

st.markdown(
    f"""
    <div class="em-topbar">
        <div class="em-topbar-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round"
                 stroke-linejoin="round" style="color:var(--em-green-700)">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <span>{convo_title}</span>
        </div>
        <span class="em-pill-online">Agente activo</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Chat area — historial
# ---------------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    for msg in current_messages():
        render_message(msg)

# ---------------------------------------------------------------------------
# Composer — input del usuario
# ---------------------------------------------------------------------------
prompt = st.chat_input("Escribe a EcoAgent — pedido, devolución, política…")

if prompt:
    # 1) Append user message
    append_message({
        "role": "user",
        "author": "Tú",
        "content": prompt,
    })

    # Render the just-appended user message immediately
    with chat_container:
        render_message(st.session_state.conversations[st.session_state.current_id]["messages"][-1])

        # 2) Show typing indicator while the agent thinks
        typing_slot = st.empty()
        with typing_slot:
            render_typing_indicator()

        # 3) Run the agent (LangChain plug-in point)
        agent_response = run_agent(
            user_message=prompt,
            history=current_messages(),
        )
        typing_slot.empty()

        # 4) Append + render the agent response
        append_message(agent_response)
        render_message(agent_response)

    # Force rerun so the chat scroll & sidebar conversation list refresh
    st.rerun()
