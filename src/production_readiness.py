from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from secrets import token_bytes, token_urlsafe

from src.domain import Actor, Role
from src.workflow import AuthorizationError


class AuthenticationError(Exception):
    pass


class SessionExpiredError(AuthenticationError):
    pass


@dataclass(frozen=True)
class UserAccount:
    user_id: str
    role: Role
    salt: bytes
    password_hash: bytes
    enabled: bool = True


@dataclass(frozen=True)
class Session:
    token: str
    user_id: str
    expires_at: float


class AuthService:
    def __init__(self, clock, session_ttl_seconds=900):
        self.clock = clock
        self.session_ttl_seconds = session_ttl_seconds
        self.users = {}
        self.sessions = {}
        self.failed_authentication_count = 0

    def register(self, user_id, role, password):
        salt = token_bytes(16)
        self.users[user_id] = UserAccount(
            user_id,
            role,
            salt,
            self._derive(password, salt),
        )

    def authenticate(self, user_id, password):
        account = self.users.get(user_id)
        if account is None or not account.enabled or self._derive(password, account.salt) != account.password_hash:
            self.failed_authentication_count += 1
            raise AuthenticationError("invalid credentials")
        token = token_urlsafe(24)
        session = Session(token, user_id, self.clock() + self.session_ttl_seconds)
        self.sessions[token] = session
        return session

    def authorize(self, token, required_role=None):
        session = self.sessions.get(token)
        if session is None:
            raise AuthenticationError("authentication required")
        if self.clock() >= session.expires_at:
            self.sessions.pop(token, None)
            raise SessionExpiredError("session expired")
        account = self.users.get(session.user_id)
        if account is None or not account.enabled:
            raise AuthenticationError("account unavailable")
        if required_role is not None and account.role not in (required_role, Role.ADMIN):
            raise AuthorizationError(f"{required_role.value.lower()} role required")
        return Actor(account.user_id, account.role)

    def logout(self, token):
        self.sessions.pop(token, None)

    @staticmethod
    def _derive(password, salt):
        return pbkdf2_hmac("sha256", password.encode(), salt, 120_000)


class MetricsService:
    def __init__(self):
        self.verification_latencies = []
        self.approval_latencies = []
        self.workflow_failures = 0
        self.high_risk_messages = 0

    def record_verification_latency(self, milliseconds):
        self.verification_latencies.append(milliseconds)

    def record_approval_latency(self, milliseconds):
        self.approval_latencies.append(milliseconds)

    def record_workflow_failure(self):
        self.workflow_failures += 1

    def record_high_risk_message(self):
        self.high_risk_messages += 1

    def snapshot(self, proposals, quarantine, idempotency, auth):
        return {
            "proposal_count": len(proposals.items),
            "quarantine_count": len(quarantine.items),
            "verification_latency_ms": self._average(self.verification_latencies),
            "approval_latency_ms": self._average(self.approval_latencies),
            "erp_request_volume": len(idempotency.values),
            "authentication_failures": auth.failed_authentication_count,
            "workflow_failures": self.workflow_failures,
            "high_risk_messages": self.high_risk_messages,
        }

    @staticmethod
    def _average(values):
        return sum(values) / len(values) if values else 0


class HealthService:
    def snapshot(self, proposals, audit, security_status):
        proposal_ids = list(proposals.items)
        audit_valid = all(audit.valid(proposal_id) for proposal_id in proposal_ids)
        invariants_valid = all(value is False for value in security_status().values())
        return {
            "status": "PASS" if audit_valid and invariants_valid else "FAIL",
            "audit_chain": "PASS" if audit_valid else "FAIL",
            "security_invariants": "PASS" if invariants_valid else "FAIL",
        }


class AlertService:
    def snapshot(self, health, metrics, high_risk_threshold=10, auth_failure_threshold=5):
        alerts = []
        if health["audit_chain"] != "PASS":
            alerts.append("AUDIT_CHAIN_FAILURE")
        if health["security_invariants"] != "PASS":
            alerts.append("SECURITY_INVARIANT_FAILURE")
        if metrics["high_risk_messages"] >= high_risk_threshold:
            alerts.append("HIGH_RISK_BEC_SURGE")
        if metrics["workflow_failures"]:
            alerts.append("WORKFLOW_PROCESSING_FAILURE")
        if metrics["authentication_failures"] >= auth_failure_threshold:
            alerts.append("AUTHENTICATION_ANOMALY")
        return tuple(alerts)


class AuthenticatedOperations:
    def __init__(self, auth, operations, worklists):
        self.auth = auth
        self.operations = operations
        self.worklists = worklists

    def proposal_queue(self, token):
        self.auth.authorize(token)
        return self.operations.proposal_queue()

    def quarantine_queue(self, token):
        self.auth.authorize(token)
        return self.operations.quarantine_queue()

    def audit_explorer(self, token):
        self.auth.authorize(token)
        return self.operations.audit_explorer()

    def security_dashboard(self, token):
        self.auth.authorize(token)
        return self.operations.security_dashboard()

    def verification_queue(self, token, vendor_id=None):
        return self.worklists.verification_queue(self.auth.authorize(token, Role.VERIFIER), vendor_id)

    def approval_queue(self, token, vendor_id=None):
        return self.worklists.approval_queue(self.auth.authorize(token, Role.APPROVER), vendor_id)

    def evidence_viewer(self, token, proposal_id):
        return self.worklists.evidence_viewer(proposal_id, self.auth.authorize(token))

    def risk_details(self, token, proposal_id):
        return self.worklists.risk_details(proposal_id, self.auth.authorize(token))

    def verify(self, token, proposal_id, expected_version):
        return self.worklists.verify(proposal_id, self.auth.authorize(token, Role.VERIFIER), expected_version)

    def approve(self, token, proposal_id, expected_version):
        return self.worklists.approve(proposal_id, self.auth.authorize(token, Role.APPROVER), expected_version)

    def reject(self, token, proposal_id, expected_version):
        return self.worklists.reject(proposal_id, self.auth.authorize(token), expected_version)

    def request_evidence(self, token, proposal_id, expected_version):
        return self.worklists.request_evidence(proposal_id, self.auth.authorize(token, Role.VERIFIER), expected_version)

    def escalate(self, token, proposal_id, expected_version):
        return self.worklists.escalate(proposal_id, self.auth.authorize(token, Role.APPROVER), expected_version)