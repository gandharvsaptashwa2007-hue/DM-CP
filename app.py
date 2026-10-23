"""Start the playground with: python -m streamlit run app.py."""

import streamlit as st

from ui.gcd_view import render_gcd
from ui.inverse_view import render_inverse
from ui.primality_view import render_primality
from ui.totient_view import render_totient
from ui.crt_view import render_crt
from ui.rsa_view import render_rsa
from ui.attack_view import render_attack
from ui.design import MODULES, apply_design, dashboard, results_pane

st.set_page_config(page_title="Number Theory Playground", page_icon="🧮", layout="wide")
apply_design()

# Preserve each screen's widget values when its widgets are temporarily absent.
# Streamlit otherwise cleans up those keys on navigation, leaving old results
# paired with default inputs when the screen is reopened.
widget_keys = ("gcd_a", "gcd_b", "gcd_preset", "inverse_a", "inverse_b", "inverse_mode", "inverse_preset",
               "prime_n", "prime_method", "prime_preset", "prime_budget", "phi_n", "phi_preset", "phi_budget",
               "crt_count", "crt_preset", "rsa_p", "rsa_q", "rsa_e", "rsa_size", "rsa_mode", "rsa_message",
               "rsa_ciphertext", "rsa_trace_kind", "rsa_trace_block", "attack_e", "attack_n", "attack_ciphertext",
               "attack_mode", "attack_budget", "attack_preset")
for key in (*widget_keys, *(f"crt_{field}_{i}" for field in ("a", "m") for i in range(6))):
    if key in st.session_state:
        st.session_state[key] = st.session_state[key]

with st.sidebar:
    st.title("Number Theory\nPlayground")
    st.caption("UNIT 5 · FROM NUMBER THEORY TO RSA")
    module = st.radio("Choose a module", ("Home", *MODULES), key="module")
    st.divider()
    st.markdown("**The learning path**")
    st.markdown("GCD → Modular inverse → Primes & phi → CRT → RSA")
    st.caption("Explore seven experiments, from Euclid’s algorithm to RSA and small-key recovery.")

if module == "Home":
    dashboard()
else:
    st.caption(f"PLAYGROUND / {module.upper()}")
    workspace, history = st.columns([7, 3], gap="large")
    with workspace, st.container(key="workspace"):
        {"GCD Visualizer": render_gcd, "Extended Euclid & Inverse": render_inverse,
         "Primality Tester": render_primality, "Euler’s Phi": render_totient,
         "CRT Solver": render_crt, "RSA Lab": render_rsa,
         "Break the Key": render_attack}[module]()
    with history:
        results_pane(module)
