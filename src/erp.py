from uuid import uuid4
from src.domain import ProposalState, Role
from src.workflow import AuthorizationError


class ERPRequestService:
    def __init__(self, proposals, engine, idempotency):
        self.proposals, self.engine, self.idempotency = proposals, engine, idempotency

    def request(self, proposal_id, actor, expected_version, key):
        prior = self.idempotency.get(key)
        if prior is not None:
            return prior
        proposal = self.proposals.get(proposal_id)
        if actor.role not in (Role.APPROVER, Role.ADMIN) or actor.id != proposal.approver_id:
            raise AuthorizationError("approver required")
        self.engine.move(proposal_id, actor, expected_version, ProposalState.ERP_UPDATE_REQUESTED, "ERP_UPDATE_REQUEST")
        result = {"request_id": str(uuid4()), "proposal_id": proposal_id, "status": "REQUESTED"}
        self.idempotency.put(key, result)
        return result
