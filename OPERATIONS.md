# Operational Governance

## Operating objectives

Monitor the workflow without expanding its authority:

- proposal and ERP-request volume;
- quarantine volume and release rate;
- verification and approval turnaround time;
- risk-score distribution and threshold changes;
- false-positive and false-negative investigations;
- audit-chain validation failures;
- authentication, authorization, and version-conflict failures.

## Required dashboards and alerts

| Signal | Review cadence | Alert condition |
|---|---|---|
| Security invariants | Every deployment and daily | Any value is `true` or unavailable |
| Audit integrity | Continuous/daily report | Any chain validation failure |
| Quarantine volume | Daily | Sudden surge or backlog breach |
| Verification/approval latency | Daily | SLA breach |
| RBAC failures | Daily | Unexpected permission pattern |
| Backup status | Daily | Failed or unverified backup |
| Access certification | Monthly/quarterly | Unreviewed privileged access |

## Governance cadence

### Daily

- Review security and audit alerts.
- Review quarantine backlog and high-risk cases.
- Confirm failed jobs are triaged without bypassing four-eyes controls.

### Monthly

- Review role assignments and dormant accounts.
- Review risk thresholds and operational metrics.
- Sample audit histories from proposal through ERP request.

### Quarterly

- Certify privileged access.
- Verify backup restoration and disaster-recovery procedures.
- Reassess threat model and separation-of-duties controls.
- Review dependencies and security findings.

### After every material change

- Run invariant tests and integration tests.
- Review changed data flows for vendor/payment side effects.
- Obtain security and change-management approval before release.

## 30-day stabilization checklist

- [ ] Monitoring and alert routing confirmed.
- [ ] On-call and fraud-escalation ownership assigned.
- [ ] Baseline proposal, quarantine, and ERP-request volumes recorded.
- [ ] False-positive and false-negative review process started.
- [ ] Backup restore test completed and documented.
- [ ] Audit-chain verification report reviewed.
- [ ] Monthly RBAC review scheduled.
- [ ] No automatic vendor update or payment path discovered.

## Incident response

If an invariant is true, unavailable, or cannot be independently verified:

1. Stop release or suspend affected workflow processing.
2. Preserve logs and audit evidence.
3. Notify security, application ownership, and fraud operations.
4. Determine whether any vendor or payment side effect occurred.
5. Remediate, test, and obtain written approval before resuming.

Never resolve an incident by weakening the invariant or bypassing verification/approval separation.
