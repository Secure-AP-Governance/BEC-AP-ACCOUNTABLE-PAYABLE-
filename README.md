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

The repository contains the approved RC-1 operational governance baseline and the v0.2 advisory BEC intelligence pipeline:

- machine-verifiable security invariants;
- CI enforcement for those invariants;
- monitoring and governance requirements;
- recurring access, audit, backup, and incident-review procedures;
- a 30-day stabilization checklist.
- email capture with headers, attachments, and thread metadata;
- SPF, DKIM, and DMARC signal analysis;
- sender, domain, reply-to, and banking-request comparison;
- deterministic risk scoring with quarantine for high-risk messages;
- low-risk proposal creation through the existing RC-1 workflow;
- audit integration for email ingestion and quarantine decisions.

BEC intelligence is advisory only. An email may create a proposal or quarantine record, but it cannot update vendor data or execute a payment. The enforced path remains:

```text
Email -> Proposal / Quarantine -> Verification -> Approval -> ERP Update Request
```

The v0.3 operations surface currently provides read-only proposal and quarantine queues, audit exploration, and security-invariant status. It does not grant verification, approval, rejection, escalation, vendor-update, or payment authority.

The v0.3 Phase 2 worklist surface adds role-restricted verification and approval queues, evidence and risk detail views, audit linkage, evidence requests, rejection, and escalation. All actions continue through the RC-1 transition engine and preserve requester/verifier/approver separation of duties.

See [SECURITY_INVARIANTS.md](SECURITY_INVARIANTS.md) and [OPERATIONS.md](OPERATIONS.md).

## Local verification

```bash
python scripts/verify_invariants.py
python scripts/security_scan.py
python -m unittest discover -s tests -v
```

A production deployment must additionally provide authenticated runtime configuration, durable audit storage, monitoring, backup/recovery testing, and an approved change-management process. No production deployment is claimed by this commit.
