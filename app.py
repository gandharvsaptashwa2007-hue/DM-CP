"""Start the playground with: python -m streamlit run app.py."""

import streamlit as st

from ui.gcd_view import render_gcd
from ui.inverse_view import render_inverse
from ui.primality_view import render_primality
from ui.totient_view import render_totient
from ui.crt_view import render_crt
from ui.rsa_view import render_rsa
from ui.attack_view import render_attack
from ui.explanation_play import render_explanation_play
from ui.design import MODULES, apply_design, dashboard, results_pane, navigate, travel, choose_page

st.set_page_config(page_title="Modular Minds", page_icon="🧮", layout="wide")
apply_design()
for key in list(st.session_state):
    if key.startswith(("challenge_", "explore_")):
        st.session_state[key] = st.session_state[key]

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

pages = ("Home", *MODULES)
module = st.session_state.setdefault("module", "Home")
navigate(module)
brand, controls = st.columns([1, 1], gap="medium")
with brand:
    st.html('<div class="brand"><h1>Modular Minds</h1><p>Explore · Experiment · Understand</p></div>')

with controls, st.container(key="page_navigation"):
    location, home, previous, following = st.columns([8, 1, 1, 1])
    index = st.session_state.page_cursor
    previous.button("←", key="page_previous", disabled=index == 0,
                    on_click=travel, args=(-1,), use_container_width=True, help="Back to previous visit")
    location.selectbox("Page", pages, key="page_picker", on_change=choose_page, label_visibility="collapsed")
    home.button("Home", key="page_home", disabled=module == "Home", on_click=navigate, args=("Home",), use_container_width=True)
    following.button("→", key="page_next", disabled=index == len(st.session_state.page_visits) - 1,
                     on_click=travel, args=(1,), use_container_width=True, help="Forward to next visit")

if module == "Home":
    dashboard()
else:
    workspace, history = st.columns([7, 3], gap="large")
    with history:
        theory = st.container(key="theory_panel")
    with workspace, st.container(key="workspace"):
        {"GCD Visualizer": render_gcd, "Extended Euclid & Inverse": render_inverse,
         "Primality Tester": render_primality, "Euler’s Phi": render_totient,
         "CRT Solver": render_crt, "RSA Lab": render_rsa,
         "Break the Key": render_attack}[module](theory)
    with theory:
        render_explanation_play(module, MODULES[module][0])
    with history:
        results_pane(module)
