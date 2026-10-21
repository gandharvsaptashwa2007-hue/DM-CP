"""Exact number-theory algorithms with immutable teaching traces."""

from .gcd import extended_gcd, gcd
from .inverse import modular_inverse
from .modular import modular_power

__all__ = ["gcd", "extended_gcd", "modular_inverse", "modular_power"]
