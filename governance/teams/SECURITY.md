# Security Team

## Purpose
Provide security verification for BEC defenses, access controls, and release gating.

## Scope
- Threat detection and risk scoring
- Email sender/authentication checks
- Quarantine handling
- Secret and credential protection
- Audit integrity
- Release violation checks

## Responsibilities
- Verify the BEC detection controls exist and are enforced.
- Confirm suspicious vendor communication is quarantined or flagged.
- Verify high-risk changes cannot directly execute payments.
- Review secrets and credential handling.
- Validate rollback and audit logging.

## Required evidence
- Security test results
- Audit evidence
- Secret scan results
- Risk and quarantine flow evidence

## Approval criteria
- Required controls are present.
- No secret exposure exists.
- High-risk events cannot execute payment or modify vendor banking without review.

## Rejection criteria
- Sensitive credentials are exposed.
- Security checks are missing.
- Critical protections are bypassable.

## Reviewer identity
PENDING_EXTERNAL_EVIDENCE

## Approval timestamp
PENDING

## Approval status
PENDING

## Evidence references
- `config/security_invariants.py`
- `scripts/verify_invariants.py`
- `scripts/security_scan.py`
- `tests/test_security_invariants.py`

## Comments
Repository evidence shows the invariant and scan checks are present and currently passing, but formal team approval is not recorded in the repository.

## Signature / attestation
Status: PENDING
