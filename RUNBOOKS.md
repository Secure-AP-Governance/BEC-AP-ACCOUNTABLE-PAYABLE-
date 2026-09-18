# Operational Runbooks

## Incident response

1. Freeze release or affected processing when an invariant, audit, or authentication alert fires.
2. Preserve application logs, audit events, queue state, and alert context.
3. Confirm that no vendor-master or payment side effect occurred.
4. Escalate to security and fraud operations.
5. Restore only after remediation, validation, and recorded approval.

## Fraud escalation

1. Keep the message quarantined.
2. Preserve headers, authentication results, attachments, thread data, and risk factors.
3. Escalate to an independent verifier and fraud owner.
4. Do not update vendor data or execute a payment from the case.

## Quarantine review

1. Review the risk score, failed authentication signals, sender comparison, and reply-to relationship.
2. Link the quarantine record to any resulting proposal.
3. Require independent verification and approval before an ERP update request.

## Recovery and rollback

1. Declare the recovery event and record the affected commit/configuration.
2. Restore the database and audit archive into an isolated environment.
3. Verify audit chains and immutable security controls.
4. Run the complete test and invariant suite.
5. Roll back only through the approved change process.