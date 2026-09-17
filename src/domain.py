from dataclasses import dataclass, field
from enum import Enum


class ProposalState(str, Enum):
    DRAFT = "DRAFT"
    VERIFICATION_PENDING = "VERIFICATION_PENDING"
    VERIFIED = "VERIFIED"
    APPROVED = "APPROVED"
    ERP_UPDATE_REQUESTED = "ERP_UPDATE_REQUESTED"


class Role(str, Enum):
    REQUESTER = "REQUESTER"
    VERIFIER = "VERIFIER"
    APPROVER = "APPROVER"
    ADMIN = "ADMIN"


@dataclass(frozen=True)
class Actor:
    id: str
    role: Role


@dataclass
class Proposal:
    id: str
    vendor_id: str
    requester_id: str
    vendor_snapshot: int
    evidence: list[str] = field(default_factory=list)
    state: ProposalState = ProposalState.DRAFT
    version: int = 1
    verifier_id: str | None = None
    approver_id: str | None = None
    last_hash: str = ""
    verified_snapshot: int | None = None


@dataclass(frozen=True)
class AuditEvent:
    proposal_id: str
    actor_id: str
    action: str
    previous_state: str
    new_state: str
    previous_hash: str
    event_hash: str
