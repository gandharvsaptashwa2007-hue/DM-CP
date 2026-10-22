"""Euler's phi from prime factors, with a small-number coprime illustration."""

from math import gcd

import streamlit as st

from core import totient
from core.primality import DEFAULT_BUDGET, TRIAL_LIMIT
from ui.inputs import parse_integer
from ui.playback import playback

PRESETS = {"Composite · 36": 36, "Prime · 13": 13, "Prime power · 81": 81,
           "RSA modulus · 3233": 3233, "Special case · 1": 1}


def clear_result():
    st.session_state.phi_result = None
    st.session_state.phi_error = None
    st.session_state.phi_position = 0


def load_example():
    st.session_state.phi_n = str(PRESETS[st.session_state.phi_preset])
    clear_result()


def calculate():
    clear_result()
    try:
        n = parse_integer(st.session_state.phi_n, "Number", limit=TRIAL_LIMIT)
        st.session_state.phi_result = totient(n, st.session_state.phi_budget)
    except (ValueError, TypeError) as error:
        st.session_state.phi_error = str(error)


def factor_expression(factors):
    return " × ".join(str(p) if exponent == 1 else f"{p}^{exponent}" for p, exponent in factors) or "1"


def render_totient():
    for key, value in {"phi_n": "36", "phi_budget": DEFAULT_BUDGET, "phi_result": None,
                       "phi_error": None, "phi_position": 0}.items():
        st.session_state.setdefault(key, value)
    st.caption("EXPERIMENT 04 / EULER’S TOTIENT")
    st.title("Count the numbers coprime to n")
    st.write("Factor your number, use each distinct prime once, and watch Euler’s phi formula take shape.")
    left, right = st.columns([2, 3], gap="large")
    with left, st.container(border=True):
        st.selectbox("Example", list(PRESETS), key="phi_preset")
        st.button("Load example", key="phi_load", on_click=load_example)
        st.text_input("Positive integer (n)", key="phi_n", max_chars=22, on_change=clear_result)
        st.caption("Accepts 1 ≤ n ≤ 10¹².")
        with st.expander("Factorization work limit"):
            st.number_input("Maximum divisibility checks", min_value=1, max_value=DEFAULT_BUDGET,
                            key="phi_budget", on_change=clear_result)
            st.caption("An unfinished factorization leaves φ(n) unresolved. No partial result is reported as the answer.")
        st.button("Calculate phi", key="phi_calculate", type="primary", on_click=calculate)
        if st.session_state.phi_error:
            st.error(st.session_state.phi_error)
    with right:
        with st.expander("Why does the prime-factor formula work?", expanded=True):
            st.latex(r"\varphi(n) = n\prod_{p\mid n}\left(1-\frac{1}{p}\right)")
            st.write("A number is coprime to n if it shares none of n's prime factors. The product counts the integers remaining after multiples of each distinct prime are excluded, accounting for overlaps. A repeated prime factor is used only once in the product.")
            st.write("The calculation uses result ÷ p × (p−1) with exact integers. φ(1) = 1 by convention, consistent with gcd(1,1) = 1.")
        st.info("RSA connection: if n = p×q for distinct primes, the formula becomes φ(n) = (p−1)(q−1).")
    result = st.session_state.phi_result
    if result is None:
        st.info("Choose an example or enter a positive integer, then select Calculate phi.")
        return
    st.divider()
    st.caption(f"Input: n = {result.n}. Divisibility checks performed: {result.attempts}.")
    st.subheader("1. Prime factorization")
    suffix = f" × {result.unresolved} (unresolved cofactor)" if not result.complete else ""
    st.code(f"{result.n} = {factor_expression(result.factors)}{suffix}", language=None)
    if result.factor_steps:
        st.table([{"Before": str(s.before), "Prime factor": str(s.prime), "After division": str(s.after), "Reason": s.reason} for s in result.factor_steps])
    if not result.complete:
        st.warning(f"Factorization stopped at the work limit. Cofactor {result.unresolved} remains unresolved; φ({result.n}) has not been calculated.")
        st.button("Reset calculation", key="phi_reset", on_click=clear_result)
        return
    st.subheader("2. Apply each distinct prime once")
    if result.steps:
        st.code(f"φ({result.n}) = {result.n} × " + " × ".join(f"(1 − 1/{p})" for p, _ in result.factors), language=None)
        position = playback("phi", len(result.steps), "Prime factor")
        step = result.steps[position]
        st.code(f"Prime {step.prime}: {step.before} ÷ {step.prime} × ({step.prime} − 1) = {step.after}", language=None)
        st.table([{"Prime": str(s.prime), "Before": str(s.before), "After": str(s.after)} for s in result.steps[:position + 1]])
        finished = position == len(result.steps) - 1
    else:
        st.write("1 has no prime factors, so the empty product leaves the starting value 1 unchanged.")
        finished = True
    if finished:
        st.metric("Euler's phi", str(result.value))
        if len(result.factors) == 2 and all(exponent == 1 for _, exponent in result.factors):
            p, q = (prime for prime, _ in result.factors)
            st.success(f"Two distinct primes: ({p}−1) × ({q}−1) = {result.value}. This is the RSA totient formula.")
        if result.n <= 100:
            coprimes = [k for k in range(1, result.n + 1) if gcd(k, result.n) == 1]
            st.subheader("3. Verify by counting coprimes")
            st.write(f"In 1 through {result.n}, these {len(coprimes)} integers have GCD 1 with {result.n}:")
            st.code(", ".join(map(str, coprimes)), language=None)
        else:
            st.caption("The explicit coprime list is limited to n ≤ 100 to keep the display readable.")
    st.button("Reset calculation", key="phi_reset", on_click=clear_result)
