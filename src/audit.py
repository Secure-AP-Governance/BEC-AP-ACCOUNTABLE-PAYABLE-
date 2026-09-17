import hashlib
import json
from src.domain import AuditEvent


class AuditService:
    def __init__(self, repository):
        self.repository = repository

    def record(self, proposal_id, actor_id, action, previous_state, new_state, previous_hash):
        data = {
            "proposal_id": proposal_id, "actor_id": actor_id, "action": action,
            "previous_state": previous_state, "new_state": new_state,
            "previous_hash": previous_hash,
        }
        digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
        event = AuditEvent(proposal_id, actor_id, action, previous_state, new_state, previous_hash, digest)
        self.repository.append(event)
        return event

    def valid(self, proposal_id):
        previous = ""
        for event in self.repository.for_proposal(proposal_id):
            data = {"proposal_id": event.proposal_id, "actor_id": event.actor_id,
                    "action": event.action, "previous_state": event.previous_state,
                    "new_state": event.new_state, "previous_hash": event.previous_hash}
            expected = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            previous = event.event_hash
        return True
