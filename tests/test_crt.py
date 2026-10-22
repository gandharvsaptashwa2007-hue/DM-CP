"""CRT examples, exhaustive small systems, and exact large products."""

from itertools import product
import unittest

from core import solve_crt


class CRTTests(unittest.TestCase):
    def test_classic_example_and_inverse_evidence(self):
        result = solve_crt(((2, 3), (3, 5), (2, 7)))
        self.assertEqual((result.value, result.period, result.total), (23, 105, 233))
        self.assertEqual([s.contribution for s in result.steps], [140, 63, 30])
        for step in result.steps:
            self.assertEqual(step.partial_product * step.inverse.value % step.modulus, 1)
            self.assertEqual(result.value % step.modulus, step.residue)

    def test_all_small_residues_against_brute_force(self):
        moduli = (3, 4, 5)
        for residues in product(*(range(m) for m in moduli)):
            result = solve_crt(tuple(zip(residues, moduli)))
            solutions = [n for n in range(60) if all(n % m == r for r, m in zip(residues, moduli))]
            self.assertEqual(solutions, [result.value])
            self.assertEqual(result.period, 60)

    def test_normalization_and_six_large_moduli(self):
        self.assertEqual(solve_crt(((-1, 3), (8, 5))).value, 8)
        moduli = (999983, 999979, 999961, 999959, 999953, 999931)
        target = 123456789012345678901234567890
        result = solve_crt(tuple((target % m, m) for m in moduli))
        self.assertEqual(result.value, target % result.period)
        self.assertGreater(result.period, 2**53)

    def test_reject_invalid_and_unsupported_systems(self):
        for equations in ((), ((1, 3),), ((1, 2),) * 7, ((1, 1), (2, 3)),
                          ((1, -3), (2, 5)), ((1, 1000001), (2, 5)), ((1,), (2, 3))):
            with self.assertRaises(ValueError):
                solve_crt(equations)
        for equations in (((1, 4), (3, 6)), ((1, 3), (1, 3))):
            with self.assertRaisesRegex(ValueError, "generalized CRT"):
                solve_crt(equations)
        for equations in (((True, 3), (2, 5)), ((1, 3.0), (2, 5))):
            with self.assertRaises(TypeError):
                solve_crt(equations)
        with self.assertRaises(TypeError):
            solve_crt("not equations")
