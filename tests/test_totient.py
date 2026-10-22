"""Verify totients against coprime counts and factorization invariants."""

from math import gcd, prod
import unittest

from core import totient


class TotientTests(unittest.TestCase):
    def test_small_values_against_coprime_count(self):
        for n in range(1, 501):
            with self.subTest(n=n):
                result = totient(n)
                self.assertTrue(result.complete)
                self.assertEqual(result.unresolved, 1)
                self.assertEqual(result.value, sum(gcd(k, n) == 1 for k in range(1, n + 1)))
                self.assertEqual(prod(p**e for p, e in result.factors), n)
                self.assertEqual(len(result.steps), len(result.factors))
                current = n
                for step in result.factor_steps:
                    self.assertEqual(step.before, current)
                    self.assertEqual(step.before, step.prime * step.after)
                    # Independent small-factor primality check.
                    self.assertTrue(all(step.prime % d for d in range(2, step.prime)))
                    current = step.after
                self.assertEqual(current, 1)
                for step in result.steps:
                    self.assertEqual(step.before % step.prime, 0)
                    self.assertEqual(step.after, step.before // step.prime * (step.prime - 1))

    def test_rsa_prime_power_and_boundary_examples(self):
        for n, expected in ((1, 1), (13, 12), (36, 12), (81, 54), (3233, 3120),
                            (10**12, 400000000000)):
            self.assertEqual(totient(n).value, expected)
        self.assertEqual(totient(36).factors, ((2, 2), (3, 2)))
        self.assertEqual(totient(81).factors, ((3, 4),))
        self.assertEqual(len(totient(81).steps), 1)

    def test_unfinished_factorization_never_returns_phi(self):
        for n, budget in ((36, 1), (101, 1), (999983 * 999979, 100000)):
            result = totient(n, budget)
            self.assertFalse(result.complete)
            self.assertIsNone(result.value)
            self.assertEqual(result.steps, ())
            self.assertEqual(result.attempts, budget)
            self.assertEqual(prod(p**e for p, e in result.factors) * result.unresolved, n)
        # The remaining cofactor can be proven prime without another check.
        self.assertEqual(totient(6, 1).value, 2)

    def test_validation(self):
        for n in (0, -1, 10**12 + 1):
            with self.assertRaises(ValueError):
                totient(n)
        for invalid in (True, 36.0, "36", None):
            with self.assertRaises(TypeError):
                totient(invalid)
        for budget in (0, -1, 100001):
            with self.assertRaises(ValueError):
                totient(36, budget)
        with self.assertRaises(TypeError):
            totient(36, True)
