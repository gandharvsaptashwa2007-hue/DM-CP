"""Run the Step 1 examples with: python demo.py."""

from core import extended_gcd, gcd, modular_inverse, modular_power


def main() -> None:
    result = gcd(252, 105)
    print("Euclid: gcd(252, 105)")
    for step in result.steps:
        print(f"  {step.dividend} = {step.divisor} * {step.quotient} + {step.remainder}")
    print(f"GCD = {result.value}\n")

    extended = extended_gcd(17, 3120)
    print("Extended Euclid: remainder as a combination of original inputs")
    for step in extended.steps:
        print(f"  {step.remainder} = 17 * ({step.x}) + 3120 * ({step.y})")
    print(f"17 * ({extended.x}) + 3120 * ({extended.y}) = {extended.value}")
    print(f"Inverse of 17 mod 3120 = {modular_inverse(17, 3120).value}\n")

    power = modular_power(4, 13, 497)
    print("Repeated squaring: 4^13 mod 497")
    for step in power.steps:
        action = "multiply" if step.bit else "keep accumulator"
        print(f"  exponent={step.exponent_before}, base={step.base_before}: "
              f"{action}, result={step.result_after}; next base={step.base_after}")
    print(f"Result = {power.value}")


if __name__ == "__main__":
    main()
