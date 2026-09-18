# Release Validation Workstream

Branch: `feature/release-validation`

This workstream collects evidence for UAT, recovery validation, security review, and the v1.0 go-live decision. Passing automated tests does not by itself approve production deployment.

## Automated evidence

Run:

```bash
python -m unittest discover -s tests -v
python scripts/verify_invariants.py
python scripts/security_scan.py
```

The release-validation scenarios cover legitimate workflow completion, spoofed sender quarantine, failed DMARC, reply-to mismatch, evidence requests, escalation, concurrent version conflicts, audit tampering detection, and immutable controls.

## Gate tracker

| Gate | Status | Evidence owner | Evidence |
|---|---|---|---|
| Authentication and authorization | Foundation implemented | Application owner | `tests/test_production_readiness.py` |
| Audit integrity and separation of duties | Automated pass | Security owner | `tests/test_release_validation.py` |
| Immutable security controls | Automated pass | Security owner | Invariant and scan output |
| Legitimate vendor-change UAT | Automated scenario ready | UAT owner | `tests/test_release_validation.py` |
| High-risk BEC UAT | Automated scenario ready | Fraud owner | `tests/test_release_validation.py` |
| Backup restoration evidence | Pending | Operations owner | Attach restoration record |
| Monitoring and alert routing | Pending integration | Operations owner | Attach alert receipt |
| SSO/MFA enterprise integration | Pending | Identity owner | Attach provider validation |
| Penetration testing | Pending | Security owner | Attach signed findings |
| Threat-model and RBAC review | Pending | Security owner | Attach review record |
| UAT sign-off | Pending | Business owner | Attach approved UAT report |

## Go-live rule

Do not approve v1.0 while any mandatory gate is pending, any invariant is unavailable, or any workflow can update vendor data or execute a payment outside the controlled ERP request boundary.