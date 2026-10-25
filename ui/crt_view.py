"""CRT input rows, inverse traces and final congruence verification."""

from math import gcd

import streamlit as st

from core import solve_crt
from ui.inputs import parse_integer
from ui.playback import playback

PRESETS = {
    "Classic · 23 modulo 105": ((2, 3), (3, 5), (2, 7)),
    "Normalize negative residues": ((-1, 3), (8, 5)),
    "Six equations": ((1, 2), (2, 3), (3, 5), (4, 7), (5, 11), (6, 13)),
    "Unsupported non-coprime moduli": ((1, 4), (3, 6)),
}


def clear_result():
    st.session_state.crt_result = None
    st.session_state.crt_error = None
    st.session_state.crt_position = 0


def load_example():
    equations = PRESETS[st.session_state.crt_preset]
    st.session_state.crt_count = len(equations)
    for index, (residue, modulus) in enumerate(equations):
        st.session_state[f"crt_a_{index}"] = str(residue)
        st.session_state[f"crt_m_{index}"] = str(modulus)
    clear_result()


def calculate():
    clear_result()
    try:
        equations = [
            (parse_integer(st.session_state[f"crt_a_{i}"], f"Residue {i + 1}"),
             parse_integer(st.session_state[f"crt_m_{i}"], f"Modulus {i + 1}", limit=10**6))
            for i in range(st.session_state.crt_count)
        ]
        st.session_state.crt_result = solve_crt(equations)
    except (TypeError, ValueError) as error:
        st.session_state.crt_error = str(error)


def render_crt(theory):
    for key, value in {"crt_count": 3, "crt_result": None, "crt_error": None, "crt_position": 0}.items():
        st.session_state.setdefault(key, value)
    for index, (residue, modulus) in enumerate(((2, 3), (3, 5), (2, 7), (1, 11), (1, 13), (1, 17))):
        st.session_state.setdefault(f"crt_a_{index}", str(residue))
        st.session_state.setdefault(f"crt_m_{index}", str(modulus))
    st.caption("EXPERIMENT 05 / CHINESE REMAINDER THEOREM")
    st.title("One number, several remainders")
    st.write("Combine congruences into a single solution and verify it against every original condition.")
    left, right = st.container(), theory
    with left, st.container(border=True):
        example, load = st.columns([3, 2], vertical_alignment="bottom")
        example.selectbox("Example", list(PRESETS), key="crt_preset")
        load.button("Load example", key="crt_load", on_click=load_example)
        st.number_input("Number of equations", min_value=2, max_value=6, key="crt_count", on_change=clear_result)
        for i in range(st.session_state.crt_count):
            st.caption(f"Equation {i + 1}: x ≡ residue (mod modulus)")
            a, m = st.columns(2)
            a.text_input(f"Residue {i + 1}", key=f"crt_a_{i}", max_chars=22, on_change=clear_result)
            m.text_input(f"Modulus {i + 1}", key=f"crt_m_{i}", max_chars=10, on_change=clear_result)
        st.caption("Residues within ±10¹⁸; pairwise coprime moduli from 2 to 1,000,000.")
        st.button("Solve system", key="crt_calculate", type="primary", on_click=calculate)
        if st.session_state.crt_error:
            st.error(st.session_state.crt_error)
    with right:
        with st.container():
            st.subheader("How the pieces combine")
            st.latex(r"N=\prod_i m_i,\quad N_i=N/m_i,\quad y_i=N_i^{-1}\pmod{m_i}")
            st.latex(r"x=\left(\sum_i a_iN_iy_i\right)\bmod N")
            st.write("Nᵢ is divisible by every other modulus. Multiplying it by its inverse modulo mᵢ makes it equal to 1 for this equation and 0 for the others. Each term therefore contributes exactly its own residue.")
            st.write("Pairwise coprime moduli guarantee one solution modulo N. Non-coprime systems need generalized CRT, which this screen does not implement.")
        st.info("RSA connection: CRT can recombine the decrypted residues modulo p and q into a message modulo n = p×q.")
    result = st.session_state.crt_result
    if result is None:
        return
    st.divider()
    st.subheader("1. Normalize and check")
    st.table([{"Original residue": str(s.original_residue), "Modulus": str(s.modulus), "Normalized residue": str(s.residue)} for s in result.steps])
    with st.expander("Pairwise GCD checks"):
        st.table([{"Moduli": f"{a.modulus}, {b.modulus}", "GCD": str(gcd(a.modulus, b.modulus))}
                  for i, a in enumerate(result.steps) for b in result.steps[i + 1:]])
    st.code(f"N = {' × '.join(str(s.modulus) for s in result.steps)} = {result.period}", language=None)
    st.subheader("2. Construct each contribution")
    position = playback("crt", len(result.steps), "Equation")
    step = result.steps[position]
    st.code(f"Nᵢ = {result.period} ÷ {step.modulus} = {step.partial_product}\nyᵢ = {step.partial_product}⁻¹ mod {step.modulus} = {step.inverse.value}\nContribution = {step.residue} × {step.partial_product} × {step.inverse.value} = {step.contribution}", language=None)
    with st.expander("Why this inverse works"):
        euclid = step.inverse.euclid
        st.code(f"{euclid.a} × ({euclid.x}) + {euclid.b} × ({euclid.y}) = 1\n{step.partial_product} × {step.inverse.value} mod {step.modulus} = 1", language=None)
    st.table([{"Residue": str(s.residue), "Nᵢ": str(s.partial_product), "Inverse": str(s.inverse.value), "Contribution": str(s.contribution)} for s in result.steps[:position + 1]])
    if position == len(result.steps) - 1:
        st.subheader("3. Combine and verify")
        st.code(f"x = {result.total} mod {result.period} = {result.value}\nAll solutions: x = {result.value} + k × {result.period}, for any integer k.", language=None)
        st.metric("Smallest nonnegative solution", str(result.value))
        st.metric("Solution period", str(result.period))
        st.table([{"Condition": f"x ≡ {s.original_residue} (mod {s.modulus})", "Computed remainder": str(result.value % s.modulus), "Expected normalized remainder": str(s.residue), "Verified": result.value % s.modulus == s.residue} for s in result.steps])
    st.button("Reset calculation", key="crt_reset", on_click=clear_result)
