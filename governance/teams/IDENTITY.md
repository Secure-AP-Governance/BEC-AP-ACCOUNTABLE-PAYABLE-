# Identity Team

## Purpose
Validate authentication, authorization, and role separation.

## Scope
- Authentication mechanisms
- Authorization model
- Role separation and least privilege
- No self-approval / no shared approval credentials

## Responsibilities
- Confirm the system separates requester, verifier, approver, and release roles.
- Verify no single actor can execute the full payment-change path.
- Validate logging and privilege boundaries.

## Required evidence
- RBAC matrix
- Role assignment evidence
- Logging and access review evidence

## Approval criteria
- No shared approval credential
- No automatic privilege escalation
- Role separation exists and is enforceable

## Rejection criteria
- One actor can self-approve or self-verify
- Sensitive operations are not independently logged

## Reviewer identity
PENDING_EXTERNAL_EVIDENCE

## Approval timestamp
PENDING

## Approval status
PENDING

## Evidence references
- `src/workflow.py`
- `src/domain.py`
- `tests/test_runtime.py`

## Comments
The runtime workflow enforces independent roles for submit/verify/approve. Formal identity-team approval evidence is still pending.

## Signature / attestation
Status: PENDING
