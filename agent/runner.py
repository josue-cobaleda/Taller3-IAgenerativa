"""AgentExecutor + adaptador al contrato de bloques del scaffold Streamlit.

Contrato (lo que el frontend espera de `run_agent`):
    {
        "role": "agent",
        "author": "EcoAgent",
        "content": [
            {"type": "tool", "fn": ..., "badge": "kb|order|check|label",
             "sub": ..., "status": "ok"|"err", "params": {...}, "result": {...}},
            {"type": "label-card", "tracking": ..., "carrier": ..., ...},
            {"type": "order-card", "id": ..., "name": ..., ...},
            {"type": "error-card", "title": ..., "msg": ...},
            {"type": "text", "html": ...},
        ]
    }
"""
from __future__ import annotations

from typing import Any, Iterable, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from agent.prompt import SYSTEM_PROMPT
from agent.tools import ALL_TOOLS
from config import get_llm

TOOL_BADGE = {
    "consultar_politica_o_faq": "kb",
    "consultar_estado_pedido": "order",
    "verificar_elegibilidad_devolucion": "check",
    "generar_etiqueta_devolucion": "label",
}

TOOL_SUB = {
    "consultar_politica_o_faq": "Búsqueda en políticas, catálogo y FAQ",
    "consultar_estado_pedido": "Consulta a base de datos de pedidos",
    "verificar_elegibilidad_devolucion": "Cruce de pedido, catálogo y política",
    "generar_etiqueta_devolucion": "Generación de etiqueta de retorno",
}

ESTADO_KIND = {
    "Entregado": "delivered",
    "En camino": "transit",
    "Procesando": "transit",
    "Retrasado": "delayed",
    "Cancelado": "cancelled",
}

_executor: AgentExecutor | None = None


def build_agent_executor() -> AgentExecutor:
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    return AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )


def get_executor() -> AgentExecutor:
    global _executor
    if _executor is None:
        _executor = build_agent_executor()
    return _executor


def _agent_msg(blocks: List[dict]) -> dict:
    return {"role": "agent", "author": "EcoAgent", "content": blocks}


def _is_error_result(observation: Any) -> bool:
    if isinstance(observation, dict):
        if observation.get("encontrado") is False:
            return True
        if observation.get("exito") is False:
            return True
        if observation.get("elegible") is False:
            return True
    return False


def _history_to_messages(history: Iterable[dict]) -> list:
    out = []
    for msg in history or []:
        role = msg.get("role")
        content = msg.get("content")
        if role == "user":
            out.append(HumanMessage(content=str(content)))
        elif role == "agent":
            if isinstance(content, list):
                text_parts = [b.get("html", "") for b in content if b.get("type") == "text"]
                text = "\n".join(p for p in text_parts if p)
            else:
                text = str(content) if content else ""
            if text:
                out.append(AIMessage(content=text))
    return out


def _build_tool_block(tool_name: str, tool_input: Any, observation: Any) -> dict:
    return {
        "type": "tool",
        "fn": tool_name,
        "badge": TOOL_BADGE.get(tool_name, "kb"),
        "sub": TOOL_SUB.get(tool_name, ""),
        "status": "err" if _is_error_result(observation) else "ok",
        "params": tool_input if isinstance(tool_input, dict) else {"input": tool_input},
        "result": observation if isinstance(observation, dict) else {"value": observation},
    }


def _maybe_extra_card(tool_name: str, tool_input: Any, observation: Any) -> dict | None:
    if not isinstance(observation, dict):
        return None

    if tool_name == "generar_etiqueta_devolucion" and observation.get("exito"):
        monto = observation.get("monto_reembolso")
        refund_str = f"COP {int(monto):,}".replace(",", ".") if monto else "Por confirmar"
        return {
            "type": "label-card",
            "tracking": observation.get("tracking_devolucion", ""),
            "carrier": "EcoLogistics",
            "cost": "Gratis",
            "refund": refund_str,
            "expires": observation.get("fecha_limite_envio", ""),
            "label_url": observation.get("url_etiqueta", ""),
        }

    if tool_name == "consultar_estado_pedido" and observation.get("encontrado"):
        order_id = (tool_input or {}).get("order_id", "") if isinstance(tool_input, dict) else ""
        return {
            "type": "order-card",
            "id": str(order_id),
            "name": "Pedido EcoMarket",
            "status": observation.get("estado", ""),
            "status_kind": ESTADO_KIND.get(observation.get("estado", ""), ""),
        }

    return None


def run_agent(user_message: str, history: list) -> dict:
    """Punto único de entrada del agente. Invoca el AgentExecutor y traduce los
    intermediate_steps al formato de bloques que entiende el frontend Streamlit."""
    chat_history = _history_to_messages(history)

    try:
        result = get_executor().invoke({
            "input": user_message,
            "chat_history": chat_history,
        })
    except Exception as e:  # noqa: BLE001 — defensa para que la UI no se rompa
        return _agent_msg([{
            "type": "error-card",
            "title": "Error del sistema",
            "msg": f"No pude completar tu solicitud: {e}",
        }])

    blocks: List[dict] = []
    for action, observation in result.get("intermediate_steps", []):
        tool_name = getattr(action, "tool", "tool")
        tool_input = getattr(action, "tool_input", {})
        blocks.append(_build_tool_block(tool_name, tool_input, observation))
        extra = _maybe_extra_card(tool_name, tool_input, observation)
        if extra:
            blocks.append(extra)

    final_text = result.get("output") or ""
    if isinstance(final_text, list):
        # Algunas versiones de Gemini devuelven bloques en lugar de string.
        final_text = "\n".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in final_text
        )
    if final_text:
        blocks.append({"type": "text", "html": str(final_text)})

    if not blocks:
        blocks.append({"type": "text", "html": "(sin respuesta)"})

    return _agent_msg(blocks)
