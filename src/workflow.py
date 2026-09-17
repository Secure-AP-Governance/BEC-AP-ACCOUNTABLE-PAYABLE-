from src.domain import ProposalState, Role
from src.repositories import ConflictError


class AuthorizationError(Exception):
    pass


class ValidationError(Exception):
    pass


class TransitionEngine:
    allowed = {
        ProposalState.DRAFT: ProposalState.VERIFICATION_PENDING,
        ProposalState.VERIFICATION_PENDING: ProposalState.VERIFIED,
        ProposalState.VERIFIED: ProposalState.APPROVED,
        ProposalState.APPROVED: ProposalState.ERP_UPDATE_REQUESTED,
    }

    def __init__(self, proposals, vendors, audit):
        self.proposals, self.vendors, self.audit = proposals, vendors, audit

    def move(self, proposal_id, actor, expected_version, target, action):
        with self.proposals.transaction():
            proposal = self.proposals.get(proposal_id)
            if proposal.version != expected_version:
                raise ConflictError("stale proposal version")
            if self.allowed.get(proposal.state) != target:
                raise ValidationError("invalid state transition")
            if target in (ProposalState.APPROVED, ProposalState.ERP_UPDATE_REQUESTED):
                if self.vendors.version(proposal.vendor_id) != proposal.vendor_snapshot:
                    raise ValidationError("vendor snapshot drift detected")
            old = proposal.state
            event = self.audit.record(proposal.id, actor.id, action, old.value, target.value, proposal.last_hash)
            proposal.state = target
            proposal.version += 1
            proposal.last_hash = event.event_hash
            self.proposals.save(proposal, expected_version)
            return proposal


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
        return self.engine.move(proposal_id, actor, expected_version, ProposalState.VERIFICATION_PENDING, "SUBMIT")


class VerificationService:
    def __init__(self, proposals, engine):
        self.proposals, self.engine = proposals, engine

    def verify(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if actor.role not in (Role.VERIFIER, Role.ADMIN) or actor.id == proposal.requester_id:
            raise AuthorizationError("independent verifier required")
        proposal.verifier_id = actor.id
        result = self.engine.move(proposal_id, actor, expected_version, ProposalState.VERIFIED, "VERIFY")
        result.verified_snapshot = result.vendor_snapshot
        return result


class ApprovalService:
    def __init__(self, proposals, engine):
        self.proposals, self.engine = proposals, engine

    def approve(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if actor.role not in (Role.APPROVER, Role.ADMIN) or actor.id in (proposal.requester_id, proposal.verifier_id):
            raise AuthorizationError("separate approver required")
        proposal.approver_id = actor.id
        return self.engine.move(proposal_id, actor, expected_version, ProposalState.APPROVED, "APPROVE")
