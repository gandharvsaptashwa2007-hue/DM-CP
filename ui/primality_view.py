"""Prime testing with divisor evidence and Miller–Rabin residue chains."""

import streamlit as st

from core import miller_rabin, trial_division
from core.primality import DEFAULT_BUDGET, MR_BASES, TRIAL_LIMIT, UINT64_LIMIT
from ui.inputs import parse_integer
from ui.playback import playback

METHODS = ("Trial division", "Miller–Rabin")
PRESETS = {
    "Prime · 97": (97, METHODS[0]),
    "Composite · 91": (91, METHODS[0]),
    "Carmichael number · 561": (561, METHODS[1]),
    "Strong pseudoprime to base 2 · 2047": (2047, METHODS[1]),
    "Large prime · 18446744073709551557": (18446744073709551557, METHODS[1]),
    "Smallest prime · 2": (2, METHODS[0]),
    "Neither prime nor composite · 1": (1, METHODS[0]),
}


def clear_result():
    st.session_state.prime_result = None
    st.session_state.prime_error = None
    st.session_state.prime_position = 0


def load_example():
    n, method = PRESETS[st.session_state.prime_preset]
    st.session_state.prime_n = str(n)
    st.session_state.prime_method = method
    clear_result()


def calculate():
    clear_result()
    try:
        trial = st.session_state.prime_method == METHODS[0]
        n = parse_integer(st.session_state.prime_n, "Number", limit=TRIAL_LIMIT if trial else UINT64_LIMIT - 1)
        if n < 0:
            raise ValueError("Enter a nonnegative integer. Prime numbers are integers greater than 1.")
        st.session_state.prime_result = trial_division(n, st.session_state.prime_budget) if trial else miller_rabin(n)
    except (ValueError, TypeError) as error:
        st.session_state.prime_error = str(error)


def render_primality(theory):
    for key, value in {"prime_n": "97", "prime_method": METHODS[0],
                       "prime_budget": DEFAULT_BUDGET, "prime_result": None,
                       "prime_error": None, "prime_position": 0}.items():
        st.session_state.setdefault(key, value)
    st.caption("EXPERIMENT 03 / PRIMALITY TESTING")
    st.title("Is this number prime?")
    st.write("Inspect divisors or follow modular residue chains to see the evidence behind the answer.")
    left, right = st.container(), theory
    with left, st.container(border=True):
        example, load = st.columns([3, 2], vertical_alignment="bottom")
        example.selectbox("Example", list(PRESETS), key="prime_preset")
        load.button("Load example", key="prime_load", on_click=load_example)
        st.radio("Method", METHODS, key="prime_method", on_change=clear_result)
        st.text_input("Number (n)", key="prime_n", max_chars=24, on_change=clear_result)
        st.caption("Trial division: 0 to 10¹². Miller–Rabin: 0 ≤ n < 2⁶⁴.")
        with st.expander("Trial division work limit"):
            st.number_input("Maximum divisibility checks", min_value=1, max_value=DEFAULT_BUDGET,
                            key="prime_budget", on_change=clear_result)
            st.caption("This limit applies only to trial division. A lower limit can demonstrate an unfinished calculation.")
        st.button("Test number", key="prime_calculate", type="primary", on_click=calculate)
        if st.session_state.prime_error:
            st.error(st.session_state.prime_error)
    with right:
        with st.container():
            st.subheader("Two approaches to the same question")
            st.write("Trial division checks 2, then odd candidate divisors up to √n. If n is composite, at least one factor is no larger than √n. A complete search without a factor proves primality.")
            st.latex(r"n-1 = 2^s d \quad (d\text{ odd})")
            st.write("For odd n, Miller–Rabin starts with x = aᵈ mod n. A base passes if x is 1 or n−1, or if up to s−1 repeated squarings reach n−1. Failure proves compositeness. Passing just one base does not prove primality.")
            st.write("This implementation uses seven fixed bases that decide primality exactly for n < 2⁶⁴. Inputs outside that range are rejected; it does not claim a proof for arbitrary-size numbers.")
        st.info("RSA connection: p and q must be prime before n = p×q and φ(n) = (p−1)(q−1) can be used.")

    result = st.session_state.prime_result
    if result is None:
        st.info("Choose an example or enter a number, then select Test number.")
        return
    st.divider()
    st.caption(f"Input: n = {result.n}. Method: {st.session_state.prime_method}.")
    st.metric("Classification", {"prime": "Prime", "composite": "Composite", "neither": "Neither", "incomplete": "Unresolved"}[result.status])
    if result.status == "incomplete":
        st.warning(result.reason)
    else:
        st.write(result.reason)
    if result.factor is not None:
        st.code(f"{result.n} = {result.factor} × {result.n // result.factor}", language=None)

    if st.session_state.prime_method == METHODS[0]:
        st.caption(f"Divisibility checks performed: {result.attempts}.")
        if len(result.steps) < result.attempts:
            st.info(f"Showing {len(result.steps)} recorded checks out of {result.attempts}: the first 200 and a later factor-discovery check, if present. Other checks were executed but are omitted from the table.")
        if result.steps:
            position = playback("prime", len(result.steps), "Recorded check")
            step = result.steps[position]
            st.code(f"{result.n} mod {step.divisor} = {step.remainder}", language=None)
            st.table([{"Divisor tested": str(s.divisor), "Remainder": str(s.remainder)} for s in result.steps[:position + 1]])
        else:
            st.info("No candidate divisions are needed for this input.")
    else:
        if result.rounds:
            st.latex(rf"{result.n - 1} = 2^{{{result.s}}} \times {result.d}")
            st.caption("Fixed bases: " + ", ".join(map(str, MR_BASES)))
            position = playback("prime", len(result.rounds), "Base")
            round_ = result.rounds[position]
            st.write(f"Base {round_.base}, reduced modulo n to {round_.reduced_base}: {round_.outcome}.")
            if round_.outcome == "skipped":
                st.info("This base reduces to 0 or 1, so it is uninformative and is skipped. Classification uses the remaining bases.")
            else:
                st.code(f"x₀ = {round_.reduced_base}^{result.d} mod {result.n} = {round_.residues[0]}", language=None)
                st.table([{"Residue": f"x{i}", "Operation": f"a^d mod n" if i == 0 else "previous residue squared mod n", "Value": str(x)} for i, x in enumerate(round_.residues)])
                if round_.outcome == "witness":
                    st.warning("This residue chain fails the strong primality condition, proving that the number is composite. A witness need not reveal a factor.")
                else:
                    st.caption("This base passes. The overall verdict uses all required bases, not this one alone.")
            st.table([{"Base": str(r.base), "Reduced base": str(r.reduced_base), "Residue chain": " → ".join(map(str, r.residues)) or "—", "Outcome": r.outcome} for r in result.rounds[:position + 1]])
        else:
            st.info("A direct small-number or even-number check decides this case; no Miller–Rabin rounds are needed.")
    if result.n in (561, 2047):
        with st.expander("Why a simple Fermat check can mislead", expanded=True):
            st.code(f"2^({result.n}−1) mod {result.n} = {pow(2, result.n - 1, result.n)}", language=None)
            st.write("This Fermat check passes although the number is composite. A single passing check is insufficient.")
            if result.n == 561:
                st.write("561 = 3×11×17 is a Carmichael number: it passes Fermat's test for every base coprime to 561.")
            else:
                st.write("2047 = 23×89 even passes Miller–Rabin at base 2. Another base supplies a witness.")
    st.button("Reset calculation", key="prime_reset", on_click=clear_result)
