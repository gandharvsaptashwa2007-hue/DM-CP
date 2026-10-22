"""Educational, unpadded RSA. Never use this module for real secrets."""

from dataclasses import dataclass
from math import gcd
import secrets

from .inverse import InverseResult, modular_inverse
from .modular import modular_power
from .primality import miller_rabin
from .validation import require_integers

MAX_PRIME = 10**6
MAX_MODULUS = MAX_PRIME**2
MAX_BLOCKS = 256
PRIME_RANGES = {"Small": (101, 997), "Medium": (1009, 9973), "Larger": (100003, 999983)}


@dataclass(frozen=True)
class RSAKeys:
    p: int
    q: int
    n: int
    phi: int
    e: int
    d: int
    inverse: InverseResult


def make_keys(p: int, q: int, e: int | None = None) -> RSAKeys:
    """Validate distinct odd educational primes and derive both exponents."""
    require_integers(p=p, q=q)
    for name, value in (("p", p), ("q", q)):
        if not 3 <= value <= MAX_PRIME:
            raise ValueError(f"{name} must be a prime between 3 and 1,000,000.")
        if miller_rabin(value).status != "prime":
            raise ValueError(f"{name} = {value} is not prime.")
    if p == q:
        raise ValueError("p and q must be distinct primes.")
    n, phi = p * q, (p - 1) * (q - 1)
    if e is None:
        e = 65537 if 65537 < phi and gcd(65537, phi) == 1 else 3
        while e < phi and gcd(e, phi) != 1:
            e += 2
    require_integers(e=e)
    if not 1 < e < phi:
        raise ValueError(f"Public exponent e must satisfy 1 < e < φ(n) = {phi}.")
    if gcd(e, phi) != 1:
        raise ValueError(f"gcd({e}, {phi}) = {gcd(e, phi)}; choose an exponent coprime to φ(n).")
    inverse = modular_inverse(e, phi)
    return RSAKeys(p, q, n, phi, e, inverse.value, inverse)


def generate_keys(size: str = "Small") -> RSAKeys:
    """Sample primes with secrets; bound the number of attempts per prime."""
    if size not in PRIME_RANGES:
        raise ValueError("Choose Small, Medium or Larger educational primes.")
    low, high = PRIME_RANGES[size]
    primes = []
    for _ in range(2):
        for _ in range(1000):
            candidate = low + 2 * secrets.randbelow((high - low) // 2 + 1)
            if candidate not in primes and miller_rabin(candidate).status == "prime":
                primes.append(candidate)
                break
        else:
            raise ValueError("Prime sampling limit reached; try generating again.")
    return make_keys(*primes)


def validate_public_key(e: int, n: int) -> None:
    require_integers(e=e, n=n)
    if not 3 <= n <= MAX_MODULUS:
        raise ValueError("Modulus n must be between 3 and 10¹².")
    if not 1 < e < n:
        raise ValueError("Public exponent must satisfy 1 < e < n.")


def validate_blocks(blocks: list[int] | tuple[int, ...], n: int) -> tuple[int, ...]:
    require_integers(n=n)
    if not 3 <= n <= MAX_MODULUS:
        raise ValueError("Modulus n must be between 3 and 10¹².")
    if not isinstance(blocks, (list, tuple)):
        raise TypeError("Blocks must be a list or tuple of integers.")
    if len(blocks) > MAX_BLOCKS:
        raise ValueError("Use at most 256 blocks.")
    for index, value in enumerate(blocks):
        require_integers(block=value)
        if not 0 <= value < n:
            raise ValueError(f"Block {index + 1} must satisfy 0 ≤ value < n = {n}.")
    return tuple(blocks)


def encode_text(text: str, n: int) -> tuple[int, ...]:
    if not isinstance(text, str):
        raise TypeError("Message must be text.")
    require_integers(n=n)
    if not 255 < n <= MAX_MODULUS:
        raise ValueError("UTF-8 text mode requires 255 < n ≤ 10¹².")
    try:
        data = text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("Message contains an invalid Unicode character.") from error
    if len(data) > MAX_BLOCKS:
        raise ValueError("Text must fit in 256 UTF-8 bytes (some characters use several bytes).")
    return tuple(data)


def decode_text(blocks: list[int] | tuple[int, ...]) -> str:
    if not isinstance(blocks, (list, tuple)):
        raise TypeError("Blocks must be a list or tuple of integers.")
    if len(blocks) > MAX_BLOCKS:
        raise ValueError("Use at most 256 bytes.")
    for value in blocks:
        require_integers(block=value)
        if not 0 <= value <= 255:
            raise ValueError("Recovered blocks are not valid bytes (0–255); check the key, ciphertext or message mode.")
    try:
        return bytes(blocks).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Recovered bytes are not valid UTF-8; check the key, ciphertext or message mode.") from error


def encrypt_blocks(blocks: list[int] | tuple[int, ...], e: int, n: int) -> tuple[int, ...]:
    validate_public_key(e, n)
    return tuple(modular_power(value, e, n).value for value in validate_blocks(blocks, n))


def decrypt_blocks(blocks: list[int] | tuple[int, ...], d: int, n: int) -> tuple[int, ...]:
    require_integers(d=d)
    validated = validate_blocks(blocks, n)
    if not 1 <= d < n:
        raise ValueError("Private exponent must satisfy 1 ≤ d < n.")
    return tuple(modular_power(value, d, n).value for value in validated)
