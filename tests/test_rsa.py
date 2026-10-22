"""RSA key contracts, exact byte round trips and all residues of a small key."""

from unittest.mock import patch
import unittest

from core import modular_power, solve_crt
from core.rsa import make_keys, generate_keys, encode_text, decode_text, encrypt_blocks, decrypt_blocks
from ui.rsa_shared import parse_ciphertext


class RSATests(unittest.TestCase):
    def setUp(self):
        self.keys = make_keys(61, 53, 17)

    def test_classroom_keys_and_hello(self):
        k = self.keys
        self.assertEqual((k.n, k.phi, k.e, k.d), (3233, 3120, 17, 2753))
        ciphertext = encrypt_blocks(encode_text("HELLO", k.n), k.e, k.n)
        self.assertEqual(ciphertext, (3000, 28, 2726, 2726, 1307))
        self.assertEqual(decode_text(decrypt_blocks(ciphertext, k.d, k.n)), "HELLO")
        self.assertEqual(encrypt_blocks((65,), k.e, k.n), (2790,))

    def test_every_integer_block_including_non_coprime_values(self):
        for k in (make_keys(3, 5, 3), make_keys(5, 7, 5), self.keys):
            for start in range(0, k.n, 256):
                plain = tuple(range(start, min(start + 256, k.n)))
                cipher = encrypt_blocks(plain, k.e, k.n)
                self.assertEqual(decrypt_blocks(cipher, k.d, k.n), plain)
            for m in (0, k.p, k.q, k.n - 1):
                c = pow(m, k.e, k.n)
                combined = solve_crt(((modular_power(c, k.d, k.p).value, k.p),
                                     (modular_power(c, k.d, k.q).value, k.q)))
                self.assertEqual(combined.value, m)

    def test_unicode_empty_spaces_and_exact_byte_limit(self):
        k = self.keys
        for message in ("", " ", "\n\t\0", "hé 🔐 नमस्ते", "A" * 256, "🔐" * 64):
            blocks = encode_text(message, k.n)
            self.assertEqual(blocks, tuple(message.encode("utf-8")))
            self.assertEqual(decode_text(decrypt_blocks(encrypt_blocks(blocks, k.e, k.n), k.d, k.n)), message)
        for message in ("A" * 257, "🔐" * 65, "\ud800"):
            with self.assertRaises(ValueError):
                encode_text(message, k.n)

    def test_invalid_keys_and_blocks(self):
        for p, q, e in ((61, 61, 17), (60, 53, 17), (61, 51, 17), (2, 53, 17),
                        (1000001, 53, 17), (61, 53, 6), (61, 53, 1), (61, 53, 3120)):
            with self.assertRaises(ValueError):
                make_keys(p, q, e)
        for p, q, e in ((True, 53, 17), (61, 53.0, 17), (61, 53, True)):
            with self.assertRaises(TypeError):
                make_keys(p, q, e)
        for blocks in ((-1,), (3233,), (0,) * 257):
            with self.assertRaises(ValueError):
                encrypt_blocks(blocks, 17, 3233)
            with self.assertRaises(ValueError):
                decrypt_blocks(blocks, 2753, 3233)
        with self.assertRaises(TypeError):
            encrypt_blocks((True,), 17, 3233)
        for e, n in ((1, 3233), (3233, 3233), (17, 2), (17, 10**12 + 1)):
            with self.assertRaises(ValueError):
                encrypt_blocks((0,), e, n)
        with self.assertRaises(ValueError):
            decrypt_blocks((0,), 0, 3233)
        with self.assertRaises(ValueError):
            encode_text("A", 255)
        with self.assertRaises(ValueError):
            decode_text((256,))
        with self.assertRaises(ValueError):
            decode_text((255,))

    def test_random_generation_and_bounded_sampling(self):
        with patch("core.rsa.secrets.randbelow", side_effect=(0, 0, 1)):
            k = generate_keys("Small")
        self.assertEqual((k.p, k.q), (101, 103))
        self.assertEqual(k.e * k.d % k.phi, 1)
        self.assertEqual(make_keys(1009, 1013).e, 65537)
        with patch("core.rsa.secrets.randbelow", return_value=2):  # candidate 105 is composite
            with self.assertRaisesRegex(ValueError, "sampling limit"):
                generate_keys("Small")
        with self.assertRaises(ValueError):
            generate_keys("2048-bit")

    def test_ciphertext_parser(self):
        for text in ("3000, 28 2726", "[3000, 28, 2726]", "3000\n28\n2726"):
            self.assertEqual(parse_ciphertext(text, 3233), (3000, 28, 2726))
        self.assertEqual(parse_ciphertext("", 3233), ())
        for text in ("-1", "3233", "2.5", "abc", "1 " * 257, "0" * 8193):
            with self.assertRaises(ValueError):
                parse_ciphertext(text, 3233)
