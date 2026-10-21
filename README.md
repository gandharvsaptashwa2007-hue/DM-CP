# Number Theory & RSA Playground

An educational project connecting Unit 5 number theory to RSA through visible
calculation steps. We are building this in small, working milestones.

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
python -m unittest discover -s tests -v
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

The core uses arbitrary-precision integers. Interactive input limits will be
enforced by the UI to keep classroom calculations responsive.

## Next milestones

1. Build the interactive Streamlit GCD page with presets and step controls.
2. Add inverse, primality, phi and CRT learning modules.
3. Connect the algorithms into the RSA Lab.
4. Add bounded small-key factorization and the classroom demo.

There is no web UI yet. Educational textbook RSA, when added, is intended for
learning and must not be used to protect real secrets.
