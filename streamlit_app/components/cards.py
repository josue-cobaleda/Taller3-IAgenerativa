"""
Cards destacadas que el agente puede emitir:
- label-card  → etiqueta de devolución generada (con tracking + acciones)
- order-card  → resumen de pedido
- error-card  → error visual elegante
"""

import html
import streamlit as st


def render_label_card(c: dict) -> None:
    """Card destacada con la etiqueta de devolución generada."""
    st.markdown(
        f"""
        <div class="em-label-card">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                <div style="width:36px; height:36px; border-radius:9px;
                            background:var(--em-green-700); color:white;
                            display:grid; place-items:center;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round"
                         stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2"/>
                        <path d="M7 7h2v10H7zM12 7h1v10h-1zM16 7h2v10h-2z"/>
                    </svg>
                </div>
                <div>
                    <div class="em-label-eyebrow">Etiqueta de devolución generada</div>
                    <div class="em-label-title">Listo para imprimir y enviar</div>
                </div>
            </div>
            <div class="em-label-grid">
                <div>
                    <div class="em-label-field-label">Tracking</div>
                    <div class="em-label-field-value">{html.escape(c.get("tracking", ""))}</div>
                </div>
                <div>
                    <div class="em-label-field-label">Transportista</div>
                    <div class="em-label-field-value" style="font-family:Inter,sans-serif;">
                        {html.escape(c.get("carrier", ""))}
                    </div>
                </div>
                <div>
                    <div class="em-label-field-label">Costo de envío</div>
                    <div class="em-label-field-value" style="font-family:Inter,sans-serif;">
                        {html.escape(c.get("cost", ""))}
                    </div>
                </div>
                <div>
                    <div class="em-label-field-label">Reembolso estimado</div>
                    <div class="em-label-field-value" style="font-family:Inter,sans-serif;">
                        {html.escape(c.get("refund", ""))}
                    </div>
                </div>
                <div style="grid-column: 1 / -1;">
                    <div class="em-label-field-label">Validez</div>
                    <div class="em-label-field-value" style="font-family:Inter,sans-serif;">
                        Hasta el {html.escape(c.get("expires", ""))}
                    </div>
                </div>
            </div>
            <div class="em-label-instructions">
                <strong>Instrucciones</strong>
                <ol style="margin:4px 0 0; padding-left:18px;">
                    <li>Imprime la etiqueta y pégala sobre el paquete (reutiliza el original si puedes).</li>
                    <li>Deposita el paquete en cualquier punto EcoLogistics.</li>
                    <li>Recibirás el reembolso 2–3 días hábiles tras la recepción.</li>
                </ol>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Acciones reales como botones de Streamlit
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        # En producción: enlazar a la URL real devuelta por la tool
        st.link_button("⬇  Descargar PDF",
                       url=c.get("label_url", "https://demo.ecomarket.io/label.pdf"),
                       use_container_width=True)
    with col2:
        if st.button("✉  Enviar por email", key=f"email_{c.get('tracking', '')}",
                     use_container_width=True):
            st.toast("Etiqueta enviada por email ✓", icon="✅")
    with col3:
        if st.button("🖨  Imprimir", key=f"print_{c.get('tracking', '')}",
                     use_container_width=True):
            st.toast("Abriendo diálogo de impresión…", icon="🖨")


def render_order_card(c: dict) -> None:
    """Card resumen de pedido."""
    status_kind = c.get("status_kind", "")
    st.markdown(
        f"""
        <div class="em-order-card">
            <div class="em-order-thumb"></div>
            <div style="display:flex; flex-direction:column; gap:2px;">
                <span class="em-order-id">#{html.escape(c.get("id", ""))}</span>
                <span class="em-order-name">{html.escape(c.get("name", ""))}</span>
            </div>
            <span class="em-order-status {status_kind}">{html.escape(c.get("status", ""))}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error_card(c: dict) -> None:
    """Card visual de error."""
    st.markdown(
        f"""
        <div class="em-error-card">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
                 stroke="currentColor" stroke-width="2" stroke-linecap="round"
                 stroke-linejoin="round" style="color:var(--em-red-700); flex-shrink:0;">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div>
                <div class="em-error-title">{html.escape(c.get("title", ""))}</div>
                <div class="em-error-msg">{html.escape(c.get("msg", ""))}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
