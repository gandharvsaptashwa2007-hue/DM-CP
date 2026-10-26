"""Small, independently stateful exercises alongside the module explanations."""

import streamlit as st

CHALLENGES = {
    "GCD Visualizer": ("What is gcd(48, 18)?", 6, "Keep replacing the pair with the divisor and remainder.", "48 = 18×2 + 12; 18 = 12×1 + 6; 12 = 6×2. The last nonzero remainder is 6."),
    "Extended Euclid & Inverse": ("What is the smallest positive inverse of 3 modulo 11?", 4, "Find x such that 3x leaves remainder 1 after division by 11.", "3×4 = 12 = 11 + 1, so 3⁻¹ ≡ 4 (mod 11)."),
    "Primality Tester": ("What is the smallest prime factor of 91?", 7, "Try prime divisors up to √91: 2, 3, 5, 7.", "91 = 7×13. Finding a divisor proves that 91 is composite."),
    "Euler’s Phi": ("How many integers from 1 through 12 are coprime to 12?", 4, "Exclude multiples of 2 and 3.", "The integers are 1, 5, 7, 11. φ(12) = 12(1−1/2)(1−1/3) = 4."),
    "CRT Solver": ("Find the smallest nonnegative x: x ≡ 2 (mod 3), x ≡ 3 (mod 5).", 8, "List 3, 8, 13… and test their remainders modulo 3.", "8 mod 3 = 2 and 8 mod 5 = 3. Every solution is 8 + 15k."),
    "RSA Lab": ("With p = 5 and q = 11, what is φ(n)?", 40, "For distinct primes, φ(pq) = (p−1)(q−1).", "n = 55 and φ(n) = 4×10 = 40. A valid public exponent must be coprime to 40."),
    "Break the Key": ("You factored n = 77 into 7×11. What is φ(n)?", 60, "Once the prime factors are known, use (p−1)(q−1).", "φ(77) = 6×10 = 60. For e = 7, d = 43 because 7×43 ≡ 1 (mod 60)."),
}


def clear_feedback(slug):
    st.session_state.pop(f"challenge_feedback_{slug}", None)


def check_answer(slug, expected):
    try:
        answer = int(st.session_state[f"challenge_answer_{slug}"].strip())
    except ValueError:
        st.session_state[f"challenge_feedback_{slug}"] = "invalid"
        return
    st.session_state[f"challenge_feedback_{slug}"] = "correct" if answer == expected else "retry"


def render_explanation_play(name, slug):
    question, answer, hint, reasoning = CHALLENGES[name]
    st.divider()
    st.subheader("Try it yourself")
    st.caption("A quick challenge · independent of your workspace inputs")
    st.write(question)
    st.text_input("Your answer", key=f"challenge_answer_{slug}", max_chars=30,
                  on_change=clear_feedback, args=(slug,))
    st.button("Check answer", key=f"challenge_check_{slug}",
              on_click=check_answer, args=(slug, answer))
    feedback = st.session_state.get(f"challenge_feedback_{slug}")
    if feedback == "correct":
        st.success("Exactly right! " + reasoning)
    elif feedback == "retry":
        st.info("Not quite yet. Try the hint, then check again.")
    elif feedback == "invalid":
        st.warning("Enter a whole number to check your answer.")
    if st.toggle("Show a hint", key=f"challenge_hint_{slug}"):
        st.write(hint)
    if st.toggle("Show worked answer", key=f"challenge_solution_{slug}"):
        st.write(reasoning)

    st.divider()
    st.subheader("Play with remainders")
    st.caption("Drag either slider to see modular arithmetic change live.")
    st.session_state.setdefault(f"explore_number_{slug}", 17)
    st.session_state.setdefault(f"explore_modulus_{slug}", 5)
    number = st.slider("Number", 0, 60, key=f"explore_number_{slug}")
    modulus = st.slider("Modulus", 2, 12, key=f"explore_modulus_{slug}")
    quotient, remainder = divmod(number, modulus)
    st.latex(rf"{number} = {modulus}\times {quotient} + {remainder}")
    st.write(f"{number} mod {modulus} = **{remainder}**")
    st.caption("The highlighted position is the remainder. After the last position, counting wraps to zero.")
    positions = "".join(
        f'<span class="residue {"selected" if i == remainder else ""}">{i}</span>'
        for i in range(modulus)
    )
    st.html(f'<div class="residue-track" aria-label="Remainder positions">{positions}</div>')
