"""Modular inverses obtained from the extended Euclidean algorithm."""

from dataclasses import dataclass

from .gcd import ExtendedGCDResult, extended_gcd
from .validation import require_integers


@dataclass(frozen=True)
class InverseResult:
    a: int
    modulus: int
    value: int
    euclid: ExtendedGCDResult


def modular_inverse(a: int, modulus: int) -> InverseResult:
    """Return the inverse in [0, modulus), or raise ValueError if absent."""
    require_integers(a=a, modulus=modulus)
    if modulus <= 1:
        raise ValueError("Modulus must be greater than 1.")
    result = extended_gcd(a, modulus)
    if result.value != 1:
        raise ValueError(
            f"No modular inverse: gcd({a}, {modulus}) = {result.value}, not 1."
        )
    return InverseResult(a, modulus, result.x % modulus, result)
