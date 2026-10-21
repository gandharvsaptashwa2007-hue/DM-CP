"""Fast modular exponentiation using right-to-left repeated squaring."""

from dataclasses import dataclass

from .validation import require_integers


@dataclass(frozen=True)
class PowerStep:
    """Before/after state for one bit, starting at the least significant bit."""

    exponent_before: int
    bit: int
    base_before: int
    result_before: int
    result_after: int
    base_after: int
    exponent_after: int


@dataclass(frozen=True)
class PowerResult:
    base: int
    exponent: int
    modulus: int
    value: int
    steps: tuple[PowerStep, ...]


def modular_power(base: int, exponent: int, modulus: int) -> PowerResult:
    """Compute base**exponent modulo modulus without forming that power.

    Negative bases are normalized; exponents must be nonnegative and the
    modulus must exceed one. Exponent zero returns one with an empty trace,
    including base zero (the same convention as Python's pow).
    """
    require_integers(base=base, exponent=exponent, modulus=modulus)
    if modulus <= 1:
        raise ValueError("Modulus must be greater than 1.")
    if exponent < 0:
        raise ValueError("Exponent must be nonnegative.")
    factor, remaining, result = base % modulus, exponent, 1
    steps = []
    while remaining:
        bit = remaining % 2
        next_result = result * factor % modulus if bit else result
        next_factor = factor * factor % modulus
        next_exponent = remaining // 2
        steps.append(PowerStep(
            remaining, bit, factor, result, next_result, next_factor, next_exponent
        ))
        factor, remaining, result = next_factor, next_exponent, next_result
    return PowerResult(base, exponent, modulus, result, tuple(steps))
