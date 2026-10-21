"""Reference checks and mathematical invariants for the teaching algorithms."""

import math
import unittest

from core import extended_gcd, gcd, modular_inverse, modular_power


class EuclidTests(unittest.TestCase):
    def test_classroom_example(self):
        result = gcd(252, 105)
        self.assertEqual(result.value, 21)
        self.assertEqual([s.remainder for s in result.steps], [42, 21, 0])

    def test_signed_inputs_zero_and_trace_identities(self):
        for a in range(-20, 21):
            for b in range(-20, 21):
                with self.subTest(a=a, b=b):
                    plain, extended = gcd(a, b), extended_gcd(a, b)
                    self.assertEqual(plain.value, math.gcd(a, b))
                    self.assertEqual(extended.value, math.gcd(a, b))
                    self.assertEqual(a * extended.x + b * extended.y, extended.value)
                    for step in (*plain.steps, *extended.steps):
                        self.assertEqual(step.dividend, step.divisor * step.quotient + step.remainder)
                        self.assertTrue(0 <= step.remainder < step.divisor)
                    for step in extended.steps:
                        self.assertEqual(a * step.x + b * step.y, step.remainder)

    def test_large_integers(self):
        a, b = 10**100 + 7, 10**80 + 13
        result = extended_gcd(a, b)
        self.assertEqual(result.value, math.gcd(a, b))
        self.assertEqual(a * result.x + b * result.y, result.value)


class InverseTests(unittest.TestCase):
    def test_rsa_example(self):
        self.assertEqual(modular_inverse(17, 3120).value, 2753)

    def test_inverses_and_non_coprime_pairs(self):
        for modulus in range(2, 35):
            for a in range(-35, 36):
                with self.subTest(a=a, modulus=modulus):
                    if math.gcd(a, modulus) == 1:
                        result = modular_inverse(a, modulus)
                        self.assertEqual(result.value, pow(a, -1, modulus))
                        self.assertEqual(a * result.value % modulus, 1)
                        self.assertTrue(0 <= result.value < modulus)
                    else:
                        with self.assertRaisesRegex(ValueError, "No modular inverse"):
                            modular_inverse(a, modulus)


class PowerTests(unittest.TestCase):
    def test_classroom_and_rsa_examples(self):
        self.assertEqual(modular_power(4, 13, 497).value, 445)
        encrypted = modular_power(65, 17, 3233).value
        self.assertEqual(encrypted, 2790)
        self.assertEqual(modular_power(encrypted, 2753, 3233).value, 65)

    def test_reference_values_and_trace_invariant(self):
        for base in range(-8, 9):
            for exponent in range(17):
                for modulus in (2, 3, 7, 19, 497):
                    with self.subTest(base=base, exponent=exponent, modulus=modulus):
                        result = modular_power(base, exponent, modulus)
                        expected = pow(base, exponent, modulus)
                        self.assertEqual(result.value, expected)
                        self.assertEqual(len(result.steps), exponent.bit_length())
                        previous_result, previous_base, previous_exponent = 1, base % modulus, exponent
                        for step in result.steps:
                            self.assertEqual((step.result_before, step.base_before, step.exponent_before),
                                             (previous_result, previous_base, previous_exponent))
                            # After each step, accumulator * remaining power is unchanged modulo m.
                            self.assertEqual(step.result_after * pow(step.base_after, step.exponent_after, modulus) % modulus, expected)
                            previous_result, previous_base, previous_exponent = step.result_after, step.base_after, step.exponent_after

    def test_zero_exponent_and_large_exponent(self):
        result = modular_power(0, 0, 13)
        self.assertEqual(result.value, 1)
        self.assertEqual(result.steps, ())
        self.assertEqual(modular_power(-123, 10**30, 3233).value, pow(-123, 10**30, 3233))


class ValidationTests(unittest.TestCase):
    def test_invalid_moduli_and_exponents(self):
        for modulus in (-9, 0, 1):
            with self.assertRaises(ValueError):
                modular_inverse(17, modulus)
            with self.assertRaises(ValueError):
                modular_power(4, 13, modulus)
        with self.assertRaises(ValueError):
            modular_power(4, -1, 7)

    def test_reject_non_integer_arguments(self):
        for function, args in ((gcd, [4, 7]), (extended_gcd, [4, 7]),
                               (modular_inverse, [4, 7]), (modular_power, [4, 13, 7])):
            for index in range(len(args)):
                for invalid in (True, 1.5, "17", None):
                    changed = args.copy()
                    changed[index] = invalid
                    with self.subTest(function=function.__name__, index=index, invalid=invalid):
                        with self.assertRaises(TypeError):
                            function(*changed)


if __name__ == "__main__":
    unittest.main()
