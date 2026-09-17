"""CI-friendly invariant verification command."""

from pathlib import Path
import sys

# Make direct execution reliable regardless of the runner's working-directory
# or PYTHONPATH configuration.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config.security_invariants import INVARIANTS, validate_invariants


if __name__ == "__main__":
    validate_invariants()
    for name, value in INVARIANTS.items():
        print(f"{name}={str(value).lower()}")
    print("SECURITY_INVARIANTS=PASS")
