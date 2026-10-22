"""Reconstruct Bézout's identity by substituting Euclidean remainders."""

from dataclasses import dataclass

from .gcd import ExtendedGCDResult

Terms = tuple[tuple[int, int], ...]  # (remainder index, coefficient)


@dataclass(frozen=True)
class SubstitutionStep:
    index: int
    quotient: int
    before: Terms
    after: Terms


@dataclass(frozen=True)
class BackSubstitution:
    remainders: tuple[int, ...]
    initial: Terms
    steps: tuple[SubstitutionStep, ...]
    x: int
    y: int


def back_substitute(result: ExtendedGCDResult) -> BackSubstitution:
    """Expand a result from extended_gcd back to its original signed inputs.

    r0 = |a|, r1 = |b|, and rj = r(j-2) - q*r(j-1). Indexed
    terms distinguish equal-valued remainders. Each substitution removes
    the largest remaining index, so the process terminates at r0 and r1.
    """
    remainders = (abs(result.a), abs(result.b), *(s.remainder for s in result.steps))
    if result.value == 0:
        return BackSubstitution(remainders, (), (), 0, 0)
    terms = {len(result.steps) if result.steps else 0: 1}
    initial = tuple(sorted(terms.items()))
    steps = []
    while max(terms) >= 2:
        index = max(terms)
        before = tuple(sorted(terms.items()))
        coefficient = terms.pop(index)
        quotient = result.steps[index - 2].quotient
        terms[index - 2] = terms.get(index - 2, 0) + coefficient
        terms[index - 1] = terms.get(index - 1, 0) - coefficient * quotient
        terms = {key: value for key, value in terms.items() if value}
        steps.append(SubstitutionStep(index, quotient, before, tuple(sorted(terms.items()))))
    x = terms.get(0, 0) * (-1 if result.a < 0 else 1)
    y = terms.get(1, 0) * (-1 if result.b < 0 else 1)
    return BackSubstitution(remainders, initial, tuple(steps), x, y)
