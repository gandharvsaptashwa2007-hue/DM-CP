"""Opt-in, browser-local spotlight tours. Never modifies experiment inputs."""
import json
from uuid import uuid4
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from ui.design import MODULES


def tour_steps(module):
    steps = [
        (".brand-lockup", "Welcome to Modular Minds", "Click the logo or website name whenever you want to return to the dashboard."),
        (".st-key-page_picker", "Choose your experiment", "Jump directly to any of the seven modules using this dropdown."),
        (".st-key-color_mode", "Make yourself comfortable", "Choose Light, Dark, or Device. Device follows your system’s appearance."),
        (".st-key-page_previous", "Retrace your visits", "Back and Forward follow your actual page visits. They are disabled when there is no visit in that direction."),
    ]
    if module == "Home":
        steps += [(f".st-key-card_{slug}", name, description + " Select this card after the tour to open the experiment.")
                  for name, (slug, _, description, _) in MODULES.items()]
    else:
        steps = []  # Shared navigation is taught only on Home.
        slug = MODULES[module][0]
        specific = {
            "inverse": [("inverse_mode", "Two ways to explore", "Switch between modular inversion and the full Bézout identity.")],
            "prime": [("prime_method", "Compare primality tests", "Trial division checks possible divisors. Miller–Rabin examines modular powers; choose a method before testing.")],
            "phi": [("phi_budget", "Bound the work", "The factorization work limit bounds divisibility checks. Incomplete factorization is reported honestly, without inventing a phi value.")],
            "crt": [("crt_count", "Build a system", "Choose two to six equations. Each row pairs a residue with its modulus; this solver requires pairwise coprime moduli.")],
            "rsa": [("rsa_demo", "Start the RSA demo", "Load the HELLO example, then build keys from p, q, and e."), ("rsa_message", "Encrypt a message", "Choose text or integer mode, enter a message, and select Encrypt."), ("rsa_ciphertext", "Bring it back", "Decrypt the ciphertext with the generated private key. Inspect a block’s modular-power trace below."), ("rsa_trace_block", "Inspect individual blocks", "Choose a message block to explore its repeated-squaring steps and the CRT decryption check.")],
            "attack": [("attack_import", "Use public information", "Import the public key and ciphertext from RSA Lab. Private key data is not supplied to the attack."), ("attack_budget", "Explore the cost of factoring", "Change the check budget and compare outcomes. Reaching the budget does not prove a key is secure.")],
        }
        steps += [
            (f".st-key-{slug}_preset", "Start with an example", "Choose a preset, then use its Load button to fill the inputs. You can also enter your own values."),
            (".st-key-workspace [data-testid='stTextInput']", "Make it your own", "Enter exact whole numbers. Labels explain each input; validation messages help you correct unsupported values."),
            (".st-key-workspace [data-testid='stBaseButton-primary']", "Run the experiment", "Use the primary action to calculate. RSA has separate actions for building keys, encryption, and decryption."),
            (".st-key-workspace [data-testid='stProgress']", "Follow the mathematics", "The progress bar shows your current step. Previous, Next step, Show all steps, and Start over control playback."),
            (".st-key-workspace [data-testid='stTable']", "Inspect the evidence", "Tables show the intermediate values. Move through the calculation to reveal more steps."),
            (".st-key-theory_panel .math-art", "Understand why it works", "The explanation below this illustration connects the algorithm to its mathematical rule and RSA."),
            (f".st-key-challenge_answer_{slug}", "Test your understanding", "Answer the short question, then select Check answer for feedback. This exercise does not change your main calculation."),
            (f".st-key-challenge_hint_{slug}", "Get a little help", "Show a hint when you need a nudge. Show worked answer reveals the full reasoning."),
            (f".st-key-explore_number_{slug}", "Explore remainders live", "Drag the Number and Modulus sliders. The equation and highlighted position update immediately."),
            (".st-key-results_pane", "Compare your discoveries", "History appears after a calculation. Scroll through previous results or clear this module’s history."),
        ]
        steps += [(f".st-key-{key}", title, description) for key, title, description in specific.get(slug, [])]
    if module == "Home":
        steps.append((".st-key-start_tour", "You’re ready to explore", "Replay this tour anytime. On module pages, calculate first and replay to also tour the result tables, playback, and history. Your inputs stay untouched."))
    return steps


def render_tour(module):
    st.button("Take a tour", icon=":material/explore:", key="start_tour", help="A guided walkthrough of the current page")
    script = Path(__file__).with_name("tour.js").read_text()
    payload = json.dumps(tour_steps(module)).replace("<", "\\u003c")
    page = json.dumps(module).replace("<", "\\u003c")
    components.html(f"<!-- {uuid4().hex} --><script>const tourPage = {page}; const tourSteps = {payload};\n{script}</script>", height=0)
