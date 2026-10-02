# -*- coding: utf-8 -*-
"""Estilos de la aplicación, alineados con la Facultad de Ciencias Sociales y Económicas (Univalle)."""

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@500;700;800&family=Source+Sans+3:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Source Sans 3', sans-serif;
    }
    h1, h2, h3, .hero h1 {
        font-family: 'Nunito', sans-serif;
    }

    .hero {
        text-align: center;
        padding: 2.1rem 2rem 1.6rem;
        background: linear-gradient(135deg, #7a1520 0%, #a51e2c 42%, #e81c25 100%);
        border-radius: 16px;
        margin-bottom: 1.5rem;
        color: #ffffff !important;
        box-shadow: 0 10px 28px rgba(165, 30, 44, 0.28);
    }
    .hero h1, .hero p, .hero span, .hero strong {
        color: #ffffff !important;
    }
    .hero h1 { margin: 0; font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; }
    .hero p  { margin: 0.75rem 0 0; opacity: 0.96; font-size: 1.05rem; }
    .hero .hero-kicker {
        display: inline-block;
        margin-bottom: 0.65rem;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.16);
        border: 1px solid rgba(243, 167, 49, 0.85);
        color: #ffe7bf !important;
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 700;
    }

    .step-card {
        background: #ffffff;
        border-left: 4px solid #e81c25;
        border-radius: 0 12px 12px 0;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 12px rgba(122, 21, 32, 0.06);
        color: #434244 !important;
    }
    .step-card h4 { margin: 0 0 0.4rem; color: #a51e2c !important; }
    .step-card p, .step-card li, .step-card span, .step-card em, .step-card code {
        color: #434244 !important;
    }
    .step-card code {
        background: #f6f1f1 !important;
        padding: 0.1em 0.35em;
        border-radius: 4px;
    }

    .context-box {
        background: #f7f5f2;
        border: 1px solid #eadfda;
        border-top: 4px solid #e81c25;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        line-height: 1.65;
        color: #434244 !important;
    }
    .context-box code {
        color: #a51e2c !important;
        background: #f3e6e7 !important;
        padding: 0.1em 0.35em;
        border-radius: 4px;
    }
    .context-box h3, .context-box h4, .context-box p, .context-box li,
    .context-box span, .context-box strong, .context-box em {
        color: #434244 !important;
    }
    .context-box h3 { color: #7a1520 !important; }
    .context-box h4 {
        margin: 1rem 0 0.4rem;
        font-size: 1rem;
        color: #a51e2c !important;
    }

    .interpret-box {
        background: #f4fbfb;
        border: 1px solid #c5e4e3;
        border-left: 4px solid #008687;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        line-height: 1.55;
        color: #434244 !important;
    }
    .interpret-box ol, .interpret-box ul {
        margin: 0.35rem 0 0.75rem 1.1rem;
        padding-left: 1rem;
    }
    .interpret-box p, .interpret-box li,
    .interpret-box span, .interpret-box strong, .interpret-box em {
        color: #434244 !important;
    }
    .interpret-box li { margin-bottom: 0.35rem; line-height: 1.5; }
    .interpret-box code {
        color: #016cb6 !important;
        background: #e7f2f8 !important;
        padding: 0.12em 0.4em;
        border-radius: 4px;
        font-size: 0.88em;
    }

    .reflection-box {
        background: linear-gradient(145deg, #fff8ec, #fdecc8);
        border: 1px solid #f3a731;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
        color: #4a3208 !important;
    }
    .reflection-box h3, .reflection-box p, .reflection-box li,
    .reflection-box span, .reflection-box strong {
        color: #4a3208 !important;
    }

    .math-box {
        background: #f7f5f2;
        border: 1px solid #e2d9d4;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0 1.5rem 0;
        line-height: 1.65;
        color: #434244 !important;
    }
    .math-box h3, .math-box h4, .math-box p, .math-box li,
    .math-box span, .math-box strong, .math-box em {
        color: #434244 !important;
    }
    .math-box h3 { color: #7a1520 !important; }
    .math-box code {
        color: #a51e2c !important;
        background: #f3e6e7 !important;
        padding: 0.1em 0.35em;
        border-radius: 4px;
    }

    .pair-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.15rem 0.4rem;
        border: 1px solid #eadfda;
        box-shadow: 0 2px 10px rgba(67, 66, 68, 0.05);
        height: 100%;
    }
    .pair-card h3 { margin-top: 0; color: #a51e2c !important; }

    .stApp[data-theme="light"] div[data-testid="stSidebar"],
    .stApp:not([data-theme="dark"]) div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fff 0%, #f7f1f1 100%);
        border-right: 3px solid #e81c25;
    }

    .stApp[data-theme="dark"] .step-card {
        background: #2a2424;
        border-left-color: #e81c25;
        box-shadow: 0 2px 12px rgba(0,0,0,0.35);
        color: #f3f3f3 !important;
    }
    .stApp[data-theme="dark"] .step-card h4 { color: #ffb4b8 !important; }
    .stApp[data-theme="dark"] .step-card p,
    .stApp[data-theme="dark"] .step-card li,
    .stApp[data-theme="dark"] .step-card span,
    .stApp[data-theme="dark"] .step-card em { color: #e7e2e2 !important; }
    .stApp[data-theme="dark"] .step-card code {
        color: #ffd089 !important;
        background: #1c1717 !important;
    }

    .stApp[data-theme="dark"] .context-box {
        background: #2a2424;
        border-color: #5c403f;
        color: #f3f3f3 !important;
    }
    .stApp[data-theme="dark"] .context-box h3,
    .stApp[data-theme="dark"] .context-box h4,
    .stApp[data-theme="dark"] .context-box p,
    .stApp[data-theme="dark"] .context-box li,
    .stApp[data-theme="dark"] .context-box span,
    .stApp[data-theme="dark"] .context-box strong,
    .stApp[data-theme="dark"] .context-box em { color: #f3f3f3 !important; }
    .stApp[data-theme="dark"] .context-box code {
        color: #ffd089 !important;
        background: #7a1520 !important;
    }

    .stApp[data-theme="dark"] .interpret-box {
        background: #163233;
        border-color: #008687;
        color: #f3f3f3 !important;
    }
    .stApp[data-theme="dark"] .interpret-box p,
    .stApp[data-theme="dark"] .interpret-box li,
    .stApp[data-theme="dark"] .interpret-box ul,
    .stApp[data-theme="dark"] .interpret-box ol,
    .stApp[data-theme="dark"] .interpret-box span,
    .stApp[data-theme="dark"] .interpret-box strong,
    .stApp[data-theme="dark"] .interpret-box em { color: #f3f3f3 !important; }
    .stApp[data-theme="dark"] .interpret-box code {
        color: #9ad7f5 !important;
        background: #01405f !important;
    }

    .stApp[data-theme="dark"] .reflection-box {
        background: linear-gradient(145deg, #3a2a12, #2a2118);
        border-color: #f3a731;
        color: #ffe7bf !important;
    }
    .stApp[data-theme="dark"] .reflection-box h3,
    .stApp[data-theme="dark"] .reflection-box p,
    .stApp[data-theme="dark"] .reflection-box li,
    .stApp[data-theme="dark"] .reflection-box span,
    .stApp[data-theme="dark"] .reflection-box strong { color: #ffe7bf !important; }

    .stApp[data-theme="dark"] .math-box {
        background: #2a2424;
        border-color: #5c403f;
        color: #f3f3f3 !important;
    }
    .stApp[data-theme="dark"] .math-box h3,
    .stApp[data-theme="dark"] .math-box h4,
    .stApp[data-theme="dark"] .math-box p,
    .stApp[data-theme="dark"] .math-box li,
    .stApp[data-theme="dark"] .math-box span,
    .stApp[data-theme="dark"] .math-box strong,
    .stApp[data-theme="dark"] .math-box em { color: #f3f3f3 !important; }
    .stApp[data-theme="dark"] .math-box code {
        color: #ffd089 !important;
        background: #7a1520 !important;
    }

    .stApp[data-theme="dark"] .pair-card {
        background: #2a2424;
        border-color: #5c403f;
    }
    .stApp[data-theme="dark"] div[data-testid="stSidebar"] {
        background: var(--secondary-background-color) !important;
        border-right: 3px solid #e81c25;
    }
    .stApp[data-theme="dark"] .stCaption,
    .stApp[data-theme="dark"] [data-testid="stCaptionContainer"] {
        color: #c8c4c4 !important;
    }
</style>
"""


def apply_styles():
    import streamlit as st

    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_hero(title: str, subtitle: str, kicker: str = ""):
    import streamlit as st

    kicker_html = f'<div class="hero-kicker">{kicker}</div>' if kicker else ""
    st.markdown(
        f"""
<div class="hero">
    {kicker_html}
    <h1>{title}</h1>
    <p>{subtitle}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_interpret_box(html_content: str):
    import streamlit as st

    st.markdown(f'<div class="interpret-box">{html_content}</div>', unsafe_allow_html=True)
