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
from ui.tour import render_tour
from ui.visuals import brand as render_brand, illustration, loading_placeholder, empty_workspace, not_found
from ui.design import MODULES, apply_design, dashboard, results_pane, navigate, travel, choose_page

st.set_page_config(page_title="Modular Minds", page_icon="🧮", layout="wide")
apply_design()
routes = {"home": "Home", **{data[0]: name for name, data in MODULES.items()}}
requested = st.query_params.get("page", "home")
if requested not in routes:
    not_found()
    st.stop()
if "module" not in st.session_state:
    st.session_state.module = routes[requested]
for key in list(st.session_state):
    if key.startswith(("challenge_answer_", "challenge_hint_", "challenge_solution_", "explore_")):
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
brand, controls = st.columns([1, 2], gap="medium", vertical_alignment="center")
with brand, st.container(key="brand_home"):
    render_brand()
    st.button("Modular Minds — Home", key="page_home", on_click=navigate, args=("Home",), use_container_width=True)

with controls, st.container(key="page_navigation"):
    location, appearance, previous, following = st.columns([5, 3, 1, 1], vertical_alignment="center")
    appearance.selectbox("Appearance", ("Device", "Light", "Dark"), key="color_mode", label_visibility="collapsed", help="Device follows your system’s color preference automatically.")
    index = st.session_state.page_cursor
    previous.button("←", key="page_previous", disabled=index == 0,
                    on_click=travel, args=(-1,), use_container_width=True, help="Back to previous visit")
    location.selectbox("Page", pages, key="page_picker", on_change=choose_page, label_visibility="collapsed")
    following.button("→", key="page_next", disabled=index == len(st.session_state.page_visits) - 1,
                     on_click=travel, args=(1,), use_container_width=True, help="Forward to next visit")

loading = loading_placeholder()
if module == "Home":
    st.html('<div class="math-banner"><span>THE BEAUTY OF NUMBERS</span><h2>Explore the patterns.<br>Unlock the possibilities.</h2><p>From a simple remainder to the mathematics of RSA.</p></div>')
    dashboard()
else:
    workspace, history = st.columns([7, 3], gap="large")
    with history:
        theory = st.container(key="theory_panel")
    with theory:
        illustration(MODULES[module][0])
    with workspace, st.container(key="workspace"):
        {"GCD Visualizer": render_gcd, "Extended Euclid & Inverse": render_inverse,
         "Primality Tester": render_primality, "Euler’s Phi": render_totient,
         "CRT Solver": render_crt, "RSA Lab": render_rsa,
         "Break the Key": render_attack}[module](theory)
        empty_workspace(MODULES[module][0])
    with theory:
        render_explanation_play(module, MODULES[module][0])
    with history:
        results_pane(module)
loading.empty()
st.html('<footer class="site-footer" aria-label="Site footer">Modular Minds</footer>')
render_tour(module)
