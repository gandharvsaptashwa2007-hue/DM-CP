"""Start the playground with: python -m streamlit run app.py."""

import streamlit as st

from ui.gcd_view import render_gcd

st.set_page_config(page_title="Number Theory Playground", page_icon="🧮", layout="wide")

with st.sidebar:
    st.title("Number Theory\nPlayground")
    st.caption("UNIT 5 · FROM NUMBER THEORY TO RSA")
    st.markdown("🧮 **GCD Visualizer**")
    st.divider()
    st.markdown("**The learning path**")
    st.markdown("GCD → Modular inverse → Primes & phi → CRT → RSA")
    st.caption("Available now: Euclid’s algorithm. More experiments will follow.")

render_gcd()
