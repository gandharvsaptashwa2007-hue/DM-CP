"""Original inline vector artwork and application feedback states."""
import streamlit as st
from base64 import b64encode

def svg_image(svg, alt):
    data = b64encode(svg.encode()).decode()
    return f'<img src="data:image/svg+xml;base64,{data}" alt="{alt}" />'

LOGO = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Modular Minds logo"><rect width="64" height="64" rx="18" fill="#4F46E5"/><path d="M14 44V22l18 18 18-18v22" fill="none" stroke="white" stroke-width="5" stroke-linejoin="round"/><circle cx="50" cy="16" r="6" fill="#14B8A6"/></svg>'''

def brand():
    st.html(f'<div class="brand-lockup">{svg_image(LOGO, "Modular Minds logo")}<div class="brand"><h1>Modular Minds</h1><p>Explore · Experiment · Understand</p></div></div>')

def illustration(slug):
    motifs = {
        "home": ("÷", "≡", "RSA"), "gcd": ("a", "b", "r"),
        "inverse": ("a", "×", "1"), "prime": ("2", "3", "5"),
        "phi": ("n", "φ", "1"), "crt": ("m₁", "m₂", "x"),
        "rsa": ("m", "e", "c"), "attack": ("n", "p", "q"),
    }
    labels = motifs[slug]
    nodes = ''.join(f'<circle cx="{65+i*100}" cy="55" r="28" fill="{color}"/><text x="{65+i*100}" y="62" text-anchor="middle" fill="white" font-family="sans-serif" font-size="18">{label}</text>' for i, (label, color) in enumerate(zip(labels, ("#4F46E5", "#0F766E", "#4F46E5"))))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 110"><path d="M65 55H265" stroke="#A5B4FC" stroke-width="3" stroke-dasharray="5 6"/>{nodes}</svg>'
    st.html(f'<div class="math-art">{svg_image(svg, slug + " mathematical symbols")}</div>')

def loading_placeholder():
    slot = st.empty()
    slot.markdown('<div class="loading-skeleton" role="status" aria-label="Loading workspace"><div></div><div></div><div></div></div>', unsafe_allow_html=True)
    return slot

def empty_workspace(slug):
    keys = ("rsa_keys",) if slug == "rsa" else (f"{slug}_result",)
    if not any(st.session_state.get(key) is not None for key in keys):
        st.html('<div class="workspace-empty"><b>Ready to explore?</b><p>Load an example or enter your own values, then use the main action above. Your calculation steps will appear here.</p></div>')

def recover_home():
    from ui.design import navigate
    st.query_params.clear()
    navigate("Home")

def not_found():
    brand()
    st.html('<div class="not-found"><span>404</span><h2>This page wandered off the number line.</h2><p>Return to the dashboard to choose one of the seven experiments.</p></div>')
    st.button("Return to dashboard", type="primary", on_click=recover_home, key="recover_home")
