"""Interactive Euclidean algorithm with session-local playback."""

import streamlit as st

from core import gcd
from ui.inputs import parse_integer

PRESETS = {
    "Classic example · 252 and 105": (252, 105),
    "Coprime numbers · 17 and 31": (17, 31),
    "Negative input · −252 and 105": (-252, 105),
    "Zero input · 42 and 0": (42, 0),
    "Both zero · 0 and 0": (0, 0),
}


def clear_result() -> None:
    st.session_state.gcd_result = None
    st.session_state.gcd_position = 0
    st.session_state.gcd_error = None


def load_example() -> None:
    a, b = PRESETS[st.session_state.gcd_preset]
    st.session_state.gcd_a = str(a)
    st.session_state.gcd_b = str(b)
    clear_result()


def calculate() -> None:
    clear_result()
    try:
        a = parse_integer(st.session_state.gcd_a, "First integer")
        b = parse_integer(st.session_state.gcd_b, "Second integer")
    except ValueError as error:
        st.session_state.gcd_error = str(error)
        return
    st.session_state.gcd_result = gcd(a, b)


def move(position: int) -> None:
    st.session_state.gcd_position = position


def render_gcd() -> None:
    for key, default in {
        "gcd_a": "252", "gcd_b": "105", "gcd_result": None,
        "gcd_position": 0, "gcd_error": None,
    }.items():
        st.session_state.setdefault(key, default)

    st.caption("EXPERIMENT 01 / EUCLID’S ALGORITHM")
    st.title("Find the greatest common divisor")
    st.write("Divide, keep the remainder, repeat. See why this simple pattern finds the largest number that divides both inputs.")

    inputs, lesson = st.container(), st.container()
    with inputs:
        with st.container(border=True):
            st.subheader("Choose your numbers")
            st.selectbox("Example", list(PRESETS), key="gcd_preset")
            st.button("Load example", on_click=load_example, key="load_example")
            st.text_input("First integer (a)", key="gcd_a", max_chars=22, on_change=clear_result)
            st.text_input("Second integer (b)", key="gcd_b", max_chars=22, on_change=clear_result)
            st.caption("Whole numbers from −10¹⁸ to 10¹⁸. Negative values and zero are welcome.")
            st.button("Calculate GCD", type="primary", on_click=calculate, key="calculate")
            if st.session_state.gcd_error:
                st.error(st.session_state.gcd_error)

    with lesson:
        with st.expander("Why does Euclid’s algorithm work?", expanded=False):
            st.latex(r"a = bq + r \quad\Longrightarrow\quad \gcd(a,b) = \gcd(b,r)")
            st.write("A number dividing both a and b also divides a − bq, which is the remainder r. Conversely, a number dividing b and r divides bq + r = a. Each replacement therefore keeps exactly the same common divisors.")
            st.write("When the remainder reaches zero, the current divisor is the GCD. We use absolute values so the answer is nonnegative.")
        st.info("RSA connection: the public exponent e must have gcd(e, φ(n)) = 1 so that its modular inverse exists.")

    result = st.session_state.gcd_result
    if result is None:
        st.info("Choose an example or enter your own numbers, then select Calculate GCD.")
        return

    st.divider()
    st.subheader("Your calculation")
    st.caption(f"Original inputs: a = {result.a}, b = {result.b}. Working values: |a| = {abs(result.a)}, |b| = {abs(result.b)}.")
    if not result.steps:
        st.metric("Greatest common divisor", str(result.value))
        if result.a == result.b == 0:
            st.info("We define gcd(0, 0) = 0 as a programming convention. Every positive integer divides zero, so there is no greatest positive common divisor. No division steps are needed.")
        else:
            st.success(f"The second working value is already zero, so gcd({result.a}, 0) = |{result.a}| = {result.value}. No divisions are needed.")
        st.button("Reset calculation", on_click=clear_result, key="reset")
        return

    position = st.session_state.gcd_position
    count = len(result.steps)
    current = result.steps[position]
    st.progress((position + 1) / count, text=f"Step {position + 1} of {count}")
    with st.container(border=True):
        st.latex(rf"{current.dividend} = {current.divisor} \times {current.quotient} + {current.remainder}")
        if current.remainder:
            st.write(f"{current.divisor} fits into {current.dividend} exactly {current.quotient} whole times, leaving {current.remainder}. Next, divide {current.divisor} by {current.remainder}.")
        else:
            st.success(f"The remainder is 0. Stop here: the greatest common divisor is {result.value}.")

    controls = st.columns(4)
    controls[0].button("Previous", key="previous", disabled=position == 0, on_click=move, args=(position - 1,))
    controls[1].button("Next step", key="next", disabled=position == count - 1, on_click=move, args=(position + 1,))
    controls[2].button("Show all steps", key="show_all", on_click=move, args=(count - 1,))
    controls[3].button("Start over", key="restart", on_click=move, args=(0,))

    st.table([
        {"Step": str(index + 1), "Dividend": str(step.dividend),
         "Divisor": str(step.divisor), "Quotient": str(step.quotient),
         "Remainder": str(step.remainder)}
        for index, step in enumerate(result.steps[:position + 1])
    ])
    if position == count - 1:
        st.metric("Greatest common divisor", str(result.value))
        if result.value == 1:
            st.caption("These numbers are coprime: their only positive common divisor is 1.")
    st.button("Reset calculation", on_click=clear_result, key="reset")
