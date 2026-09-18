from contextlib import contextmanager
from copy import deepcopy
from threading import RLock
from src.domain import AuditEvent, Proposal


class ConflictError(Exception):
    pass


class NotFoundError(Exception):
    pass


class ProposalRepository:
    def __init__(self):
        self.items = {}
        self.lock = RLock()

    @contextmanager
    def transaction(self):
        with self.lock:
            yield

    def get(self, proposal_id):
        with self.lock:
            if proposal_id not in self.items:
                raise NotFoundError(proposal_id)
            return deepcopy(self.items[proposal_id])

    def create(self, proposal):
        with self.lock:
            if proposal.id in self.items:
                raise ConflictError("proposal already exists")
            self.items[proposal.id] = deepcopy(proposal)
            return deepcopy(proposal)

    def save(self, proposal, expected_version):
        with self.lock:
            current = self.items.get(proposal.id)
            if current is None:
                raise NotFoundError(proposal.id)
            if current.version != expected_version:
                raise ConflictError("stale proposal version")
            self.items[proposal.id] = deepcopy(proposal)
            return deepcopy(proposal)


class AuditRepository:
    def __init__(self):
        self.events = {}
        self.lock = RLock()

    def append(self, event):
        with self.lock:
            self.events.setdefault(event.proposal_id, []).append(event)

    def for_proposal(self, proposal_id):
        with self.lock:
            return list(self.events.get(proposal_id, []))


class VendorRepository:
    def __init__(self):
        self.versions = {}

    def set_version(self, vendor_id, version):
        self.versions[vendor_id] = version

    def version(self, vendor_id):
        return self.versions.get(vendor_id, 1)


class IdempotencyRepository:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def put(self, key, value):
        self.values[key] = value
