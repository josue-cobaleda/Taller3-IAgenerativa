"""
CSS personalizado para EcoMarket.
Replica la estética del artifact HTML aprobado:
- Verdes naturales eco-friendly
- Tipografía Inter + JetBrains Mono
- Bordes redondeados sutiles, espaciado generoso
"""

import streamlit as st

CSS = """
<style>
    /* Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --em-bg: #f7f7f4;
        --em-surface: #ffffff;
        --em-sidebar: #fbfaf6;
        --em-border: #e7e6df;
        --em-border-strong: #d6d4cb;
        --em-ink: #1a1f1c;
        --em-ink-2: #4a544d;
        --em-ink-3: #7a8479;
        --em-green-900: oklch(0.32 0.06 155);
        --em-green-700: oklch(0.45 0.08 155);
        --em-green-600: oklch(0.55 0.09 155);
        --em-green-200: oklch(0.92 0.04 155);
        --em-green-100: oklch(0.96 0.025 155);
        --em-green-50:  oklch(0.98 0.015 155);
        --em-amber-700: oklch(0.62 0.13 75);
        --em-amber-100: oklch(0.95 0.04 80);
        --em-red-700: oklch(0.55 0.16 27);
        --em-red-100: oklch(0.95 0.035 27);
        --em-blue-700: oklch(0.52 0.12 245);
        --em-blue-100: oklch(0.95 0.03 245);
        --em-violet-700: oklch(0.5 0.13 290);
        --em-violet-100: oklch(0.95 0.03 290);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stApp { background: var(--em-bg); }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: var(--em-sidebar);
        border-right: 1px solid var(--em-border);
    }

    /* Topbar */
    .em-topbar {
        display: flex; align-items: center; gap: 16px;
        padding: 10px 4px 14px;
        border-bottom: 1px solid var(--em-border);
        margin-bottom: 18px;
    }
    .em-topbar-title {
        display: flex; align-items: center; gap: 10px;
        font-size: 14px; font-weight: 600; color: var(--em-ink);
    }
    .em-pill-online {
        display: inline-flex; align-items: center; gap: 6px;
        font-size: 11.5px; font-weight: 500;
        padding: 3px 8px; border-radius: 999px;
        background: var(--em-green-100); color: var(--em-green-900);
    }
    .em-pill-online::before {
        content: ''; width: 6px; height: 6px; border-radius: 50%;
        background: var(--em-green-600);
        box-shadow: 0 0 0 3px rgba(0,128,72,0.15);
    }

    /* Chat message customization */
    [data-testid="stChatMessage"] {
        background: transparent;
        border: none;
        padding: 4px 0;
    }
    [data-testid="stChatMessageContent"] p { margin: 0 0 8px; line-height: 1.55; }
    [data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0; }

    /* Tool-call trace card */
    .em-tool-call {
        border: 1px solid var(--em-border);
        background: var(--em-surface);
        border-radius: 12px;
        overflow: hidden;
        margin: 8px 0;
        box-shadow: 0 1px 2px rgba(20, 30, 24, 0.04);
    }
    .em-tool-head {
        display: flex; align-items: center; gap: 10px;
        padding: 10px 12px;
        border-bottom: 1px solid var(--em-border);
    }
    .em-tool-badge {
        width: 26px; height: 26px; border-radius: 7px;
        display: grid; place-items: center; flex-shrink: 0;
    }
    .em-tool-badge.kb     { background: var(--em-blue-100);   color: var(--em-blue-700); }
    .em-tool-badge.order  { background: var(--em-green-100);  color: var(--em-green-700); }
    .em-tool-badge.check  { background: var(--em-amber-100);  color: var(--em-amber-700); }
    .em-tool-badge.label  { background: var(--em-violet-100); color: var(--em-violet-700); }
    .em-tool-fn {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 12.5px; font-weight: 500; color: var(--em-ink);
    }
    .em-tool-status {
        font-size: 10.5px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.06em;
        padding: 2px 7px; border-radius: 4px; margin-left: 8px;
    }
    .em-tool-status.ok { background: var(--em-green-100); color: var(--em-green-900); }
    .em-tool-status.err { background: var(--em-red-100); color: var(--em-red-700); }
    .em-tool-status.run { background: var(--em-amber-100); color: var(--em-amber-700); }
    .em-tool-sub { font-size: 11.5px; color: var(--em-ink-3); margin-top: 2px; }
    .em-tool-section {
        padding: 10px 12px;
        border-bottom: 1px solid var(--em-border);
        background: var(--em-green-50);
    }
    .em-tool-section:last-child { border-bottom: none; }
    .em-tool-section-label {
        font-size: 10px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em;
        color: var(--em-ink-3); margin-bottom: 6px;
    }
    .em-tool-code {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 12px; line-height: 1.55; color: var(--em-ink-2);
        white-space: pre-wrap; word-break: break-word; margin: 0;
    }

    /* Label card (return label) */
    .em-label-card {
        border: 1px solid var(--em-green-200);
        background: linear-gradient(180deg, var(--em-green-50), var(--em-surface) 80%);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 4px 14px -6px rgba(20, 30, 24, 0.10);
        position: relative;
        overflow: hidden;
        margin: 10px 0;
    }
    .em-label-card::before {
        content: ''; position: absolute; left: 0; top: 0; bottom: 0;
        width: 4px; background: var(--em-green-700);
    }
    .em-label-eyebrow {
        font-size: 10.5px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.08em;
        color: var(--em-green-700);
    }
    .em-label-title { font-size: 15px; font-weight: 600; color: var(--em-ink); }
    .em-label-grid {
        display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px;
        margin: 14px 0;
    }
    .em-label-field-label {
        font-size: 10.5px; color: var(--em-ink-3);
        text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 3px;
    }
    .em-label-field-value {
        font-family: 'JetBrains Mono', ui-monospace, monospace;
        font-size: 13px; font-weight: 500; color: var(--em-ink);
    }
    .em-label-instructions {
        font-size: 12.5px; color: var(--em-ink-2);
        margin-top: 12px; padding: 10px 12px;
        background: rgba(0,0,0,0.02); border-radius: 8px;
    }

    /* Order card */
    .em-order-card {
        border: 1px solid var(--em-border);
        border-radius: 12px;
        padding: 12px 14px;
        background: var(--em-surface);
        display: grid;
        grid-template-columns: auto 1fr auto;
        gap: 12px; align-items: center;
        margin: 8px 0;
    }
    .em-order-thumb {
        width: 40px; height: 40px; border-radius: 8px;
        background: repeating-linear-gradient(135deg,
            var(--em-green-100), var(--em-green-100) 4px,
            var(--em-green-50) 4px, var(--em-green-50) 8px);
        border: 1px solid var(--em-border);
    }
    .em-order-id {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11.5px; color: var(--em-ink-3);
    }
    .em-order-name { font-weight: 500; font-size: 13.5px; }
    .em-order-status {
        font-size: 11.5px; font-weight: 500;
        padding: 4px 9px; border-radius: 999px;
        background: var(--em-green-100); color: var(--em-green-900);
    }
    .em-order-status.transit { background: var(--em-blue-100); color: var(--em-blue-700); }

    /* Error card */
    .em-error-card {
        border: 1px solid oklch(0.85 0.06 27);
        background: var(--em-red-100);
        border-radius: 12px;
        padding: 12px 14px;
        display: flex; gap: 10px; align-items: flex-start;
        margin: 8px 0;
    }
    .em-error-title { font-weight: 600; color: var(--em-red-700); font-size: 13px; }
    .em-error-msg { font-size: 12.5px; color: var(--em-ink-2); margin-top: 2px; }

    /* Typing indicator */
    .em-typing {
        display: inline-flex; gap: 4px;
        padding: 12px 14px;
        background: var(--em-surface);
        border: 1px solid var(--em-border);
        border-radius: 12px; align-items: center;
    }
    .em-typing span {
        width: 6px; height: 6px; border-radius: 50%;
        background: #a8b0a5;
        animation: em-bounce 1.2s infinite ease-in-out;
    }
    .em-typing span:nth-child(2) { animation-delay: 0.15s; }
    .em-typing span:nth-child(3) { animation-delay: 0.3s; }
    @keyframes em-bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
        30% { transform: translateY(-4px); opacity: 1; }
    }

    /* Sidebar tool list */
    .em-tool-row {
        display: flex; align-items: center; gap: 10px;
        padding: 8px 0;
        font-size: 12.5px; color: var(--em-ink-2);
        border-bottom: 1px solid var(--em-border);
    }
    .em-tool-row:last-child { border-bottom: none; }
    .em-tool-icon-sm {
        width: 26px; height: 26px; border-radius: 7px;
        background: var(--em-surface);
        border: 1px solid var(--em-border);
        display: grid; place-items: center; flex-shrink: 0;
    }
    .em-status-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: var(--em-green-600);
        box-shadow: 0 0 0 3px var(--em-green-100);
        flex-shrink: 0; margin-left: auto;
    }
    .em-side-label {
        font-size: 10.5px; font-weight: 600;
        color: var(--em-ink-3);
        letter-spacing: 0.08em; text-transform: uppercase;
        margin: 14px 0 6px;
    }
</style>
"""


def inject_css() -> None:
    """Inyecta el CSS personalizado en la página."""
    st.markdown(CSS, unsafe_allow_html=True)
