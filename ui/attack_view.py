"""Factor small public RSA moduli and reconstruct the private exponent."""

import streamlit as st

from core.attacks import break_key
from core.primality import DEFAULT_BUDGET
from core.rsa import decode_text, encode_text, encrypt_blocks
from ui.inputs import parse_integer
from ui.playback import playback
from ui.rsa_shared import MESSAGE_MODES, parse_ciphertext

PRESETS = {
    "Tiny public key · n = 3233": (17, 3233),
    "Medium public key · n = 1022117": (65537, 1022117),
    "Beyond this trial budget · n = 999962000357": (65537, 999962000357),
}


def clear_result():
    st.session_state.attack_result = None
    st.session_state.attack_error = None
    st.session_state.attack_position = 0


def load_example():
    e, n = PRESETS[st.session_state.attack_preset]
    st.session_state.attack_e, st.session_state.attack_n = str(e), str(n)
    st.session_state.attack_mode = MESSAGE_MODES[0]
    st.session_state.attack_ciphertext = ", ".join(map(str, encrypt_blocks(encode_text("HELLO", n), e, n)))
    clear_result()


def import_public_data():
    clear_result()
    keys = st.session_state.get("rsa_keys")
    if keys is None:
        st.session_state.attack_error = "Build keys and encrypt a message in RSA Lab first."
        return
    st.session_state.attack_e, st.session_state.attack_n = str(keys.e), str(keys.n)
    st.session_state.attack_ciphertext = st.session_state.get("rsa_ciphertext", "")
    st.session_state.attack_mode = st.session_state.get("rsa_mode", MESSAGE_MODES[0])


def attack():
    clear_result()
    try:
        e = parse_integer(st.session_state.attack_e, "e", limit=10**12)
        n = parse_integer(st.session_state.attack_n, "n", limit=10**12)
        ciphertext = parse_ciphertext(st.session_state.attack_ciphertext, n)
        if st.session_state.attack_mode == MESSAGE_MODES[0] and n <= 255:
            raise ValueError("UTF-8 text mode requires n > 255; use Integer mode for smaller keys.")
        if st.session_state.attack_mode == MESSAGE_MODES[1] and len(ciphertext) != 1:
            raise ValueError("Integer mode requires exactly one ciphertext block.")
        st.session_state.attack_result = break_key(e, n, ciphertext, st.session_state.attack_budget)
    except (ValueError, TypeError) as error:
        st.session_state.attack_error = str(error)


def render_attack(theory):
    for key, value in {"attack_e": "17", "attack_n": "3233", "attack_ciphertext": "3000, 28, 2726, 2726, 1307",
                       "attack_mode": MESSAGE_MODES[0], "attack_budget": DEFAULT_BUDGET,
                       "attack_result": None, "attack_error": None, "attack_position": 0}.items():
        st.session_state.setdefault(key, value)
    st.caption("EXPERIMENT 07 / BREAK THE KEY")
    st.title("Recover a small RSA key from public data")
    st.write("The attack receives only e, n and ciphertext. It must discover the factors of n before it can reconstruct the private exponent.")
    left, right = st.container(), theory
    with left, st.container(border=True):
        st.selectbox("Example", list(PRESETS), key="attack_preset")
        st.button("Load public-key example", key="attack_load", on_click=load_example)
        st.button("Use RSA Lab public data", key="attack_import", on_click=import_public_data)
        st.text_input("Public exponent e", key="attack_e", max_chars=16, on_change=clear_result)
        st.text_input("Public modulus n", key="attack_n", max_chars=16, on_change=clear_result)
        st.radio("Interpret recovered blocks as", MESSAGE_MODES, key="attack_mode", on_change=clear_result)
        st.text_area("Ciphertext blocks", key="attack_ciphertext", max_chars=8192, on_change=clear_result)
        st.number_input("Maximum candidate checks", min_value=1, max_value=DEFAULT_BUDGET, key="attack_budget", on_change=clear_result)
        st.button("Try to break the key", key="attack_run", type="primary", on_click=attack)
        if st.session_state.attack_error:
            st.error(st.session_state.attack_error)
    with right:
        st.latex(r"n\xrightarrow{\text{factor}}p,q\quad\Rightarrow\quad\varphi(n)\quad\Rightarrow\quad d=e^{-1}\pmod{\varphi(n)}")
        st.write("The search tries 2, then odd candidate divisors. Once a factor is found, it verifies the other factor is prime and checks the public exponent before recovering d.")
        st.info("Scope: two distinct odd primes, each at most 1,000,000; n ≤ 10¹². At most 100,000 checks. Reaching the limit means this attempt is unfinished, not that the key is secure.")
        st.write("Properly generated 2048-bit RSA is far beyond this classroom trial-division attack. These measured timings are not predictions for advanced factoring algorithms or a proof of security. Real encryption also needs secure padding and vetted implementations.")
    result = st.session_state.attack_result
    if result is None:
        return
    st.divider()
    st.metric("Candidate checks", str(result.trial.attempts))
    st.metric("Measured run time (ms)", f"{result.elapsed_seconds * 1000:.3f}")
    st.caption("Elapsed time includes factor search, key recovery and decryption for this run; it varies by machine.")
    if result.trial.steps:
        if len(result.trial.steps) < result.trial.attempts:
            st.info("The trace shows the first 200 checks and a later successful factor check if one was found; intervening checks are omitted from display.")
        position = playback("attack", len(result.trial.steps), "Recorded candidate")
        st.table([{"Candidate divisor": str(s.divisor), "n mod candidate": str(s.remainder)} for s in result.trial.steps[:position + 1]])
    if result.status == "recovered":
        st.success(result.reason)
        st.code(f"n = {result.p} × {result.q}\nφ(n) = ({result.p}−1)({result.q}−1) = {result.phi}\nRecovered d = {result.d}", language=None)
        st.subheader("Recovered message")
        st.code("Recovered blocks: " + ", ".join(map(str, result.recovered)), language=None)
        if st.session_state.attack_mode == MESSAGE_MODES[0]:
            try:
                text = decode_text(result.recovered)
                st.code(text if text else "(empty string)", language=None)
            except ValueError as error:
                st.error(f"The key was recovered, but text decoding failed: {error}")
        else:
            st.code(str(result.recovered[0]), language=None)
        st.caption("Successful decoding is not authentication. This educational attack demonstrates factorization-based key recovery.")
    else:
        st.warning(result.reason)
        if result.p is not None:
            st.code(f"Factors found: {result.p} × {result.q}", language=None)
    st.button("Reset attack", key="attack_reset", on_click=clear_result)
