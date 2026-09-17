# Security Invariants

These controls are permanent release blockers. They must remain false in source configuration, CI, runtime health checks, and deployment configuration.

| Invariant | Required value | Meaning |
|---|---:|---|
| `PAYMENT_EXECUTION_ENABLED` | `false` | No payment execution capability |
| `AUTOMATIC_PAYMENT_DISPATCH` | `false` | No automatic wire, ACH, or payment dispatch |
| `AUTOMATIC_BANK_CHANGE` | `false` | No automatic vendor banking/master-data change |

## Enforcement

`config/security_invariants.py` is the single source of truth for this baseline. `scripts/verify_invariants.py` exits non-zero if a value is anything other than the boolean `False`. CI runs this check on every push and pull request.

Any future service that handles email, risk scoring, proposals, or ERP requests must terminate at `PROPOSAL`, `QUARANTINE`, or `ERP_UPDATE_REQUESTED`. It must not call a payment executor or mutate vendor master/bank data.

## Release gate

A release is **NO-GO** if any invariant is true, missing, dynamically overridden, or not verifiable. This check does not replace security review, access certification, penetration testing, or operational approval.
