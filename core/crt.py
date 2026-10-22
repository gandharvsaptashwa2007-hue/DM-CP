"""Chinese remainder theorem for two to six pairwise coprime moduli."""

from dataclasses import dataclass
from math import prod

from .gcd import gcd
from .inverse import InverseResult, modular_inverse
from .validation import require_integers


@dataclass(frozen=True)
class CRTStep:
    original_residue: int
    residue: int
    modulus: int
    partial_product: int
    inverse: InverseResult
    contribution: int


@dataclass(frozen=True)
class CRTResult:
    value: int
    period: int
    total: int
    steps: tuple[CRTStep, ...]


def solve_crt(equations: list[tuple[int, int]] | tuple[tuple[int, int], ...]) -> CRTResult:
    """Solve x ≡ a_i (mod m_i), normalizing residues and returning 0 ≤ x < N.

    This elementary solver intentionally rejects non-coprime moduli, including
    compatible systems that would require generalized CRT.
    """
    if not isinstance(equations, (list, tuple)):
        raise TypeError("Equations must be a list or tuple of (residue, modulus) pairs.")
    if not 2 <= len(equations) <= 6:
        raise ValueError("Enter between 2 and 6 congruences.")
    normalized = []
    for index, pair in enumerate(equations, 1):
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError(f"Equation {index} must contain a residue and a modulus.")
        residue, modulus = pair
        require_integers(residue=residue, modulus=modulus)
        if not 2 <= modulus <= 10**6:
            raise ValueError(f"Equation {index}: modulus must be between 2 and 1,000,000.")
        for previous_index, (_, previous_modulus) in enumerate(normalized, 1):
            common = gcd(modulus, previous_modulus).value
            if common != 1:
                raise ValueError(
                    f"Equations {previous_index} and {index} have moduli with GCD {common}. "
                    "This solver requires pairwise coprime moduli. This does not imply "
                    "that the system has no solution; generalized CRT is not supported."
                )
        normalized.append((residue, modulus))
    period = prod(modulus for _, modulus in normalized)
    steps = []
    for original, modulus in normalized:
        residue = original % modulus
        partial = period // modulus
        inverse = modular_inverse(partial, modulus)
        steps.append(CRTStep(original, residue, modulus, partial, inverse, residue * partial * inverse.value))
    total = sum(step.contribution for step in steps)
    return CRTResult(total % period, period, total, tuple(steps))
