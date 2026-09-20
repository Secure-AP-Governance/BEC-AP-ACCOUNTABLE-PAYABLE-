# Reviewer Instructions

Each reviewer must independently verify the evidence for their gate before recording any decision.

## Required review record
Each reviewer must record all of the following in their review artifact:
- identity
- role
- date/time
- decision
- evidence references
- comments
- exceptions

## Independence requirement
A reviewer must not approve a gate based solely on another team’s approval. The gate must be assessed using project evidence, current repository state, and review of the relevant artifacts.

## Required decision values
Use only the following values when recording a decision:
- PASS
- PENDING
- PENDING_EXTERNAL_EVIDENCE
- BLOCKED
- REJECTED

## Evidence handling rules
- Do not fabricate signatures, review dates, or approvals.
- Do not record a PASS without evidence references.
- Do not approve a release if the release authority gate remains pending.
- Do not change production authorization without actual release evidence.

## Release gate rule
Production authorization remains NOT AUTHORIZED unless a valid, independent release-authority review explicitly records approval.
