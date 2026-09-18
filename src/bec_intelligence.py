from dataclasses import dataclass, field
from re import search

from src.domain import Proposal


@dataclass(frozen=True)
class EmailMessage:
    message_id: str
    sender: str
    reply_to: str
    subject: str
    headers: dict[str, str] = field(default_factory=dict)
    attachments: tuple[str, ...] = ()
    thread_id: str | None = None
    body: str = ""


@dataclass(frozen=True)
class AuthenticationSignals:
    spf: str
    dkim: str
    dmarc: str


@dataclass(frozen=True)
class VendorProfile:
    vendor_id: str
    name: str
    domains: frozenset[str]
    sender_addresses: frozenset[str]
    vendor_snapshot: int = 1


@dataclass(frozen=True)
class BECAnalysis:
    authentication: AuthenticationSignals
    factors: tuple[str, ...]
    risk_score: int
    bank_change_request: bool
    unknown_sender: bool
    unknown_domain: bool
    reply_to_mismatch: bool


@dataclass(frozen=True)
class QuarantineRecord:
    quarantine_id: str
    email: EmailMessage
    analysis: BECAnalysis
    status: str = "QUARANTINED"


class BECIntelligenceService:
    QUARANTINE_THRESHOLD = 60

    def __init__(self, proposals, vendors, audit, proposal_service, quarantine):
        self.proposals = proposals
        self.vendors = vendors
        self.audit = audit
        self.proposal_service = proposal_service
        self.quarantine = quarantine

    def analyze(self, email, authentication, vendor):
        sender_domain = self._domain(email.sender)
        reply_domain = self._domain(email.reply_to)
        unknown_sender = email.sender.lower() not in {
            address.lower() for address in vendor.sender_addresses
        }
        unknown_domain = sender_domain not in {
            domain.lower() for domain in vendor.domains
        }
        reply_to_mismatch = bool(email.reply_to) and reply_domain != sender_domain
        bank_change_request = bool(
            search(r"\b(bank|banking|account|wire|payment|remittance|routing)\b", email.subject + " " + email.body, flags=2)
            and search(r"\b(change|new|update|replace|confirm)\b", email.subject + " " + email.body, flags=2)
        )

        factors = []
        score = 0
        for name, value, weight in (
            ("failed_spf", authentication.spf, 15),
            ("failed_dkim", authentication.dkim, 15),
            ("failed_dmarc", authentication.dmarc, 30),
        ):
            if value.upper() != "PASS":
                factors.append(name)
                score += weight
        if unknown_sender:
            factors.append("unknown_sender")
            score += 10
        if unknown_domain:
            factors.append("unknown_domain")
            score += 10
        if reply_to_mismatch:
            factors.append("reply_to_mismatch")
            score += 20
        if bank_change_request:
            factors.append("bank_change_request")
            score += 30

        return BECAnalysis(
            authentication=authentication,
            factors=tuple(factors),
            risk_score=min(score, 100),
            bank_change_request=bank_change_request,
            unknown_sender=unknown_sender,
            unknown_domain=unknown_domain,
            reply_to_mismatch=reply_to_mismatch,
        )

    def ingest(self, email, authentication, vendor, requester_id):
        analysis = self.analyze(email, authentication, vendor)
        if analysis.risk_score >= self.QUARANTINE_THRESHOLD:
            record = QuarantineRecord(
                quarantine_id=f"quarantine:{email.message_id}",
                email=email,
                analysis=analysis,
            )
            self.quarantine.create(record)
            self.audit.record(
                record.quarantine_id,
                "bec-intelligence",
                "BEC_QUARANTINED",
                "EMAIL",
                record.status,
                "",
            )
            return record

        proposal = Proposal(
            id=f"email:{email.message_id}",
            vendor_id=vendor.vendor_id,
            requester_id=requester_id,
            vendor_snapshot=vendor.vendor_snapshot,
            evidence=[
                f"message-id:{email.message_id}",
                f"subject:{email.subject}",
                f"risk-score:{analysis.risk_score}",
                *(f"risk-factor:{factor}" for factor in analysis.factors),
            ],
            risk_score=analysis.risk_score,
        )
        created = self.proposal_service.create(proposal)
        event = self.audit.record(
            created.id,
            "bec-intelligence",
            "EMAIL_INGESTED",
            "EMAIL",
            created.state.value,
            created.last_hash,
        )
        created.last_hash = event.event_hash
        return self.proposals.save(created, created.version)

    @staticmethod
    def _domain(address):
        return address.rsplit("@", 1)[-1].lower() if "@" in address else ""