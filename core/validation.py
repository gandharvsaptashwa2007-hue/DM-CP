"""Shared validation for the mathematical API (UI limits belong in the UI)."""


def require_integers(**values: int) -> None:
    for name, value in values.items():
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(f"{name} must be an integer.")
