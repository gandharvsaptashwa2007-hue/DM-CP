"""Bounded trial division and deterministic Miller–Rabin below 2**64."""

from dataclasses import dataclass
from math import isqrt

from .modular import modular_power
from .validation import require_integers

TRIAL_LIMIT = 10**12
UINT64_LIMIT = 2**64
DEFAULT_BUDGET = 100_000
TRACE_LIMIT = 200
# Deterministic for n < 2**64; not a guarantee for arbitrary-size integers.
# https://cp-algorithms.com/algebra/primality_tests.html
MR_BASES = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


@dataclass(frozen=True)
class TrialStep:
    divisor: int
    remainder: int


@dataclass(frozen=True)
class TrialResult:
    n: int
    status: str  # prime, composite, neither, or incomplete
    factor: int | None
    attempts: int
    steps: tuple[TrialStep, ...]
    reason: str


def trial_division(n: int, max_checks: int = DEFAULT_BUDGET) -> TrialResult:
    """Test 2 then odd divisors through isqrt(n), with a hard work budget.

    Retain the first 200 checks and a later factor-discovery check, if any.
    Exhausting the budget never reports a number as prime.
    """
    require_integers(n=n, max_checks=max_checks)
    if not 0 <= n <= TRIAL_LIMIT:
        raise ValueError("Trial division requires 0 ≤ n ≤ 10¹².")
    if not 1 <= max_checks <= DEFAULT_BUDGET:
        raise ValueError("Work budget must be between 1 and 100,000 checks.")
    if n < 2:
        return TrialResult(n, "neither", None, 0, (), "0 and 1 are neither prime nor composite.")
    divisor, attempts, steps = 2, 0, []
    bound = isqrt(n)
    while divisor <= bound:
        if attempts == max_checks:
            return TrialResult(n, "incomplete", None, attempts, tuple(steps), "Work budget reached; primality is unresolved. Try Miller–Rabin.")
        remainder = n % divisor
        attempts += 1
        if len(steps) < TRACE_LIMIT or remainder == 0:
            steps.append(TrialStep(divisor, remainder))
        if remainder == 0:
            return TrialResult(n, "composite", divisor, attempts, tuple(steps), f"{n} = {divisor} × {n // divisor}.")
        divisor = 3 if divisor == 2 else divisor + 2
    return TrialResult(n, "prime", None, attempts, tuple(steps), f"No divisor found through floor(√n) = {bound}; n is prime.")


@dataclass(frozen=True)
class MillerRabinRound:
    base: int
    reduced_base: int
    residues: tuple[int, ...]
    outcome: str  # passed, witness, skipped


@dataclass(frozen=True)
class MillerRabinResult:
    n: int
    status: str
    s: int
    d: int
    rounds: tuple[MillerRabinRound, ...]
    factor: int | None
    reason: str


def miller_rabin(n: int) -> MillerRabinResult:
    """Classify n exactly in [0, 2**64) using the seven fixed bases.

    One passed base is not proof of primality. Only passing all applicable
    fixed bases within this bounded domain establishes the prime result.
    """
    require_integers(n=n)
    if not 0 <= n < UINT64_LIMIT:
        raise ValueError("Miller–Rabin requires 0 ≤ n < 2⁶⁴.")
    if n < 2:
        return MillerRabinResult(n, "neither", 0, 0, (), None, "0 and 1 are neither prime nor composite.")
    if n in (2, 3):
        return MillerRabinResult(n, "prime", 0, 0, (), None, f"{n} is prime by direct inspection.")
    if n % 2 == 0:
        return MillerRabinResult(n, "composite", 0, 0, (), 2, f"{n} is even and greater than 2.")
    s, d = 0, n - 1
    while d % 2 == 0:
        s, d = s + 1, d // 2
    rounds = []
    for base in MR_BASES:
        reduced = base % n
        if reduced in (0, 1):
            rounds.append(MillerRabinRound(base, reduced, (), "skipped"))
            continue
        x = modular_power(reduced, d, n).value
        residues = [x]
        passed = x in (1, n - 1)
        if not passed:
            for _ in range(s - 1):
                x = x * x % n
                residues.append(x)
                if x == n - 1:
                    passed = True
                    break
                if x == 1:
                    break
        rounds.append(MillerRabinRound(base, reduced, tuple(residues), "passed" if passed else "witness"))
        if not passed:
            return MillerRabinResult(n, "composite", s, d, tuple(rounds), None, f"Base {base} is a witness proving that n is composite.")
    return MillerRabinResult(n, "prime", s, d, tuple(rounds), None, "All applicable fixed bases passed. This base set is deterministic for n < 2⁶⁴.")
