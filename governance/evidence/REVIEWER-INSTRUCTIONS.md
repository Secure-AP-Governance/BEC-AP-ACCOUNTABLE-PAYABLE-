# Reviewer Instructions

Each reviewer must be an authorized member of the assigned governance function and must independently verify the evidence for their gate before recording any decision.

## Required review record
Each reviewer must record all of the following in their review artifact:
- identity
- role
- date/time
- decision
- evidence references
- verification performed
- findings
- exceptions
- approval/signature reference

## Independence requirement
A reviewer must not approve a gate based solely on another team’s approval. A reviewer must not approve documentation that merely claims evidence exists. A reviewer must not approve without inspecting the required evidence. The gate must be assessed using project evidence, current repository state, and direct review of the relevant artifacts.

## Required decision values
Use only the following values when recording a decision:
- PASS
- PENDING
- PENDING_EXTERNAL_EVIDENCE
- BLOCKED
- REJECTED

## Evidence handling rules
- Reviewers must identify the exact commit or release being reviewed.
- Do not fabricate signatures, review dates, or approvals.
- Do not record a PASS without evidence references.
- If evidence is incomplete, the correct decision is PENDING_EXTERNAL_EVIDENCE.
- If the control fails, the decision must identify the failure and remain non-approved.
- Do not approve a release if the release authority gate remains pending.
- Do not change production authorization without actual release evidence.
- Only genuine external reviewer evidence may transition a gate to PASS.

## Release gate rule
Production authorization remains NOT AUTHORIZED unless a valid, independent release-authority review explicitly records approval after verifying all prerequisite gates.
