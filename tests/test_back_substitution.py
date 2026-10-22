"""Verify that every backward substitution preserves the GCD identity."""

import unittest

from core import extended_gcd
from core.back_substitution import back_substitute


class BackSubstitutionTests(unittest.TestCase):
    def test_signed_zero_and_equal_inputs(self):
        for a in range(-20, 21):
            for b in range(-20, 21):
                with self.subTest(a=a, b=b):
                    result = extended_gcd(a, b)
                    trace = back_substitute(result)
                    self.assertEqual((trace.x, trace.y), (result.x, result.y))
                    self.assertEqual(a * trace.x + b * trace.y, result.value)
                    previous = trace.initial
                    for step in trace.steps:
                        self.assertEqual(step.before, previous)
                        for expression in (step.before, step.after):
                            self.assertEqual(sum(trace.remainders[i] * coefficient for i, coefficient in expression), result.value)
                        self.assertLess(max(i for i, _ in step.after), step.index)
                        previous = step.after

    def test_rsa_example(self):
        trace = back_substitute(extended_gcd(17, 3120))
        self.assertEqual((trace.x, trace.y), (-367, 2))
        # Includes the initial 17 = 17 - 0*3120 substitution because a < b.
        self.assertEqual(len(trace.steps), 4)
        self.assertEqual(trace.remainders, (17, 3120, 17, 9, 8, 1, 0))

    def test_large_inputs(self):
        a, b = -(10**80 + 7), 10**60 + 11
        trace = back_substitute(extended_gcd(a, b))
        self.assertEqual(a * trace.x + b * trace.y, extended_gcd(a, b).value)
