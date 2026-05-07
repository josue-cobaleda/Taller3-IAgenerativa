"""Tool que simula la generación de una etiqueta de devolución."""
import json
import re
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from langchain.tools import tool
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = ROOT_DIR / "logs"
VERIFICACIONES_PATH = LOGS_DIR / "verificaciones_temp.json"
DEVOLUCIONES_LOG_PATH = LOGS_DIR / "devoluciones_log.json"

VENTANA_VERIFICACION_HORAS = 1
PLAZO_ENVIO_DIAS = 7
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _verificacion_reciente_existe(order_id: str, product_id: str) -> bool:
    if not VERIFICACIONES_PATH.exists():
        return False
    try:
        registros = json.loads(VERIFICACIONES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False

    limite = datetime.utcnow() - timedelta(hours=VENTANA_VERIFICACION_HORAS)
    for r in reversed(registros):
        if (
            r.get("order_id") == str(order_id)
            and r.get("product_id") == str(product_id).upper()
            and r.get("elegible") is True
        ):
            try:
                ts = datetime.fromisoformat(r["timestamp"])
            except (KeyError, ValueError):
                continue
            if ts >= limite:
                return True
    return False


def _registrar_devolucion(payload: dict) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    registros = []
    if DEVOLUCIONES_LOG_PATH.exists():
        try:
            registros = json.loads(DEVOLUCIONES_LOG_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            registros = []
    registros.append(payload)
    DEVOLUCIONES_LOG_PATH.write_text(
        json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8"
    )


class _EtiquetaInput(BaseModel):
    order_id: str = Field(..., description="Número del pedido (ej. '1002').")
    product_id: str = Field(..., description="ID del producto a devolver (ej. 'P002').")
    email_cliente: str = Field(..., description="Correo electrónico del cliente.")


class EtiquetaResponse(BaseModel):
    exito: bool
    tracking_devolucion: Optional[str] = None
    url_etiqueta: Optional[str] = None
    instrucciones: Optional[str] = None
    fecha_limite_envio: Optional[str] = None
    monto_reembolso: Optional[float] = None
    error: Optional[str] = None


@tool("generar_etiqueta_devolucion", args_schema=_EtiquetaInput)
def generar_etiqueta_devolucion(order_id: str, product_id: str, email_cliente: str) -> dict:
    """Genera la etiqueta de envío de retorno para un producto previamente verificado
    como elegible. Esta herramienta SOLO debe invocarse después de que
    `verificar_elegibilidad_devolucion` haya devuelto `elegible=true` para el mismo
    par (order_id, product_id) en esta misma conversación.

    Args:
        order_id: Número del pedido.
        product_id: ID del producto.
        email_cliente: Correo del cliente al cual enviar la etiqueta.

    Returns:
        dict con `exito` (bool) y, si tuvo éxito, `tracking_devolucion`,
        `url_etiqueta`, `instrucciones`, `fecha_limite_envio` y `monto_reembolso`.
        En caso de error: `error` con el código del problema.
    """
    order_id = str(order_id).strip()
    product_id = str(product_id).strip().upper()
    email_cliente = str(email_cliente).strip()

    if not _verificacion_reciente_existe(order_id, product_id):
        return EtiquetaResponse(
            exito=False,
            error="elegibilidad_no_verificada",
        ).model_dump()

    if not EMAIL_REGEX.match(email_cliente):
        return EtiquetaResponse(exito=False, error="email_invalido").model_dump()

    tracking = "RET-" + uuid.uuid4().hex[:8].upper()
    fecha_limite = (date.today() + timedelta(days=PLAZO_ENVIO_DIAS)).isoformat()
    url = f"https://ecomarket.example.com/etiquetas/{tracking}.pdf"
    instrucciones = (
        "1) Imprime la etiqueta y pégala sobre el paquete (reutiliza el original si "
        "es posible). 2) Deposita el paquete en cualquier punto EcoLogistics. "
        "3) Recibirás el reembolso en 2-3 días hábiles tras la recepción."
    )

    monto = None
    if VERIFICACIONES_PATH.exists():
        try:
            registros = json.loads(VERIFICACIONES_PATH.read_text(encoding="utf-8"))
            for r in reversed(registros):
                if r.get("order_id") == order_id and r.get("product_id") == product_id and r.get("elegible"):
                    monto = r.get("monto_reembolso")
                    break
        except json.JSONDecodeError:
            pass

    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "order_id": order_id,
        "product_id": product_id,
        "email_cliente": email_cliente,
        "tracking_devolucion": tracking,
        "url_etiqueta": url,
        "fecha_limite_envio": fecha_limite,
    }
    _registrar_devolucion(payload)

    return EtiquetaResponse(
        exito=True,
        tracking_devolucion=tracking,
        url_etiqueta=url,
        instrucciones=instrucciones,
        fecha_limite_envio=fecha_limite,
        monto_reembolso=monto,
    ).model_dump()
