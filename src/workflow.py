from dataclasses import replace

from src.domain import ProposalState, Role
from src.repositories import ConflictError


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


class TransitionEngine:
    allowed = {
        ProposalState.DRAFT: {ProposalState.VERIFICATION_PENDING},
        ProposalState.VERIFICATION_PENDING: {
            ProposalState.EVIDENCE_REQUESTED,
            ProposalState.REJECTED,
            ProposalState.VERIFIED,
        },
        ProposalState.EVIDENCE_REQUESTED: {ProposalState.VERIFICATION_PENDING},
        ProposalState.VERIFIED: {
            ProposalState.APPROVED,
            ProposalState.ESCALATED,
            ProposalState.REJECTED,
        },
        ProposalState.APPROVED: {ProposalState.ERP_UPDATE_REQUESTED},
    }

    def __init__(self, proposals, vendors, audit):
        self.proposals, self.vendors, self.audit = proposals, vendors, audit

    def move(self, proposal_id, actor, expected_version, target, action):
        with self.proposals.transaction():
            stored = self.proposals.get(proposal_id)
            if stored.version != expected_version:
                raise ConflictError("stale proposal version")
            if target not in self.allowed.get(stored.state, set()):
                raise ValidationError("invalid state transition")
            if target in (ProposalState.APPROVED, ProposalState.ERP_UPDATE_REQUESTED):
                if self.vendors.version(stored.vendor_id) != stored.vendor_snapshot:
                    raise ValidationError("vendor snapshot drift detected")

            old = stored.state
            event = self.audit.record(
                stored.id, actor.id, action, old.value, target.value, stored.last_hash
            )
            candidate = replace(
                stored,
                state=target,
                version=expected_version + 1,
                last_hash=event.event_hash,
            )
            self.proposals.save(candidate, expected_version)
            return candidate


class ProposalService:
    def __init__(self, proposals, engine):
        self.proposals, self.engine = proposals, engine

    def create(self, proposal):
        if not proposal.evidence:
            raise ValidationError("evidence is required")
        return self.proposals.create(proposal)

    def submit(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if actor.id != proposal.requester_id or actor.role not in (Role.REQUESTER, Role.ADMIN):
            raise AuthorizationError("requester required")
        return self.engine.move(
            proposal_id,
            actor,
            expected_version,
            ProposalState.VERIFICATION_PENDING,
            "SUBMIT",
        )


class VerificationService:
    def __init__(self, proposals, engine):
        self.proposals, self.engine = proposals, engine

    def verify(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if actor.role not in (Role.VERIFIER, Role.ADMIN) or actor.id == proposal.requester_id:
            raise AuthorizationError("independent verifier required")
        proposal.verifier_id = actor.id
        proposal.verified_snapshot = proposal.vendor_snapshot
        self.proposals.save(proposal, expected_version)
        result = self.engine.move(
            proposal_id,
            actor,
            expected_version,
            ProposalState.VERIFIED,
            "VERIFY",
        )
        return result


class ApprovalService:
    def __init__(self, proposals, engine):
        self.proposals, self.engine = proposals, engine

    def approve(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if actor.role not in (Role.APPROVER, Role.ADMIN) or actor.id in (proposal.requester_id, proposal.verifier_id):
            raise AuthorizationError("separate approver required")
        proposal.approver_id = actor.id
        self.proposals.save(proposal, expected_version)
        result = self.engine.move(
            proposal_id,
            actor,
            expected_version,
            ProposalState.APPROVED,
            "APPROVE",
        )
        return result
