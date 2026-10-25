"""A guided educational RSA lab with explicit key/message state invalidation."""

import streamlit as st

from core import modular_power, solve_crt
from core.rsa import make_keys, generate_keys, encode_text, decode_text, encrypt_blocks, decrypt_blocks, PRIME_RANGES
from ui.inputs import parse_integer
from ui.rsa_shared import MESSAGE_MODES, parse_ciphertext, render_power, reset_power


def clear_messages():
    st.session_state.rsa_packet = None
    st.session_state.rsa_recovered = None
    st.session_state.rsa_ciphertext = ""
    st.session_state.rsa_message_error = None
    st.session_state.rsa_trace_block = 0
    st.session_state.rsa_trace_kind = "Encryption"
    st.session_state.rsa_power_position = 0


def clear_keys():
    st.session_state.rsa_keys = None
    st.session_state.rsa_key_error = None
    clear_messages()


def change_mode():
    st.session_state.rsa_message = "HELLO" if st.session_state.rsa_mode == MESSAGE_MODES[0] else "65"
    clear_messages()


def change_ciphertext():
    st.session_state.rsa_packet = None
    st.session_state.rsa_recovered = None
    st.session_state.rsa_message_error = None
    st.session_state.rsa_trace_block = 0
    st.session_state.rsa_power_position = 0


def load_demo():
    st.session_state.rsa_p, st.session_state.rsa_q, st.session_state.rsa_e = "61", "53", "17"
    st.session_state.rsa_mode, st.session_state.rsa_message = MESSAGE_MODES[0], "HELLO"
    clear_keys()


def build_keys():
    clear_keys()
    try:
        st.session_state.rsa_keys = make_keys(
            parse_integer(st.session_state.rsa_p, "p", limit=10**6),
            parse_integer(st.session_state.rsa_q, "q", limit=10**6),
            parse_integer(st.session_state.rsa_e, "e", limit=10**12),
        )
    except (ValueError, TypeError) as error:
        st.session_state.rsa_key_error = str(error)


def random_keys():
    clear_keys()
    try:
        keys = generate_keys(st.session_state.rsa_size)
        st.session_state.rsa_p, st.session_state.rsa_q, st.session_state.rsa_e = str(keys.p), str(keys.q), str(keys.e)
        st.session_state.rsa_keys = keys
    except ValueError as error:
        st.session_state.rsa_key_error = str(error)


def encrypt():
    clear_messages()
    keys = st.session_state.rsa_keys
    if keys is None:
        st.session_state.rsa_message_error = "Build valid keys first."
        return
    try:
        mode, message = st.session_state.rsa_mode, st.session_state.rsa_message
        plain = encode_text(message, keys.n) if mode == MESSAGE_MODES[0] else (parse_integer(message, "Message integer", limit=10**12),)
        cipher = encrypt_blocks(plain, keys.e, keys.n)
        st.session_state.rsa_packet = {"plain": plain, "cipher": cipher, "mode": mode}
        st.session_state.rsa_ciphertext = ", ".join(map(str, cipher))
    except (ValueError, TypeError) as error:
        st.session_state.rsa_message_error = str(error)


def decrypt():
    st.session_state.rsa_recovered = None
    st.session_state.rsa_message_error = None
    st.session_state.rsa_trace_block = 0
    st.session_state.rsa_power_position = 0
    keys = st.session_state.rsa_keys
    if keys is None:
        st.session_state.rsa_message_error = "Build valid keys first."
        return
    try:
        cipher = parse_ciphertext(st.session_state.rsa_ciphertext, keys.n)
        mode = st.session_state.rsa_mode
        if mode == MESSAGE_MODES[0] and keys.n <= 255:
            raise ValueError("UTF-8 text mode requires n > 255.")
        if mode == MESSAGE_MODES[1] and len(cipher) != 1:
            raise ValueError("Integer mode requires exactly one ciphertext block.")
        plain = decrypt_blocks(cipher, keys.d, keys.n)
        text = decode_text(plain) if mode == MESSAGE_MODES[0] else str(plain[0])
        st.session_state.rsa_recovered = {"cipher": cipher, "plain": plain, "text": text, "mode": mode}
        st.session_state.rsa_trace_kind = "Decryption"
    except (ValueError, TypeError) as error:
        st.session_state.rsa_message_error = str(error)


def render_rsa(theory):
    defaults = {"rsa_p": "61", "rsa_q": "53", "rsa_e": "17", "rsa_size": "Small", "rsa_keys": None,
                "rsa_key_error": None, "rsa_message_error": None, "rsa_mode": MESSAGE_MODES[0], "rsa_message": "HELLO",
                "rsa_ciphertext": "", "rsa_packet": None, "rsa_recovered": None, "rsa_trace_kind": "Encryption",
                "rsa_trace_block": 0, "rsa_power_position": 0}
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)
    st.caption("EXPERIMENT 06 / RSA LAB")
    st.title("Turn number theory into encryption")
    st.warning("Educational textbook RSA: small keys, no padding, and one UTF-8 byte per block. It leaks patterns and is not suitable for private messages or passwords.")
    st.subheader("1. Choose primes and build keys")
    st.button("Load HELLO demo", key="rsa_demo", on_click=load_demo)
    cols = st.columns(3)
    for col, label, key in zip(cols, ("Prime p", "Prime q", "Public exponent e"), ("rsa_p", "rsa_q", "rsa_e")):
        col.text_input(label, key=key, max_chars=16, on_change=clear_keys)
    st.button("Build keys", key="rsa_build", type="primary", on_click=build_keys)
    with st.expander("Generate educational keys"):
        st.selectbox("Prime size", list(PRIME_RANGES), key="rsa_size")
        st.button("Generate random keys", key="rsa_generate", on_click=random_keys)
        st.caption("Samples distinct primes using secrets. Chooses e = 65537 when valid, otherwise a smaller coprime odd exponent. These remain classroom-sized keys.")
    if st.session_state.rsa_key_error:
        st.error(st.session_state.rsa_key_error)
    keys = st.session_state.rsa_keys
    if keys:
        st.code(f"p = {keys.p}, q = {keys.q} (distinct primes)\nn = p × q = {keys.n}\nφ(n) = (p−1)(q−1) = {keys.phi}\ngcd(e, φ(n)) = 1\nd = e⁻¹ mod φ(n) = {keys.d}", language=None)
        public, private = st.columns(2)
        public.metric("Public key (e, n)", f"({keys.e}, {keys.n})")
        private.metric("Private key (d, n) — visible for learning", f"({keys.d}, {keys.n})")
        with st.expander("Extended Euclid behind the private exponent"):
            eg = keys.inverse.euclid
            st.table([{"Remainder": str(s.remainder), "Quotient": str(s.quotient), "x": str(s.x), "y": str(s.y)} for s in eg.steps])
            st.code(f"{keys.e} × ({eg.x}) + {keys.phi} × ({eg.y}) = 1\nd = {eg.x} mod {keys.phi} = {keys.d}\n(e × d) mod φ(n) = {(keys.e * keys.d) % keys.phi}", language=None)

    st.subheader("2. Enter a message and encrypt")
    st.radio("Message mode", MESSAGE_MODES, key="rsa_mode", on_change=change_mode)
    st.text_area("Message", key="rsa_message", max_chars=1024, on_change=clear_messages)
    st.caption("Text: up to 256 UTF-8 bytes; n must exceed 255. Integer: 0 ≤ m < n. Empty text is allowed and produces zero blocks.")
    st.button("Encrypt message", key="rsa_encrypt", disabled=keys is None, on_click=encrypt)
    packet = st.session_state.rsa_packet
    if packet is not None:
        st.code("Encoded blocks: " + ", ".join(map(str, packet["plain"])), language=None)
        if packet["plain"]:
            st.table([{"Block": str(i + 1), "Message value m": str(m), "Ciphertext c = m^e mod n": str(c)} for i, (m, c) in enumerate(zip(packet["plain"], packet["cipher"]))])
        else:
            st.info("Empty text: no blocks to encrypt.")
        st.caption("Equal message bytes produce equal ciphertext blocks. For HELLO, both L bytes encrypt to the same number — one reason textbook RSA is insecure.")

    st.subheader("3. Decrypt ciphertext")
    st.text_area("Ciphertext blocks (commas or spaces)", key="rsa_ciphertext", max_chars=8192, on_change=change_ciphertext)
    st.button("Decrypt ciphertext", key="rsa_decrypt", disabled=keys is None, on_click=decrypt)
    if st.session_state.rsa_message_error:
        st.error(st.session_state.rsa_message_error)
    recovered = st.session_state.rsa_recovered
    if recovered is not None:
        st.success("Decryption completed.")
        st.code(recovered["text"] if recovered["text"] else "(empty string)", language=None)
        st.code("Recovered blocks: " + ", ".join(map(str, recovered["plain"])), language=None)
        if packet is not None:
            if recovered["plain"] == packet["plain"]:
                st.success("Round trip verified: every recovered block matches the original message.")
            else:
                st.error("Recovered blocks differ from the original message.")
        else:
            st.caption("Externally entered ciphertext has no original message here to compare against. Decoding successfully does not authenticate a message.")

    options = []
    if packet is not None and packet["plain"]:
        options.append("Encryption")
    if recovered is not None and recovered["plain"]:
        options.append("Decryption")
    if keys and options:
        st.subheader("4. Inspect one block’s arithmetic")
        if st.session_state.rsa_trace_kind not in options:
            st.session_state.rsa_trace_kind = options[0]
        st.radio("Trace direction", options, key="rsa_trace_kind", on_change=reset_power, args=("rsa_power",))
        data = packet if st.session_state.rsa_trace_kind == "Encryption" else recovered
        st.selectbox("Block to inspect", list(range(len(data["plain"]))), format_func=lambda i: f"Block {i + 1}", key="rsa_trace_block", on_change=reset_power, args=("rsa_power",))
        index = st.session_state.rsa_trace_block
        encryption = st.session_state.rsa_trace_kind == "Encryption"
        render_power(data["plain"][index] if encryption else data["cipher"][index], keys.e if encryption else keys.d, keys.n, "rsa_power")
        if not encryption:
            c = data["cipher"][index]
            mp = modular_power(c, keys.d, keys.p).value
            mq = modular_power(c, keys.d, keys.q).value
            combined = solve_crt(((mp, keys.p), (mq, keys.q)))
            with st.expander("Check the same block using CRT", expanded=True):
                st.code(f"c^d mod p = {mp}\nc^d mod q = {mq}\nCRT combines these residues into {combined.value} mod {combined.period}\nDirect decryption gives {data['plain'][index]}", language=None)
                st.table([{"Modulus": str(s.modulus), "Residue": str(s.residue), "Partial product": str(s.partial_product), "Inverse": str(s.inverse.value), "Contribution": str(s.contribution)} for s in combined.steps])
    with theory:
        st.subheader("Why does decryption restore every valid message block?")
        st.write("ed = 1 + kφ(n). Euler’s theorem proves m^(ed) ≡ m mod n when m is coprime to n. For all valid message blocks, including multiples of p or q, use Fermat’s theorem (or the zero residue) separately modulo each prime, then CRT to recover the unique residue modulo n.")
        st.write("Real systems use vetted cryptographic libraries and padding such as RSA-OAEP. This demonstration intentionally exposes the unpadded arithmetic.")
    st.button("Reset lab", key="rsa_reset", on_click=load_demo)
