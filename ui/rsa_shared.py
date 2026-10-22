"""Ciphertext parsing and selected-block traces shared by the RSA screens."""

import re

import streamlit as st

from core import modular_power
from core.rsa import validate_blocks
from ui.inputs import parse_integer
from ui.playback import playback

MESSAGE_MODES = ("UTF-8 text", "Integer")


def parse_ciphertext(text: str, n: int) -> tuple[int, ...]:
    if len(text) > 8192:
        raise ValueError("Ciphertext input is too long; use at most 256 integer blocks.")
    value = text.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1].strip()
    parts = re.split(r"[\s,]+", value) if value else []
    if len(parts) > 256:
        raise ValueError("Use at most 256 ciphertext blocks.")
    return validate_blocks(tuple(parse_integer(part, "Ciphertext block", limit=10**12) for part in parts), n)


def reset_power(prefix: str):
    st.session_state[f"{prefix}_position"] = 0


def render_power(base: int, exponent: int, modulus: int, prefix: str):
    trace = modular_power(base, exponent, modulus)
    st.code(f"{base}^{exponent} mod {modulus} = {trace.value}", language=None)
    position = playback(prefix, len(trace.steps), "Exponent bit")
    st.caption("Read exponent bits from right to left. Multiply the accumulator only for a 1 bit, square the base modulo n, then halve the remaining exponent.")
    st.table([{"Exponent before": str(s.exponent_before), "Bit": str(s.bit), "Base before": str(s.base_before),
               "Accumulator before": str(s.result_before), "Accumulator after": str(s.result_after), "Next squared base": str(s.base_after)}
              for s in trace.steps[:position + 1]])
