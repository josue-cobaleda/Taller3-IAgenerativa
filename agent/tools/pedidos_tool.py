"""Tool determinista de consulta de estado de pedido."""
import json
from pathlib import Path
from typing import List, Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
PEDIDOS_PATH = ROOT_DIR / "data" / "pedidos.json"

_PEDIDOS_INDEX: Optional[dict] = None


def _load_pedidos() -> dict:
    global _PEDIDOS_INDEX
    if _PEDIDOS_INDEX is None:
        data = json.loads(PEDIDOS_PATH.read_text(encoding="utf-8"))
        _PEDIDOS_INDEX = {p["tracking_number"]: p for p in data}
    return _PEDIDOS_INDEX


class _PedidoInput(BaseModel):
    order_id: str = Field(..., description="Número de pedido / tracking (ej. '1001').")


class EstadoPedidoResponse(BaseModel):
    encontrado: bool
    estado: Optional[str] = None
    fecha_entrega: Optional[str] = None
    detalle: Optional[str] = None
    productos: Optional[List[str]] = None
    mensaje: Optional[str] = None


@tool("consultar_estado_pedido", args_schema=_PedidoInput)
def consultar_estado_pedido(order_id: str) -> dict:
    """Consulta el estado y detalles de un pedido específico de EcoMarket por su
    número de pedido (tracking number).

    Args:
        order_id: Número del pedido (ej. '1001').

    Returns:
        dict con `encontrado` y, si existe, `estado`, `fecha_entrega`, `detalle`,
        `productos`. Si no existe, `mensaje` con la explicación.
    """
    pedidos = _load_pedidos()
    pedido = pedidos.get(str(order_id).strip())

    if pedido is None:
        return EstadoPedidoResponse(
            encontrado=False,
            mensaje=f"No encontré el pedido {order_id}. Verifica el número en tu correo de confirmación.",
        ).model_dump()

    return EstadoPedidoResponse(
        encontrado=True,
        estado=pedido["estado"],
        fecha_entrega=pedido["fecha_entrega"],
        detalle=pedido["detalle"],
        productos=pedido.get("productos", []),
    ).model_dump()
