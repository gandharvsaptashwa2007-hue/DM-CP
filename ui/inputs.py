"""Exact integer entry shared by the learning screens."""

import re

LIMIT = 10**18


def parse_integer(text: str, label: str, *, limit: int = LIMIT) -> int:
    """Parse bounded decimal integers without browser numeric rounding."""
    value = text.strip()
    if not re.fullmatch(r"[+-]?[0-9]+", value):
        raise ValueError(f"{label}: enter a whole number, such as 252 or -105.")
    digits = value.lstrip("+-").lstrip("0") or "0"
    if len(digits) > len(str(limit)):
        raise ValueError(f"{label}: use a value between {-limit} and {limit}.")
    number = int(digits) * (-1 if value.startswith("-") else 1)
    if abs(number) > limit:
        raise ValueError(f"{label}: use a value between {-limit} and {limit}.")
    return number
