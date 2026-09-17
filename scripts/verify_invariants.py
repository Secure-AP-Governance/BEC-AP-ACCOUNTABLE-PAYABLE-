"""CI-friendly invariant verification command."""

from config.security_invariants import INVARIANTS, validate_invariants


if __name__ == "__main__":
    validate_invariants()
    for name, value in INVARIANTS.items():
        print(f"{name}={str(value).lower()}")
    print("SECURITY_INVARIANTS=PASS")
