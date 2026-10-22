"""Bounded trial-factor attack accepting only public information."""

from dataclasses import dataclass
from time import perf_counter

from .primality import DEFAULT_BUDGET, TrialResult, miller_rabin, trial_division
from .rsa import decrypt_blocks, make_keys, validate_blocks, validate_public_key


@dataclass(frozen=True)
class AttackResult:
    status: str  # recovered, incomplete, unsupported, invalid_key
    reason: str
    trial: TrialResult
    elapsed_seconds: float
    p: int | None = None
    q: int | None = None
    phi: int | None = None
    d: int | None = None
    recovered: tuple[int, ...] | None = None


def break_key(e: int, n: int, ciphertext: list[int] | tuple[int, ...],
              max_checks: int = DEFAULT_BUDGET) -> AttackResult:
    """Recover an educational private key from (e,n) and ciphertext only.

    A fixed operation budget bounds trial division. Elapsed time measures this
    run, not a security estimate. Distinct odd primes must each be ≤ 10**6.
    """
    validate_public_key(e, n)
    blocks = validate_blocks(ciphertext, n)
    started = perf_counter()
    trial = trial_division(n, max_checks)
    if trial.status == "incomplete":
        return AttackResult("incomplete", "Not factored within the check budget; no private key was recovered.", trial, perf_counter() - started)
    if trial.factor is None:
        return AttackResult("unsupported", "n is not a product of two distinct supported odd primes.", trial, perf_counter() - started)
    p, q = trial.factor, n // trial.factor
    if p == q or p < 3 or q > 10**6 or miller_rabin(q).status != "prime":
        return AttackResult("unsupported", "Factorization found, but this lab requires two distinct odd primes, each at most 1,000,000.", trial, perf_counter() - started, p=p, q=q)
    try:
        keys = make_keys(p, q, e)
    except ValueError as error:
        return AttackResult("invalid_key", str(error), trial, perf_counter() - started, p=p, q=q, phi=(p - 1) * (q - 1))
    recovered = decrypt_blocks(blocks, keys.d, n)
    return AttackResult("recovered", "Factored n and reconstructed the private exponent from public data.", trial, perf_counter() - started, p, q, keys.phi, keys.d, recovered)
