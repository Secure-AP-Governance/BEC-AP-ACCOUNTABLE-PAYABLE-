# BEC AP Accountable Payable

Operational governance baseline for a proposal, verification, approval, audit, and ERP-request workflow.

## Safety boundary

This repository intentionally does **not** execute payments, dispatch wires/ACH, or update vendor master data automatically. The workflow may create an ERP update request, but a separate controlled ERP process must perform any eventual change.

Locked release invariants:

```text
PAYMENT_EXECUTION_ENABLED=false
AUTOMATIC_PAYMENT_DISPATCH=false
AUTOMATIC_BANK_CHANGE=false
```

## Operational phase

The repository currently contains the operational governance baseline:

- machine-verifiable security invariants;
- CI enforcement for those invariants;
- monitoring and governance requirements;
- recurring access, audit, backup, and incident-review procedures;
- a 30-day stabilization checklist.

See [SECURITY_INVARIANTS.md](SECURITY_INVARIANTS.md) and [OPERATIONS.md](OPERATIONS.md).

## Local verification

```bash
python scripts/verify_invariants.py
python -m unittest discover -s tests -v
```

A production deployment must additionally provide authenticated runtime configuration, durable audit storage, monitoring, backup/recovery testing, and an approved change-management process. No production deployment is claimed by this commit.
