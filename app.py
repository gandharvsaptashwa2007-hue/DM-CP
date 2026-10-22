"""Start the playground with: python -m streamlit run app.py."""

import streamlit as st

from ui.gcd_view import render_gcd
from ui.inverse_view import render_inverse
from ui.primality_view import render_primality
from ui.totient_view import render_totient
from ui.crt_view import render_crt
from ui.rsa_view import render_rsa
from ui.attack_view import render_attack

st.set_page_config(page_title="Number Theory Playground", page_icon="🧮", layout="wide")

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
    module = st.radio("Choose a module", ("GCD Visualizer", "Extended Euclid & Inverse", "Primality Tester", "Euler’s Phi", "CRT Solver", "RSA Lab", "Break the Key"), key="module")
    st.divider()
    st.markdown("**The learning path**")
    st.markdown("GCD → Modular inverse → Primes & phi → CRT → RSA")
    st.caption("Explore seven experiments, from Euclid’s algorithm to RSA and small-key recovery.")

if module == "GCD Visualizer":
    render_gcd()
elif module == "Extended Euclid & Inverse":
    render_inverse()
elif module == "Primality Tester":
    render_primality()
elif module == "Euler’s Phi":
    render_totient()
elif module == "CRT Solver":
    render_crt()
elif module == "RSA Lab":
    render_rsa()
else:
    render_attack()
