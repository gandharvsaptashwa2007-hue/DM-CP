"""Euclid and extended Euclid, including signed inputs and zero."""

from dataclasses import dataclass

from .validation import require_integers


@dataclass(frozen=True)
class DivisionStep:
    dividend: int
    divisor: int
    quotient: int
    remainder: int


@dataclass(frozen=True)
class GCDResult:
    a: int
    b: int
    value: int
    steps: tuple[DivisionStep, ...]


def gcd(a: int, b: int) -> GCDResult:
    """Return the nonnegative GCD and divisions on absolute inputs.

    gcd(0, 0) is defined as zero by convention; no divisions are needed.
    """
    require_integers(a=a, b=b)
    left, right = abs(a), abs(b)
    steps = []
    while right:
        quotient, remainder = divmod(left, right)
        steps.append(DivisionStep(left, right, quotient, remainder))
        left, right = right, remainder
    return GCDResult(a, b, left, tuple(steps))


@dataclass(frozen=True)
class ExtendedStep:
    """One division and coefficients satisfying a*x + b*y = remainder."""

    dividend: int
    divisor: int
    quotient: int
    remainder: int
    x: int
    y: int


@dataclass(frozen=True)
class ExtendedGCDResult:
    a: int
    b: int
    value: int
    x: int
    y: int
    steps: tuple[ExtendedStep, ...]


def extended_gcd(a: int, b: int) -> ExtendedGCDResult:
    """Return g, x, y and a trace with a*x + b*y = g >= 0.

    Coefficients refer to original signed inputs. Each next coefficient
    pair is the dividend's pair minus quotient times the divisor's pair.
    For two zero inputs the result and both coefficients are zero.
    """
    require_integers(a=a, b=b)
    if a == b == 0:
        return ExtendedGCDResult(a, b, 0, 0, 0, ())
    left, right = abs(a), abs(b)
    old_x, x = (-1 if a < 0 else 1), 0
    old_y, y = 0, (-1 if b < 0 else 1)
    steps = []
    while right:
        quotient, remainder = divmod(left, right)
        next_x = old_x - quotient * x
        next_y = old_y - quotient * y
        steps.append(ExtendedStep(left, right, quotient, remainder, next_x, next_y))
        left, right = right, remainder
        old_x, x = x, next_x
        old_y, y = y, next_y
    return ExtendedGCDResult(a, b, left, old_x, old_y, tuple(steps))
