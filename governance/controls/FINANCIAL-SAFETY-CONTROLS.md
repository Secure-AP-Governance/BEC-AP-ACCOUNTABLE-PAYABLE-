# Financial Safety Controls

## Control 1 — No automatic payment
The intelligence system may detect, classify, score, recommend, quarantine, or route an event. It must not execute a payment.

## Control 2 — No automatic bank change
The intelligence system may detect and propose a bank-detail change. It must not silently modify vendor master data.

## Control 3 — Human verification
Bank changes require independent verification.

## Control 4 — Dual approval
High-risk changes require the required independent approval roles.

## Control 5 — Auditability
Every material decision must be recorded.

## Control 6 — Rollback
Changes must be reversible through an authorized process.

## Verified repository baseline
- PAYMENT_EXECUTION_ENABLED = false
- AUTOMATIC_PAYMENT_DISPATCH = false
- AUTOMATIC_BANK_CHANGE = false

These values are enforced in `config/security_invariants.py` and validated by `scripts/verify_invariants.py`.
