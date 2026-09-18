import unittest

from src.application import Application
from src.domain import Actor, Proposal, Role
from src.production_readiness import AuthenticationError, SessionExpiredError
from src.workflow import AuthorizationError


class ProductionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.now = [1000.0]
        self.app = Application()
        self.app.auth.clock = lambda: self.now[0]
        self.app.auth.register("requester", Role.REQUESTER, "requester-secret")
        self.app.auth.register("verifier", Role.VERIFIER, "verifier-secret")
        self.app.auth.register("approver", Role.APPROVER, "approver-secret")
        self.app.create(Proposal("p1", "v1", "requester", 1, ["invoice:1"]))

    def test_authentication_required_for_ui_action(self):
        with self.assertRaises(AuthenticationError):
            self.app.authenticated.proposal_queue("missing-token")
        session = self.app.auth.authenticate("requester", "requester-secret")
        self.assertEqual(self.app.authenticated.proposal_queue(session.token)[0]["proposal_id"], "p1")

    def test_session_expiration(self):
        session = self.app.auth.authenticate("requester", "requester-secret")
        self.now[0] += self.app.auth.session_ttl_seconds
        with self.assertRaises(SessionExpiredError):
            self.app.authenticated.proposal_queue(session.token)

    def test_roles_enforced_server_side(self):
        requester = self.app.auth.authenticate("requester", "requester-secret")
        with self.assertRaises(AuthorizationError):
            self.app.authenticated.verification_queue(requester.token)
        verifier = self.app.auth.authenticate("verifier", "verifier-secret")
        self.app.authenticated.verification_queue(verifier.token)

    def test_health_and_metrics(self):
        health = self.app.health_status()
        self.assertEqual(health["status"], "PASS")
        metrics = self.app.metrics_snapshot()
        self.assertEqual(metrics["proposal_count"], 1)
        self.assertEqual(metrics["quarantine_count"], 0)
        self.assertEqual(self.app.alert_snapshot(), ())

    def test_authentication_failures_are_measured(self):
        for _ in range(5):
            with self.assertRaises(AuthenticationError):
                self.app.auth.authenticate("requester", "wrong")
        self.assertEqual(self.app.metrics_snapshot()["authentication_failures"], 5)
        self.assertIn("AUTHENTICATION_ANOMALY", self.app.alert_snapshot())


if __name__ == "__main__":
    unittest.main()