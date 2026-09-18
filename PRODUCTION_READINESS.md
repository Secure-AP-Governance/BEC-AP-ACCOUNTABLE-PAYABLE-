# Production Readiness

## Release gate

The production-readiness branch must keep these controls false:

```text
PAYMENT_EXECUTION_ENABLED=false
AUTOMATIC_PAYMENT_DISPATCH=false
AUTOMATIC_BANK_CHANGE=false
```

## Implemented foundation

- expiring password-authenticated sessions;
- server-side role checks for all operations gateway actions;
- health status for security invariants and audit-chain integrity;
- metrics for queue volume, ERP requests, latency, failures, and authentication anomalies;
- alert evaluation for invariant, audit, workflow, BEC-risk, and authentication failures.

## Remaining release work

- integrate an approved SSO/MFA identity provider;
- replace in-memory stores with durable, encrypted persistence;
- connect metrics and alerts to monitored production services;
- complete backup and restoration testing;
- complete runbooks and UAT evidence;
- perform security review and penetration testing.

No production deployment is claimed by this branch.