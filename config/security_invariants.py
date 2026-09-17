"""Locked safety invariants for the accountable-payables workflow.

Keep these as literal booleans. Do not read them from an untrusted environment
variable or permit runtime overrides without an explicit security review.
"""

PAYMENT_EXECUTION_ENABLED = False
AUTOMATIC_PAYMENT_DISPATCH = False
AUTOMATIC_BANK_CHANGE = False

INVARIANTS = {
    "PAYMENT_EXECUTION_ENABLED": PAYMENT_EXECUTION_ENABLED,
    "AUTOMATIC_PAYMENT_DISPATCH": AUTOMATIC_PAYMENT_DISPATCH,
    "AUTOMATIC_BANK_CHANGE": AUTOMATIC_BANK_CHANGE,
}


def validate_invariants() -> None:
    """Raise if the locked safety boundary is not intact."""
    invalid = [name for name, value in INVARIANTS.items() if value is not False]
    if invalid:
        raise RuntimeError(f"Security invariants violated: {', '.join(invalid)}")
