"""Bounded prime factorization and Euler's totient with exact integer traces."""

from dataclasses import dataclass

from .primality import DEFAULT_BUDGET, TRIAL_LIMIT
from .validation import require_integers


@dataclass(frozen=True)
class FactorStep:
    before: int
    prime: int
    after: int
    reason: str


@dataclass(frozen=True)
class TotientStep:
    prime: int
    before: int
    after: int


@dataclass(frozen=True)
class TotientResult:
    n: int
    complete: bool
    factors: tuple[tuple[int, int], ...]
    unresolved: int
    attempts: int
    factor_steps: tuple[FactorStep, ...]
    steps: tuple[TotientStep, ...]
    value: int | None


def totient(n: int, max_checks: int = DEFAULT_BUDGET) -> TotientResult:
    """Factor n ≤ 10**12, then apply φ(n) = n ∏(1 - 1/p).

    Count each candidate divisibility check, including repeated prime powers.
    An unresolved cofactor at the budget limit yields no totient value.
    n=1 has an empty factorization and φ(1)=1.
    """
    require_integers(n=n, max_checks=max_checks)
    if not 1 <= n <= TRIAL_LIMIT:
        raise ValueError("Euler's phi requires 1 ≤ n ≤ 10¹².")
    if not 1 <= max_checks <= DEFAULT_BUDGET:
        raise ValueError("Work budget must be between 1 and 100,000 checks.")
    remaining, candidate, attempts = n, 2, 0
    factors = {}
    factor_steps = []
    while remaining > 1:
        if candidate * candidate > remaining:
            factors[remaining] = factors.get(remaining, 0) + 1
            factor_steps.append(FactorStep(remaining, remaining, 1, "All smaller possible factors were exhausted; this cofactor is prime."))
            remaining = 1
            break
        if attempts == max_checks:
            return TotientResult(n, False, tuple(factors.items()), remaining, attempts, tuple(factor_steps), (), None)
        attempts += 1
        if remaining % candidate == 0:
            quotient = remaining // candidate
            factors[candidate] = factors.get(candidate, 0) + 1
            factor_steps.append(FactorStep(remaining, candidate, quotient, "Exact division by the next prime factor."))
            remaining = quotient
        else:
            candidate = 3 if candidate == 2 else candidate + 2
    value, steps = n, []
    for prime in factors:
        next_value = value // prime * (prime - 1)
        steps.append(TotientStep(prime, value, next_value))
        value = next_value
    return TotientResult(n, True, tuple(factors.items()), 1, attempts, tuple(factor_steps), tuple(steps), value)
