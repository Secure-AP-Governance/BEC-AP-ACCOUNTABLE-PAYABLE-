import unittest

from src.application import Application
from src.domain import Actor, Proposal, ProposalState, Role
from src.workflow import AuthorizationError


class WorkflowWorklistTests(unittest.TestCase):
    def setUp(self):
        self.app = Application()
        self.requester = Actor("requester", Role.REQUESTER)
        self.verifier = Actor("verifier", Role.VERIFIER)
        self.approver = Actor("approver", Role.APPROVER)
        self.other = Actor("other", Role.REQUESTER)
        self.app.create(Proposal("p1", "v1", "requester", 1, ["invoice:1", "risk-factor:failed_dmarc"], risk_score=30))
        self.app.proposal.submit("p1", self.requester, 1)

    def test_verification_queue_access(self):
        queue = self.app.worklists.verification_queue(self.verifier)
        self.assertEqual(queue[0]["proposal_id"], "p1")

    def test_approval_queue_access(self):
        self.app.worklists.verify("p1", self.verifier, 2)
        queue = self.app.worklists.approval_queue(self.approver)
        self.assertEqual(queue[0]["proposal_id"], "p1")

    def test_non_verifier_denied(self):
        with self.assertRaises(AuthorizationError):
            self.app.worklists.verification_queue(self.other)
        with self.assertRaises(AuthorizationError):
            self.app.worklists.verify("p1", self.other, 2)

    def test_non_approver_denied(self):
        self.app.worklists.verify("p1", self.verifier, 2)
        with self.assertRaises(AuthorizationError):
            self.app.worklists.approval_queue(self.other)
        with self.assertRaises(AuthorizationError):
            self.app.worklists.approve("p1", self.other, 3)

    def test_evidence_viewer_loads(self):
        details = self.app.worklists.evidence_viewer("p1", self.requester)
        self.assertEqual(details["evidence"], ("invoice:1", "risk-factor:failed_dmarc"))
        self.assertEqual(details["audit"][0]["action"], "SUBMIT")

    def test_risk_details_load(self):
        details = self.app.worklists.risk_details("p1", self.requester)
        self.assertEqual(details["risk_score"], 30)
        self.assertEqual(details["factors"], ("failed_dmarc",))

    def test_audit_linkage_visible(self):
        self.app.worklists.request_evidence("p1", self.verifier, 2)
        details = self.app.worklists.evidence_viewer("p1", self.verifier)
        self.assertEqual(details["audit"][-1]["action"], "REQUEST_EVIDENCE")
        self.assertTrue(self.app.audit_valid("p1"))

    def test_queue_filtering(self):
        self.assertEqual(self.app.worklists.verification_queue(self.verifier, vendor_id="other"), ())
        self.assertEqual(self.app.worklists.verification_queue(self.verifier, vendor_id="v1")[0]["state"], "VERIFICATION_PENDING")

    def test_verifier_rejects_and_approver_escalates(self):
        rejected = self.app.worklists.reject("p1", self.verifier, 2)
        self.assertEqual(rejected.state, ProposalState.REJECTED)

        self.app.create(Proposal("p2", "v1", "requester", 1, ["invoice:2"]))
        self.app.proposal.submit("p2", self.requester, 1)
        self.app.worklists.verify("p2", self.verifier, 2)
        escalated = self.app.worklists.escalate("p2", self.approver, 3)
        self.assertEqual(escalated.state, ProposalState.ESCALATED)


if __name__ == "__main__":
    unittest.main()