# Number Theory & RSA Playground

An educational project connecting Unit 5 number theory to RSA through visible
calculation steps. We are building this in small, working milestones.

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
Original inputs are preserved. Trace values are numbers that the future UI can
display as equations or tables. The extended trace records coefficient updates;
a separate back-substitution presentation will be added with the interface.

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

1. Add the extended Euclid / modular inverse screen after stage review.
2. Add primality, phi and CRT learning modules.
3. Connect the algorithms into the RSA Lab.
4. Add bounded small-key factorization and the classroom demo.

Educational textbook RSA, when added, is intended for
learning and must not be used to protect real secrets.
