"""Extended Euclid and modular inverse, with forward and backward traces."""

import streamlit as st

from core import extended_gcd, modular_inverse
from core.back_substitution import back_substitute
from ui.inputs import parse_integer

MODES = ("Modular inverse", "Extended Euclid")
PRESETS = {
    "RSA example · 17 mod 3120": (17, 3120, MODES[0]),
    "No inverse · 6 mod 9": (6, 9, MODES[0]),
    "Negative number · −3 mod 11": (-3, 11, MODES[0]),
    "Bézout identity · 252 and 105": (252, 105, MODES[1]),
    "Signed inputs · −252 and −105": (-252, -105, MODES[1]),
    "Zero input · 42 and 0": (42, 0, MODES[1]),
    "Both zero · 0 and 0": (0, 0, MODES[1]),
}


def clear_result():
    st.session_state.inverse_result = None
    st.session_state.inverse_value = None
    st.session_state.inverse_error = None
    st.session_state.inverse_position = 0


def load_example():
    a, b, mode = PRESETS[st.session_state.inverse_preset]
    st.session_state.inverse_a = str(a)
    st.session_state.inverse_b = str(b)
    st.session_state.inverse_mode = mode
    clear_result()


def calculate():
    clear_result()
    try:
        a = parse_integer(st.session_state.inverse_a, "First integer")
        b = parse_integer(st.session_state.inverse_b, "Second integer / modulus")
        if st.session_state.inverse_mode == MODES[0] and b <= 1:
            raise ValueError("Modulus must be greater than 1. Use Extended Euclid mode for zero or negative second inputs.")
    except ValueError as error:
        st.session_state.inverse_error = str(error)
        return
    result = extended_gcd(a, b)
    st.session_state.inverse_result = result
    if st.session_state.inverse_mode == MODES[0] and result.value == 1:
        st.session_state.inverse_value = modular_inverse(a, b).value


def move(position):
    st.session_state.inverse_position = position


def expression(terms, remainders):
    return " + ".join(f"({coefficient}) × {remainders[index]}" for index, coefficient in terms) or "0"


def render_inverse(theory):
    for key, value in {
        "inverse_a": "17", "inverse_b": "3120", "inverse_mode": MODES[0],
        "inverse_result": None, "inverse_value": None, "inverse_error": None,
        "inverse_position": 0,
    }.items():
        st.session_state.setdefault(key, value)

    st.caption("EXPERIMENT 02 / EXTENDED EUCLID & MODULAR INVERSE")
    st.title("Find the numbers behind the GCD")
    st.write("Express the GCD as a combination of your inputs, then discover when that identity gives a modular inverse.")
    left, right = st.container(), theory
    with left, st.container(border=True):
        st.selectbox("Example", list(PRESETS), key="inverse_preset")
        st.button("Load example", key="inverse_load", on_click=load_example)
        st.radio("Calculation", MODES, key="inverse_mode", on_change=clear_result)
        st.text_input("First integer (a)", key="inverse_a", max_chars=22, on_change=clear_result)
        st.text_input("Second integer (b) / modulus (m)", key="inverse_b", max_chars=22, on_change=clear_result)
        st.caption("Exact whole numbers within ±10¹⁸. Inverse mode requires m > 1.")
        st.button("Calculate", key="inverse_calculate", type="primary", on_click=calculate)
        if st.session_state.inverse_error:
            st.error(st.session_state.inverse_error)
    with right:
        with st.container():
            st.subheader("How do coefficients lead to an inverse?")
            st.latex(r"ax + by = \gcd(a,b)")
            st.write("Extended Euclid tracks coefficients x and y alongside the usual divisions. At every step, the remainder is still a combination of the original signed inputs.")
            st.latex(r"ax + my = 1 \quad\Longrightarrow\quad ax \equiv 1 \pmod m")
            st.write("When the GCD is 1, reduce x modulo m to get the inverse. If the GCD is greater than 1, there is no inverse. The GCD and Bézout identity are still valid results.")
        st.info("RSA connection: setting a = e and m = φ(n) gives the private exponent d = e⁻¹ mod φ(n).")

    result = st.session_state.inverse_result
    if result is None:
        st.info("Load an example or enter two integers, then select Calculate.")
        return
    st.divider()
    st.caption(f"Original inputs: a = {result.a}, b = {result.b}. Divisions use |a| = {abs(result.a)} and |b| = {abs(result.b)}; coefficients use the original signs.")
    position = st.session_state.inverse_position
    count = len(result.steps)
    if count:
        step = result.steps[position]
        st.subheader("Forward calculation")
        st.progress((position + 1) / count, text=f"Division {position + 1} of {count}")
        st.latex(rf"{step.dividend} = {step.divisor} \times {step.quotient} + {step.remainder}")
        st.code(f"{step.remainder} = ({result.a}) × ({step.x}) + ({result.b}) × ({step.y})", language=None)
        st.caption("For each new remainder: new coefficient = dividend coefficient − quotient × divisor coefficient. The terminal zero row is not the final Bézout coefficient pair.")
        controls = st.columns(4)
        controls[0].button("Previous", key="inverse_previous", disabled=position == 0, on_click=move, args=(position - 1,))
        controls[1].button("Next step", key="inverse_next", disabled=position == count - 1, on_click=move, args=(position + 1,))
        controls[2].button("Show all steps", key="inverse_show_all", on_click=move, args=(count - 1,))
        controls[3].button("Start over", key="inverse_restart", on_click=move, args=(0,))
        rows = [
            {"Row": "Initial |a|", "Remainder": str(abs(result.a)), "Quotient": "—", "x": str(-1 if result.a < 0 else 1), "y": "0"},
            {"Row": "Initial |b|", "Remainder": str(abs(result.b)), "Quotient": "—", "x": "0", "y": str(-1 if result.b < 0 else 1)},
        ]
        rows.extend({"Row": f"Division {i + 1}", "Remainder": str(s.remainder), "Quotient": str(s.quotient), "x": str(s.x), "y": str(s.y)} for i, s in enumerate(result.steps[:position + 1]))
        st.table(rows)
    else:
        st.info("The second working value is zero, so no division steps are needed.")

    if not count or position == count - 1:
        st.subheader("Bézout identity")
        st.metric("Greatest common divisor", str(result.value))
        st.code(f"({result.a}) × ({result.x}) + ({result.b}) × ({result.y}) = {result.value}", language=None)
        if result.a == result.b == 0:
            st.info("We use gcd(0, 0) = 0 by programming convention, with x = y = 0. There is no greatest positive common divisor.")
        if st.session_state.inverse_mode == MODES[0]:
            if result.value == 1:
                inverse = st.session_state.inverse_value
                st.metric("Modular inverse", str(inverse))
                st.code(f"x mod m = {result.x} mod {result.b} = {inverse}\nCheck: ({result.a} × {inverse}) mod {result.b} = {(result.a * inverse) % result.b}", language=None)
                st.success(f"The inverse of {result.a} modulo {result.b} is {inverse}.")
            else:
                st.warning(f"No modular inverse exists: gcd({result.a}, {result.b}) = {result.value}, not 1. Every combination a×x + m×y is divisible by {result.value}, so it cannot equal 1.")
        with st.expander("Back-substitution: work backwards to the original inputs", expanded=True):
            trace = back_substitute(result)
            st.write("Start with the GCD (the last nonzero remainder). Replace each remainder using an earlier division, then collect coefficients. These substitutions use absolute input values; the final identity restores the original signs.")
            st.code(f"{result.value} = {expression(trace.initial, trace.remainders)}", language=None)
            for index, substitution in enumerate(trace.steps, 1):
                j = substitution.index
                st.markdown(f"**Substitution {index}**")
                st.code(f"Replace {trace.remainders[j]} with {trace.remainders[j - 2]} − {substitution.quotient} × {trace.remainders[j - 1]}\n{result.value} = {expression(substitution.before, trace.remainders)}\n{result.value} = {expression(substitution.after, trace.remainders)}", language=None)
            if not trace.steps:
                st.write("The GCD is already an original working value (or both inputs are zero); no substitutions are needed.")
            st.code(f"Original signs: {result.value} = ({result.a}) × ({trace.x}) + ({result.b}) × ({trace.y})", language=None)
    st.button("Reset calculation", key="inverse_reset", on_click=clear_result)
