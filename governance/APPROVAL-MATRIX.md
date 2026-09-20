# Approval Matrix

## Status definitions
- PASS: evidence exists and the gate has been independently verified.
- PENDING: evidence is required and not yet available.
- BLOCKED: a gate is prevented by an unresolved risk or missing required evidence.
- REJECTED: a gate has been formally rejected.
- PENDING_EXTERNAL_EVIDENCE: actual approval evidence is not available from the current environment.

| Gate | Owner | Required Evidence | Status |
|---|---|---|---|
| Security | Security Team | Security verification | PENDING |
| Identity | Identity Team | RBAC / SoD verification | PENDING |
| Operations | Operations Team | Operational readiness | PENDING |
| Infrastructure | Infrastructure Team | Infrastructure validation | PENDING |
| Business/AP | AP Owner | Business acceptance | PENDING |
| Release | Release Authority | Final release authorization | PENDING |

This matrix intentionally does not claim any approval without repository evidence.
