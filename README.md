# Number Theory & RSA Playground

An educational project connecting Unit 5 number theory to RSA through visible
calculation steps. We are building this in small, working milestones.

## Steps 4 and 5 — primality and Euler's phi

Two new sidebar modules connect prime testing and factorization to RSA.

### Primality Tester

- **Trial division** tests 2 and then odd divisors through the integer square
  root, returning a factor when found. Accepts `0 ≤ n ≤ 10^12`.
- **Miller–Rabin** displays `n−1 = 2^s × d`, each fixed base and its modular
  residue chain. The seven bases `2, 325, 9375, 28178, 450775, 9780504,
  1795265022` are deterministic for `0 ≤ n < 2^64`. Larger inputs are rejected;
  a single passing base is never described as proof of primality.
- 0 and 1 are classified as neither prime nor composite. Negative inputs are
  rejected. Small primes and even composites are decided directly.
- Presets include 97, 91, 561 (a Carmichael number), 2047 (a strong pseudoprime
  to base 2), and the large prime 18446744073709551557. The last example uses
  exact text entry so browser floating-point limits do not change the input.
- The classification is displayed immediately; Previous / Next / Show all /
  Start over let you explore its evidence. Trial division stores the first
  200 checks plus a later factor-discovery check if needed. Omitted checks
  still execute and the screen explicitly reports the trace reduction.

The fixed-base reference is
[CP-Algorithms: Primality tests](https://cp-algorithms.com/algebra/primality_tests.html).

### Euler's Phi

Factor a positive integer up to `10^12`, display the successful divisions,
then apply `result = result // p * (p - 1)` once per distinct prime factor.
All arithmetic is exact. Repeated prime powers do not repeat a phi update.

Examples: `36 = 2^2 × 3^2` gives `36 → 18 → 12`; `81 = 3^4` gives 54;
`3233 = 53 × 61` gives `(53−1)(61−1) = 3120`. For `n ≤ 100`, the screen also
lists and counts the integers from 1 through n that are coprime to n.
The special case `φ(1) = 1` uses an empty prime-factor product.

### Work limits and testing

Trial division and phi factorization each have a configurable maximum of
100,000 divisibility checks. There is no wall-clock promise: this is a
deterministic operation budget. If exhausted, primality is **Unresolved**;
phi shows known factors and the unresolved cofactor, with no totient answer.
Some large inputs within the accepted range therefore cannot be completed
by these bounded trial methods. Miller–Rabin can still classify large inputs
within its own range but does not generally factor them.

No new dependencies are required. The full suite now contains 41 tests,
including independent sieve comparisons for 0–3000, direct coprime counting
for 1–500, pseudoprimes, exact large inputs, budget exhaustion and navigation
through all four screens. Run the test command below after installing Streamlit.

## Step 3 — extended Euclid and modular inverse

Choose **Extended Euclid & Inverse** in the sidebar. This screen includes two
modes: signed-integer Bézout identities, and modular inverses with modulus > 1.
Forward playback shows quotient, remainder and coefficient updates. At the end,
the backward trace substitutes each remainder into earlier divisions, collects
coefficients, and restores the signs of the original inputs.

Try the RSA example: `17 × (-367) + 3120 × 2 = 1`. Reducing `-367` modulo
`3120` gives the inverse `2753`. The app also verifies `(17 × 2753) mod 3120 = 1`.
For `6 mod 9`, there is no inverse, but the GCD and Bézout calculation remain
visible. Seven presets include negative and zero inputs. Changing inputs or
mode clears stale results; switching modules preserves each module's own
inputs, playback position and result in the current browser session.

The pure `core/back_substitution.py` helper reconstructs the backward trace
from the existing extended-GCD result. Equal numerical remainders are tracked
by their indices so they are not confused. `ui/inputs.py` shares integer
validation across the screens. No additional dependencies are needed for this
stage; the installation commands below apply to both screens.

## Step 2 — interactive GCD Visualizer

The first browser screen includes exact integer inputs, five examples, Previous /
Next / Show all / Start over controls, an accumulating division table, and a
short explanation of the mathematics and its RSA connection. Editing an input
clears the previous calculation. Negative numbers and zero are supported.

### Windows setup (Command Prompt)

Open a terminal inside your local DM-CP folder. Requires Python 3.11 or later:

```bat
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Streamlit opens a browser tab on your own laptop. If it does not open
automatically, use the local address printed in that terminal. Keep the terminal
running while using the app; press Ctrl+C to stop it. If Windows recognizes
`py` rather than `python`, use `py -m venv .venv` for the first command.

### Linux / macOS / cloud workspace

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

### Test the whole project

On Windows:

```bat
.venv\Scripts\python -m unittest discover -s tests -v
```

On Linux/macOS, replace `.venv\Scripts\python` with `.venv/bin/python`.
The UI tests use Streamlit AppTest to exercise actual widget interactions;
no browser driver is needed. Foundation-only tests still work without Streamlit:

```sh
python -m unittest discover -s tests -p test_foundation.py -v
```

Try the default 252 / 105 calculation: the three remainders are 42, 21, 0.
The final GCD is 21. Try loading the negative and zero examples, then enter
`2.5` to check validation. Reset clears the calculation but keeps your inputs;
Start over returns to the first step of the current calculation.

## Step 1 — mathematical foundation

Implemented using Python's standard library:

| Function | Purpose | Teaching trace |
| --- | --- | --- |
| `gcd(a, b)` | Greatest common divisor | Every Euclidean division |
| `extended_gcd(a, b)` | Find `g, x, y` with `ax + by = g` | Remainders and coefficients for original inputs |
| `modular_inverse(a, modulus)` | Find `x` with `ax ≡ 1 (mod m)` | Complete extended Euclid result |
| `modular_power(base, exponent, modulus)` | Efficient modular exponentiation | Each exponent bit and accumulator/base update |

All functions return immutable dataclass results with a `.value` field. GCD,
extended GCD and modular power have `.steps`; inverse has `.euclid.steps`.
Original inputs are preserved. Trace values are numbers that the UI displays
as equations or tables. The extended trace records coefficient updates;
the inverse screen also presents backward substitution.

### Run the examples

Requires Python 3.11 or later (tested with Python 3.12). No package installation
is needed for this milestone. In a terminal, enter the repository directory:

```sh
cd /workspace/DM-CP
python demo.py
python -m unittest discover -s tests -p test_foundation.py -v
```

On your own computer, replace `/workspace/DM-CP` with your checkout directory.
The test suite uses the standard-library `unittest` runner and can also be
collected by pytest when we add development dependencies.

The demo shows `gcd(252, 105) = 21`, the inverse `2753` of `17` modulo `3120`,
and `4^13 mod 497 = 445`.

### Use a function

```python
from core import modular_inverse

result = modular_inverse(17, 3120)
print(result.value)  # 2753
print(result.euclid.x, result.euclid.y)  # -367, 2
```

### Input rules

- Inputs must be Python integers; booleans, decimals and strings are rejected.
- GCD accepts negative numbers and zero; `gcd(0, 0) = 0` by convention.
- Extended Euclid coefficients always refer to the original signed inputs.
- Moduli must exceed one. Inverses require coprime inputs.
- Modular exponentiation accepts nonnegative exponents and negative bases.
  Exponent zero returns one, including `0^0`, following Python's convention.
- Invalid types raise `TypeError`; invalid mathematical inputs raise `ValueError`.

The core uses arbitrary-precision integers. The GCD UI enforces an absolute
input limit of 10¹⁸ to keep classroom calculations responsive. Text inputs and
string table cells preserve exact large integers through the browser.

## Next milestones

1. Add the CRT solver after the combined stage review.
2. Connect the algorithms into the RSA Lab and add bounded small-key factorization.
3. Polish the frontend, complete the report and prepare the classroom demo.

Educational textbook RSA, when added, is intended for
learning and must not be used to protect real secrets.
