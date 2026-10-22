"""Independent sieve checks, pseudoprimes, range limits and trace identities."""

from math import isqrt
import unittest

from core import miller_rabin, trial_division
from core.primality import MR_BASES, TRACE_LIMIT, UINT64_LIMIT


def sieve(limit):
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for prime in range(2, isqrt(limit) + 1):
        if flags[prime]:
            for multiple in range(prime * prime, limit + 1, prime):
                flags[multiple] = False
    return flags


class PrimalityTests(unittest.TestCase):
    def test_both_methods_against_independent_sieve(self):
        for n, is_prime in enumerate(sieve(3000)):
            with self.subTest(n=n):
                expected = "neither" if n < 2 else "prime" if is_prime else "composite"
                for result in (trial_division(n), miller_rabin(n)):
                    self.assertEqual(result.status, expected)
                    if result.factor is not None:
                        self.assertEqual(n % result.factor, 0)
                        self.assertTrue(1 < result.factor < n)

    def test_miller_rabin_known_large_primes_and_pseudoprimes(self):
        for prime in (2**61 - 1, 18446744073709551557):
            self.assertEqual(miller_rabin(prime).status, "prime")
        for composite in (561, 1105, 1729, 2047, 3215031751, 341550071728321,
                          3825123056546413051, UINT64_LIMIT - 1):
            self.assertEqual(miller_rabin(composite).status, "composite")
        result = miller_rabin(2047)
        self.assertEqual(result.rounds[0].outcome, "passed")
        self.assertEqual(result.rounds[-1].outcome, "witness")

    def test_miller_rabin_residue_chains_and_skips(self):
        saw_skip = False
        for n in (5, 13, 97, 193, 561, 2047, 18446744073709551557):
            result = miller_rabin(n)
            self.assertEqual(n - 1, 2**result.s * result.d)
            self.assertEqual(result.d % 2, 1)
            for round_ in result.rounds:
                self.assertEqual(round_.reduced_base, round_.base % n)
                if round_.outcome == "skipped":
                    saw_skip = True
                    self.assertIn(round_.reduced_base, (0, 1))
                    self.assertEqual(round_.residues, ())
                    continue
                self.assertEqual(round_.residues[0], pow(round_.reduced_base, result.d, n))
                for before, after in zip(round_.residues, round_.residues[1:]):
                    self.assertEqual(after, before * before % n)
                passed = round_.residues[0] == 1 or n - 1 in round_.residues
                self.assertEqual(round_.outcome, "passed" if passed else "witness")
            if result.status == "prime":
                self.assertEqual(tuple(r.base for r in result.rounds), MR_BASES)
        self.assertTrue(saw_skip)

    def test_trial_budget_is_not_a_prime_verdict(self):
        result = trial_division(101, max_checks=1)
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.attempts, 1)
        self.assertIsNone(result.factor)
        self.assertEqual(trial_division(49, max_checks=4).factor, 7)
        self.assertEqual(trial_division(5, max_checks=1).status, "prime")

    def test_trial_trace_is_bounded_and_keeps_late_factor(self):
        prime = trial_division(1000003)
        self.assertEqual(prime.status, "prime")
        self.assertGreater(prime.attempts, TRACE_LIMIT)
        self.assertEqual(len(prime.steps), TRACE_LIMIT)
        composite = trial_division(401 * 409)
        self.assertEqual(composite.factor, 401)
        self.assertEqual(len(composite.steps), TRACE_LIMIT + 1)
        self.assertEqual(composite.steps[-1].remainder, 0)
        for step in composite.steps:
            self.assertEqual(step.remainder, composite.n % step.divisor)

    def test_validation(self):
        for function in (trial_division, miller_rabin):
            for invalid in (True, 2.5, "97", None):
                with self.assertRaises(TypeError):
                    function(invalid)
            with self.assertRaises(ValueError):
                function(-1)
        with self.assertRaises(ValueError):
            miller_rabin(UINT64_LIMIT)
        with self.assertRaises(ValueError):
            trial_division(10**12 + 1)
        for budget in (0, -1, 100001):
            with self.assertRaises(ValueError):
                trial_division(97, budget)
        with self.assertRaises(TypeError):
            trial_division(97, True)
