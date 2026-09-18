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