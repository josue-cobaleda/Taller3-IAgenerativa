from agent.tools.rag_tool import consultar_politica_o_faq
from agent.tools.pedidos_tool import consultar_estado_pedido
from agent.tools.elegibilidad_tool import verificar_elegibilidad_devolucion
from agent.tools.etiquetas_tool import generar_etiqueta_devolucion

ALL_TOOLS = [
    consultar_politica_o_faq,
    consultar_estado_pedido,
    verificar_elegibilidad_devolucion,
    generar_etiqueta_devolucion,
]
