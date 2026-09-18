# UAT and Security Review Plan

| Scenario | Expected result |
|---|---|
| Legitimate vendor change | Proposal follows verification, approval, and ERP-request path |
| Spoofed sender | Message is quarantined |
| Failed DMARC | Risk factor is recorded and score increases |
| Reply-to mismatch | Risk factor is recorded |
| Evidence request | Proposal moves to evidence-requested state and is audited |
| Escalation | Separate approver can escalate and the action is audited |
| Concurrent approval | Stale version is rejected |
| Audit tampering attempt | Audit validation fails and alert is raised |

Every scenario must demonstrate that vendor-master mutation, payment execution, and fund dispatch remain unavailable.