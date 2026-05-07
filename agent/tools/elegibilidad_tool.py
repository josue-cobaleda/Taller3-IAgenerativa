"""Tool determinista que verifica si un producto de un pedido es devolvible."""
import json
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
PEDIDOS_PATH = ROOT_DIR / "data" / "pedidos.json"
CATALOGO_PATH = ROOT_DIR / "data" / "catalogo_productos.json"
LOGS_DIR = ROOT_DIR / "logs"
VERIFICACIONES_PATH = LOGS_DIR / "verificaciones_temp.json"

VENTANA_DIAS = 30

_PEDIDOS_INDEX: Optional[dict] = None
_CATALOGO_INDEX: Optional[dict] = None


def _load_pedidos() -> dict:
    global _PEDIDOS_INDEX
    if _PEDIDOS_INDEX is None:
        data = json.loads(PEDIDOS_PATH.read_text(encoding="utf-8"))
        _PEDIDOS_INDEX = {p["tracking_number"]: p for p in data}
    return _PEDIDOS_INDEX


def _load_catalogo() -> dict:
    global _CATALOGO_INDEX
    if _CATALOGO_INDEX is None:
        data = json.loads(CATALOGO_PATH.read_text(encoding="utf-8"))
        _CATALOGO_INDEX = {p["producto_id"]: p for p in data}
    return _CATALOGO_INDEX


def _registrar_verificacion(
    order_id: str,
    product_id: str,
    elegible: bool,
    monto_reembolso: Optional[float] = None,
) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    registros = []
    if VERIFICACIONES_PATH.exists():
        try:
            registros = json.loads(VERIFICACIONES_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            registros = []
    registros.append({
        "order_id": str(order_id),
        "product_id": str(product_id),
        "elegible": bool(elegible),
        "monto_reembolso": monto_reembolso,
        "timestamp": datetime.utcnow().isoformat(),
    })
    VERIFICACIONES_PATH.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8"
    )


class _ElegibilidadInput(BaseModel):
    order_id: str = Field(..., description="Número del pedido (ej. '1002').")
    product_id: str = Field(..., description="ID del producto a devolver (ej. 'P002').")


class ElegibilidadResponse(BaseModel):
    elegible: bool
    razon: str
    dias_restantes: Optional[int] = None
    monto_reembolso: Optional[float] = None
    categoria_producto: Optional[str] = None


@tool("verificar_elegibilidad_devolucion", args_schema=_ElegibilidadInput)
def verificar_elegibilidad_devolucion(order_id: str, product_id: str) -> dict:
    """Verifica si un producto específico de un pedido específico es elegible para
    devolución según las reglas de negocio: el pedido debe estar entregado, el producto
    debe pertenecer al pedido, debe estar dentro de la ventana de 30 días desde la
    entrega, y el producto debe ser devolvible según el catálogo (algunos productos
    de higiene o líquidos no admiten devolución).

    Args:
        order_id: Número del pedido (ej. '1002').
        product_id: ID del producto (ej. 'P002').

    Returns:
        dict con `elegible` (bool), `razon` (str), y si elegible: `dias_restantes`,
        `monto_reembolso`, `categoria_producto`.
    """
    order_id = str(order_id).strip()
    product_id = str(product_id).strip().upper()

    pedidos = _load_pedidos()
    catalogo = _load_catalogo()

    pedido = pedidos.get(order_id)
    if pedido is None:
        resp = ElegibilidadResponse(elegible=False, razon=f"Pedido {order_id} no encontrado.")
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    if pedido["estado"] != "Entregado":
        resp = ElegibilidadResponse(
            elegible=False,
            razon=f"El pedido aún no ha sido entregado (estado actual: {pedido['estado']}).",
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    if product_id not in pedido.get("productos", []):
        resp = ElegibilidadResponse(
            elegible=False,
            razon=f"El producto {product_id} no aparece en el pedido {order_id}.",
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    try:
        fecha_entrega = date.fromisoformat(pedido["fecha_entrega"])
    except ValueError:
        resp = ElegibilidadResponse(
            elegible=False,
            razon="No es posible determinar la fecha de entrega del pedido.",
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    dias_desde_entrega = (date.today() - fecha_entrega).days
    if dias_desde_entrega > VENTANA_DIAS:
        resp = ElegibilidadResponse(
            elegible=False,
            razon=f"Ya pasaron {dias_desde_entrega} días desde la entrega; la ventana es de {VENTANA_DIAS} días.",
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    producto = catalogo.get(product_id)
    if producto is None:
        resp = ElegibilidadResponse(
            elegible=False,
            razon=f"El producto {product_id} no figura en el catálogo.",
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    if not producto.get("devolvible", False):
        razon_no_dev = producto.get("razon_no_devolvible", "Producto no devolvible.")
        resp = ElegibilidadResponse(
            elegible=False,
            razon=razon_no_dev,
            categoria_producto=producto.get("categoria"),
        )
        _registrar_verificacion(order_id, product_id, False)
        return resp.model_dump()

    monto = float(producto.get("precio", 0.0))
    resp = ElegibilidadResponse(
        elegible=True,
        razon="Producto elegible para devolución.",
        dias_restantes=max(VENTANA_DIAS - dias_desde_entrega, 0),
        monto_reembolso=monto,
        categoria_producto=producto.get("categoria"),
    )
    _registrar_verificacion(order_id, product_id, True, monto_reembolso=monto)
    return resp.model_dump()
