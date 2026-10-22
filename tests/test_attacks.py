"""Public-information-only key recovery and bounded failure behavior."""

import unittest

from core.attacks import break_key
from core.rsa import decode_text


class AttackTests(unittest.TestCase):
    def test_recover_hello_from_public_information(self):
        result = break_key(17, 3233, (3000, 28, 2726, 2726, 1307))
        self.assertEqual(result.status, "recovered")
        self.assertEqual((result.p, result.q, result.phi, result.d), (53, 61, 3120, 2753))
        self.assertEqual(decode_text(result.recovered), "HELLO")
        self.assertGreaterEqual(result.elapsed_seconds, 0)
        self.assertEqual(result.trial.steps[-1].remainder, 0)

    def test_integer_empty_and_exact_budget(self):
        self.assertEqual(break_key(17, 3233, (2790,)).recovered, (65,))
        self.assertEqual(break_key(17, 3233, ()).recovered, ())
        self.assertEqual(break_key(17, 3233, (), 27).status, "recovered")
        result = break_key(17, 3233, (), 26)
        self.assertEqual(result.status, "incomplete")
        self.assertIsNone(result.d)
        self.assertIsNone(result.recovered)

    def test_larger_key_exhausts_budget(self):
        result = break_key(65537, 999983 * 999979, (1,))
        self.assertEqual(result.status, "incomplete")
        self.assertEqual(result.trial.attempts, 100000)
        self.assertIsNone(result.d)

    def test_unsupported_moduli_and_invalid_exponent(self):
        for n in (13, 49, 30, 12):
            self.assertEqual(break_key(5, n, (1,)).status, "unsupported")
        result = break_key(6, 3233, (1,))
        self.assertEqual(result.status, "invalid_key")
        self.assertIsNone(result.d)
        self.assertIsNone(result.recovered)
        with self.assertRaises(ValueError):
            break_key(17, 3233, (3233,))
        with self.assertRaises(TypeError):
            break_key(True, 3233, (1,))
