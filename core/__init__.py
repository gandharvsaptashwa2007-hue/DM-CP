"""Exact number-theory algorithms with immutable teaching traces."""

from .gcd import extended_gcd, gcd
from .inverse import modular_inverse
from .modular import modular_power
from .primality import miller_rabin, trial_division
from .totient import totient
from .crt import solve_crt

__all__ = ["gcd", "extended_gcd", "modular_inverse", "modular_power", "miller_rabin", "trial_division", "totient", "solve_crt"]
