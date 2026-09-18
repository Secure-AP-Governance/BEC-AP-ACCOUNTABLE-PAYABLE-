from config.security_invariants import INVARIANTS, validate_invariants
from src.audit import AuditService
from src.bec_intelligence import BECIntelligenceService
from src.domain import Actor, Proposal
from src.erp import ERPRequestService
from src.operations_ui import OperationsView, WorkflowWorklists
from src.production_readiness import (
    AlertService,
    AuthenticatedOperations,
    AuthService,
    HealthService,
    MetricsService,
)
from time import time
from src.repositories import AuditRepository, IdempotencyRepository, ProposalRepository, QuarantineRepository, VendorRepository
from src.workflow import ApprovalService, ProposalService, TransitionEngine, VerificationService


class Application:
    def __init__(self):
        validate_invariants()
        self.proposals = ProposalRepository()
        self.audit_repo = AuditRepository()
        self.vendors = VendorRepository()
        self.idempotency = IdempotencyRepository()
        self.quarantine = QuarantineRepository()
        self.audit = AuditService(self.audit_repo)
        self.engine = TransitionEngine(self.proposals, self.vendors, self.audit)
        self.proposal = ProposalService(self.proposals, self.engine)
        self.verification = VerificationService(self.proposals, self.engine)
        self.approval = ApprovalService(self.proposals, self.engine)
        self.erp = ERPRequestService(self.proposals, self.engine, self.idempotency)
        self.bec = BECIntelligenceService(
            self.proposals,
            self.vendors,
            self.audit,
            self.proposal,
            self.quarantine,
        )
        self.operations = OperationsView(
            self.proposals,
            self.quarantine,
            self.audit_repo,
            self.security_status,
        )
        self.worklists = WorkflowWorklists(
            self.proposals,
            self.engine,
            self.verification,
            self.approval,
            self.audit_repo,
        )
        self.auth = AuthService(time)
        self.metrics = MetricsService()
        self.health = HealthService()
        self.alerts = AlertService()
        self.authenticated = AuthenticatedOperations(self.auth, self.operations, self.worklists)

    def health_status(self):
        return self.health.snapshot(self.proposals, self.audit, self.security_status)

    def metrics_snapshot(self):
        return self.metrics.snapshot(self.proposals, self.quarantine, self.idempotency, self.auth)

    def alert_snapshot(self):
        return self.alerts.snapshot(self.health_status(), self.metrics_snapshot())

    def create(self, proposal: Proposal):
        self.vendors.set_version(proposal.vendor_id, proposal.vendor_snapshot)
        return self.proposal.create(proposal)

    def audit_valid(self, proposal_id):
        return self.audit.valid(proposal_id)

    def security_status(self):
        return dict(INVARIANTS)
