import unittest
from src.application import Application
from src.domain import Actor, Proposal, ProposalState, Role
from src.repositories import ConflictError
from src.workflow import AuthorizationError, ValidationError


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.requester = Actor("requester", Role.REQUESTER)
        self.verifier = Actor("verifier", Role.VERIFIER)
        self.approver = Actor("approver", Role.APPROVER)
        self.app.create(Proposal("p1", "v1", "requester", 1, ["email:1"]))

    def submit(self):
        return self.app.proposal.submit("p1", self.requester, 1)

    def test_happy_path_and_audit_chain(self):
        self.submit(); self.app.verification.verify("p1", self.verifier, 2)
        self.app.approval.approve("p1", self.approver, 3)
        result = self.app.erp.request("p1", self.approver, 4, "k1")
        self.assertEqual(result["status"], "REQUESTED")
        self.assertEqual(self.app.proposals.get("p1").state, ProposalState.ERP_UPDATE_REQUESTED)
        self.assertTrue(self.app.audit_valid("p1"))

    def test_requester_cannot_verify_or_approve(self):
        self.submit()
        with self.assertRaises(AuthorizationError): self.app.verification.verify("p1", self.requester, 2)
        with self.assertRaises(AuthorizationError): self.app.approval.approve("p1", self.requester, 2)

    def test_verifier_cannot_approve(self):
        self.submit(); self.app.verification.verify("p1", self.verifier, 2)
        with self.assertRaises(AuthorizationError): self.app.approval.approve("p1", self.verifier, 3)

    def test_snapshot_drift_and_stale_version(self):
        self.submit(); self.app.verification.verify("p1", self.verifier, 2)
        self.app.vendors.set_version("v1", 2)
        with self.assertRaises(ValidationError): self.app.approval.approve("p1", self.approver, 3)
        with self.assertRaises(ConflictError): self.app.approval.approve("p1", self.approver, 2)

    def test_idempotency(self):
        self.submit(); self.app.verification.verify("p1", self.verifier, 2); self.app.approval.approve("p1", self.approver, 3)
        first = self.app.erp.request("p1", self.approver, 4, "same")
        self.assertEqual(first, self.app.erp.request("p1", self.approver, 99, "same"))


if __name__ == "__main__": unittest.main()
