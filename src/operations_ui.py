from src.domain import ProposalState, Role
from src.workflow import AuthorizationError, ValidationError


class OperationsView:
    """Read-only dashboard queries for operational visibility."""

    def __init__(self, proposals, quarantine, audit, security_status):
        self.proposals = proposals
        self.quarantine = quarantine
        self.audit = audit
        self.security_status = security_status

    def proposal_queue(self):
        return tuple(
            {
                "proposal_id": proposal.id,
                "state": proposal.state.value,
                "version": proposal.version,
                "vendor_id": proposal.vendor_id,
                "requester_id": proposal.requester_id,
            }
            for proposal in sorted(self.proposals.items.values(), key=lambda item: item.id)
        )

    def quarantine_queue(self):
        return tuple(
            {
                "quarantine_id": record.quarantine_id,
                "message_id": record.email.message_id,
                "subject": record.email.subject,
                "risk_score": record.analysis.risk_score,
                "factors": record.analysis.factors,
                "status": record.status,
            }
            for record in sorted(self.quarantine.items.values(), key=lambda item: item.quarantine_id)
        )

    def audit_explorer(self):
        return tuple(
            {
                "proposal_id": event.proposal_id,
                "actor_id": event.actor_id,
                "action": event.action,
                "previous_state": event.previous_state,
                "new_state": event.new_state,
                "previous_hash": event.previous_hash,
                "event_hash": event.event_hash,
            }
            for event in self.audit.all_events()
        )

    def security_dashboard(self):
        controls = self.security_status()
        return {
            "status": "PASS" if all(value is False for value in controls.values()) else "ALERT",
            "payment_execution_enabled": controls["PAYMENT_EXECUTION_ENABLED"],
            "automatic_payment_dispatch": controls["AUTOMATIC_PAYMENT_DISPATCH"],
            "automatic_bank_change": controls["AUTOMATIC_BANK_CHANGE"],
        }


class WorkflowWorklists:
    """Role-restricted Phase 2 worklists and workflow actions."""

    def __init__(self, proposals, engine, verification, approval, audit):
        self.proposals = proposals
        self.engine = engine
        self.verification = verification
        self.approval = approval
        self.audit = audit

    def verification_queue(self, actor, vendor_id=None):
        self._require_role(actor, Role.VERIFIER)
        return self._queue(ProposalState.VERIFICATION_PENDING, vendor_id)

    def approval_queue(self, actor, vendor_id=None):
        self._require_role(actor, Role.APPROVER)
        return self._queue(ProposalState.VERIFIED, vendor_id)

    def evidence_viewer(self, proposal_id, actor):
        self._require_participant(proposal_id, actor)
        proposal = self.proposals.get(proposal_id)
        return {
            "proposal_id": proposal.id,
            "evidence": tuple(proposal.evidence),
            "vendor_id": proposal.vendor_id,
            "state": proposal.state.value,
            "audit": tuple(self._audit_event(event) for event in self.audit.for_proposal(proposal_id)),
        }

    def risk_details(self, proposal_id, actor):
        self._require_participant(proposal_id, actor)
        proposal = self.proposals.get(proposal_id)
        return {
            "proposal_id": proposal.id,
            "risk_score": proposal.risk_score,
            "factors": tuple(
                evidence.removeprefix("risk-factor:")
                for evidence in proposal.evidence
                if evidence.startswith("risk-factor:")
            ),
            "state": proposal.state.value,
        }

    def verify(self, proposal_id, actor, expected_version):
        self._require_role(actor, Role.VERIFIER)
        return self.verification.verify(proposal_id, actor, expected_version)

    def approve(self, proposal_id, actor, expected_version):
        self._require_role(actor, Role.APPROVER)
        return self.approval.approve(proposal_id, actor, expected_version)

    def reject(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        if proposal.state == ProposalState.VERIFICATION_PENDING:
            self._require_independent_verifier(proposal, actor)
            action = "REJECT_VERIFICATION"
        elif proposal.state == ProposalState.VERIFIED:
            self._require_separate_approver(proposal, actor)
            action = "REJECT_APPROVAL"
        else:
            raise ValidationError("proposal is not awaiting rejection")
        return self.engine.move(proposal_id, actor, expected_version, ProposalState.REJECTED, action)

    def request_evidence(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        self._require_independent_verifier(proposal, actor)
        return self.engine.move(
            proposal_id,
            actor,
            expected_version,
            ProposalState.EVIDENCE_REQUESTED,
            "REQUEST_EVIDENCE",
        )

    def escalate(self, proposal_id, actor, expected_version):
        proposal = self.proposals.get(proposal_id)
        self._require_separate_approver(proposal, actor)
        return self.engine.move(
            proposal_id,
            actor,
            expected_version,
            ProposalState.ESCALATED,
            "ESCALATE",
        )

    def _queue(self, state, vendor_id):
        return tuple(
            {
                "proposal_id": proposal.id,
                "state": proposal.state.value,
                "version": proposal.version,
                "vendor_id": proposal.vendor_id,
                "risk_score": proposal.risk_score,
            }
            for proposal in sorted(self.proposals.items.values(), key=lambda item: item.id)
            if proposal.state == state and (vendor_id is None or proposal.vendor_id == vendor_id)
        )

    def _require_participant(self, proposal_id, actor):
        proposal = self.proposals.get(proposal_id)
        if actor.role == Role.ADMIN:
            return
        if actor.id not in (proposal.requester_id, proposal.verifier_id, proposal.approver_id):
            if actor.role == Role.VERIFIER and proposal.state in (
                ProposalState.VERIFICATION_PENDING,
                ProposalState.EVIDENCE_REQUESTED,
            ):
                return
            if actor.role == Role.APPROVER and proposal.state in (
                ProposalState.VERIFIED,
                ProposalState.ESCALATED,
            ):
                return
            raise AuthorizationError("proposal participant required")

    @staticmethod
    def _require_role(actor, role):
        if actor.role not in (role, Role.ADMIN):
            raise AuthorizationError(f"{role.value.lower()} role required")

    @staticmethod
    def _require_independent_verifier(proposal, actor):
        if actor.role not in (Role.VERIFIER, Role.ADMIN) or actor.id == proposal.requester_id:
            raise AuthorizationError("independent verifier required")

    @staticmethod
    def _require_separate_approver(proposal, actor):
        if actor.role not in (Role.APPROVER, Role.ADMIN) or actor.id in (proposal.requester_id, proposal.verifier_id):
            raise AuthorizationError("separate approver required")

    @staticmethod
    def _audit_event(event):
        return {
            "action": event.action,
            "actor_id": event.actor_id,
            "new_state": event.new_state,
            "event_hash": event.event_hash,
        }