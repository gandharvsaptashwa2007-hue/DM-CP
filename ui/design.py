"""Shared visual system, navigation cards and session-local result journal."""

from html import escape
from pathlib import Path

import streamlit as st

MODULES = {
    "GCD Visualizer": ("gcd", "bar_chart", "Follow each division and remainder to discover what two integers share.", "gcd(a, b) = gcd(b, a mod b)"),
    "Extended Euclid & Inverse": ("inverse", "swap_horiz", "Trace Bézout’s identity and find the inverse that makes RSA possible.", "ax + by = gcd(a, b)"),
    "Primality Tester": ("prime", "verified", "Explore trial division and Miller–Rabin. See the evidence behind each verdict.", "n − 1 = 2ˢd · d odd"),
    "Euler’s Phi": ("phi", "donut_large", "Factor an integer and count the numbers that are coprime to it.", "φ(n) = n ∏ (1 − 1/p)"),
    "CRT Solver": ("crt", "account_tree", "Bring several remainder conditions together into one verified solution.", "x = Σ aᵢNᵢyᵢ mod N"),
    "RSA Lab": ("rsa", "lock", "Build a key pair, encrypt a message, and watch the mathematics bring it back.", "c = mᵉ mod n · m = cᵈ mod n"),
    "Break the Key": ("attack", "key", "Factor a small public key and discover why key size matters.", "n = pq → φ(n) → d"),
}


def apply_design():
    st.html(f"<style>{Path(__file__).with_name('theme.css').read_text()}</style>")
    from base64 import b64encode
    artwork = b64encode((Path(__file__).parent / 'assets/math-landscape.svg').read_bytes()).decode()
    st.html(f'<style>.math-banner {{ background-image: url("data:image/svg+xml;base64,{artwork}"); }}</style>')
    mode = st.session_state.get("color_mode", "Device")
    dark = Path(__file__).with_name("color_modes.css").read_text()
    if mode == "Dark":
        st.html(f"<style>{dark}</style>")
    elif mode == "Device":
        st.html(f"<style>@media (prefers-color-scheme: dark) {{{dark}}}</style>")


def navigate(name):
    visits = st.session_state.setdefault("page_visits", ["Home"])
    cursor = st.session_state.setdefault("page_cursor", 0)
    if visits[cursor] != name:
        del visits[cursor + 1:]
        visits.append(name)
        st.session_state.page_cursor = len(visits) - 1
    st.session_state.module = name
    st.session_state.page_picker = name


def travel(offset):
    cursor = st.session_state.page_cursor + offset
    visits = st.session_state.page_visits
    if 0 <= cursor < len(visits):
        st.session_state.page_cursor = cursor
        st.session_state.module = visits[cursor]
        st.session_state.page_picker = visits[cursor]


def choose_page():
    navigate(st.session_state.page_picker)


def dashboard():
    from ui.visuals import illustration
    intro, artwork = st.columns([3, 1])
    intro.subheader("Small experiments. Big ideas.", anchor=False)
    with artwork:
        illustration("home")
    st.write("Your number theory playground. Start with a remainder, follow the steps, and build your way to RSA.")
    st.html('<div class="learning-strip"><span>01 / Foundations</span><b>GCD & inverses</b><span>→</span><b>Primes & congruences</b><span>→</span><b>Encryption & discovery</b></div>')
    st.subheader("Choose an experiment")
    names = list(MODULES)
    for start in range(0, len(names), 3):
        columns = st.columns(3, gap="medium")
        for column, name in zip(columns, names[start:start + 3]):
            slug, icon, description, _ = MODULES[name]
            with column, st.container(key=f"card_{slug}"):
                st.button(f"**{name}**\n\n{description}", icon=f":material/{icon}:",
                          key=f"open_{slug}", use_container_width=True,
                          on_click=navigate, args=(name,))
    st.caption("A guided learning lab · Exact arithmetic · Every step explained")


def summarize(key, result):
    if key == "gcd_result":
        return f"gcd({result.a}, {result.b}) = {result.value}"
    if key == "inverse_result":
        inverse = st.session_state.get("inverse_value")
        return f"{result.a}x + {result.b}y = {result.value}" + (f" · inverse = {inverse}" if inverse is not None else "")
    if key == "prime_result":
        return f"{result.n}: {result.status}"
    if key == "phi_result":
        return f"φ({result.n}) = {result.value}" if result.complete else f"φ({result.n}): incomplete — work budget reached"
    if key == "crt_result":
        return f"x ≡ {result.value} (mod {result.period})"
    if key == "rsa_keys":
        return f"Keys built · public (e, n) = ({result.e}, {result.n})"
    if key in ("rsa_packet", "rsa_recovered"):
        action = "Encrypted" if key == "rsa_packet" else "Decrypted"
        return f"{action} {len(result['cipher'])} blocks · {result['mode']}"
    return f"n = {result.trial.n} · {result.status.replace('_', ' ')}"


def capture_results(slug):
    """Record new result objects once; playback and navigation never duplicate them."""
    keys = ("rsa_keys", "rsa_packet", "rsa_recovered") if slug == "rsa" else (f"{slug}_result",)
    history = st.session_state.setdefault(f"history_{slug}", [])
    for key in keys:
        result = st.session_state.get(key)
        previous = st.session_state.get(f"journal_seen_{key}")
        if result is not None and result is not previous:
            history.insert(0, summarize(key, result))
            del history[20:]
        st.session_state[f"journal_seen_{key}"] = result


def results_pane(name):
    slug, _, _, formula = MODULES[name]
    capture_results(slug)
    if not st.session_state.get(f"history_{slug}"):
        return
    with st.container(key="results_pane"):
        st.subheader("History & results")
        st.caption("This session · newest first")
        history = st.session_state.get(f"history_{slug}", [])
        with st.container(height=130, border=False):
            if not history:
                st.html('<div class="empty-history"><b>Your discoveries start here</b><p>Run an experiment to save a result. Move through the steps at your own pace.</p></div>')
            for index, entry in enumerate(history):
                st.html(f'<div class="history-entry"><small>{"LATEST RESULT" if index == 0 else "PREVIOUS RESULT"}</small><p>{escape(entry)}</p></div>')
        st.button("Clear history", key=f"clear_history_{slug}", disabled=not history,
                  on_click=lambda: st.session_state.update({f"history_{slug}": []}))
