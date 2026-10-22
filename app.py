"""Start the playground with: python -m streamlit run app.py."""

import streamlit as st

from ui.gcd_view import render_gcd
from ui.inverse_view import render_inverse

st.set_page_config(page_title="Number Theory Playground", page_icon="🧮", layout="wide")

# Preserve each screen's widget values when its widgets are temporarily absent.
# Streamlit otherwise cleans up those keys on navigation, leaving old results
# paired with default inputs when the screen is reopened.
for key in ("gcd_a", "gcd_b", "gcd_preset", "inverse_a", "inverse_b", "inverse_mode", "inverse_preset"):
    if key in st.session_state:
        st.session_state[key] = st.session_state[key]

with st.sidebar:
    st.title("Number Theory\nPlayground")
    st.caption("UNIT 5 · FROM NUMBER THEORY TO RSA")
    module = st.radio("Choose a module", ("GCD Visualizer", "Extended Euclid & Inverse"), key="module")
    st.divider()
    st.markdown("**The learning path**")
    st.markdown("GCD → Modular inverse → Primes & phi → CRT → RSA")
    st.caption("Available now: GCD, extended Euclid and modular inverses.")

if module == "GCD Visualizer":
    render_gcd()
else:
    render_inverse()
